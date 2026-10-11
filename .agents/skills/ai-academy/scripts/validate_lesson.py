"""Lesson and pilot-pack structural validation; Python standard library only.

Usage:
  python validate_lesson.py <lesson.json|pack.json> <blueprint.json> <knowledge-registry.json> [graph.json ...]

Single lesson mode (lesson-policy.md / gate 4.3 section 24):
  Identity        1 lesson_id exists in blueprint, 2 module_id matches, 3 title matches,
                  4 lesson_role matches, 5 status=pilot
  Grounding       6 learner_outcomes do not exceed blueprint, 7 knowledge_refs are a subset of
                  the blueprint lesson refs, 8 lesson references all blueprint refs for that lesson,
                  9 graph_support_refs add no unknown edge
  Teaching       10 teaching_points non-empty, 11 every point has >=1 knowledge_ref,
                 12 point refs are a subset of the lesson knowledge_refs
  Practice       13 guided_practice non-empty, 14 independent_practice non-empty,
                 15 completion_check non-empty
  Scope          16 scope non-empty, 17 scope not wider than blueprint, 18 limitations non-empty,
                 19 boundaries_and_misconceptions non-empty

Pack mode (input has pack_id), additionally:
  Pack           20 lesson_order <-> lesson_files one-to-one, every lesson file loads and validates,
                 21 within one module, PREREQUISITE_OF / PROCEDURE_PRECEDES crossing lessons must be
                    respected by the pack order, 22 pilot_a / pilot_b blocks present and consistent

It does not judge teaching quality or natural-language truth.
"""

import json
import re
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
read_json = runpy.run_path(str(HERE / "validate_source_registry.py"))["read_json"]
SCHEMA = HERE.parent / "assets/lesson.schema.json"

ORDER_RELATIONS = ("PREREQUISITE_OF", "PROCEDURE_PRECEDES")
TYPES = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
# markers that would widen a lesson scope beyond the blueprint scope
WIDENING_MARKERS = (
    "所有客户端",
    "全部客户端",
    "永久",
    "所有账号",
    "全部账号",
    "所有版本",
    "任何客户端",
    "所有地区",
)
PACK_REQUIRED = ("pack_id", "curriculum_id", "blueprint_id", "status", "selection_rationale",
                 "lesson_order", "lesson_files", "pilot_a", "pilot_b")


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
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"STRUCTURAL: {path}: blank or malformed text")
        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"STRUCTURAL: {path}: invalid enum {value!r}")


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def collect_graph_edges(paths):
    edges = []
    for path in paths:
        graph = read_json(path)
        for edge in graph.get("edges", []):
            if isinstance(edge, dict):
                edges.append(edge)
    return edges


def validate_lesson(data, schema, blueprint_index, known_knowledge, edge_ids, label="lesson"):
    errors = []
    structure(data, schema, label, errors)
    if errors:
        return errors

    def fail(message):
        errors.append(f"CONSISTENCY: {label}: {message}")

    lesson_id = data["lesson_id"]
    spec = blueprint_index.get(lesson_id)
    if spec is None:
        fail(f"lesson_id {lesson_id!r} does not exist in the blueprint")
        return errors

    if data["module_id"] != spec["module_id"]:
        fail(f"module_id {data['module_id']!r} != blueprint {spec['module_id']!r}")
    if normalize(data["title"]) != normalize(spec["title"]):
        fail("title does not match the blueprint title")
    if data["lesson_role"] != spec["lesson_role"]:
        fail(f"lesson_role {data['lesson_role']!r} != blueprint {spec['lesson_role']!r}")

    blueprint_outcomes = {normalize(o) for o in spec["learner_outcomes"]}
    for outcome in data["learner_outcomes"]:
        if normalize(outcome) not in blueprint_outcomes:
            fail(f"learner_outcome {outcome!r} exceeds the blueprint outcomes")

    blueprint_refs = set(spec["knowledge_refs"])
    lesson_refs = set(data["knowledge_refs"])
    extra = sorted(lesson_refs - blueprint_refs)
    if extra:
        fail("knowledge_refs outside the blueprint lesson refs: " + ", ".join(extra))
    missing = sorted(blueprint_refs - lesson_refs)
    if missing:
        fail("lesson does not reference all blueprint refs for this lesson: " + ", ".join(missing))
    for ref in lesson_refs:
        if ref not in known_knowledge:
            fail(f"unknown knowledge_ref {ref!r}")

    blueprint_edges = set(spec["graph_support_refs"])
    for ref in data["graph_support_refs"]:
        if ref not in edge_ids:
            fail(f"unknown graph_support_ref {ref!r}")
        if ref not in blueprint_edges:
            fail(f"graph_support_ref {ref!r} is not in the blueprint for this lesson")

    for point in data["teaching_points"]:
        for ref in point["knowledge_refs"]:
            if ref not in lesson_refs:
                fail(f"{point['point_id']}: knowledge_ref {ref!r} is outside the lesson knowledge_refs")

    blueprint_scope = normalize(spec["scope"])
    lesson_scope = normalize(data["scope"])
    for marker in WIDENING_MARKERS:
        if marker in lesson_scope and marker not in blueprint_scope:
            fail(f"scope appears wider than the blueprint (marker {marker!r})")
    return errors


def validate_pack(data, blueprint_index, known_knowledge, edge_ids, base_dir):
    errors = []
    for field in PACK_REQUIRED:
        if field not in data:
            errors.append(f"STRUCTURAL: pack: missing {field}")
    if errors:
        return errors

    def fail(message):
        errors.append("CONSISTENCY: pack: " + message)

    if data["status"] != "pilot":
        fail(f"status must be 'pilot'; found {data['status']!r}")

    order = data["lesson_order"]
    files = data["lesson_files"]
    if len(set(order)) != len(order):
        fail("lesson_order contains duplicates")
    if set(order) != set(files):
        fail("lesson_order and lesson_files must correspond one-to-one")

    lessons = {}
    for lesson_id in order:
        rel = files.get(lesson_id)
        if not isinstance(rel, str) or not rel.strip():
            fail(f"{lesson_id}: lesson_files entry missing")
            continue
        path = (base_dir / rel).resolve()
        if not path.is_file():
            fail(f"{lesson_id}: lesson file not found at {rel}")
            continue
        lesson = read_json(str(path))
        errors.extend(validate_lesson(lesson, read_json(SCHEMA), blueprint_index,
                                      known_knowledge, edge_ids, label=lesson_id))
        lessons[lesson_id] = lesson

    return errors, lessons


def check_pack_order(edges, lessons, order, errors):
    position = {lid: i for i, lid in enumerate(order)}
    module_of = {lid: l["module_id"] for lid, l in lessons.items()}
    knowledge_lesson = {}
    for lid, lesson in lessons.items():
        for ref in lesson["knowledge_refs"]:
            knowledge_lesson.setdefault(ref, set()).add(lid)
    for edge in edges:
        if edge.get("relation") not in ORDER_RELATIONS:
            continue
        source, target = edge.get("from"), edge.get("to")
        if source not in knowledge_lesson or target not in knowledge_lesson:
            continue
        for source_lesson in sorted(knowledge_lesson[source]):
            for target_lesson in sorted(knowledge_lesson[target]):
                if source_lesson == target_lesson:
                    continue
                if module_of.get(source_lesson) != module_of.get(target_lesson):
                    continue
                if source_lesson not in position or target_lesson not in position:
                    continue
                if position[source_lesson] > position[target_lesson]:
                    errors.append(
                        f"CONSISTENCY: pack: {edge['edge_id']} ({edge['relation']} {source} -> {target}) "
                        f"requires {source_lesson} before {target_lesson}, but pack order violates it"
                    )
    return errors


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) < 3:
        print("FAIL")
        print(
            "- Usage: python validate_lesson.py <lesson.json|pack.json> <blueprint.json> "
            "<knowledge-registry.json> [graph.json ...]"
        )
        return 1
    try:
        data = read_json(args[0])
        blueprint = read_json(args[1])
        knowledge = read_json(args[2])
        edges = collect_graph_edges(args[3:])
        edge_ids = {edge["edge_id"] for edge in edges if isinstance(edge.get("edge_id"), str)}
        known_knowledge = {item["knowledge_id"] for item in knowledge["items"]}
        blueprint_index = {
            lesson["lesson_id"]: lesson
            for module in blueprint["module_blueprints"]
            for lesson in module["lessons"]
        }
        if isinstance(data, dict) and "pack_id" in data:
            errors, lessons = validate_pack(
                data, blueprint_index, known_knowledge, edge_ids, Path(args[0]).resolve().parent
            )
            errors = check_pack_order(edges, lessons, data["lesson_order"], errors)
        else:
            errors = validate_lesson(data, read_json(SCHEMA), blueprint_index,
                                     known_knowledge, edge_ids)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"STRUCTURAL: unable to read or validate JSON: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print("- " + error)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
