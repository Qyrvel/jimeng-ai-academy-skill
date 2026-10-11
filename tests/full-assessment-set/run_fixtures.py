"""Run every tests/full-assessment-set/ fixture and compare with its declared expectation.

Usage:
  python tests/full-assessment-set/run_fixtures.py [fixture-name ...] [--verbose]
  python tests/full-assessment-set/run_fixtures.py --emit

--emit prints every generated file (including the shared _baseline package) so it can be persisted
verbatim; the default mode runs the validator against the fixture manifests.

For each fixture the runner:
  1. runs validate_full_assessment_set.py with the fixture's declared inputs and mutation,
  2. records stdout, stderr, exit code, expected verdict and every observed diagnostic code,
  3. decides MATCH with the strict declared-code policy below.

Strict declared-code policy (Gate 4.7A-CONT7-R3A-CONT2-R2)
----------------------------------------------------------
A fixture is a MATCH only when all three hold:

    required_codes  <=  observed_codes
    observed_codes  <=  (required_codes | allowed_companion_codes)
    exit code       ==  expected_exit

and when every diagnostic head the runner cannot attribute to a validator code is absent.  An
observed code that no declaration allows is an UNEXPECTED code and makes the fixture a MISMATCH;
`MATCH` next to `UNEXPECTED codes` is not a reachable state.  The runner never trusts the declared
expectation alone and never edits an expectation to match an observation.
"""

import ast
import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = Path(__file__).resolve().parent
VALIDATOR = ROOT / ".agents/skills/ai-academy/scripts/validate_full_assessment_set.py"
CANONICAL_SET = ROOT / "academy-data/jimeng/assessment/full-assessments/full-assessment-set.json"

sys.path.insert(0, str(FIXTURE_ROOT))
import generate_fixtures  # noqa: E402


def validator_codes():
    """Diagnostic codes read out of the validator source, not guessed from the message text.

    The validator keys every diagnostic on a code constant; the runner must recognise each one
    even when the message that follows begins with non-Latin text (CJK fixture evidence), which
    a case/shape heuristic silently drops.
    """
    tree = ast.parse(io.open(VALIDATOR, encoding="utf-8").read())
    codes = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            function = node.func.id if isinstance(node.func, ast.Name) else None
            if function in ("fail", "append") and node.args:
                first = node.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    text = first.value
                    if text and text == text.upper() and text.replace("_", "").isalpha():
                        codes.add(text)
        elif isinstance(node, ast.Tuple):
            for element in node.elts:
                if isinstance(element, ast.Constant) and isinstance(element.value, str):
                    text = element.value
                    if text and text == text.upper() and " " not in text \
                            and text.replace("_", "").isalpha():
                        codes.add(text)
    return codes


VALIDATOR_DIAGNOSTIC_CODES = validator_codes()

# Fixed report field names printed by the validator before its diagnostic list.
REPORT_FIELDS = {
    "FULL_SET_VALIDATOR", "SET_IDENTITY", "COURSE_IDENTITY", "CANONICAL_ASSESSMENT_COUNT",
    "CANONICAL_ASSESSMENT_VALIDATOR_PASS_COUNT",
    "CANONICAL_ASSESSMENT_MARKDOWN_CONSISTENCY_PASS_COUNT", "PILOT_SOURCE_ASSESSMENT_COUNT",
    "PROMOTED_CANONICAL_PILOT_COUNT", "PILOT_PROMOTION_SEMANTIC_DIFF_COUNT",
    "COVERED_REQUIRED_REQUIREMENT_COUNT", "UNCOVERED_REQUIRED_REQUIREMENT_COUNT",
    "COVERED_LEARNER_OUTCOME_COUNT", "UNCOVERED_LEARNER_OUTCOME_COUNT",
    "DERIVED_METRIC_MISMATCH_COUNT", "NON_ORDER_ASSESSMENT_PREREQUISITE_MISUSE_COUNT",
    "MASTERY_DECISION_REACHABILITY", "COVERAGE_MANIFEST_SHA256",
    "UNCOVERED_LEARNER_OUTCOME_REF", "COVERED_REQUIREMENT_IDS", "COVERED_LEARNER_OUTCOME_REFS",
}


def read_json(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def set_manifest_path(fixture):
    if fixture.get("set_manifest_mode") == "canonical":
        return CANONICAL_SET
    return ROOT / fixture["set_manifest"]


def run(fixture):
    set_path = set_manifest_path(fixture)
    if fixture.get("set_manifest_mode") != "canonical":
        set_path.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-X", "utf8", str(VALIDATOR), str(set_path)]
    for key, value in sorted((fixture.get("inputs") or {}).items()):
        if value is None:
            continue
        command.append(key)
        # --graphs is variadic in the validator: pass every graph as its own token, exactly as
        # the usage string advertises.  No comma-joined collapsing happens here.
        tokens = value if isinstance(value, (list, tuple)) else [value]
        for token in tokens:
            for item in str(token).split(","):
                if not item:
                    continue
                candidate = ROOT / item
                command.append(str(candidate) if candidate.exists() else item)
    mutation_rel = fixture.get("mutation_descriptor")
    if mutation_rel and fixture.get("set_manifest_mode") != "canonical":
        descriptor = ROOT / mutation_rel
        if descriptor.is_file():
            command += ["--apply-mutation", str(descriptor)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=600)
    stdout = (result.stdout or "").strip()
    lines = [line for line in stdout.splitlines() if line.strip()]
    codes = set()
    unknown_heads = set()
    for line in lines:
        if not line.startswith("- ") or ": " not in line:
            continue
        head = line[2:].split(": ", 1)[0].strip()
        if not head or " " in head or not head.isupper():
            continue
        if head in REPORT_FIELDS:
            continue
        if head not in VALIDATOR_DIAGNOSTIC_CODES:
            unknown_heads.add(head)
            continue
        codes.add(head)
    codes = sorted(codes)
    first = lines[0] if lines else ""
    expected_exit = fixture.get("expected_exit", 0)
    required = set(fixture.get("expected_codes") or [])
    allowed = required | set(fixture.get("companion_codes") or [])
    observed = set(codes)
    missing = sorted(required - observed)
    unexpected = sorted(observed - allowed)
    exit_ok = result.returncode == expected_exit
    # Strict acceptance: required codes present, no undeclared code present, exit as declared, and
    # no diagnostic head the runner could not attribute to a validator code.
    ok = exit_ok and not missing and not unexpected and not unknown_heads
    return {
        "fixture": fixture["fixture"],
        "command": " ".join(command),
        "stdout": stdout,
        "stderr": (result.stderr or "").strip(),
        "output_lines": lines,
        "exit": result.returncode,
        "expected_exit": expected_exit,
        "expected": fixture.get("expected"),
        "actual": "PASS" if result.returncode == 0 else "FAIL",
        "expected_codes": sorted(required),
        "companion_codes": sorted(set(fixture.get("companion_codes") or [])),
        "allowed_codes": sorted(allowed),
        "unexpected_codes": unexpected,
        "unknown_codes": sorted(unknown_heads),
        "observed_codes": codes,
        "missing_codes": missing,
        "verdict": "MATCH" if ok else "MISMATCH",
    }


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    verbose = "--verbose" in args
    emit = "--emit" in args
    wanted = [a for a in args if not a.startswith("--")]
    index = generate_fixtures.build_index()
    fixtures = [f for f in index["fixtures"] if not wanted or f["fixture"] in wanted]

    if emit:
        for path, text in generate_fixtures.fixture_files():
            print(f"=== FILE {path} ===")
            sys.stdout.write(text if text.endswith("\n") else text + "\n")
        print(f"=== SUMMARY {len(fixtures)} fixtures ===")
        return 0

    results = [run(fixture) for fixture in fixtures]

    matched = 0
    unexpected_fixtures = 0
    for item in results:
        if item["unexpected_codes"]:
            unexpected_fixtures += 1
        print(f"FIXTURE: {item['fixture']}")
        print(f"  command: {item['command']}")
        print(f"  stdout[0]: {item['output_lines'][0] if item['output_lines'] else ''}")
        print(f"  exit: {item['exit']} (expected {item['expected_exit']})")
        print(f"  expected: {item['expected']}  actual: {item['actual']}")
        print(f"  required codes: {item['expected_codes']}")
        if item["companion_codes"]:
            print(f"  allowed companion codes: {item['companion_codes']}")
        print(f"  observed codes: {item['observed_codes']}")
        if item["missing_codes"]:
            print(f"  MISSING required codes: {item['missing_codes']}")
        if item["unexpected_codes"]:
            print(f"  UNEXPECTED codes: {item['unexpected_codes']}")
        if item["unknown_codes"]:
            print(f"  UNATTRIBUTED diagnostic heads: {item['unknown_codes']}")
        print(f"  verdict: {item['verdict']}")
        if verbose:
            for line in item["output_lines"]:
                print(f"    {line}")
            if item["stderr"]:
                print(f"    stderr: {item['stderr']}")
        if item["verdict"] == "MATCH":
            matched += 1
    print(f"FULL_SET_FIXTURE_COUNT_THIS_ROUND: {len(results)}")
    print(f"FULL_SET_FIXTURE_EXPECTATION_MATCH_COUNT_THIS_ROUND: {matched}")
    print(f"UNEXPECTED_CODE_FIXTURE_COUNT_THIS_ROUND: {unexpected_fixtures}")
    print(f"CRITICAL_FULL_SET_FIXTURES: {'PASS' if matched == len(results) else 'FAIL'}")
    return 0 if matched == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
