"""Offline Gate 1.1 structural and semantic validator; Python standard library only."""

import json
import re
import sys
from datetime import date
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "assets/source-registry.schema.json"


def reject_constant(value):
    raise ValueError(f"Non-JSON numeric constant: {value}")


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON object key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(
        Path(path).read_text(encoding="utf-8-sig"),
        parse_constant=reject_constant,
        object_pairs_hook=unique_keys,
    )


def validate_structure(data, schema):
    # Implements this registry's fixed contract, not a general JSON Schema engine.
    errors = []
    if not isinstance(data, dict):
        return ["root: must be an object"]
    for key in data.keys() - {"sources"}:
        errors.append(f"root: unexpected field {key}")
    if "sources" not in data:
        return errors + ["root: missing required field sources"]
    if not isinstance(data["sources"], list):
        return errors + ["sources: must be an array"]

    definition = schema["$defs"]["source"]
    properties = definition["properties"]
    seen = {}
    for index, source in enumerate(data["sources"]):
        prefix = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        for field in definition["required"]:
            if field not in source:
                errors.append(f"{prefix}: missing required field {field}")
        for field in sorted(source.keys() - properties.keys()):
            errors.append(f"{prefix}: unexpected field {field}")
        for field, rules in properties.items():
            if field not in source:
                continue
            value = source[field]
            label = f"{prefix}.{field}"
            if rules.get("format") == "date":
                if value is None:
                    continue
                if not isinstance(value, str) or not re.fullmatch(rules["pattern"], value):
                    errors.append(f"{label}: must be YYYY-MM-DD or null")
                    continue
                try:
                    date.fromisoformat(value)
                except ValueError:
                    errors.append(f"{label}: invalid calendar date {value!r}")
                continue
            if not isinstance(value, str):
                errors.append(f"{label}: must be a string")
                continue
            if "enum" in rules and value not in rules["enum"]:
                errors.append(f"{label}: invalid value {value!r}; allowed: {', '.join(rules['enum'])}")
            elif rules.get("minLength") and not value.strip():
                errors.append(f"{label}: must not be empty or whitespace")
        source_id = source.get("source_id")
        if isinstance(source_id, str) and source_id.strip():
            if source_id in seen:
                errors.append(f"{prefix}.source_id: duplicate {source_id!r} (first at sources[{seen[source_id]}])")
            else:
                seen[source_id] = index
    return errors


def validate_semantics(data):
    """Check cross-field rules after structural validation has passed."""
    errors = []
    for index, source in enumerate(data["sources"]):
        prefix = f"SEMANTIC: sources[{index}]"
        status = source["status"]
        information_type = source["information_type"]
        if status == "accepted":
            if information_type == "UNVERIFIED":
                errors.append(f"{prefix}: accepted source cannot be UNVERIFIED")
            if source["trust_tier"] == "E":
                errors.append(f"{prefix}: accepted source cannot have trust_tier E")
            if source["last_verified_at"] is None:
                errors.append(f"{prefix}: accepted source requires non-null last_verified_at")
        if not source["notes"].strip():
            if information_type == "OBSERVED":
                errors.append(f"{prefix}: OBSERVED source requires non-blank notes describing the experiment or its record")
            if status == "rejected":
                errors.append(f"{prefix}: rejected source requires non-blank notes explaining rejection")
            if status in {"stale", "deprecated"}:
                errors.append(f"{prefix}: {status} source requires non-blank notes explaining why it is outdated or invalid")
    return errors


def validate_registry(data, schema):
    errors = validate_structure(data, schema)
    if errors:
        return errors
    return validate_semantics(data)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("FAIL")
        print("- Usage: python validate_source_registry.py <registry.json>")
        return 1
    try:
        schema = read_json(SCHEMA_PATH)
        data = read_json(args[0])
        errors = validate_registry(data, schema)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"Unable to read or validate JSON: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
