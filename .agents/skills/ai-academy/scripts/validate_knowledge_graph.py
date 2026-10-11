"""Gate 3.0 offline knowledge graph validation; Python standard library only."""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE.parent / "assets/knowledge-graph.schema.json"
SOURCE = runpy.run_path(str(HERE / "validate_source_registry.py"))
read_json = SOURCE["read_json"]

ROOT_FIELDS = ("graph_id", "scope", "nodes", "edges")
NODE_FIELDS = ("knowledge_id",)
EDGE_FIELDS = ("edge_id", "from", "relation", "to", "epistemic_status", "rationale", "limitations")
RELATIONS = ("PREREQUISITE_OF", "PROCEDURE_PRECEDES", "CONSTRAINS", "VERSION_CONTEXT_FOR", "SCOPE_PARALLEL_TO", "VERSION_VARIANT_OF", "STEP_OF", "ENFORCEMENT_CONTEXT_FOR")
STATUSES = ("DOCUMENTED", "INFERRED")
CONSTRAINING_TYPES = ("CONSTRAINT", "POLICY")
SYMMETRIC_RELATIONS = ("SCOPE_PARALLEL_TO", "VERSION_VARIANT_OF")
# Gate 3.0-R1: STEP_OF is directional; the reverse edge is a semantic contradiction, not an equivalent duplicate
DIRECTIONAL_RELATIONS = ("STEP_OF", "ENFORCEMENT_CONTEXT_FOR")
# Enforcement roles and single-edge direction require evidence-backed semantic review.


def text(value):
    return isinstance(value, str) and bool(value.strip())


def index_items(knowledge):
    by_id = {}
    if isinstance(knowledge, dict) and isinstance(knowledge.get("items"), list):
        for item in knowledge["items"]:
            if isinstance(item, dict) and text(item.get("knowledge_id")):
                by_id[item["knowledge_id"]] = item
    return by_id


def normalization_pairs(review):
    """Map unordered item pairs to the set of relation labels declared for them."""
    pairs = {}
    if isinstance(review, dict) and isinstance(review.get("reviews"), list):
        for entry in review["reviews"]:
            if not isinstance(entry, dict):
                continue
            ids = entry.get("item_ids")
            relation = entry.get("relation")
            if isinstance(ids, list) and len(ids) >= 2 and text(relation):
                for first in range(len(ids)):
                    for second in range(first + 1, len(ids)):
                        key = frozenset((ids[first], ids[second]))
                        pairs.setdefault(key, set()).add(relation)
    return pairs


def validate_graph(data, knowledge, review, schema):
    errors = []

    # --- schema self-check -------------------------------------------------
    if not isinstance(schema, dict):
        return ["STRUCTURAL: graph schema is unreadable"]
    if tuple(schema.get("required", ())) != ROOT_FIELDS:
        errors.append("STRUCTURAL: graph schema root required fields differ from the validator contract")
    node_def = schema.get("$defs", {}).get("node", {})
    if tuple(node_def.get("required", ())) != NODE_FIELDS:
        errors.append("STRUCTURAL: graph schema node required fields differ from the validator contract")
    edge_def = schema.get("$defs", {}).get("edge", {})
    if tuple(edge_def.get("required", ())) != EDGE_FIELDS:
        errors.append("STRUCTURAL: graph schema edge required fields differ from the validator contract")
    if tuple(edge_def.get("properties", {}).get("relation", {}).get("enum", ())) != RELATIONS:
        errors.append("STRUCTURAL: graph schema relation enum differs from the validator contract")
    if tuple(edge_def.get("properties", {}).get("epistemic_status", {}).get("enum", ())) != STATUSES:
        errors.append("STRUCTURAL: graph schema epistemic_status enum differs from the validator contract")
    if errors:
        return errors

    # --- root -------------------------------------------------------------
    if not isinstance(data, dict):
        return ["STRUCTURAL: root: must be an object"]
    for field in ROOT_FIELDS:
        if field not in data:
            errors.append(f"STRUCTURAL: root: missing required field {field}")
    for field in sorted(set(data) - set(ROOT_FIELDS)):
        errors.append(f"STRUCTURAL: root: unexpected field {field}")
    for field in ("graph_id", "scope"):
        if not text(data.get(field)):
            errors.append(f"STRUCTURAL: root.{field}: must be a non-blank string")

    items = index_items(knowledge)
    pairs = normalization_pairs(review)

    # --- nodes ------------------------------------------------------------
    node_ids = []
    if not isinstance(data.get("nodes"), list):
        errors.append("STRUCTURAL: root.nodes: must be an array")
        nodes_ok = False
    else:
        nodes_ok = True
        seen_nodes = set()
        for index, node in enumerate(data["nodes"]):
            label = f"nodes[{index}]"
            if not isinstance(node, dict):
                errors.append(f"STRUCTURAL: {label}: must be an object")
                continue
            for field in NODE_FIELDS:
                if field not in node:
                    errors.append(f"STRUCTURAL: {label}: missing required field {field}")
            for field in sorted(set(node) - set(NODE_FIELDS)):
                errors.append(f"STRUCTURAL: {label}: unexpected field {field}")
            node_id = node.get("knowledge_id")
            if not text(node_id):
                errors.append(f"STRUCTURAL: {label}.knowledge_id: must be a non-blank string")
                continue
            if node_id in seen_nodes:
                errors.append(f"NODE: {label}: duplicate node {node_id!r}")
            seen_nodes.add(node_id)
            if node_id not in items:
                errors.append(f"NODE: {label}: knowledge_id {node_id!r} does not exist in Knowledge Registry")
            node_ids.append(node_id)
    node_set = set(node_ids)

    # --- edges ------------------------------------------------------------
    if not isinstance(data.get("edges"), list):
        errors.append("STRUCTURAL: root.edges: must be an array")
        return errors

    seen_edges = set()
    directed = {}
    for index, edge in enumerate(data["edges"]):
        label = f"edges[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"STRUCTURAL: {label}: must be an object")
            continue
        for field in EDGE_FIELDS:
            if field not in edge:
                errors.append(f"STRUCTURAL: {label}: missing required field {field}")
        for field in sorted(set(edge) - set(EDGE_FIELDS)):
            errors.append(f"STRUCTURAL: {label}: unexpected field {field}")

        edge_id = edge.get("edge_id")
        if not text(edge_id):
            errors.append(f"STRUCTURAL: {label}.edge_id: must be a non-blank string")
        elif edge_id in seen_edges:
            errors.append(f"EDGE: {label}: duplicate edge_id {edge_id!r}")
        else:
            seen_edges.add(edge_id)

        edge_from = edge.get("from")
        edge_to = edge.get("to")
        relation = edge.get("relation")
        status = edge.get("epistemic_status")

        for field, value in (("from", edge_from), ("to", edge_to)):
            if not text(value):
                errors.append(f"STRUCTURAL: {label}.{field}: must be a non-blank string")
        if relation not in RELATIONS:
            errors.append(f"STRUCTURAL: {label}.relation: invalid value {relation!r}; allowed: {', '.join(RELATIONS)}")
        if status not in STATUSES:
            errors.append(f"STRUCTURAL: {label}.epistemic_status: invalid value {status!r}; allowed: {', '.join(STATUSES)}")
        if not text(edge.get("rationale")):
            errors.append(f"STRUCTURAL: {label}.rationale: must be a non-blank string")
        if not text(edge.get("limitations")):
            errors.append(f"STRUCTURAL: {label}.limitations: must be a non-blank string")

        # rule 4 / 5
        if text(edge_from) and text(edge_to):
            for field, value in (("from", edge_from), ("to", edge_to)):
                if value not in node_set:
                    errors.append(f"EDGE: {label}.{field}: {value!r} is not declared in root.nodes")
            if edge_from == edge_to:
                errors.append(f"EDGE: {label}: self edge is forbidden ({edge_from!r})")

        # rule 10
        if status == "INFERRED" and not (isinstance(edge.get("limitations"), str) and "INFERENCE_BOUNDARY:" in edge["limitations"]):
            errors.append(f"EPISTEMIC: {label}: INFERRED requires 'INFERENCE_BOUNDARY:' inside limitations")

        # rules 11-13 : type rules
        source_item = items.get(edge_from) if text(edge_from) else None
        target_item = items.get(edge_to) if text(edge_to) else None
        source_type = source_item.get("knowledge_type") if source_item else None
        target_type = target_item.get("knowledge_type") if target_item else None
        if relation == "CONSTRAINS" and source_item is not None and source_type not in CONSTRAINING_TYPES:
            errors.append(f"TYPE: {label}: CONSTRAINS requires from type in {CONSTRAINING_TYPES}; found {source_type!r}")
        if relation == "VERSION_CONTEXT_FOR" and source_item is not None and source_type != "VERSION_CONTEXT":
            errors.append(f"TYPE: {label}: VERSION_CONTEXT_FOR requires from type VERSION_CONTEXT; found {source_type!r}")
        if relation == "PROCEDURE_PRECEDES":
            if source_item is not None and source_type != "PROCEDURE":
                errors.append(f"TYPE: {label}: PROCEDURE_PRECEDES requires from type PROCEDURE; found {source_type!r}")
            if target_item is not None and target_type != "PROCEDURE":
                errors.append(f"TYPE: {label}: PROCEDURE_PRECEDES requires to type PROCEDURE; found {target_type!r}")
        if relation == "STEP_OF":
            if source_item is not None and source_type != "PROCEDURE":
                errors.append(f"TYPE: {label}: STEP_OF requires from type PROCEDURE; found {source_type!r}")
            if target_item is not None and target_type != "PROCEDURE":
                errors.append(f"TYPE: {label}: STEP_OF requires to type PROCEDURE; found {target_type!r}")
        if relation == "ENFORCEMENT_CONTEXT_FOR":
            if source_item is not None and source_type != "POLICY":
                errors.append(f"TYPE: {label}: ENFORCEMENT_CONTEXT_FOR requires from type POLICY; found {source_type!r}")
            if target_item is not None and target_type != "POLICY":
                errors.append(f"TYPE: {label}: ENFORCEMENT_CONTEXT_FOR requires to type POLICY; found {target_type!r}")

        # rules 16-17 : normalization support
        pair = frozenset((edge_from, edge_to)) if text(edge_from) and text(edge_to) else None
        declared = pairs.get(pair, set()) if pair else set()
        rationale = edge.get("rationale") if isinstance(edge.get("rationale"), str) else ""
        if relation == "SCOPE_PARALLEL_TO":
            if "SCOPE_PARALLEL" not in declared and "NORMALIZATION_JUSTIFICATION:" not in rationale:
                errors.append(f"NORMALIZATION: {label}: SCOPE_PARALLEL_TO needs a Normalization Review pair with relation SCOPE_PARALLEL or 'NORMALIZATION_JUSTIFICATION:' in rationale")
        if relation == "VERSION_VARIANT_OF":
            if "VERSION_VARIANT" not in declared and "VERSION_JUSTIFICATION:" not in rationale:
                errors.append(f"NORMALIZATION: {label}: VERSION_VARIANT_OF needs a Normalization Review pair with relation VERSION_VARIANT or 'VERSION_JUSTIFICATION:' in rationale")

        # rule 18 : conflict safety
        if pair and "CONFLICT_CANDIDATE" in declared:
            errors.append(f"CONFLICT: {label}: pair {sorted(pair)} is a CONFLICT_CANDIDATE in Normalization Review; no graph edge may be created for it")

        if relation in SYMMETRIC_RELATIONS + DIRECTIONAL_RELATIONS and text(edge_from) and text(edge_to):
            directed.setdefault((relation, edge_from, edge_to), []).append(label)

    # rules 14-15 : symmetry
    for (relation, edge_from, edge_to), labels in sorted(directed.items()):
        if relation not in SYMMETRIC_RELATIONS:
            continue
        if (relation, edge_to, edge_from) in directed:
            errors.append(
                f"SYMMETRY: {relation} stores both directions {edge_from!r} -> {edge_to!r} "
                f"({', '.join(labels)} and {', '.join(directed[(relation, edge_to, edge_from)])}); symmetric relations must be stored once"
            )
    # Gate 3.0-R1 addendum: STEP_OF is directional, so a stored reverse edge is a semantic contradiction
    for (relation, edge_from, edge_to), labels in sorted(directed.items()):
        if relation not in DIRECTIONAL_RELATIONS or edge_from == edge_to:
            continue
        reverse = directed.get((relation, edge_to, edge_from))
        if reverse:
            errors.append(
                f"DIRECTION: {relation} stores both directions {edge_from!r} -> {edge_to!r} "
                f"({', '.join(labels)} and {', '.join(reverse)}); opposite edges for this directional relation cannot coexist"
            )
    if not nodes_ok:
        errors.append("STRUCTURAL: graph nodes could not be validated")
    return errors


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 3:
        print("FAIL")
        print("- Usage: python validate_knowledge_graph.py <graph.json> <knowledge-registry.json> <normalization-review.json>")
        return 1
    try:
        data = read_json(args[0])
        knowledge = read_json(args[1])
        review = read_json(args[2])
        schema = read_json(SCHEMA_PATH)
        errors = validate_graph(data, knowledge, review, schema)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"STRUCTURAL: unable to read or validate JSON: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
