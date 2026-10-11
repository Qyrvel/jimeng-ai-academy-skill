"""Gate 4.7B deterministic course-level evaluation engine; Python standard library only.

Usage:
  python evaluate_course_completion.py <contract.json> <snapshot.json> <mastery-map.json> \
      <course-manifest.json> [graph.json ...] [--json]

The engine answers one question only: given the frozen course structure and one ephemeral
evaluation snapshot, what is the deterministic course-level evaluation result?

It never re-invents Lesson mastery.  It consumes the production mastery decision contract
(`PASS` / `RETRY` / `REMEDIATION` / `BLOCKED`) and only:

  * aggregates Lesson decisions into Module results,
  * aggregates Module results plus hard-sequence integrity into the Course result,
  * routes RETRY / REMEDIATION / BLOCKED targets losslessly,
  * rejects an evaluation snapshot that cannot legally exist.

No network, no database, no persistent learner write, no student identity, no numeric grade,
no synthetic Track level.  Every output collection is deterministically ordered.
"""

import io
import json
import re
import sys
from pathlib import Path

DECISIONS = ("PASS", "RETRY", "REMEDIATION", "BLOCKED")
COURSE_STATUSES = ("COMPLETE", "RETRY_REQUIRED", "REMEDIATION_REQUIRED", "BLOCKED")
INCONSISTENT = "INCONSISTENT_EVALUATION_SNAPSHOT"
ORDER_RELATIONS = ("PREREQUISITE_OF", "PROCEDURE_PRECEDES")
LESSON_RE = re.compile(r"^JCA-M[0-9]{2}-L[0-9]{2}$")
UNIT_RE = re.compile(r"^JCA-MU-L[0-9]{2}$")
OUTCOME_RE = re.compile(r"^(JCA-M[0-9]{2}-L[0-9]{2})#([0-9]+)$")

LESSON_TO_MODULE_DECISION = {
    "PASS": "COMPLETE",
    "RETRY": "RETRY_REQUIRED",
    "REMEDIATION": "REMEDIATION_REQUIRED",
    "BLOCKED": "BLOCKED",
}

MODULE_PRECEDENCE = ("BLOCKED", "REMEDIATION_REQUIRED", "RETRY_REQUIRED", "COMPLETE")
COURSE_PRECEDENCE = ("BLOCKED", "REMEDIATION_REQUIRED", "RETRY_REQUIRED", "COMPLETE")

# Fields that would turn this ephemeral snapshot into a persistent learner record.
FORBIDDEN_SNAPSHOT_KEYS = (
    "student_id", "user_id", "learner_id", "learner_profile", "profile",
    "history", "attempt_history", "attempt_sequence", "attempts",
    "timestamp", "timestamps", "created_at", "updated_at", "saved_at",
    "progress", "saved_progress", "progress_timeline", "timeline",
    "database_key", "db_key", "record_id", "persistent_id", "session_id",
    "grade", "score", "percentage", "gpa", "final_score", "letter_grade",
)


class SnapshotError(Exception):
    """A snapshot that cannot legally be evaluated; carries a code and a message."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def read_json(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_json_or_fail(path):
    try:
        return read_json(path)
    except (OSError, ValueError) as exc:
        raise SnapshotError("STRUCTURAL", f"unable to read input {path}: {exc}")


# --------------------------------------------------------------------------------------
# frozen structure
# --------------------------------------------------------------------------------------

class CourseStructure(object):
    """The authoritative course / module / mastery structure, recomputed from frozen truth."""

    def __init__(self, manifest, lessons, mastery, graphs):
        self.manifest = manifest
        self.lessons = lessons
        self.mastery = mastery
        self.module_order = list(manifest["module_order"])
        self.lessons_by_module = {m: list(manifest["lesson_order_by_module"][m])
                                  for m in self.module_order}
        self.lesson_order = [lid for m in self.module_order for lid in self.lessons_by_module[m]]
        self.module_of = {lid: m for m in self.module_order for lid in self.lessons_by_module[m]}
        self.unit_by_id = {u["mastery_unit_id"]: u for u in mastery["units"]}
        self.unit_of_lesson = {}
        for uid, unit in self.unit_by_id.items():
            for lid in unit.get("lesson_ids") or []:
                self.unit_of_lesson[lid] = uid
        self.lesson_of_unit = {uid: (u.get("lesson_ids") or [None])[0]
                               for uid, u in self.unit_by_id.items()}
        self.graphs = graphs
        self.order_edges = []
        self.hard_transitions = {}
        self.supporting_edges = []
        self.non_order_grounded_pairs = []
        self._build_sequence()

    def _build_sequence(self):
        knowledge_of_lesson = {}
        for lid, lesson in self.lessons.items():
            for ref in lesson.get("knowledge_refs") or []:
                knowledge_of_lesson.setdefault(ref, set()).add(lid)
        for graph in self.graphs:
            for edge in graph.get("edges") or []:
                frm = set(knowledge_of_lesson.get(edge.get("from"), set()))
                to = set(knowledge_of_lesson.get(edge.get("to"), set()))
                pairs = [(a, b) for a in sorted(frm) for b in sorted(to)
                         if a != b and self.module_of.get(a) == self.module_of.get(b)]
                if not pairs:
                    continue
                if edge.get("relation") in ORDER_RELATIONS:
                    for a, b in pairs:
                        self.supporting_edges.append({
                            "edge_id": edge.get("edge_id"),
                            "relation": edge.get("relation"),
                            "from_lesson_id": a,
                            "to_lesson_id": b,
                        })
                        self.hard_transitions.setdefault(b, set()).add(a)
                else:
                    # A non-order relation never becomes a gate; it is recorded only so the
                    # guard has a real, non-empty population to prove exclusion against.
                    for a, b in pairs:
                        self.non_order_grounded_pairs.append({
                            "edge_id": edge.get("edge_id"),
                            "relation": edge.get("relation"),
                            "from_lesson_id": a,
                            "to_lesson_id": b,
                        })
        self.hard_transitions = {k: sorted(v) for k, v in sorted(self.hard_transitions.items())}

    def prerequisite_units_of(self, lesson_id):
        """Mastery units that must already be PASS before this lesson can be PASS."""
        units = []
        for prior_lesson in self.hard_transitions.get(lesson_id, []):
            uid = self.unit_of_lesson.get(prior_lesson)
            if uid:
                units.append(uid)
        declared = self.unit_by_id.get(self.unit_of_lesson.get(lesson_id), {})
        for uid in declared.get("hard_prerequisite_units") or []:
            if uid not in units:
                units.append(uid)
        return sorted(units)

    def hard_sequence_integrity(self, per_lesson_decision):
        """A snapshot that declares a later unit PASS while its hard prerequisite is not PASS
        cannot legally exist; it is reported, never silently rewritten to BLOCKED."""
        violations = []
        for lesson_id in sorted(self.hard_transitions):
            if per_lesson_decision.get(lesson_id) != "PASS":
                continue
            for prior_lesson in self.hard_transitions[lesson_id]:
                if prior_lesson not in per_lesson_decision:
                    continue
                if per_lesson_decision[prior_lesson] != "PASS":
                    violations.append({
                        "lesson_id": lesson_id,
                        "hard_prerequisite_lesson_id": prior_lesson,
                        "declared_decision": "PASS",
                        "hard_prerequisite_decision": per_lesson_decision[prior_lesson],
                    })
        return {
            "hard_transition_count": len(self.hard_transitions),
            "supporting_hard_edge_count": len(self.supporting_edges),
            "hard_transitions": {k: list(v) for k, v in self.hard_transitions.items()},
            "satisfied_count": sum(1 for lesson_id in self.hard_transitions
                                   if per_lesson_decision.get(lesson_id) == "PASS"
                                   and all(per_lesson_decision.get(p) == "PASS"
                                           for p in self.hard_transitions[lesson_id])),
            "violation_count": len(violations),
            "violations": violations,
            "satisfied": not violations,
        }


# --------------------------------------------------------------------------------------
# snapshot
# --------------------------------------------------------------------------------------

def check_snapshot_shape(snapshot):
    """Reject anything that is not a one-shot, identity-free evaluation snapshot."""
    for key in sorted(snapshot):
        if key.lower() in FORBIDDEN_SNAPSHOT_KEYS:
            raise SnapshotError("STUDENT_STATE_FIELD",
                                f"snapshot carries forbidden non-ephemeral field {key!r}")
    if "lessons" not in snapshot:
        raise SnapshotError("STRUCTURAL", "snapshot must carry a 'lessons' array")
    entries = snapshot["lessons"]
    if not isinstance(entries, list):
        raise SnapshotError("STRUCTURAL", "snapshot 'lessons' must be an array")
    return entries


def normalise_lesson_results(structure, entries):
    """Map one declared result per canonical lesson; the Lesson is the observable unit.

    `lesson_id` is required for every entry.  `mastery_unit_id` is optional and, when present,
    must be the production mastery unit of that lesson.
    """
    results = {}
    outcome_refs = {}
    blocked_refs = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise SnapshotError("STRUCTURAL", f"lessons[{index}] must be an object")
        for key in sorted(entry):
            if key.lower() in FORBIDDEN_SNAPSHOT_KEYS:
                raise SnapshotError("STUDENT_STATE_FIELD",
                                    f"lessons[{index}] carries forbidden field {key!r}")
        lesson_id = entry.get("lesson_id")
        if not isinstance(lesson_id, str) or not LESSON_RE.match(lesson_id):
            raise SnapshotError("EXTRA_LESSON_RESULT",
                                f"lessons[{index}].lesson_id {lesson_id!r} is not a canonical lesson")
        if lesson_id not in structure.lessons:
            raise SnapshotError("EXTRA_LESSON_RESULT",
                                f"lessons[{index}].lesson_id {lesson_id!r} is not a canonical lesson")
        unit_id = entry.get("mastery_unit_id")
        if unit_id is not None:
            if not isinstance(unit_id, str) or not UNIT_RE.match(unit_id):
                raise SnapshotError("UNKNOWN_MASTERY_UNIT",
                                    f"{lesson_id}: mastery_unit_id {unit_id!r} is malformed")
            if unit_id not in structure.unit_by_id:
                raise SnapshotError("UNKNOWN_MASTERY_UNIT",
                                    f"{lesson_id}: unknown mastery unit {unit_id!r}")
            if structure.unit_of_lesson.get(lesson_id) != unit_id:
                raise SnapshotError(
                    "UNKNOWN_MASTERY_UNIT",
                    f"{lesson_id}: mastery unit {unit_id!r} is not the production mastery unit "
                    f"of this lesson ({structure.unit_of_lesson.get(lesson_id)!r})")
        decision = entry.get("decision")
        if decision not in DECISIONS:
            raise SnapshotError("UNKNOWN_DECISION",
                                f"{lesson_id}: decision {decision!r} is not one of {list(DECISIONS)}")
        if lesson_id in results:
            raise SnapshotError("DUPLICATE_LESSON_RESULT",
                                f"{lesson_id}: duplicate Lesson result in snapshot")
        results[lesson_id] = decision
        refs = entry.get("unmet_outcome_refs") or []
        if not isinstance(refs, list):
            raise SnapshotError("STRUCTURAL", f"{lesson_id}: unmet_outcome_refs must be an array")
        for ref in refs:
            if not isinstance(ref, str) or not OUTCOME_RE.match(ref):
                raise SnapshotError("STRUCTURAL",
                                    f"{lesson_id}: unmet_outcome_ref {ref!r} is malformed")
            owner = OUTCOME_RE.match(ref).group(1)
            if owner != lesson_id:
                raise SnapshotError(
                    "INVALID_ROUTING_TARGET",
                    f"{lesson_id}: unmet_outcome_ref {ref!r} does not belong to this Lesson")
        outcome_refs[lesson_id] = sorted(set(refs))
        prereqs = entry.get("blocked_by_mastery_units") or []
        if not isinstance(prereqs, list):
            raise SnapshotError("STRUCTURAL",
                                f"{lesson_id}: blocked_by_mastery_units must be an array")
        for uid in prereqs:
            if not isinstance(uid, str) or not UNIT_RE.match(uid) or uid not in structure.unit_by_id:
                raise SnapshotError("UNKNOWN_MASTERY_UNIT",
                                    f"{lesson_id}: blocked_by_mastery_units names unknown unit {uid!r}")
            legal = structure.prerequisite_units_of(lesson_id)
            if uid not in legal:
                raise SnapshotError(
                    "NON_ORDER_COURSE_COMPLETION_GATE",
                    f"{lesson_id}: unit {uid!r} is not a legal hard prerequisite of this Lesson")
        blocked_refs[lesson_id] = sorted(set(prereqs))

    extra = sorted(set(results) - set(structure.lesson_order))
    if extra:
        raise SnapshotError("EXTRA_LESSON_RESULT",
                            "snapshot carries non-canonical Lesson results: " + ", ".join(extra))
    missing = sorted(set(structure.lesson_order) - set(results))
    if missing:
        raise SnapshotError("MISSING_LESSON_RESULT",
                            "snapshot omits canonical Lesson results: " + ", ".join(missing))

    # A declared BLOCKED reason must be the real unmet hard prerequisite set for that Lesson.
    # The snapshot's own words are checked against the snapshot's own decisions; nothing is
    # silently rewritten to BLOCKED and nothing declared BLOCKED is silently accepted.
    for lesson_id in structure.lesson_order:
        if results[lesson_id] != "BLOCKED":
            continue
        real = []
        for uid in structure.prerequisite_units_of(lesson_id):
            prereq_lesson = structure.lesson_of_unit.get(uid)
            if prereq_lesson is None or results.get(prereq_lesson) != "PASS":
                real.append(uid)
        declared = blocked_refs.get(lesson_id) or []
        if sorted(set(real)) != sorted(set(declared)):
            raise SnapshotError(
                "BLOCKED_PREREQUISITE_INCONSISTENT",
                f"{lesson_id}: declared unmet hard prerequisite units {sorted(set(declared))} "
                f"differ from the real unmet set {sorted(set(real))}")
    return results, outcome_refs, blocked_refs


# --------------------------------------------------------------------------------------
# aggregation
# --------------------------------------------------------------------------------------

def module_results(structure, per_lesson_decision):
    results = []
    for module_id in structure.module_order:
        lesson_ids = structure.lessons_by_module[module_id]
        by_lesson = {lid: per_lesson_decision[lid] for lid in lesson_ids}
        module_decision = "COMPLETE"
        for candidate in MODULE_PRECEDENCE:
            if candidate == "COMPLETE":
                continue
            if any(LESSON_TO_MODULE_DECISION[d] == candidate for d in by_lesson.values()):
                module_decision = candidate
                break
        results.append({
            "module_id": module_id,
            "lesson_count": len(lesson_ids),
            "lesson_decisions": by_lesson,
            "lesson_results": [{"lesson_id": lid,
                                "mastery_unit_id": structure.unit_of_lesson.get(lid),
                                "decision": by_lesson[lid]} for lid in lesson_ids],
            "all_lessons_pass": all(d == "PASS" for d in by_lesson.values()),
            "module_status": module_decision,
        })
    return results


def course_status(structure, modules, integrity):
    if integrity["violation_count"]:
        # Could not legally happen; reported as-is, never converted into BLOCKED.
        return INCONSISTENT
    statuses = {m["module_status"] for m in modules}
    if statuses == {"COMPLETE"}:
        status = "COMPLETE"
    else:
        status = "COMPLETE"
        for candidate in COURSE_PRECEDENCE:
            if candidate == "COMPLETE":
                continue
            if candidate in statuses:
                status = candidate
                break
    # Course completion additionally requires every canonical Lesson to be PASS.
    if status == "COMPLETE" and not all(
            d == "PASS" for m in modules for d in m["lesson_decisions"].values()):
        return "BLOCKED"
    return status


def routing(structure, per_lesson_decision, outcome_refs, blocked_refs):
    retry_targets, remediation_targets, blocked_targets = [], [], []
    blocked_by_mastery_units = []
    for lesson_id in structure.lesson_order:
        decision = per_lesson_decision[lesson_id]
        unit_id = structure.unit_of_lesson.get(lesson_id)
        if decision == "RETRY":
            retry_targets.append({
                "lesson_id": lesson_id,
                "mastery_unit_id": unit_id,
                "assessment_evidence_required": True,
            })
        elif decision == "REMEDIATION":
            refs = outcome_refs.get(lesson_id) or []
            remediation_targets.append({
                "lesson_id": lesson_id,
                "mastery_unit_id": unit_id,
                "unmet_outcome_refs": refs,
                "recommended_review_scope": lesson_id,
            })
        elif decision == "BLOCKED":
            declared = blocked_refs.get(lesson_id) or []
            prereqs = declared or structure.prerequisite_units_of(lesson_id)
            unmet = []
            for uid in prereqs:
                prereq_lesson = structure.lesson_of_unit.get(uid)
                if prereq_lesson is None:
                    unmet.append(uid)
                    continue
                if per_lesson_decision.get(prereq_lesson) != "PASS":
                    unmet.append(uid)
            blocked_targets.append({
                "lesson_id": lesson_id,
                "mastery_unit_id": unit_id,
                "unmet_hard_prerequisite_units": sorted(set(unmet)),
            })
            for uid in sorted(set(unmet)):
                blocked_by_mastery_units.append({
                    "mastery_unit_id": uid,
                    "lesson_id": structure.lesson_of_unit.get(uid),
                    "blocks_lesson_id": lesson_id,
                })
    return {
        "retry_targets": sorted(retry_targets, key=lambda t: t["lesson_id"]),
        "remediation_targets": sorted(remediation_targets, key=lambda t: t["lesson_id"]),
        "blocked_targets": sorted(blocked_targets, key=lambda t: t["lesson_id"]),
        "blocked_by_mastery_units": sorted(blocked_by_mastery_units,
                                           key=lambda t: (t["blocks_lesson_id"],
                                                          t["mastery_unit_id"])),
    }


def all_targets_empty(routes):
    return not (routes["retry_targets"] or routes["remediation_targets"]
                or routes["blocked_targets"] or routes["blocked_by_mastery_units"])


def evaluate(contract, snapshot, structure):
    entries = check_snapshot_shape(snapshot)
    if snapshot.get("contract_id") not in (None, contract.get("contract_id")):
        raise SnapshotError("CONTRACT_IDENTITY",
                            f"snapshot contract_id {snapshot.get('contract_id')!r} != "
                            f"{contract.get('contract_id')!r}")
    if snapshot.get("course_id") != contract.get("course_id"):
        raise SnapshotError("COURSE_IDENTITY",
                            f"snapshot course_id {snapshot.get('course_id')!r} != "
                            f"{contract.get('course_id')!r}")
    per_lesson_decision, outcome_refs, blocked_refs = normalise_lesson_results(structure, entries)
    modules = module_results(structure, per_lesson_decision)
    integrity = structure.hard_sequence_integrity(per_lesson_decision)
    routes = routing(structure, per_lesson_decision, outcome_refs, blocked_refs)
    status = course_status(structure, modules, integrity)
    if status == "COMPLETE" and not all_targets_empty(routes):
        raise SnapshotError("ROUTING_FIDELITY",
                            "COMPLETE course cannot carry non-empty routing targets")
    return {
        "evaluation_id": f"{contract.get('contract_id')}:{snapshot.get('snapshot_id')}",
        "contract_id": contract.get("contract_id"),
        "course_id": contract.get("course_id"),
        "snapshot_id": snapshot.get("snapshot_id"),
        "module_results": modules,
        "module_statuses": {m["module_id"]: m["module_status"] for m in modules},
        "course_status": status,
        "hard_sequence_integrity": integrity,
        "track_completion_applicability": contract.get("track_completion_applicability"),
        "track_results": [],
        "retry_targets": routes["retry_targets"],
        "remediation_targets": routes["remediation_targets"],
        "blocked_targets": routes["blocked_targets"],
        "blocked_by_mastery_units": routes["blocked_by_mastery_units"],
        "derived": {
            "module_count": len(modules),
            "complete_module_count": sum(1 for m in modules if m["module_status"] == "COMPLETE"),
            "lesson_count": len(per_lesson_decision),
            "pass_lesson_count": sum(1 for d in per_lesson_decision.values() if d == "PASS"),
            "retry_lesson_count": sum(1 for d in per_lesson_decision.values() if d == "RETRY"),
            "remediation_lesson_count": sum(1 for d in per_lesson_decision.values()
                                            if d == "REMEDIATION"),
            "blocked_lesson_count": sum(1 for d in per_lesson_decision.values() if d == "BLOCKED"),
            "retry_target_count": len(routes["retry_targets"]),
            "remediation_target_count": len(routes["remediation_targets"]),
            "blocked_target_count": len(routes["blocked_targets"]),
            "blocked_by_mastery_unit_count": len(routes["blocked_by_mastery_units"]),
            "hard_sequence_violation_count": integrity["violation_count"],
            "student_state_field_count": 0,
            "numeric_grade_field_count": 0,
            "synthetic_track_entity_count": 0,
        },
    }


def build_structure(contract, mastery_path, manifest_path, graph_paths):
    manifest = load_json_or_fail(manifest_path)
    mastery = load_json_or_fail(mastery_path)
    root = Path(manifest_path).resolve().parent
    lessons = {}
    for entry in manifest["lesson_files"]:
        lessons[entry["lesson_id"]] = load_json_or_fail((root / entry["json_path"]).resolve())
    graphs = [load_json_or_fail(p) for p in graph_paths]
    return CourseStructure(manifest, lessons, mastery, graphs)


def canonical_snapshot(contract, manifest_path):
    """The canonical all-PASS demonstration snapshot for this contract.

    It is ephemeral: it carries no learner identity and no history, and it exists so the
    canonical contract can be validated end to end against a real, decidable input.  Its
    Lesson order comes from the frozen course manifest.
    """
    manifest = load_json_or_fail(manifest_path)
    order = [lid for module in manifest["module_order"]
             for lid in manifest["lesson_order_by_module"][module]]
    return {
        "snapshot_id": "canonical-all-pass",
        "contract_id": contract.get("contract_id"),
        "course_id": contract.get("course_id"),
        "ephemeral": True,
        "note": "Canonical demonstration snapshot: every canonical Lesson mastery unit declared "
                "PASS against the production mastery decision contract. It is not a learner "
                "record, not a grade and not stored progress.",
        "lessons": [{"lesson_id": lid, "decision": "PASS"} for lid in order],
    }


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    emit_json = "--json" in args
    use_stdin = "--stdin" in args
    emit_canonical = "--canonical-for-contract" in args
    args = [a for a in args if not a.startswith("--")]
    if emit_canonical:
        if not args:
            print("FAIL")
            print("- STRUCTURAL: --canonical-for-contract needs <contract.json> <course-manifest>")
            return 2
        contract = load_json_or_fail(args[0])
        manifest_path = args[1] if len(args) > 1 else args[0]
        print(json.dumps(canonical_snapshot(contract, manifest_path), ensure_ascii=False,
                         indent=2))
        return 0
    if len(args) < 4:
        print("FAIL")
        print("- STRUCTURAL: usage: evaluate_course_completion.py <contract.json> "
              "[<snapshot.json>|-] <mastery-map.json> <course-manifest.json> "
              "[graph.json ...] [--json] [--stdin]")
        return 2
    contract_path, snapshot_path, mastery_path, manifest_path = args[:4]
    graph_paths = args[4:]
    try:
        contract = load_json_or_fail(contract_path)
        if use_stdin:
            snapshot = json.loads(sys.stdin.read())
        else:
            snapshot = load_json_or_fail(snapshot_path)
        structure = build_structure(contract, mastery_path, manifest_path, graph_paths)
        result = evaluate(contract, snapshot, structure)
    except SnapshotError as exc:
        print("FAIL")
        print(f"- {exc.code}: {exc.message}")
        return 1
    except ValueError as exc:
        print("FAIL")
        print(f"- STRUCTURAL: unable to read the snapshot: {exc}")
        return 1
    if result["course_status"] == INCONSISTENT:
        print("FAIL")
        print(f"- {INCONSISTENT}: hard sequence integrity violated by the evaluation snapshot")
        for v in result["hard_sequence_integrity"]["violations"]:
            print(f"- {'INCONSISTENT_EVALUATION_SNAPSHOT'}: {v['lesson_id']} is declared PASS "
                  f"while its hard prerequisite {v['hard_prerequisite_lesson_id']} is "
                  f"{v['hard_prerequisite_decision']}")
        if emit_json:
            print(json.dumps({"evaluation": result}, ensure_ascii=False, indent=1,
                             sort_keys=False))
        return 1
    print("PASS")
    print(f"- COURSE_EVALUATION: {result['course_status']}")
    print(f"- module_statuses: {json.dumps(result['module_statuses'], ensure_ascii=False)}")
    print(f"- COURSE_STATUS: {result['course_status']}")
    print(f"- RETRY_TARGETS: {json.dumps(result['retry_targets'], ensure_ascii=False)}")
    print(f"- REMEDIATION_TARGETS: {json.dumps(result['remediation_targets'], ensure_ascii=False)}")
    print(f"- BLOCKED_TARGETS: {json.dumps(result['blocked_targets'], ensure_ascii=False)}")
    print(f"- BLOCKED_BY_MASTERY_UNITS: "
          f"{json.dumps(result['blocked_by_mastery_units'], ensure_ascii=False)}")
    print(f"- HARD_SEQUENCE_INTEGRITY: "
          f"{json.dumps(result['hard_sequence_integrity'], ensure_ascii=False)}")
    print(f"- DERIVED: {json.dumps(result['derived'], ensure_ascii=False)}")
    if emit_json:
        print(json.dumps({"evaluation": result}, ensure_ascii=False, indent=1, sort_keys=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
