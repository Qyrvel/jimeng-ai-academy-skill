"""Canonical course package assembly validation; Python standard library only.

Usage:
  python validate_course_assembly.py <course-manifest.json> <curriculum.json> <lesson-blueprint.json> \
      <knowledge-registry.json> [graph.json ...] [--lessons-root DIR]

Checks (course-assembly-policy.md / gate 4.4B2 sections 18-25):
  Identity      1 course_id non-empty, 2 curriculum_id matches, 3 blueprint_id matches,
                4 status = assembled_v1
  Modules       5 module_order == curriculum.module_order exactly, 6 no missing/extra/duplicate module
  Membership    7 manifest lesson ID set == blueprint lesson ID set (exact set equality)
  Order         8 lesson_order_by_module == blueprint lesson_order, per module
  Files         9 json exists, 10 markdown exists, 11 json lesson_id matches, 12 module_id matches,
                13 role matches, 14 json status = full_course, 15 validate_lesson PASS
  Paths        16 no historical / probe / recovery / review / temp path, 17 path inside lessons root
  Sequence     18 PREREQUISITE_OF / PROCEDURE_PRECEDES crossing lessons in one module resolved,
                19 no hard-sequence violation
  Guard        20 lesson_files contain only canonical lesson pairs
  Summaries    21 coverage / sequence / role summaries match recomputed values

It never judges teaching quality; unsupported-claim, scope-expansion and model/product-leakage
counts are human-reviewed values and only their shape is checked here.
"""

import json
import re
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_lesson_module = runpy.run_path(str(HERE / "validate_lesson.py"))
read_json = _lesson_module["read_json"]
validate_lesson = _lesson_module["validate_lesson"]
SCHEMA = HERE.parent / "assets/course-assembly.schema.json"
LESSON_SCHEMA = HERE.parent / "assets/lesson.schema.json"

TYPES = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
ORDER_RELATIONS = ("PREREQUISITE_OF", "PROCEDURE_PRECEDES")
FORBIDDEN_PATH_MARKERS = (
    "pilot-lessons",
    "role-expansion",
    "temporary",
    "probe",
    "acl-recovery",
    "recovery",
    "diagnostic",
    "/reviews/",
    "\\reviews\\",
    ".txt",
)


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
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            errors.append(f"STRUCTURAL: {path}: too few properties")
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
        for i, item in enumerate(value):
            structure(item, schema["items"], f"{path}[{i}]", errors)
    else:
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"STRUCTURAL: {path}: blank or malformed text")
        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"STRUCTURAL: {path}: invalid enum {value!r}")


def collect_edges(paths):
    edges = []
    for path in paths:
        graph = read_json(path)
        for edge in graph.get("edges", []):
            if isinstance(edge, dict):
                edges.append(edge)
    return edges


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    lessons_root_override = None
    if "--lessons-root" in args:
        i = args.index("--lessons-root")
        lessons_root_override = args[i + 1]
        del args[i:i + 2]
    if len(args) < 4:
        print("FAIL")
        print(
            "- Usage: python validate_course_assembly.py <course-manifest.json> <curriculum.json> "
            "<lesson-blueprint.json> <knowledge-registry.json> [graph.json ...] [--lessons-root DIR]"
        )
        return 1

    manifest_path = Path(args[0]).resolve()
    errors = []
    try:
        data = read_json(args[0])
        curriculum = read_json(args[1])
        blueprint = read_json(args[2])
        knowledge = read_json(args[3])
        edges = collect_edges(args[4:])
        schema = read_json(str(SCHEMA))
        lesson_schema = read_json(str(LESSON_SCHEMA))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("FAIL")
        print(f"- STRUCTURAL: unable to read input: {exc}")
        return 1

    structure(data, schema, "manifest", errors)
    if errors:
        print("FAIL")
        for e in errors:
            print("- " + e)
        return 1

    def fail(message):
        errors.append("CONSISTENCY: " + message)

    lessons_root = Path(lessons_root_override).resolve() if lessons_root_override else manifest_path.parent

    # 1-4 identity
    if data["curriculum_id"] != curriculum.get("curriculum_id"):
        fail(f"curriculum_id {data['curriculum_id']!r} != curriculum {curriculum.get('curriculum_id')!r}")
    if data["blueprint_id"] != blueprint.get("blueprint_id"):
        fail(f"blueprint_id {data['blueprint_id']!r} != blueprint {blueprint.get('blueprint_id')!r}")

    # 5-6 modules
    curriculum_modules = list(curriculum.get("module_order", []))
    manifest_modules = list(data["module_order"])
    if len(set(manifest_modules)) != len(manifest_modules):
        fail("module_order contains duplicate module ids")
    if manifest_modules != curriculum_modules:
        fail(f"module_order must equal curriculum.module_order exactly; found {manifest_modules}")

    # 7 membership
    blueprint_lessons = {
        lesson["lesson_id"]: {"module_id": module["module_id"], "role": lesson["lesson_role"]}
        for module in blueprint["module_blueprints"]
        for lesson in module["lessons"]
    }
    blueprint_order = {m["module_id"]: list(m["lesson_order"]) for m in blueprint["module_blueprints"]}
    # the blueprint index is built from the REAL blueprint argument, never from the manifest itself,
    # so that rule 15 (validate_lesson PASS) compares a canonical lesson against its blueprint spec
    blueprint_index = {
        lesson["lesson_id"]: lesson
        for module in blueprint["module_blueprints"]
        for lesson in module["lessons"]
    }
    manifest_ids = [entry["lesson_id"] for entry in data["lesson_files"]]
    if len(set(manifest_ids)) != len(manifest_ids):
        fail("lesson_files contains duplicate lesson ids")
    missing = sorted(set(blueprint_lessons) - set(manifest_ids))
    extra = sorted(set(manifest_ids) - set(blueprint_lessons))
    if missing:
        fail("missing lessons: " + ", ".join(missing))
    if extra:
        fail("extra lessons: " + ", ".join(extra))

    # 8 lesson order
    order_map = data["lesson_order_by_module"]
    if set(order_map) != set(curriculum_modules):
        fail(f"lesson_order_by_module keys must equal module_order; found {sorted(order_map)}")
    for module_id in curriculum_modules:
        if module_id not in order_map or module_id not in blueprint_order:
            continue
        if list(order_map[module_id]) != blueprint_order[module_id]:
            fail(
                f"{module_id}: lesson_order_by_module must equal blueprint lesson_order exactly; "
                f"found {list(order_map[module_id])}"
            )

    # 9-15 canonical files
    loaded = {}
    known_knowledge = {item["knowledge_id"] for item in knowledge["items"]}
    edge_ids = {e["edge_id"] for e in edges if isinstance(e.get("edge_id"), str)}
    for entry in data["lesson_files"]:
        lesson_id = entry["lesson_id"]
        for key in ("json_path", "markdown_path"):
            rel = entry[key]
            for marker in FORBIDDEN_PATH_MARKERS:
                if marker in rel:
                    fail(f"{lesson_id}: {key} references a non-course path ({marker}): {rel}")
        json_path = (lessons_root / entry["json_path"]).resolve()
        md_path = (lessons_root / entry["markdown_path"]).resolve()
        if lessons_root not in json_path.parents and json_path.parent != lessons_root:
            fail(f"{lesson_id}: json_path escapes the canonical lessons root: {entry['json_path']}")
        if not json_path.is_file():
            fail(f"{lesson_id}: canonical json missing at {entry['json_path']}")
            continue
        if not md_path.is_file():
            fail(f"{lesson_id}: canonical markdown missing at {entry['markdown_path']}")
        lesson = read_json(str(json_path))
        loaded[lesson_id] = lesson
        if lesson.get("lesson_id") != lesson_id:
            fail(f"{lesson_id}: json lesson_id is {lesson.get('lesson_id')!r}")
        if lesson.get("module_id") != entry["module_id"]:
            fail(f"{lesson_id}: json module_id {lesson.get('module_id')!r} != manifest {entry['module_id']!r}")
        if lesson.get("lesson_role") != entry["role"]:
            fail(f"{lesson_id}: json lesson_role {lesson.get('lesson_role')!r} != manifest {entry['role']!r}")
        if lesson.get("status") != "full_course":
            fail(f"{lesson_id}: json status must be 'full_course'; found {lesson.get('status')!r}")
        if lesson_id in blueprint_lessons:
            errors.extend(
                validate_lesson(lesson, lesson_schema, blueprint_index,
                                known_knowledge, edge_ids, label=lesson_id)
            )

    # 18-19 hard sequence
    knowledge_lesson = {}
    for lesson_id, lesson in loaded.items():
        for ref in lesson.get("knowledge_refs", []):
            knowledge_lesson.setdefault(ref, set()).add(lesson_id)
    position = {}
    for module_id, ids in order_map.items():
        for i, lid in enumerate(ids):
            position[lid] = (curriculum_modules.index(module_id) if module_id in curriculum_modules else 0, i)
    module_of = {lid: lesson.get("module_id") for lid, lesson in loaded.items()}
    resolved_edges = set()
    pairs = 0
    violations = 0
    for edge in edges:
        if edge.get("relation") not in ORDER_RELATIONS:
            continue
        source, target = edge.get("from"), edge.get("to")
        if source not in knowledge_lesson or target not in knowledge_lesson:
            continue
        for sl in sorted(knowledge_lesson[source]):
            for tl in sorted(knowledge_lesson[target]):
                if sl == tl:
                    continue
                if module_of.get(sl) != module_of.get(tl):
                    continue
                if sl not in position or tl not in position:
                    continue
                resolved_edges.add(edge["edge_id"])
                pairs += 1
                if position[sl] > position[tl]:
                    violations += 1
                    fail(
                        f"hard sequence: {edge['edge_id']} ({edge['relation']} {source} -> {target}) "
                        f"requires {sl} before {tl}, but manifest order violates it"
                    )
    resolved = len(resolved_edges)
    graph_constrained_lessons = sum(
        1
        for module in blueprint["module_blueprints"]
        for lesson in module["lessons"]
        if lesson.get("order_basis") == "GRAPH_CONSTRAINED"
    )

    # 21 summaries
    roles = sorted({lesson.get("lesson_role") for lesson in loaded.values()})
    blueprint_roles = sorted({v["role"] for v in blueprint_lessons.values()})
    missing_roles = sorted(set(blueprint_roles) - set(roles))
    expected_coverage = {
        "module_count": len(manifest_modules),
        "blueprint_lesson_count": len(blueprint_lessons),
        "canonical_lesson_count": len(loaded),
        "canonical_json_count": sum(1 for e in data["lesson_files"] if (lessons_root / e["json_path"]).is_file()),
        "canonical_markdown_count": sum(1 for e in data["lesson_files"] if (lessons_root / e["markdown_path"]).is_file()),
        "unmapped_mandatory_domain_count": 0,
        "missing_lesson_count": len(missing),
        "extra_lesson_count": len(extra),
    }
    for key, value in expected_coverage.items():
        if data["coverage_summary"][key] != value:
            fail(f"coverage_summary.{key}: expected {value}; found {data['coverage_summary'][key]}")
    for key, value in (
        ("hard_sequence_resolution_count", resolved),
        ("hard_sequence_violation_count", violations),
        ("non_order_relation_misuse_count", 0),
    ):
        if data["sequence_summary"][key] != value:
            fail(f"sequence_summary.{key}: expected {value}; found {data['sequence_summary'][key]}")
    if data["sequence_summary"]["lesson_hard_sequence_count"] != graph_constrained_lessons:
        fail(
            "sequence_summary.lesson_hard_sequence_count: expected "
            f"{graph_constrained_lessons} (GRAPH_CONSTRAINED lessons in the blueprint); "
            f"found {data['sequence_summary']['lesson_hard_sequence_count']}"
        )
    example_markers = 0
    for lesson in loaded.values():
        for field in ("opening", "guided_practice", "independent_practice", "lesson_summary"):
            if "PEDAGOGICAL_EXAMPLE" in str(lesson.get(field, "")):
                example_markers += 1
        for point in lesson.get("teaching_points", []):
            if "PEDAGOGICAL_EXAMPLE" in str(point.get("explanation", "")):
                example_markers += 1
    if data["grounding_summary"]["pedagogical_example_count"] != example_markers:
        fail(
            "grounding_summary.pedagogical_example_count: expected "
            f"{example_markers}; found {data['grounding_summary']['pedagogical_example_count']}"
        )
    if data["role_coverage_summary"]["blueprint_role_count"] != len(blueprint_roles):
        fail(f"role_coverage_summary.blueprint_role_count: expected {len(blueprint_roles)}")
    if data["role_coverage_summary"]["canonical_role_count"] != len(roles):
        fail(f"role_coverage_summary.canonical_role_count: expected {len(roles)}")
    if data["role_coverage_summary"]["missing_role_count"] != len(missing_roles):
        fail(f"role_coverage_summary.missing_role_count: expected {len(missing_roles)}")
    if sorted(data["role_coverage_summary"]["missing_role_set"]) != missing_roles:
        fail(f"role_coverage_summary.missing_role_set: expected {missing_roles}")
    if data["assembly_metadata"]["hard_sequence_count"] != graph_constrained_lessons:
        fail(
            "assembly_metadata.hard_sequence_count: expected "
            f"{graph_constrained_lessons} (lesson-level GRAPH_CONSTRAINED transitions)"
        )
    if data["assembly_metadata"]["hard_sequence_violation_count"] != violations:
        fail(f"assembly_metadata.hard_sequence_violation_count: expected {violations}")
    for key in ("canonical_lesson_count",):
        if data["assembly_metadata"][key] != len(loaded):
            fail(f"assembly_metadata.{key}: expected {len(loaded)}")

    print("FAIL" if errors else "PASS")
    for error in errors:
        print("- " + error)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
