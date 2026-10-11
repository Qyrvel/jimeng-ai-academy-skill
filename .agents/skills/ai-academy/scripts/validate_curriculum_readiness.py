"""Structural assessment checks only; Python standard library, no semantic NLP."""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
read_json = runpy.run_path(str(HERE / "validate_source_registry.py"))["read_json"]
SCHEMA = HERE.parent / "assets/curriculum-readiness.schema.json"


def structure(value, schema, path, errors):
    kind = schema["type"]
    if not isinstance(value, {"object": dict, "array": list, "string": str}[kind]):
        errors.append(f"STRUCTURAL: {path}: expected {kind}")
        return
    if kind == "object":
        for key in schema["required"]:
            if key not in value:
                errors.append(f"STRUCTURAL: {path}: missing {key}")
        for key in value:
            if key not in schema["properties"]:
                errors.append(f"STRUCTURAL: {path}: unknown field {key}")
            else:
                structure(value[key], schema["properties"][key], f"{path}.{key}", errors)
    elif kind == "array":
        if len(value) < schema.get("minItems", 0):
            errors.append(f"STRUCTURAL: {path}: too few items")
        for i, item in enumerate(value):
            structure(item, schema["items"], f"{path}[{i}]", errors)
    else:
        if not value.strip():
            errors.append(f"STRUCTURAL: {path}: blank text")
        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"STRUCTURAL: {path}: invalid enum {value!r}")


def validate(data, schema):
    errors = []
    structure(data, schema, "root", errors)
    if errors:
        return errors
    def fail(message):
        errors.append("CONSISTENCY: " + message)
    domains = {}
    for d in data["domains"]:
        if d["domain_id"] in domains:
            fail("duplicate domain_id " + d["domain_id"])
        domains[d["domain_id"]] = d
    seen, by_domain = set(), {}
    engines = {"SOURCE_GAP": "SOURCE_ENGINE", "KNOWLEDGE_INGESTION_GAP": "KNOWLEDGE_ENGINE",
               "GRAPH_DATA_GAP": "GRAPH_DATA_EXPANSION"}
    for g in data["blocking_gaps"]:
        if g["gap_id"] in seen:
            fail("duplicate gap_id " + g["gap_id"])
        seen.add(g["gap_id"])
        if g["domain_id"] not in domains:
            fail(g["gap_id"] + ": unknown domain_id")
        by_domain.setdefault(g["domain_id"], []).append(g)
        if engines[g["gap_type"]] != g["next_engine"]:
            fail(g["gap_id"] + ": gap_type / next_engine mismatch")
    for key, d in domains.items():
        gaps = by_domain.get(key, [])
        status, decision, criticality = d["status"], d["decision"], d["criticality"]
        blocking = decision in ("TARGETED_INGESTION_FIRST", "GRAPH_DATA_EXPANSION_FIRST")
        if status == "READY" and (blocking or gaps):
            fail(key + ": READY cannot have blocking decision or gap")
        if status == "BLOCKED" and not gaps:
            fail(key + ": BLOCKED requires a blocking gap")
        if bool(gaps) != blocking:
            fail(key + ": blocking gaps and decision must agree")
        if decision == "TARGETED_INGESTION_FIRST" and not any(g["gap_type"] != "GRAPH_DATA_GAP" for g in gaps):
            fail(key + ": targeted decision requires source or knowledge gap")
        if decision == "GRAPH_DATA_EXPANSION_FIRST" and (not gaps or any(g["gap_type"] != "GRAPH_DATA_GAP" for g in gaps)):
            fail(key + ": graph decision requires only graph gaps")
        for c, choice in [("DYNAMIC", "DEFER_DYNAMIC"), ("OPTIONAL", "DEFER_OPTIONAL")]:
            if decision == choice and criticality != c:
                fail(key + ": defer decision / criticality mismatch")
        if (criticality == "OUT_OF_SCOPE") != (status == "NOT_APPLICABLE") or (status == "NOT_APPLICABLE") != (decision == "NOT_APPLICABLE"):
            fail(key + ": OUT_OF_SCOPE / NOT_APPLICABLE must agree")
        if criticality in ("FOUNDATIONAL", "CORE") and status != "READY" and not gaps:
            fail(key + ": non-ready core domain requires an explicit blocking gap")
    verdict = data["track_verdict"]
    core = [d for d in domains.values() if d["criticality"] in ("FOUNDATIONAL", "CORE")]
    if not core:
        fail("track requires a FOUNDATIONAL or CORE domain")
    if verdict == "READY_FOR_CURRICULUM_DESIGN" and (data["blocking_gaps"] or any(d["status"] != "READY" for d in core)):
        fail("ready track cannot have blocking gaps or non-ready core domains")
    if verdict == "READY_AFTER_TARGETED_INGESTION" and not any(by_domain.get(d["domain_id"]) for d in core):
        fail("targeted verdict requires a core blocking gap")
    return errors


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    try:
        if len(args) != 1:
            raise ValueError("Usage: python validate_curriculum_readiness.py <assessment.json>")
        errors = validate(read_json(args[0]), read_json(SCHEMA))
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"STRUCTURAL: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print("- " + error)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
