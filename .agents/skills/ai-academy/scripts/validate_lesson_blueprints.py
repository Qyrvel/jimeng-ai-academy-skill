"""Lesson blueprint structural validation; Python standard library only.

Usage:
  python validate_lesson_blueprints.py <blueprint.json> <curriculum.json> <knowledge-registry.json> [graph.json ...]

Checks (lesson-blueprint-policy.md / gate 4.2 section 34):
  Identity          1 blueprint_id non-empty, 2 curriculum_id matches skeleton,
                    3 status=blueprint, 4 lesson_id globally unique, 5 lesson_id prefix matches module_id
  Module integrity  6 every Gate 4.1 module has exactly one module blueprint, 7 no unknown module,
                    8 lesson_order <-> lessons one-to-one, 9 no duplicate lesson
  Knowledge        10 each lesson >=1 ref, 11 all refs exist,
                   12 per-module lesson knowledge union covers the Gate 4.1 module knowledge_refs
  Graph            13 graph_support_ref exists, 14 GRAPH_CONSTRAINED needs >=1 real graph support,
                   15 cross-lesson PREREQUISITE_OF / PROCEDURE_PRECEDES inside a module must not be violated
  Pedagogy         16 PEDAGOGICAL needs 'PEDAGOGICAL_RATIONALE:', 17 order_basis enum
  Evidence         18 learner_outcomes non-empty, 19 practice_intent non-empty, 20 completion_evidence
                   non-empty, 21 scope non-empty, 22 limitations non-empty

It does NOT judge teaching quality; human review owns semantics.
"""

import runpy
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
read_json = runpy.run_path(str(HERE / "validate_source_registry.py"))["read_json"]
SCHEMA = HERE.parent / "assets/lesson-blueprint.schema.json"

LESSON_ID_PATTERN = re.compile(r"^(JCA-M[0-9]{2})-L[0-9]{2}$")
PEDAGOGICAL_MARKER = "PEDAGOGICAL_RATIONALE:"
ORDER_RELATIONS = ("PREREQUISITE_OF", "PROCEDURE_PRECEDES")
TYPES = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}


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


def collect_graph_edges(paths):
    edges = []
    for path in paths:
        graph = read_json(path)
        for edge in graph.get("edges", []):
            if isinstance(edge, dict) and isinstance(edge.get("edge_id"), str):
                edges.append(edge)
    return edges


def validate(data, schema, curriculum, knowledge, graph_edges):
    errors = []
    structure(data, schema, "root", errors)
    if errors:
        return errors

    def fail(message):
        errors.append("CONSISTENCY: " + message)

    known_knowledge = {item["knowledge_id"] for item in knowledge["items"]}
    edge_ids = {edge["edge_id"] for edge in graph_edges}
    module_specs = {m["module_id"]: m for m in curriculum["modules"]}

    # identity / curriculum binding
    if data["curriculum_id"] != curriculum["curriculum_id"]:
        fail(
            f"curriculum_id {data['curriculum_id']!r} does not match skeleton "
            f"{curriculum['curriculum_id']!r}"
        )

    blueprints = data["module_blueprints"]
    blueprint_ids = [b["module_id"] for b in blueprints]
    if len(set(blueprint_ids)) != len(blueprint_ids):
        fail("duplicate module_id in module_blueprints")
    if set(blueprint_ids) != set(module_specs):
        missing = sorted(set(module_specs) - set(blueprint_ids))
        unknown = sorted(set(blueprint_ids) - set(module_specs))
        if missing:
            fail("modules without a module blueprint: " + ", ".join(missing))
        if unknown:
            fail("module blueprints for unknown modules: " + ", ".join(unknown))

    # lessons
    all_lesson_ids = []
    per_module_lessons = {}
    for blueprint in blueprints:
        module_id = blueprint["module_id"]
        lessons = blueprint["lessons"]
        lesson_ids = [lesson["lesson_id"] for lesson in lessons]
        all_lesson_ids.extend(lesson_ids)
        per_module_lessons[module_id] = lessons

        if len(set(lesson_ids)) != len(lesson_ids):
            fail(f"{module_id}: duplicate lesson_id inside module")
        if len(set(blueprint["lesson_order"])) != len(blueprint["lesson_order"]):
            fail(f"{module_id}: lesson_order contains duplicate entries")
        if set(blueprint["lesson_order"]) != set(lesson_ids):
            fail(f"{module_id}: lesson_order and lessons must correspond one-to-one")

        for lesson in lessons:
            lesson_id = lesson["lesson_id"]
            match = LESSON_ID_PATTERN.match(lesson_id)
            if not match:
                fail(f"{lesson_id}: lesson_id must match JCA-M##-L##")
            elif match.group(1) != module_id:
                fail(f"{lesson_id}: lesson_id prefix does not match module_id {module_id}")
            if lesson["module_id"] != module_id:
                fail(f"{lesson_id}: lesson.module_id {lesson['module_id']!r} != {module_id!r}")
            for ref in lesson["knowledge_refs"]:
                if ref not in known_knowledge:
                    fail(f"{lesson_id}: unknown knowledge_ref {ref!r}")
            for ref in lesson["graph_support_refs"]:
                if ref not in edge_ids:
                    fail(f"{lesson_id}: unknown graph_support_ref {ref!r}")
            if lesson["order_basis"] == "PEDAGOGICAL" and PEDAGOGICAL_MARKER not in lesson["order_rationale"]:
                fail(
                    f"{lesson_id}: order_basis PEDAGOGICAL requires "
                    f"'{PEDAGOGICAL_MARKER}' in order_rationale"
                )
            if lesson["order_basis"] == "GRAPH_CONSTRAINED" and not lesson["graph_support_refs"]:
                fail(f"{lesson_id}: GRAPH_CONSTRAINED requires at least one graph_support_ref")

    if len(set(all_lesson_ids)) != len(all_lesson_ids):
        fail("lesson_id must be globally unique")

    # module knowledge preservation
    mapped = 0
    unmapped_pairs = []
    for module_id, spec in sorted(module_specs.items()):
        lessons = per_module_lessons.get(module_id, [])
        lesson_union = set()
        for lesson in lessons:
            lesson_union.update(lesson["knowledge_refs"])
        for ref in spec["knowledge_refs"]:
            if ref in lesson_union:
                mapped += 1
            else:
                unmapped_pairs.append(f"{module_id}:{ref}")
    if unmapped_pairs:
        fail("Gate 4.1 module knowledge_refs not covered by any lesson: " + ", ".join(unmapped_pairs))

    # cross-lesson hard order inside a module
    for module_id, lessons in sorted(per_module_lessons.items()):
        order = None
        for blueprint in blueprints:
            if blueprint["module_id"] == module_id:
                order = blueprint["lesson_order"]
        lesson_index = {lesson_id: i for i, lesson_id in enumerate(order)}
        knowledge_lesson = {}
        for lesson in lessons:
            for ref in lesson["knowledge_refs"]:
                knowledge_lesson.setdefault(ref, set()).add(lesson["lesson_id"])
        for edge in graph_edges:
            if edge.get("relation") not in ORDER_RELATIONS:
                continue
            source, target = edge.get("from"), edge.get("to")
            if source not in knowledge_lesson or target not in knowledge_lesson:
                continue
            for source_lesson in sorted(knowledge_lesson[source]):
                for target_lesson in sorted(knowledge_lesson[target]):
                    if source_lesson == target_lesson:
                        continue  # internal lesson structure, not an order
                    if lesson_index[source_lesson] > lesson_index[target_lesson]:
                        fail(
                            f"{module_id}: {edge['edge_id']} ({edge['relation']} {source} -> {target}) "
                            f"requires {source_lesson} before {target_lesson}, but lesson_order violates it"
                        )

    # summary truthfulness
    transition_count = sum(max(len(b["lessons"]) - 1, 0) for b in blueprints)
    non_first = [
        lesson
        for b in blueprints
        for lesson in b["lessons"][1:]
    ]
    expected_sequence = {
        "lesson_transition_count": transition_count,
        "graph_constrained_transition_count": sum(
            1 for lesson in non_first if lesson["order_basis"] == "GRAPH_CONSTRAINED"
        ),
        "pedagogical_transition_count": sum(
            1 for lesson in non_first if lesson["order_basis"] == "PEDAGOGICAL"
        ),
        "independent_transition_count": sum(
            1 for lesson in non_first if lesson["order_basis"] == "INDEPENDENT"
        ),
    }
    for key, value in expected_sequence.items():
        if data["sequence_summary"][key] != value:
            fail(f"sequence_summary.{key}: expected {value}; found {data['sequence_summary'][key]}")

    expected_coverage = {
        "module_count": len(blueprints),
        "lesson_count": len(all_lesson_ids),
        "mapped_module_knowledge_ref_count": mapped,
        "unmapped_module_knowledge_ref_count": len(unmapped_pairs),
    }
    for key, value in expected_coverage.items():
        if data["coverage_summary"][key] != value:
            fail(f"coverage_summary.{key}: expected {value}; found {data['coverage_summary'][key]}")

    return errors


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) < 3:
        print("FAIL")
        print(
            "- Usage: python validate_lesson_blueprints.py <blueprint.json> <curriculum.json> "
            "<knowledge-registry.json> [graph.json ...]"
        )
        return 1
    try:
        data = read_json(args[0])
        curriculum = read_json(args[1])
        knowledge = read_json(args[2])
        graph_edges = collect_graph_edges(args[3:])
        errors = validate(data, read_json(SCHEMA), curriculum, knowledge, graph_edges)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"STRUCTURAL: unable to read or validate JSON: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print("- " + error)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
