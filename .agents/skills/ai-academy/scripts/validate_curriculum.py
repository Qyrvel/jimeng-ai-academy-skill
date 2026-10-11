"""Curriculum skeleton structural validation; Python standard library only.

Usage:
  python validate_curriculum.py <curriculum.json> <knowledge-registry.json> <curriculum-readiness.json> [graph.json ...]

Checks (curriculum-policy.md section 8 / gate 4.1 section 22):
  Root      1 schema shape, 2 curriculum_id, 3 status=skeleton, 4 module_order non-empty,
            5 module_order <-> modules one-to-one, 6 no duplicate module_id
  Knowledge 7 knowledge_refs exist, 8 every module has >=1 knowledge_ref
  Domain    9 every READY FOUNDATIONAL/CORE domain covered, 10 unknown domain_id fails,
            11 deferred DYNAMIC/OPTIONAL domains must not be mandatory module coverage
  Order     12 order_basis enum, 13 PEDAGOGICAL needs 'PEDAGOGICAL_RATIONALE:',
            14 GRAPH_CONSTRAINED needs >=1 graph_support_ref, 15 graph_support_ref must exist
  Outcomes  16 learner_outcomes non-empty, 17 no blank outcome
  Scope     18 scope non-empty, 19 limitations non-empty

It does NOT judge whether a module teaches well; human review owns semantics.
"""

import runpy
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
read_json = runpy.run_path(str(HERE / "validate_source_registry.py"))["read_json"]
SCHEMA = HERE.parent / "assets/curriculum.schema.json"

MODULE_ID_PATTERN = re.compile(r"^JCA-M[0-9]{2}$")
MANDATORY_CRITICALITY = ("FOUNDATIONAL", "CORE")
DEFERRED_DECISIONS = ("DEFER_DYNAMIC", "DEFER_OPTIONAL")
PEDAGOGICAL_MARKER = "PEDAGOGICAL_RATIONALE:"
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


def validate(data, schema, knowledge, readiness, graph_edges):
    errors = []
    structure(data, schema, "root", errors)
    if errors:
        return errors

    def fail(message):
        errors.append("CONSISTENCY: " + message)

    modules = data["modules"]
    order = data["module_order"]
    module_ids = [m["module_id"] for m in modules]

    # root: id uniqueness / bijection / id format
    if len(set(module_ids)) != len(module_ids):
        fail("duplicate module_id in modules")
    if len(set(order)) != len(order):
        fail("module_order contains duplicate entries")
    if set(order) != set(module_ids):
        fail("module_order and modules must correspond one-to-one")
    for module_id in module_ids:
        if not MODULE_ID_PATTERN.match(module_id):
            fail(f"module_id {module_id!r} must match JCA-M##")

    # knowledge existence
    known_knowledge = {item["knowledge_id"] for item in knowledge["items"]}
    for module in modules:
        for ref in module["knowledge_refs"]:
            if ref not in known_knowledge:
                fail(f"{module['module_id']}: unknown knowledge_ref {ref!r}")

    # domain coverage
    domains = {d["domain_id"]: d for d in readiness["domains"]}
    mandatory = {
        d["domain_id"]
        for d in readiness["domains"]
        if d["criticality"] in MANDATORY_CRITICALITY and d["status"] == "READY"
    }
    deferred = {
        d["domain_id"] for d in readiness["domains"] if d["decision"] in DEFERRED_DECISIONS
    }
    covered = {}
    for module in modules:
        for domain_id in module["target_domain_ids"]:
            if domain_id not in domains:
                fail(f"{module['module_id']}: unknown target_domain_id {domain_id!r}")
                continue
            covered.setdefault(domain_id, []).append(module["module_id"])
            if domain_id in deferred:
                fail(
                    f"{module['module_id']}: deferred domain {domain_id} must not be mandatory module coverage"
                )
    unmapped = sorted(mandatory - set(covered))
    if unmapped:
        fail("READY FOUNDATIONAL/CORE domains not covered by any module: " + ", ".join(unmapped))

    # order contract
    for module in modules:
        basis = module["order_basis"]
        refs = module["graph_support_refs"]
        if basis == "PEDAGOGICAL" and PEDAGOGICAL_MARKER not in module["order_rationale"]:
            fail(
                f"{module['module_id']}: order_basis PEDAGOGICAL requires "
                f"'{PEDAGOGICAL_MARKER}' in order_rationale"
            )
        if basis == "GRAPH_CONSTRAINED" and not refs:
            fail(f"{module['module_id']}: GRAPH_CONSTRAINED requires at least one graph_support_ref")
        for ref in refs:
            if ref not in graph_edges:
                fail(f"{module['module_id']}: unknown graph_support_ref {ref!r}")

    # deferred declarations
    for entry in data["deferred_domains"]:
        domain_id = entry["domain_id"]
        if domain_id not in domains:
            fail(f"deferred_domains: unknown domain_id {domain_id!r}")
        elif domain_id in mandatory:
            fail(f"deferred_domains: {domain_id} is a READY mandatory domain and cannot be deferred")

    # coverage_summary truthfulness
    summary = data["coverage_summary"]
    expected = {
        "module_count": len(modules),
        "foundational_domain_count": sum(
            1 for d in readiness["domains"] if d["criticality"] == "FOUNDATIONAL" and d["status"] == "READY"
        ),
        "core_domain_count": sum(
            1 for d in readiness["domains"] if d["criticality"] == "CORE" and d["status"] == "READY"
        ),
        "mapped_mandatory_count": len(mandatory & set(covered)),
        "unmapped_mandatory_count": len(unmapped),
    }
    for key, value in expected.items():
        if summary[key] != value:
            fail(f"coverage_summary.{key}: expected {value}; found {summary[key]}")

    return errors


def collect_graph_edges(paths):
    edges = set()
    for path in paths:
        graph = read_json(path)
        for edge in graph.get("edges", []):
            edge_id = edge.get("edge_id")
            if isinstance(edge_id, str) and edge_id.strip():
                edges.add(edge_id)
    return edges


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) < 3:
        print("FAIL")
        print(
            "- Usage: python validate_curriculum.py <curriculum.json> <knowledge-registry.json> "
            "<curriculum-readiness.json> [graph.json ...]"
        )
        return 1
    try:
        data = read_json(args[0])
        knowledge = read_json(args[1])
        readiness = read_json(args[2])
        graph_edges = collect_graph_edges(args[3:])
        errors = validate(data, read_json(SCHEMA), knowledge, readiness, graph_edges)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"STRUCTURAL: unable to read or validate JSON: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print("- " + error)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
