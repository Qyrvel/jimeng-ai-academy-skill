"""Gate 3.1 offline edge review validation; Python standard library only."""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = runpy.run_path(str(HERE / "validate_source_registry.py"))
read_json = SOURCE["read_json"]

ROOT_FIELDS = ("reviews",)
REVIEW_FIELDS = ("edge_id", "status", "review_reason", "directness", "curriculum_leakage")
STATUSES = ("KEEP", "MODIFY", "REMOVE", "NEEDS_REVIEW")
DIRECTNESS = ("DIRECT", "TRANSITIVE", "NOT_APPLICABLE")
CHANGE_STATUSES = ("MODIFY", "REMOVE")


def text(value):
    return isinstance(value, str) and bool(value.strip())


def validate_reviews(data, graph, final=False):
    errors = []
    if not isinstance(data, dict):
        return ["STRUCTURAL: root: must be an object"]
    for field in ROOT_FIELDS:
        if field not in data:
            errors.append(f"STRUCTURAL: root: missing required field {field}")
    for field in sorted(set(data) - set(ROOT_FIELDS)):
        errors.append(f"STRUCTURAL: root: unexpected field {field}")
    reviews = data.get("reviews")
    if not isinstance(reviews, list):
        errors.append("STRUCTURAL: root.reviews: must be an array")
        return errors

    graph_edge_ids = []
    if isinstance(graph, dict) and isinstance(graph.get("edges"), list):
        for edge in graph["edges"]:
            if isinstance(edge, dict) and text(edge.get("edge_id")):
                graph_edge_ids.append(edge["edge_id"])
    graph_ids = set(graph_edge_ids)

    seen = set()
    for index, review in enumerate(reviews):
        label = f"reviews[{index}]"
        if not isinstance(review, dict):
            errors.append(f"STRUCTURAL: {label}: must be an object")
            continue
        for field in REVIEW_FIELDS:
            if field not in review:
                errors.append(f"STRUCTURAL: {label}: missing required field {field}")
        for field in sorted(set(review) - set(REVIEW_FIELDS)):
            errors.append(f"STRUCTURAL: {label}: unexpected field {field}")
        edge_id = review.get("edge_id")
        if not text(edge_id):
            errors.append(f"STRUCTURAL: {label}.edge_id: must be a non-blank string")
        elif edge_id not in graph_ids:
            errors.append(f"REFERENCE: {label}.edge_id: {edge_id!r} does not exist in the graph")
        else:
            if edge_id in seen:
                errors.append(f"REVIEW: {label}: duplicate review for edge_id {edge_id!r}")
            seen.add(edge_id)
        status = review.get("status")
        if status not in STATUSES:
            errors.append(f"STRUCTURAL: {label}.status: invalid value {status!r}; allowed: {', '.join(STATUSES)}")
        directness = review.get("directness")
        if directness not in DIRECTNESS:
            errors.append(f"STRUCTURAL: {label}.directness: invalid value {directness!r}; allowed: {', '.join(DIRECTNESS)}")
        reason = review.get("review_reason")
        if not text(reason):
            errors.append(f"STRUCTURAL: {label}.review_reason: must be a non-blank string")
        leakage = review.get("curriculum_leakage")
        if not isinstance(leakage, bool):
            errors.append(f"STRUCTURAL: {label}.curriculum_leakage: must be a boolean")
        if final:
            if status != "KEEP":
                errors.append(f"FINAL: {label}: retained edge requires status KEEP; found {status!r}")
            if leakage is not False:
                errors.append(f"FINAL: {label}: retained edge requires curriculum_leakage=false")
        # rule 8 : a change decision must always be explained
        if status in CHANGE_STATUSES and not text(reason):
            errors.append(f"REVIEW: {label}: status {status} requires a non-blank review_reason")
        # rule 9 : a transitive edge may not be silently kept
        if directness == "TRANSITIVE" and status == "KEEP":
            if not (isinstance(reason, str) and "DIRECT_DEPENDENCY_JUSTIFICATION:" in reason):
                errors.append(
                    f"REVIEW: {label}: directness TRANSITIVE with status KEEP requires 'DIRECT_DEPENDENCY_JUSTIFICATION:' in review_reason"
                )

    for edge_id in graph_edge_ids:
        if edge_id not in seen:
            errors.append(f"REVIEW: graph edge {edge_id!r} has no review entry")
    return errors


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    final = len(args) == 3 and args[2] == "--final"
    if len(args) != 2 and not final:
        print("FAIL")
        print("- Usage: python validate_edge_review.py <edge-review.json> <graph.json> [--final]")
        return 1
    try:
        data = read_json(args[0])
        graph = read_json(args[1])
        errors = validate_reviews(data, graph, final=final)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"STRUCTURAL: unable to read or validate JSON: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
