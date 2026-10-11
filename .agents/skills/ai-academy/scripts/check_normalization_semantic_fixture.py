"""Gate 2.1-R1 semantic fixture checker; Python standard library only.

Compares an agent-produced normalization review with the expected fixture and
compares review files mechanically. It makes no natural-language judgement.
"""

import runpy
import sys
from pathlib import Path

SOURCE = runpy.run_path(str(Path(__file__).resolve().parent / "validate_source_registry.py"))
read_json = SOURCE["read_json"]


def text(value):
    return isinstance(value, str) and bool(value.strip())


def index_reviews(data, label):
    errors = []
    if not isinstance(data, dict) or not isinstance(data.get("reviews"), list):
        return {}, [f"{label}: expected an object containing a reviews array"]
    by_id = {}
    for position, review in enumerate(data["reviews"]):
        if not isinstance(review, dict):
            errors.append(f"{label}: reviews[{position}] must be an object")
            continue
        review_id = review.get("review_id")
        if not text(review_id):
            errors.append(f"{label}: reviews[{position}] has no usable review_id")
            continue
        if review_id in by_id:
            errors.append(f"{label}: duplicate review_id {review_id!r}")
            continue
        by_id[review_id] = review
    return by_id, errors


def itemset(review):
    ids = review.get("item_ids")
    if not isinstance(ids, list):
        return None
    return set(ids)


def compare(actual, expected):
    errors = []
    actual_by_id, actual_errors = index_reviews(actual, "actual")
    expected_by_id, expected_errors = index_reviews(expected, "expected")
    errors.extend(actual_errors)
    errors.extend(expected_errors)
    if errors:
        return errors

    missing = sorted(set(expected_by_id) - set(actual_by_id))
    extra = sorted(set(actual_by_id) - set(expected_by_id))
    for review_id in missing:
        errors.append(f"{review_id}: missing from actual review")
    for review_id in extra:
        errors.append(f"{review_id}: unexpected review_id in actual review")

    for review_id in sorted(set(expected_by_id) & set(actual_by_id)):
        want = expected_by_id[review_id]
        got = actual_by_id[review_id]
        want_items = itemset(want)
        got_items = itemset(got)
        if want_items is None:
            errors.append(f"{review_id}: expected item_ids must be an array")
        elif got_items is None:
            errors.append(f"{review_id}: actual item_ids must be an array")
        elif want_items != got_items:
            errors.append(
                f"{review_id}: item_ids mismatch; expected {sorted(want_items)}; actual {sorted(got_items)}"
            )
        want_relation = want.get("relation")
        got_relation = got.get("relation")
        if want_relation != got_relation:
            errors.append(
                f"{review_id}: relation mismatch; expected relation {want_relation}; actual relation {got_relation}"
            )
        want_decision = want.get("decision")
        got_decision = got.get("decision")
        if want_decision != got_decision:
            errors.append(
                f"{review_id}: decision mismatch; expected decision {want_decision}; actual decision {got_decision}"
            )
    return errors


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("FAIL")
        print("- Usage: python check_normalization_semantic_fixture.py <actual-review.json> <expected-review.json>")
        return 1
    try:
        actual = read_json(args[0])
        expected = read_json(args[1])
        errors = compare(actual, expected)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"unable to read or compare review files: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
