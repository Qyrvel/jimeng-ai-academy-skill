"""Mastery contract validation and deterministic decision simulation; Python standard library only.

Usage:
  python validate_mastery.py <mastery-map.json> <full-assessment-mapping.json> <course-manifest.json> [graph.json ...]
  python validate_mastery.py --decision <evidence-snapshot.json> <mastery-map.json>

Checks (gate 4.6 section 39):
  Unit         1 mastery_unit_id unique + format, 2 lesson_ids valid, 3 required_requirement_ids exist
  Outcomes     4 required_outcomes in range, 5 every lesson unit covers all of its lesson's outcomes
  Requirements 6 every required outcome is supported by >= 1 required requirement
  Hard order   7 the 4 lesson-level hard transitions are mapped as mastery gates,
               8 the 5 supporting hard edges resolve, 9 transition and edge counts stay separate,
               10 non-order relations must not become gates
  Rules       11 pass_rule / 12 retry_rule / 13 remediation_rule non-empty,
               14 decision enum valid, 15 reason enum valid
  Derived     16 every declared derived metric is recomputed and compared

Decision mode evaluates an evidence snapshot and compares it with the snapshot's expected_decision.
It is a pure function of the snapshot: no student identity, history or persistent state is stored.
"""

import re
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
read_json = runpy.run_path(str(HERE / "validate_source_registry.py"))["read_json"]

DECISIONS = ("PASS", "RETRY", "REMEDIATION", "BLOCKED")
REASONS = ("PASS_ALL_REQUIRED_OUTCOMES", "RETRY_EXECUTION_INCOMPLETE", "RETRY_EVIDENCE_INCOMPLETE",
           "REMEDIATE_OUTCOME_GAP", "REMEDIATE_BOUNDARY_MISCONCEPTION", "BLOCKED_BY_HARD_PREREQUISITE")
ORDER_RELATIONS = ("PREREQUISITE_OF", "PROCEDURE_PRECEDES")
UNIT_TYPES = ("LESSON", "SEQUENCE_PAIR")
REF_PATTERN = re.compile(r"^(JCA-M[0-9]{2}-L[0-9]{2})#([0-9]+)$")


def load_course(manifest_path):
    manifest = read_json(str(manifest_path))
    root = Path(manifest_path).resolve().parent
    lessons = {}
    for entry in manifest["lesson_files"]:
        lessons[entry["lesson_id"]] = read_json(str((root / entry["json_path"]).resolve()))
    return manifest, lessons


def decide(snapshot, unit):
    """Deterministic decision contract; the order of the branches IS the contract.

    Execution/evidence-layer gaps produce RETRY; an outcome-layer gap produces REMEDIATION.
    """
    required = set(unit["required_outcomes"])
    if not snapshot.get("hard_prerequisites_satisfied", True):
        return "BLOCKED", "BLOCKED_BY_HARD_PREREQUISITE"
    satisfied = set(snapshot.get("satisfied_outcomes", []))
    misconceptions = set(snapshot.get("misconception_outcomes", []))
    missing = required - satisfied
    if not missing:
        return "PASS", "PASS_ALL_REQUIRED_OUTCOMES"
    if missing & misconceptions:
        return "REMEDIATION", "REMEDIATE_BOUNDARY_MISCONCEPTION"
    if not snapshot.get("evidence_submitted", True):
        return "RETRY", "RETRY_EVIDENCE_INCOMPLETE"
    if not snapshot.get("execution_criteria_met", True):
        return "RETRY", "RETRY_EXECUTION_INCOMPLETE"
    return "REMEDIATION", "REMEDIATE_OUTCOME_GAP"


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)

    # ---- decision mode -------------------------------------------------
    if args and args[0] == "--decision":
        if len(args) < 3:
            print("FAIL")
            print("- Usage: python validate_mastery.py --decision <evidence-snapshot.json> <mastery-map.json>")
            return 1
        try:
            snap = read_json(args[1])
            mapp = read_json(args[2])
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print("FAIL")
            print(f"- STRUCTURAL: unable to read input: {exc}")
            return 1
        units = {u["mastery_unit_id"]: u for u in mapp.get("units", [])}
        errors = []
        uid = snap.get("mastery_unit_id")
        if uid not in units:
            print("FAIL")
            print(f"- CONSISTENCY: snapshot: unknown mastery_unit_id {uid!r}")
            return 1
        unit = units[uid]
        for ref in snap.get("satisfied_outcomes", []) + snap.get("misconception_outcomes", []):
            parsed = REF_PATTERN.match(ref) if isinstance(ref, str) else None
            if not parsed or ref not in unit["required_outcomes"]:
                errors.append(f"CONSISTENCY: snapshot: {ref!r} is not a required outcome of {uid}")
        if snap.get("expected_decision") not in DECISIONS:
            errors.append(f"STRUCTURAL: snapshot: expected_decision {snap.get('expected_decision')!r} invalid")
        if snap.get("expected_reason") not in REASONS:
            errors.append(f"STRUCTURAL: snapshot: expected_reason {snap.get('expected_reason')!r} invalid")
        decision, reason = decide(snap, unit)
        if decision != snap.get("expected_decision"):
            errors.append(f"CONSISTENCY: {uid}: computed {decision}/{reason}, "
                          f"snapshot expected {snap.get('expected_decision')}/{snap.get('expected_reason')}")
        elif reason != snap.get("expected_reason"):
            errors.append(f"CONSISTENCY: {uid}: computed reason {reason}, "
                          f"snapshot expected {snap.get('expected_reason')}")
        print("FAIL" if errors else "PASS")
        for e in errors:
            print("- " + e)
        return int(bool(errors))

    # ---- mapping mode --------------------------------------------------
    if len(args) < 3:
        print("FAIL")
        print("- Usage: python validate_mastery.py <mastery-map.json> <full-assessment-mapping.json> "
              "<course-manifest.json> [graph.json ...]")
        return 1
    try:
        data = read_json(args[0])
        mapping = read_json(args[1])
        manifest, lessons = load_course(Path(args[2]).resolve())
        edges = []
        for p in args[3:]:
            edges += read_json(p).get("edges", [])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("FAIL")
        print(f"- STRUCTURAL: unable to read input: {exc}")
        return 1
    errors = []

    def fail(message):
        errors.append("CONSISTENCY: " + message)

    reqs = {r["requirement_id"]: r for r in mapping.get("requirements", [])}
    contract = data.get("decision_contract") or {}
    if sorted(contract.get("decision_enum") or []) != sorted(DECISIONS):
        fail(f"decision_contract.decision_enum must be exactly {list(DECISIONS)}")
    for value in contract.get("reason_enum") or []:
        if value not in REASONS:
            fail(f"decision_contract.reason_enum contains invalid value {value!r}")
    units = data.get("units") or []
    uids = [u.get("mastery_unit_id") for u in units]
    if len(set(uids)) != len(uids):
        fail("mastery_unit_id must be unique")
    for uid in uids:
        if not isinstance(uid, str) or not re.match(r"^JCA-MU-L[0-9]{2}$", uid):
            fail(f"mastery_unit_id {uid!r} must match JCA-MU-L##")

    unit_of_lesson = {}
    for unit in units:
        uid = unit.get("mastery_unit_id")
        if unit.get("unit_type") not in UNIT_TYPES:
            fail(f"{uid}: unit_type {unit.get('unit_type')!r} is not allowed")
        for lid in unit.get("lesson_ids") or []:
            if lid not in lessons:
                fail(f"{uid}: lesson_id {lid!r} is not a canonical lesson")
            unit_of_lesson[lid] = uid
        for rid in unit.get("required_requirement_ids") or []:
            if rid not in reqs:
                fail(f"{uid}: required_requirement_id {rid!r} does not exist in the mapping")
        refs = unit.get("required_outcomes") or []
        if not refs:
            fail(f"{uid}: required_outcomes must not be empty")
        for ref in refs:
            parsed = REF_PATTERN.match(ref) if isinstance(ref, str) else None
            if not parsed:
                fail(f"{uid}: required_outcome {ref!r} must look like <lesson_id>#<index>")
                continue
            lid, idx = parsed.group(1), int(parsed.group(2))
            if lid not in lessons:
                fail(f"{uid}: required_outcome references unknown lesson {lid!r}")
            elif lid not in (unit.get("lesson_ids") or []):
                fail(f"{uid}: required_outcome {ref!r} is outside lesson_ids")
            elif idx >= len(lessons[lid]["learner_outcomes"]):
                fail(f"{uid}: required_outcome {ref!r} is out of range")
        for key in ("pass_rule", "retry_rule", "remediation_rule", "limitations"):
            if not str(unit.get(key, "")).strip():
                fail(f"{uid}: {key} must not be empty")
        for field, allowed in (("decision_enum", DECISIONS), ("reason_enum", REASONS)):
            if field in unit:
                for value in unit[field]:
                    if value not in allowed:
                        fail(f"{uid}: {field} contains invalid value {value!r}")

    # 5: every lesson unit covers all outcomes of its lesson
    for unit in units:
        if unit.get("unit_type") != "LESSON":
            continue
        for lid in unit.get("lesson_ids") or []:
            if lid not in lessons:
                continue
            expected = {f"{lid}#{i}" for i in range(len(lessons[lid]["learner_outcomes"]))}
            missing = expected - set(unit.get("required_outcomes") or [])
            if missing:
                fail(f"{unit['mastery_unit_id']}: required_outcomes misses {sorted(missing)}")
    missing_units = sorted({lid for lid in lessons} - set(unit_of_lesson))
    if missing_units:
        fail("canonical lessons without a mastery unit: " + ", ".join(missing_units))

    # 6: every required outcome is supported by at least one required requirement
    for unit in units:
        supported = set()
        for rid in unit.get("required_requirement_ids") or []:
            if rid in reqs:
                supported |= set(reqs[rid].get("target_outcomes") or [])
        unsupported = set(unit.get("required_outcomes") or []) - supported
        if unsupported:
            fail(f"{unit['mastery_unit_id']}: required outcomes without a requirement: {sorted(unsupported)}")

    # 7-10: hard sequence gating
    kl, module_of = {}, {}
    for lid, lesson in lessons.items():
        module_of[lid] = lesson["module_id"]
        for k in lesson["knowledge_refs"]:
            kl.setdefault(k, set()).add(lid)
    gates = {}
    supporting = 0
    for edge in edges:
        if edge.get("relation") not in ORDER_RELATIONS:
            continue
        for sl in sorted(kl.get(edge.get("from"), set())):
            for tl in sorted(kl.get(edge.get("to"), set())):
                if sl == tl or module_of.get(sl) != module_of.get(tl):
                    continue
                supporting += 1
                gates.setdefault(tl, set()).add(sl)
    expected_gate_count = len(gates)
    declared = data.get("hard_sequence_summary") or {}
    for unit in units:
        lid = (unit.get("lesson_ids") or [None])[0]
        expected_prev = sorted(unit_of_lesson[p] for p in gates.get(lid, set()) if p in unit_of_lesson)
        declared_prev = sorted(unit.get("hard_prerequisite_units") or [])
        if expected_prev != declared_prev:
            fail(f"{unit.get('mastery_unit_id')}: hard_prerequisite_units expected {expected_prev}; "
                 f"found {declared_prev}")

    derived = data.get("derived")
    if derived is None:
        fail("derived metrics block is required: every declared metric must be recomputable")
    else:
        expected = {
            "mastery_unit_count": len(units),
            "lesson_mastery_unit_count": sum(1 for u in units if u.get("unit_type") == "LESSON"),
            "sequence_pair_mastery_unit_count": sum(1 for u in units if u.get("unit_type") == "SEQUENCE_PAIR"),
            "mastery_hard_transition_count": expected_gate_count,
            "mastery_supporting_hard_edge_count": supporting,
            "non_order_mastery_gate_misuse_count": 0,
        }
        for key, value in expected.items():
            if derived.get(key) != value:
                fail(f"derived.{key}: expected {value}; found {derived.get(key)}")
    if declared.get("mastery_hard_transition_count") not in (None, expected_gate_count):
        fail(f"hard_sequence_summary.mastery_hard_transition_count: expected {expected_gate_count}")
    if declared.get("mastery_supporting_hard_edge_count") not in (None, supporting):
        fail(f"hard_sequence_summary.mastery_supporting_hard_edge_count: expected {supporting}")

    print("FAIL" if errors else "PASS")
    for error in errors:
        print("- " + error)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
