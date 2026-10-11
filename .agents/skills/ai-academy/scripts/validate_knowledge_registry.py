"""Gate 2.0 offline validation; standard library and local Source Validator only."""

import re
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE.parent / "assets/knowledge-registry.schema.json"
SOURCE = runpy.run_path(str(HERE / "validate_source_registry.py"))
read_json = SOURCE["read_json"]


def check(value, rules, path, schema):
    """Only the local contract's object/array/string subset, not full JSON Schema."""
    if "$ref" in rules:
        rules = schema["$defs"][rules["$ref"].split("/")[-1]]
    errors = []
    label = f"STRUCTURAL: {path}"
    kind = rules["type"]
    if kind == "object":
        if not isinstance(value, dict):
            return [f"{label}: must be an object"]
        for field in rules["required"]:
            if field not in value:
                errors.append(f"{label}: missing required field {field}")
        properties = rules["properties"]
        for field in sorted(value.keys() - properties.keys()):
            errors.append(f"{label}: unexpected field {field}")
        for field, field_rules in properties.items():
            if field in value:
                errors.extend(check(value[field], field_rules, f"{path}.{field}", schema))
    elif kind == "array":
        if not isinstance(value, list):
            return [f"{label}: must be an array"]
        if len(value) < rules.get("minItems", 0):
            errors.append(f"{label}: must be a non-empty array")
        for index, entry in enumerate(value):
            errors.extend(check(entry, rules["items"], f"{path}[{index}]", schema))
    elif kind == "string":
        if not isinstance(value, str) or not value.strip():
            return [f"{label}: must be a non-blank string"]
        if "enum" in rules and value not in rules["enum"]:
            errors.append(f"{label}: invalid value {value!r}; allowed: {', '.join(rules['enum'])}")
    else:
        raise ValueError(f"Unsupported contract type: {kind}")
    return errors


def validate_structure(data, schema):
    errors = check(data, schema, "root", schema)
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        return errors
    seen_ids = set()
    for index, item in enumerate(data["items"]):
        if not isinstance(item, dict):
            continue
        kid = item.get("knowledge_id")
        if isinstance(kid, str) and kid.strip():
            if kid in seen_ids:
                errors.append(f"STRUCTURAL: items[{index}].knowledge_id: duplicate {kid!r}")
            seen_ids.add(kid)
        refs = item.get("evidence_refs")
        if not isinstance(refs, list):
            continue
        seen_refs = set()
        for ref_index, ref in enumerate(refs):
            sid = ref.get("source_id") if isinstance(ref, dict) else None
            if isinstance(sid, str) and sid.strip():
                if sid in seen_refs:
                    errors.append(f"STRUCTURAL: items[{index}].evidence_refs[{ref_index}]: duplicate source_id {sid!r}")
                seen_refs.add(sid)
    return errors


def validate_evidence(data, sources):
    """Inputs must first pass their respective structural validation."""
    errors = []
    by_id = {source["source_id"]: source for source in sources["sources"]}
    for index, item in enumerate(data["items"]):
        path = f"items[{index}]"
        accepted = []
        for ref in item["evidence_refs"]:
            sid = ref["source_id"]
            source = by_id.get(sid)
            if source is None:
                errors.append(f"PROVENANCE: {path}: source_id {sid!r} does not exist")
            elif source["status"] != "accepted":
                errors.append(f"PROVENANCE: {path}: source_id {sid!r} has status {source['status']!r}; required accepted")
            else:
                accepted.append(source)
        info = item["information_type"]
        if info in {"DOCUMENTED", "OBSERVED"}:
            if not any(source["information_type"] == info for source in accepted):
                errors.append(f"EPISTEMIC: {path}: {info} requires at least one accepted {info} source")
        elif info == "INFERRED":
            texts = [item["limitations"]] + [ref["support_note"] for ref in item["evidence_refs"]]
            if not any(re.search(r"INFERENCE_BOUNDARY:[ \t]*\S", text) for text in texts):
                errors.append(f"EPISTEMIC: {path}: INFERRED requires INFERENCE_BOUNDARY: followed by a non-blank explanation")
    return errors


def validate_registry(data, sources, schema, source_schema):
    errors = validate_structure(data, schema)
    if errors:
        return errors
    source_errors = SOURCE["validate_registry"](sources, source_schema)
    if source_errors:
        return [f"STRUCTURAL: source registry validation failed: {error}" for error in source_errors]
    return validate_evidence(data, sources)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("FAIL")
        print("- Usage: python validate_knowledge_registry.py <knowledge-registry.json> <source-registry.json>")
        return 1
    try:
        data = read_json(args[0])
        sources = read_json(args[1])
        schema = read_json(SCHEMA_PATH)
        source_schema = read_json(SOURCE["SCHEMA_PATH"])
        errors = validate_registry(data, sources, schema, source_schema)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"STRUCTURAL: unable to read or validate JSON: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
