"""Assessment spec validation; Python standard library only.

Usage:
  python validate_assessment.py <assessment.json|pack.json> <course-manifest.json> <knowledge-registry.json>

Assessment mode (assessment-policy.md / gate 4.5 sections 29-33, 42):
  Identity     1 assessment_id format, 2 status = pilot, 3 assessment_type in the 7 allowed types,
               4 lesson_ids reference canonical lessons of the course
  Alignment    5 target_outcomes subset of union(lesson.learner_outcomes),
               6 knowledge_refs subset of union(lesson.knowledge_refs),
               7 lesson_pair_reason required when 2 lessons are referenced
  Scope        8 scope not wider than the referenced lesson scope
  Task         9 task non-empty, 10 expected_evidence non-empty
  Criteria    11 criteria non-empty, 12 criterion_id unique, 13 weight > 0,
              14 pass_condition non-empty, 15 evidence_source non-empty,
              16 max_score == sum(weight), 17 pass_score <= max_score
  Alignment   18 alignment.completion_check_alignment in the 3 allowed relations (UNRELATED is not),
              19 alignment.rationale non-empty

Pack mode (input has pack_id):
  Pack        20 required pack fields, 21 assessment_order <-> assessment_files one-to-one,
              22 every assessment file loads and validates, 23 assessment_id unique across the pack,
              24 assessment lesson_ids are course lessons

It never judges whether an outcome is genuinely observable or whether a task is fair.
"""

import re
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
read_json = runpy.run_path(str(HERE / "validate_source_registry.py"))["read_json"]
SCHEMA = HERE.parent / "assets/assessment.schema.json"

TYPES = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
WIDENING_MARKERS = ("所有客户端", "全部客户端", "永久", "所有账号", "全部账号", "所有版本", "任何客户端", "所有地区")
PACK_REQUIRED = ("pack_id", "course_id", "status", "assessment_order", "assessment_files",
                 "coverage_summary", "alignment_summary")


def structure(value, schema, path, errors):
    kind = schema["type"]
    if kind == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"STRUCTURAL: {path}: expected integer")
            return
    elif not isinstance(value, TYPES[kind]):
        errors.append(f"STRUCTURAL: {path}: expected {kind}")
        return
    if kind == "object":
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"STRUCTURAL: {path}: missing {key}")
        additional = schema.get("additionalProperties")
        for key in value:
            if key in properties:
                structure(value[key], properties[key], f"{path}.{key}", errors)
            elif isinstance(additional, dict):
                structure(value[key], additional, f"{path}.{key}", errors)
            else:
                errors.append(f"STRUCTURAL: {path}: unknown field {key}")
    elif kind == "array":
        if len(value) < schema.get("minItems", 0):
            errors.append(f"STRUCTURAL: {path}: too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"STRUCTURAL: {path}: too many items")
        for i, item in enumerate(value):
            structure(item, schema["items"], f"{path}[{i}]", errors)
    else:
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"STRUCTURAL: {path}: blank or malformed text")
        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"STRUCTURAL: {path}: invalid enum {value!r}")


def load_course(manifest_path):
    manifest = read_json(str(manifest_path))
    root = Path(manifest_path).resolve().parent
    lessons = {}
    for entry in manifest["lesson_files"]:
        lessons[entry["lesson_id"]] = read_json(str((root / entry["json_path"]).resolve()))
    return manifest, lessons


def validate_assessment(data, schema, lessons, known_knowledge, label="assessment"):
    errors = []
    structure(data, schema, label, errors)
    if errors:
        return errors

    def fail(message):
        errors.append(f"CONSISTENCY: {label}: {message}")

    refs = [lessons[lid] for lid in data["lesson_ids"] if lid in lessons]
    for lid in data["lesson_ids"]:
        if lid not in lessons:
            fail(f"lesson_id {lid!r} is not a canonical lesson of this course")
    if not refs:
        return errors

    goals = {o for lesson in refs for o in lesson["learner_outcomes"]}
    for outcome in data["target_outcomes"]:
        if outcome not in goals:
            fail(f"target_outcome {outcome!r} is not a learner_outcome of the referenced lessons")
    allowed_knowledge = {k for lesson in refs for k in lesson["knowledge_refs"]}
    for ref in data["knowledge_refs"]:
        if ref not in allowed_knowledge:
            fail(f"knowledge_ref {ref!r} is outside the referenced lessons' knowledge_refs")
        if ref not in known_knowledge:
            fail(f"knowledge_ref {ref!r} does not exist in the registry")

    if len(data["lesson_ids"]) == 2 and data.get("lesson_pair_reason") in (None, "NOT_APPLICABLE"):
        fail("two-lesson assessments must give lesson_pair_reason SEQUENCE_PAIR or INTEGRATED_SKILL")
    if len(data["lesson_ids"]) == 1 and data.get("lesson_pair_reason") not in (None, "NOT_APPLICABLE"):
        fail("single-lesson assessments must not claim a lesson_pair_reason")

    lesson_scope = " ".join(lesson["scope"] for lesson in refs)
    for marker in WIDENING_MARKERS:
        if marker in data["scope"] and marker not in lesson_scope:
            fail(f"scope appears wider than the lesson scope (marker {marker!r})")

    ids = [c["criterion_id"] for c in data["scoring_criteria"]]
    if len(set(ids)) != len(ids):
        fail("criterion_id must be unique inside one assessment")
    total = sum(c["weight"] for c in data["scoring_criteria"])
    if data["max_score"] != total:
        fail(f"max_score: expected sum(weight) = {total}; found {data['max_score']}")
    if data["pass_score"] > data["max_score"]:
        fail(f"pass_score {data['pass_score']} exceeds max_score {data['max_score']}")
    return errors


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 3:
        print("FAIL")
        print("- Usage: python validate_assessment.py <assessment.json|pack.json> "
              "<course-manifest.json> <knowledge-registry.json>")
        return 1
    try:
        data = read_json(args[0])
        manifest, lessons = load_course(Path(args[1]).resolve())
        knowledge = read_json(args[2])
        schema = read_json(str(SCHEMA))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("FAIL")
        print(f"- STRUCTURAL: unable to read input: {exc}")
        return 1
    known_knowledge = {item["knowledge_id"] for item in knowledge["items"]}

    if isinstance(data, dict) and "pack_id" in data:
        errors = []
        for field in PACK_REQUIRED:
            if field not in data:
                errors.append(f"STRUCTURAL: pack: missing {field}")
        if errors:
            print("FAIL")
            for e in errors:
                print("- " + e)
            return 1
        if data["status"] != "pilot":
            errors.append(f"CONSISTENCY: pack: status must be 'pilot'; found {data['status']!r}")
        if data["course_id"] != manifest["course_id"]:
            errors.append(f"CONSISTENCY: pack: course_id != course manifest ({manifest['course_id']!r})")
        order, files = data["assessment_order"], data["assessment_files"]
        if len(set(order)) != len(order):
            errors.append("CONSISTENCY: pack: assessment_order contains duplicates")
        if set(order) != set(files):
            errors.append("CONSISTENCY: pack: assessment_order and assessment_files must correspond one-to-one")
        base = Path(args[0]).resolve().parent
        seen = set()
        for aid in order:
            rel = files.get(aid)
            if not isinstance(rel, str):
                errors.append(f"CONSISTENCY: pack: {aid} has no file entry")
                continue
            path = (base / rel).resolve()
            if not path.is_file():
                errors.append(f"CONSISTENCY: pack: {aid} file not found at {rel}")
                continue
            assessment = read_json(str(path))
            if assessment.get("assessment_id") != aid:
                errors.append(f"CONSISTENCY: pack: {aid} file declares {assessment.get('assessment_id')!r}")
            if aid in seen:
                errors.append(f"CONSISTENCY: pack: duplicate assessment_id {aid}")
            seen.add(aid)
            errors.extend(validate_assessment(assessment, schema, lessons, known_knowledge, label=aid))
    else:
        errors = validate_assessment(data, schema, lessons, known_knowledge)

    print("FAIL" if errors else "PASS")
    for error in errors:
        print("- " + error)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
