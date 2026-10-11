"""Offline baseline manifest and pilot regression checks; standard library only."""
import runpy
import subprocess
import sys
from pathlib import Path, PureWindowsPath

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DEFAULT = HERE.parent / "assets/graph-contract-baseline.json"
VALIDATORS = ["validate_knowledge_graph.py", "validate_graph_integrity.py",
              "validate_edge_review.py"]
FIELDS = {"contract_name", "baseline_version", "freeze_gate", "relation_types",
          "validators", "validated_pilots"}
INPUTS = {"graph", "knowledge", "normalization", "review"}
read_json = runpy.run_path(str(HERE / "validate_source_registry.py"))["read_json"]


def project_file(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("pilot paths must be non-blank strings")
    if Path(value).is_absolute() or PureWindowsPath(value).drive:
        raise ValueError("pilot paths must be project-relative")
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f"missing or out-of-project file: {value}")
    return path


def check_manifest(data):
    if not isinstance(data, dict) or set(data) != FIELDS:
        raise ValueError("manifest must contain exactly the six baseline fields")
    for key, expected in [("contract_name", "ai-academy-knowledge-graph"),
                          ("baseline_version", "1.0"), ("freeze_gate", "Gate 3.3")]:
        if data[key] != expected:
            raise ValueError(f"{key}: expected {expected!r}")
    relations = data["relation_types"]
    if not isinstance(relations, list) or not all(isinstance(r, str) for r in relations):
        raise ValueError("relation_types must be an array of strings")
    if len(relations) != len(set(relations)):
        raise ValueError("relation_types contains duplicates")
    schema = read_json(HERE.parent / "assets/knowledge-graph.schema.json")
    if relations != schema["$defs"]["edge"]["properties"]["relation"]["enum"]:
        raise ValueError("relation_types differs from Schema enum (including order)")
    if data["validators"] != VALIDATORS:
        raise ValueError("validators must list the three official validators in order")
    for name in VALIDATORS:
        if not (HERE / name).is_file():
            raise ValueError(f"missing validator: {name}")
    pilots = data["validated_pilots"]
    if not isinstance(pilots, list) or len(pilots) < 2:
        raise ValueError("validated_pilots must contain at least two pilots")
    resolved, seen = [], set()
    for pilot in pilots:
        if not isinstance(pilot, dict) or set(pilot) != INPUTS:
            raise ValueError("each pilot requires graph, knowledge, normalization, review")
        paths = {key: project_file(pilot[key]) for key in sorted(INPUTS)}
        if paths["graph"] in seen:
            raise ValueError("duplicate pilot graph")
        seen.add(paths["graph"])
        resolved.append(paths)
    return resolved


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    errors = []
    try:
        if len(args) > 1:
            raise ValueError("Usage: python validate_graph_contract_baseline.py [baseline.json]")
        pilots = check_manifest(read_json(args[0] if args else DEFAULT))
        for p in pilots:
            calls = [(VALIDATORS[0], [p["graph"], p["knowledge"], p["normalization"]]),
                     (VALIDATORS[1], [p["graph"], p["knowledge"]]),
                     (VALIDATORS[2], [p["review"], p["graph"]]),
                     (VALIDATORS[2], [p["review"], p["graph"], "--final"])]
            for script, inputs in calls:
                command = [sys.executable, "-X", "utf8", str(HERE / script), *map(str, inputs)]
                result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                        text=True, encoding="utf-8", timeout=60)
                label = f"{p['graph'].name}: {script}" + (" --final" if "--final" in inputs else "")
                passed = result.returncode == 0 and result.stdout.splitlines()[:1] == ["PASS"]
                print(f"{label}: {'PASS' if passed else 'FAIL'}")
                if not passed:
                    errors.append(f"{label}: exit={result.returncode}; "
                                  f"stdout={result.stdout.strip()!r}; stderr={result.stderr.strip()!r}")
    except (OSError, ValueError, KeyError, TypeError, RecursionError,
            subprocess.TimeoutExpired) as exc:
        errors.append(str(exc))
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
