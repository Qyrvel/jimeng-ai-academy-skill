"""Gate 2.1 offline normalization review validation; Python standard library only."""

import re
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE.parent / "assets/normalization-review.schema.json"
SOURCE = runpy.run_path(str(HERE / "validate_source_registry.py"))
read_json = SOURCE["read_json"]

RELATIONS = ("DISTINCT", "EXACT_DUPLICATE", "PARTIAL_OVERLAP", "VERSION_VARIANT", "SCOPE_PARALLEL", "CONFLICT_CANDIDATE")
DECISIONS = ("KEEP_SEPARATE", "MERGE_CANDIDATE", "NEEDS_REVIEW")
REQUIRED_FIELDS = ("review_id", "item_ids", "relation", "decision", "normalized_label", "rationale", "scope_check", "version_check", "provenance_check")
TEXT_FIELDS = ("review_id", "normalized_label", "rationale", "scope_check", "version_check", "provenance_check")

# relation -> decisions that the local contract allows
ALLOWED_DECISIONS = {
    "DISTINCT": ("KEEP_SEPARATE",),
    "EXACT_DUPLICATE": ("MERGE_CANDIDATE", "NEEDS_REVIEW"),
    "PARTIAL_OVERLAP": ("KEEP_SEPARATE", "NEEDS_REVIEW"),
    "VERSION_VARIANT": ("KEEP_SEPARATE",),
    "SCOPE_PARALLEL": ("KEEP_SEPARATE",),
    "CONFLICT_CANDIDATE": ("NEEDS_REVIEW",),
}


def text(value):
    return isinstance(value, str) and bool(value.strip())


def validate_reviews(data, knowledge):
    errors = []
    if not isinstance(data, dict) or set(data) != {"reviews"} or not isinstance(data["reviews"], list):
        return ["STRUCTURAL: root: expected an object containing only a reviews array"]
    known_ids = set()
    if isinstance(knowledge, dict) and isinstance(knowledge.get("items"), list):
        for item in knowledge["items"]:
            if isinstance(item, dict) and text(item.get("knowledge_id")):
                known_ids.add(item["knowledge_id"])
    seen_reviews = set()
    for index, review in enumerate(data["reviews"]):
        label = f"reviews[{index}]"
        if not isinstance(review, dict):
            errors.append(f"STRUCTURAL: {label}: must be an object")
            continue
        for field in REQUIRED_FIELDS:
            if field not in review:
                errors.append(f"STRUCTURAL: {label}: missing required field {field}")
        for field in sorted(set(review) - set(REQUIRED_FIELDS)):
            errors.append(f"STRUCTURAL: {label}: unexpected field {field}")
        for field in TEXT_FIELDS:
            if field in review and not text(review[field]):
                errors.append(f"STRUCTURAL: {label}.{field}: must be a non-blank string")
        review_id = review.get("review_id")
        if text(review_id):
            if review_id in seen_reviews:
                errors.append(f"STRUCTURAL: {label}.review_id: duplicate {review_id!r}")
            seen_reviews.add(review_id)
        item_ids = review.get("item_ids")
        if not isinstance(item_ids, list):
            errors.append(f"STRUCTURAL: {label}.item_ids: must be an array")
        else:
            if len(item_ids) < 2:
                errors.append(f"STRUCTURAL: {label}.item_ids: must contain at least 2 items")
            seen_items = set()
            for position, item_id in enumerate(item_ids):
                if not text(item_id):
                    errors.append(f"STRUCTURAL: {label}.item_ids[{position}]: must be a non-blank string")
                    continue
                if item_id in seen_items:
                    errors.append(f"STRUCTURAL: {label}.item_ids: duplicate item_id {item_id!r}")
                seen_items.add(item_id)
                if item_id not in known_ids:
                    errors.append(f"REFERENCE: {label}.item_ids: knowledge_id {item_id!r} does not exist in Knowledge Registry")
        relation = review.get("relation")
        decision = review.get("decision")
        if relation is not None and relation not in RELATIONS:
            errors.append(f"STRUCTURAL: {label}.relation: invalid value {relation!r}; allowed: {', '.join(RELATIONS)}")
        if decision is not None and decision not in DECISIONS:
            errors.append(f"STRUCTURAL: {label}.decision: invalid value {decision!r}; allowed: {', '.join(DECISIONS)}")
        if relation in ALLOWED_DECISIONS and decision in DECISIONS:
            if decision not in ALLOWED_DECISIONS[relation]:
                errors.append(
                    f"CONTRACT: {label}: relation {relation} requires decision "
                    + " or ".join(ALLOWED_DECISIONS[relation])
                    + f"; found {decision}"
                )
    return errors


def validate_schema_shape(data, schema):
    """Minimal check that the local schema itself still matches this validator's contract."""
    errors = []
    if not isinstance(schema, dict) or "reviews" not in schema.get("properties", {}):
        return ["STRUCTURAL: normalization schema is unreadable or missing the reviews property"]
    definition = schema.get("$defs", {}).get("review")
    if not isinstance(definition, dict):
        return ["STRUCTURAL: normalization schema is missing the review definition"]
    if tuple(definition.get("required", ())) != REQUIRED_FIELDS:
        errors.append("STRUCTURAL: normalization schema required fields differ from the validator contract")
    if tuple(definition.get("properties", {}).get("relation", {}).get("enum", ())) != RELATIONS:
        errors.append("STRUCTURAL: normalization schema relation enum differs from the validator contract")
    if tuple(definition.get("properties", {}).get("decision", {}).get("enum", ())) != DECISIONS:
        errors.append("STRUCTURAL: normalization schema decision enum differs from the validator contract")
    return errors


def validate_registry(data, knowledge, schema):
    shape_errors = validate_schema_shape(data, schema)
    if shape_errors:
        return shape_errors
    return validate_reviews(data, knowledge)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("FAIL")
        print("- Usage: python validate_normalization_review.py <normalization-review.json> <knowledge-registry.json>")
        return 1
    try:
        data = read_json(args[0])
        knowledge = read_json(args[1])
        schema = read_json(SCHEMA_PATH)
        errors = validate_registry(data, knowledge, schema)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"STRUCTURAL: unable to read or validate JSON: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
