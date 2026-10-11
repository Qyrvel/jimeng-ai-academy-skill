"""Gate 3.1 offline graph integrity validation; Python standard library only.

Mechanical checks only. Whether a PREREQUISITE_OF is semantically justified is a
human audit responsibility; this script checks the structural rules the Graph
Integrity Policy Addendum defines.
"""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = runpy.run_path(str(HERE / "validate_source_registry.py"))
read_json = SOURCE["read_json"]

DAG_RELATIONS = ("PREREQUISITE_OF", "PROCEDURE_PRECEDES", "STEP_OF")
PROCEDURE_ONLY_RELATIONS = ("PROCEDURE_PRECEDES", "STEP_OF")
CONFLICTING_PAIRS = (
    ("PREREQUISITE_OF", "VERSION_VARIANT_OF"),
    ("PREREQUISITE_OF", "SCOPE_PARALLEL_TO"),
    ("STEP_OF", "VERSION_VARIANT_OF"),
    ("STEP_OF", "SCOPE_PARALLEL_TO"),
)
CYCLE_LABELS = {
    "PREREQUISITE_OF": "PREREQUISITE_CYCLE_REVIEW",
    "PROCEDURE_PRECEDES": "PROCEDURE_ORDER_CYCLE_REVIEW",
    "STEP_OF": "STEP_OF_CYCLE_REVIEW",
}
# Gate 3.2-R1: enforcement-context rules
ENFORCEMENT_RELATION = "ENFORCEMENT_CONTEXT_FOR"
GROUP_REFERENCE_MARKER = "DOCUMENTED_GROUP_REFERENCE:"
DIRECT_REFERENCE_MARKER = "DIRECT_REFERENCE:"
ENFORCEMENT_FANOUT_THRESHOLD = 3
# combinations rejected outright, without the PAIR_RELATION_JUSTIFICATION escape
HARD_CONFLICT_PAIRS = (
    (ENFORCEMENT_RELATION, "VERSION_VARIANT_OF"),
    (ENFORCEMENT_RELATION, "SCOPE_PARALLEL_TO"),
)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def index_items(knowledge):
    by_id = {}
    if isinstance(knowledge, dict) and isinstance(knowledge.get("items"), list):
        for item in knowledge["items"]:
            if isinstance(item, dict) and text(item.get("knowledge_id")):
                by_id[item["knowledge_id"]] = item
    return by_id


def find_cycles(edges):
    """Return a list of cycles; each cycle is a list of node ids in traversal order."""
    adjacency = {}
    for edge in edges:
        adjacency.setdefault(edge["from"], []).append(edge["to"])
    cycles = []
    seen_cycle_keys = set()
    state = {}
    stack = []

    def visit(node):
        state[node] = 1
        stack.append(node)
        for neighbour in adjacency.get(node, []):
            if state.get(neighbour, 0) == 1:
                start = stack.index(neighbour)
                cycle = stack[start:] + [neighbour]
                key = frozenset(cycle)
                if key not in seen_cycle_keys:
                    seen_cycle_keys.add(key)
                    cycles.append(cycle)
            elif state.get(neighbour, 0) == 0:
                visit(neighbour)
        stack.pop()
        state[node] = 2

    for node in list(adjacency):
        if state.get(node, 0) == 0:
            visit(node)
    return cycles


def validate_integrity(graph, knowledge):
    errors = []
    warnings = []
    if not isinstance(graph, dict):
        return ["STRUCTURAL: graph: must be an object"], warnings
    edges = graph.get("edges")
    if not isinstance(edges, list):
        return ["STRUCTURAL: graph.edges: must be an array"], warnings
    items = index_items(knowledge)

    # rule 10 : edge_id unique
    seen_ids = set()
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"STRUCTURAL: edges[{index}]: must be an object")
            continue
        edge_id = edge.get("edge_id")
        if not text(edge_id):
            errors.append(f"STRUCTURAL: edges[{index}].edge_id: must be a non-blank string")
            continue
        if edge_id in seen_ids:
            errors.append(f"EDGE: edges[{index}]: duplicate edge_id {edge_id!r}")
        seen_ids.add(edge_id)

    usable = [
        edge for edge in edges
        if isinstance(edge, dict)
        and text(edge.get("edge_id")) and text(edge.get("from")) and text(edge.get("to"))
        and text(edge.get("relation"))
    ]

    # rules 1-3 : acyclicity
    for relation in DAG_RELATIONS:
        subset = [edge for edge in usable if edge["relation"] == relation]
        for cycle in find_cycles(subset):
            errors.append(
                f"CYCLE: {relation} forms a cycle {' -> '.join(cycle)}; "
                f"mark and review manually as {CYCLE_LABELS[relation]}; do not auto-delete any edge"
            )

    # rule 4 : STEP_OF reverse pair
    step_pairs = {(edge["from"], edge["to"]) for edge in usable if edge["relation"] == "STEP_OF"}
    for source, target in sorted(step_pairs):
        if (target, source) in step_pairs:
            errors.append(f"DIRECTION: STEP_OF stores both {source!r} -> {target!r} and {target!r} -> {source!r}; the reverse edge is forbidden")

    # rules 5-6 : procedure type rules
    for index, edge in enumerate(usable):
        if edge["relation"] not in PROCEDURE_ONLY_RELATIONS:
            continue
        for side in ("from", "to"):
            item = items.get(edge[side])
            item_type = item.get("knowledge_type") if item else None
            if item is not None and item_type != "PROCEDURE":
                errors.append(f"TYPE: {edge['edge_id']}: {edge['relation']} requires {side} type PROCEDURE; found {item_type!r}")

    # rule 7 : STEP_OF + PROCEDURE_PRECEDES consistency
    parent_of = {}
    for edge in usable:
        if edge["relation"] == "STEP_OF":
            parent_of.setdefault(edge["from"], set()).add(edge["to"])
    for edge in usable:
        if edge["relation"] != "PROCEDURE_PRECEDES":
            continue
        source_parents = parent_of.get(edge["from"], set())
        target_parents = parent_of.get(edge["to"], set())
        if not source_parents or not target_parents:
            continue
        if source_parents & target_parents:
            continue
        rationale = edge.get("rationale") if isinstance(edge.get("rationale"), str) else ""
        if "CROSS_WORKFLOW_ORDER_JUSTIFICATION:" not in rationale:
            errors.append(
                f"WORKFLOW: {edge['edge_id']}: {edge['from']} and {edge['to']} belong to different STEP_OF parents "
                f"({sorted(source_parents)} vs {sorted(target_parents)}); rationale must contain 'CROSS_WORKFLOW_ORDER_JUSTIFICATION:'"
            )

    # rule 8 : pair relation conflicts
    relations_by_pair = {}
    for edge in usable:
        relations_by_pair.setdefault((edge["from"], edge["to"]), []).append(edge)
    for (source, target), pair_edges in sorted(relations_by_pair.items()):
        present = {edge["relation"] for edge in pair_edges}
        for first, second in CONFLICTING_PAIRS:
            if first in present and second in present:
                justified = any(
                    "PAIR_RELATION_JUSTIFICATION:" in edge.get("rationale", "")
                    for edge in pair_edges if isinstance(edge.get("rationale"), str)
                )
                if not justified:
                    errors.append(
                        f"PAIR: {source!r} -> {target!r} carries both {first} and {second}; mark PAIR_RELATION_CONFLICT and explain, "
                        f"or add 'PAIR_RELATION_JUSTIFICATION:' to a rationale"
                    )

    # rule 9 : INFERRED needs INFERENCE_BOUNDARY
    for edge in usable:
        if edge.get("epistemic_status") == "INFERRED":
            limitations = edge.get("limitations") if isinstance(edge.get("limitations"), str) else ""
            if "INFERENCE_BOUNDARY:" not in limitations:
                errors.append(f"EPISTEMIC: {edge['edge_id']}: INFERRED requires 'INFERENCE_BOUNDARY:' inside limitations")

    # Curriculum leakage is decided by evidence-backed Edge Review, not text matching.

    # Gate 3.2-R1 : enforcement-context rules
    enforcement = [edge for edge in usable if edge["relation"] == ENFORCEMENT_RELATION]
    enforcement_fanout = {}
    for edge in enforcement:
        enforcement_fanout.setdefault(edge["from"], []).append(edge)
    for source, group in sorted(enforcement_fanout.items()):
        if len(group) >= ENFORCEMENT_FANOUT_THRESHOLD:
            for edge in group:
                rationale = edge.get("rationale") if isinstance(edge.get("rationale"), str) else ""
                if GROUP_REFERENCE_MARKER not in rationale:
                    errors.append(
                        f"GROUP: {edge['edge_id']}: from {source!r} carries {len(group)} {ENFORCEMENT_RELATION} edges; "
                        f"every rationale must contain '{GROUP_REFERENCE_MARKER}'"
                    )
    for edge in enforcement:
        if edge.get("epistemic_status") != "DOCUMENTED":
            continue
        rationale = edge.get("rationale") if isinstance(edge.get("rationale"), str) else ""
        if GROUP_REFERENCE_MARKER not in rationale and DIRECT_REFERENCE_MARKER not in rationale:
            errors.append(
                f"EPISTEMIC: {edge['edge_id']}: a DOCUMENTED {ENFORCEMENT_RELATION} needs "
                f"'{GROUP_REFERENCE_MARKER}' or '{DIRECT_REFERENCE_MARKER}' in its rationale"
            )
    # pair combinations rejected outright, checked in both directions
    undirected = {}
    for edge in usable:
        undirected.setdefault(frozenset((edge["from"], edge["to"])), []).append(edge)
    for pair, pair_edges in sorted(undirected.items(), key=lambda entry: sorted(entry[0])):
        present = {edge["relation"] for edge in pair_edges}
        for first, second in HARD_CONFLICT_PAIRS:
            if first in present and second in present:
                errors.append(
                    f"PAIR: pair {sorted(pair)} carries both {first} and {second}; this combination is rejected outright "
                    f"(no justification escape)"
                )

    # warning only : transitive prerequisite redundancy
    prerequisite_pairs = {(edge["from"], edge["to"]) for edge in usable if edge["relation"] == "PREREQUISITE_OF"}
    for source, middle in sorted(prerequisite_pairs):
        for inner_source, target in sorted(prerequisite_pairs):
            if inner_source != middle:
                continue
            if (source, target) in prerequisite_pairs and source != target:
                warnings.append(
                    f"POTENTIAL_TRANSITIVE_REDUNDANCY: {source} PREREQUISITE_OF {middle} PREREQUISITE_OF {target} "
                    f"and {source} PREREQUISITE_OF {target}; decide KEEP_DIRECT / REMOVE_REDUNDANT / NEEDS_REVIEW (warning only)"
                )
    return errors, warnings


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("FAIL")
        print("- Usage: python validate_graph_integrity.py <graph.json> <knowledge-registry.json>")
        return 1
    try:
        graph = read_json(args[0])
        knowledge = read_json(args[1])
        errors, warnings = validate_integrity(graph, knowledge)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors, warnings = [f"STRUCTURAL: unable to read or validate JSON: {exc}"], []
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    for warning in warnings:
        print(f"- WARNING: {warning}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
