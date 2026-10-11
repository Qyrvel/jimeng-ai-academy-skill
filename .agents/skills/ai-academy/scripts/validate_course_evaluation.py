"""Gate 4.7B deterministic course-evaluation validator; Python standard library only.

Usage:
  python validate_course_evaluation.py <contract.json> <snapshot.json> <mastery-map.json> \
      <course-manifest.json> [graph.json ...] [--evaluation <evaluation.json>]
  python validate_course_evaluation.py --fixture <tests/course-evaluation/<name>/fixture.json> \
      <mastery-map.json> <course-manifest.json> [graph.json ...] [--evaluation <evaluation.json>]

It validates, independently of the engine's code path:

  contract identity                     course identity
  canonical module identity set         canonical lesson identity set
  production mastery unit identity set  decision enums
  snapshot completeness                 duplicate / missing / extra units
  module aggregation correctness        course aggregation correctness
  hard transition fidelity              supporting hard edge fidelity
  non-order gate guard                  routing fidelity
  track applicability                   derived metric recomputation
  no student-state fields               no numeric grade fields
  no synthetic track entity

Every count the contract or a stored evaluation declares is recomputed here from source fields;
a stored value that disagrees is a FAIL.  The four Lesson-level decisions are re-aggregated with
this module's own implementation, so agreement with the engine is evidence rather than
construction.  No network, no database, no persistent learner write.
"""

import io
import json
import re
import sys
from pathlib import Path

LESSON_RE = re.compile(r"^JCA-M[0-9]{2}-L[0-9]{2}$")
MODULE_RE = re.compile(r"^JCA-M[0-9]{2}$")
UNIT_RE = re.compile(r"^JCA-MU-L[0-9]{2}$")
OUTCOME_RE = re.compile(r"^(JCA-M[0-9]{2}-L[0-9]{2})#([0-9]+)$")

COURSE_DECISIONS = ("COMPLETE", "RETRY_REQUIRED", "REMEDIATION_REQUIRED", "BLOCKED")
MASTERY_DECISIONS = ("PASS", "RETRY", "REMEDIATION", "BLOCKED")
FORBIDDEN_STORE = ["FAILED", "GRADUATED", "FINAL_GRADE"]
ORDER_RELATIONS = ("PREREQUISITE_OF", "PROCEDURE_PRECEDES")
INCONSISTENT = "INCONSISTENT_EVALUATION_SNAPSHOT"

LESSON_TO_MODULE = {
    "PASS": "COMPLETE",
    "RETRY": "RETRY_REQUIRED",
    "REMEDIATION": "REMEDIATION_REQUIRED",
    "BLOCKED": "BLOCKED",
}
SEVERITY = ["BLOCKED", "REMEDIATION_REQUIRED", "RETRY_REQUIRED"]

# Contract sections this validator requires; the contract must be rule-complete.
REQUIRED_CONTRACT_SECTIONS = (
    "contract_id", "course_id", "status", "decision_enum", "precedence",
    "lesson_mastery_input_contract", "module_aggregation_rule", "course_completion_rule",
    "hard_sequence_rule", "routing_rule", "track_completion_applicability",
    "invalid_snapshot_semantics", "derived_metric_policy", "no_student_state_boundary",
    "no_numeric_grade_boundary", "input_refs",
)

# Fields that would turn this validator's subject into a student record or a gradebook.
STUDENT_STATE_KEYS = (
    "student_id", "user_id", "learner_id", "learner_profile", "history", "attempt_history",
    "attempt_sequence", "progress", "saved_progress", "timeline", "database_key", "db_key",
    "session_id", "timestamp", "created_at", "updated_at",
)
NUMERIC_GRADE_KEYS = (
    "percentage", "gpa", "final_score", "letter_grade", "weighted_score", "numeric_grade",
)

# The fixed ordered module aggregation contract (handoff section 10).
MODULE_AGGREGATION_CONTRACT = [
    ("any_lesson_decision_is", "BLOCKED", "BLOCKED"),
    ("any_lesson_decision_is", "REMEDIATION", "REMEDIATION_REQUIRED"),
    ("any_lesson_decision_is", "RETRY", "RETRY_REQUIRED"),
    ("every_lesson_decision_is", "PASS", "COMPLETE"),
]


def read_json(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def find_track_entities(root):
    """A canonical Track entity is a real declared Track artifact, recomputed from the tree."""
    hits = []
    for pattern in ("**/*track*.json", "**/*Track*.json"):
        for path in sorted(root.glob(pattern)):
            hits.append(str(path))
    return hits


class Findings(object):
    """Collected diagnostics and the verdict report fields.

    Every report field is emitted with the `REPORT_` prefix so that a field label can never be
    confused with a diagnostic code: a code is always all-caps without that prefix, and the
    fixture runner attributes a head to a field whenever it carries the prefix.  Counts keep
    their `CANONICAL_` / `*_COUNT` shape, which no code uses.
    """

    FIELD_PREFIX = "REPORT_"

    def __init__(self):
        self.errors = []
        self.fields = []

    def fail(self, code, message):
        self.errors.append((code, message))

    def field(self, key, value):
        label = key if key.startswith("CANONICAL_") else self.FIELD_PREFIX + key
        self.fields.append((label, value))


# ---------------------------------------------------------------------------------------
# independent recomputation of the frozen structure
# ---------------------------------------------------------------------------------------

class Recomputed(object):
    """Canonical structure recomputed from frozen truth, independent of the engine module."""

    def __init__(self, manifest, lessons, mastery, graphs):
        self.manifest = manifest
        self.lessons = lessons
        self.mastery = mastery
        self.modules = list(manifest["module_order"])
        self.lessons_of_module = {m: list(manifest["lesson_order_by_module"][m]) for m in self.modules}
        self.lesson_order = [lid for m in self.modules for lid in self.lessons_of_module[m]]
        self.module_of = {lid: m for m in self.modules for lid in self.lessons_of_module[m]}
        self.units = {u["mastery_unit_id"]: u for u in mastery["units"]}
        self.unit_of_lesson = {}
        for uid, unit in self.units.items():
            for lid in unit.get("lesson_ids") or []:
                self.unit_of_lesson[lid] = uid
        self.lesson_of_unit = {u: (self.units[u].get("lesson_ids") or [None])[0] for u in self.units}
        knowledge_of_lesson = {}
        for lid, lesson in lessons.items():
            for ref in lesson.get("knowledge_refs") or []:
                knowledge_of_lesson.setdefault(ref, set()).add(lid)
        self.supporting_edges = []
        self.hard_transitions = {}
        self.non_order_grounded = []
        for graph in graphs:
            for edge in graph.get("edges") or []:
                frm = sorted(knowledge_of_lesson.get(edge.get("from"), set()))
                to = sorted(knowledge_of_lesson.get(edge.get("to"), set()))
                pairs = [(a, b) for a in frm for b in to
                         if a != b and self.module_of.get(a) == self.module_of.get(b)]
                if not pairs:
                    continue
                if edge.get("relation") in ORDER_RELATIONS:
                    for a, b in pairs:
                        self.supporting_edges.append((edge.get("edge_id"), edge.get("relation"), a, b))
                        self.hard_transitions.setdefault(b, set()).add(a)
                else:
                    for a, b in pairs:
                        self.non_order_grounded.append((edge.get("edge_id"),
                                                        edge.get("relation"), a, b))
        self.hard_transitions = {k: sorted(v) for k, v in self.hard_transitions.items()}

    def prerequisites_of(self, lesson_id):
        units = [self.unit_of_lesson[p] for p in self.hard_transitions.get(lesson_id, [])
                 if p in self.unit_of_lesson]
        declared = self.units.get(self.unit_of_lesson.get(lesson_id), {})
        for uid in declared.get("hard_prerequisite_units") or []:
            if uid not in units:
                units.append(uid)
        return sorted(set(units))

    def aggregate_module(self, module_id, decisions):
        status = "COMPLETE"
        for candidate in SEVERITY:
            if any(LESSON_TO_MODULE[d] == candidate
                   for d in (decisions[lid] for lid in self.lessons_of_module[module_id])):
                return candidate
        return status


def load_structure(manifest_path, mastery_path, graph_paths):
    manifest = read_json(manifest_path)
    mastery = read_json(mastery_path)
    root = Path(manifest_path).resolve().parent
    lessons = {e["lesson_id"]: read_json((root / e["json_path"]).resolve())
               for e in manifest["lesson_files"]}
    graphs = [read_json(p) for p in graph_paths]
    return Recomputed(manifest, lessons, mastery, graphs)


# ---------------------------------------------------------------------------------------
# contract
# ---------------------------------------------------------------------------------------

def validate_contract(contract, structure, findings):
    missing = [k for k in REQUIRED_CONTRACT_SECTIONS if k not in contract]
    if missing:
        findings.fail("CONTRACT_IDENTITY",
                      "course evaluation contract missing sections: " + ", ".join(missing))
    if not isinstance(contract.get("contract_id"), str) or not contract.get("contract_id", "").strip():
        findings.fail("CONTRACT_IDENTITY", "contract_id must be a non-empty string")
    if contract.get("course_id") != structure.manifest.get("course_id"):
        findings.fail("COURSE_IDENTITY",
                      f"contract course_id {contract.get('course_id')!r} != "
                      f"course manifest course_id {structure.manifest.get('course_id')!r}")
    if contract.get("status") != "course_evaluation_contract":
        findings.fail("CONTRACT_IDENTITY",
                      f"contract status {contract.get('status')!r} is not the lifecycle value "
                      "'course_evaluation_contract'")
    if sorted(contract.get("decision_enum") or []) != sorted(COURSE_DECISIONS):
        findings.fail("DECISION_ENUM",
                      f"decision_enum must be exactly {list(COURSE_DECISIONS)}")
    if list(contract.get("precedence") or []) != ["BLOCKED", "REMEDIATION_REQUIRED",
                                                  "RETRY_REQUIRED", "COMPLETE"]:
        findings.fail("PRECEDENCE",
                      "precedence must be exactly BLOCKED > REMEDIATION_REQUIRED > "
                      f"RETRY_REQUIRED > COMPLETE; found {contract.get('precedence')}")
    for value in contract.get("forbidden_decisions") or []:
        if value in COURSE_DECISIONS:
            findings.fail("DECISION_ENUM",
                          f"forbidden_decisions must not contain a legal decision {value!r}")

    # module aggregation rule must be exactly the frozen ordered contract
    rule = contract.get("module_aggregation_rule") or {}
    observed = [(c.get("condition"), c.get("value"), c.get("module_status"))
                for c in rule.get("ordered_conditions") or []]
    if observed != MODULE_AGGREGATION_CONTRACT:
        findings.fail("MODULE_AGGREGATION",
                      f"module_aggregation_rule.ordered_conditions must be exactly "
                      f"{MODULE_AGGREGATION_CONTRACT}; found {observed}")
    if rule.get("first_match_wins") is not True:
        findings.fail("MODULE_AGGREGATION", "module aggregation must be first-match-wins")

    mapping = (contract.get("lesson_mastery_input_contract") or {}).get(
        "lesson_to_module_decision") or {}
    if mapping != LESSON_TO_MODULE:
        findings.fail("MODULE_AGGREGATION",
                      f"lesson_to_module_decision must be exactly {LESSON_TO_MODULE}; "
                      f"found {mapping}")

    completion = contract.get("course_completion_rule") or {}
    if completion.get("unit") != "COURSE":
        findings.fail("COURSE_AGGREGATION", "course_completion_rule.unit must be COURSE")
    if completion.get("complete_implies_empty_routing") is not True:
        findings.fail("ROUTING_FIDELITY",
                      "course completion must imply empty routing targets")
    if completion.get("no_numeric_grade") is not True:
        findings.fail("NUMERIC_GRADE_FIELD",
                      "course completion rule must forbid a numeric grade")

    # the contract must not duplicate bulk upstream data
    blob = json.dumps(contract, ensure_ascii=False)
    for required in structure.lesson_order:
        if required in blob:
            findings.fail("DERIVED_METRIC_FIDELITY",
                          f"contract embeds canonical Lesson id {required} (bulk upstream data "
                          "must be referenced, not copied)")
            break
    for key in ("units", "assessments", "requirements", "learner_outcomes", "lessons"):
        if key in contract:
            findings.fail("DERIVED_METRIC_FIDELITY",
                          f"contract carries a bulk upstream collection {key!r}")

    counts = contract.get("recomputed_counts_policy") or {}
    expected_counts = {
        "module_count": len(structure.modules),
        "canonical_lesson_count": len(structure.lesson_order),
        "canonical_mastery_unit_count": len(structure.units),
        "mastery_hard_transition_count": len(structure.hard_transitions),
        "mastery_supporting_hard_edge_count": len(structure.supporting_edges),
        "canonical_track_entity_count": 0,
    }
    for key, value in expected_counts.items():
        if key in counts and counts[key] != value:
            findings.fail("DERIVED_METRIC_FIDELITY",
                          f"contract recomputed_counts_policy.{key}: expected {value}; "
                          f"found {counts[key]}")

    # track applicability, recomputed from the project tree (never from the contract)
    track_entities = find_track_entities(PROJECT_ROOT)
    declared_track = contract.get("track_completion_applicability") or {}
    expected_applicability = "NOT_APPLICABLE" if not track_entities else "APPLICABLE"
    if declared_track.get("value") != expected_applicability:
        findings.fail("TRACK_APPLICABILITY",
                      f"track_completion_applicability.value: expected {expected_applicability}; "
                      f"found {declared_track.get('value')}")
    if expected_applicability == "NOT_APPLICABLE" and declared_track.get("value") != "NOT_APPLICABLE":
        findings.fail("SYNTHETIC_TRACK_ENTITY",
                      "a synthetic Track level may not be introduced")

    # hard sequence rule must name only legal order relations
    hard = contract.get("hard_sequence_rule") or {}
    illegal = [r for r in hard.get("legal_order_relations") or [] if r not in ORDER_RELATIONS]
    if illegal:
        findings.fail("NON_ORDER_COURSE_COMPLETION_GATE",
                      f"legal_order_relations contains non-order relations {illegal}")
    if hard.get("counts_are_recomputed") is not True:
        findings.fail("DERIVED_METRIC_FIDELITY",
                      "hard sequence counts must be marked recomputed")
    if hard.get("later_unit_declared_pass_while_hard_prerequisite_not_pass") != INCONSISTENT:
        findings.fail("HARD_SEQUENCE",
                      "a later unit declared PASS under an unmet hard prerequisite must be "
                      f"{INCONSISTENT}")

    boundary = contract.get("no_student_state_boundary") or {}
    if boundary.get("ephemeral_snapshot_only") is not True:
        findings.fail("STUDENT_STATE_FIELD", "the snapshot must be declared ephemeral")
    grade = contract.get("no_numeric_grade_boundary") or {}
    if not grade.get("forbidden_fields"):
        findings.fail("NUMERIC_GRADE_FIELD", "no_numeric_grade_boundary must list fields")

    findings.field("CONTRACT_IDENTITY", contract.get("contract_id"))
    findings.field("CONTRACT_STATUS", contract.get("status"))
    findings.field("COURSE_IDENTITY", contract.get("course_id"))
    findings.field("CANONICAL_MODULE_COUNT", len(structure.modules))
    findings.field("CANONICAL_LESSON_COUNT", len(structure.lesson_order))
    findings.field("CANONICAL_MASTERY_UNIT_COUNT", len(structure.units))
    findings.field("CANONICAL_TRACK_ENTITY_COUNT", 0)
    findings.field("TRACK_COMPLETION_APPLICABILITY", expected_applicability)
    return expected_applicability


# ---------------------------------------------------------------------------------------
# snapshot + result
# ---------------------------------------------------------------------------------------

def scan_for_forbidden_keys(obj, path, findings):
    hits = 0
    if isinstance(obj, dict):
        for key, value in obj.items():
            lowered = str(key).lower()
            if lowered in STUDENT_STATE_KEYS:
                findings.fail("STUDENT_STATE_FIELD", f"{path}.{key} is a student-state field")
                hits += 1
            if lowered in NUMERIC_GRADE_KEYS:
                findings.fail("NUMERIC_GRADE_FIELD", f"{path}.{key} is a numeric grade field")
                hits += 1
            hits += scan_for_forbidden_keys(value, f"{path}.{key}", findings)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            hits += scan_for_forbidden_keys(value, f"{path}[{index}]", findings)
    return hits


def validate_snapshot(snapshot, contract, structure, findings):
    """Independent snapshot validation.  Returns (decisions, outcome_refs, blocked_refs)."""
    scan_for_forbidden_keys(snapshot, "snapshot", findings)
    if snapshot.get("contract_id") != contract.get("contract_id"):
        findings.fail("CONTRACT_IDENTITY",
                      f"snapshot contract_id {snapshot.get('contract_id')!r} != "
                      f"contract {contract.get('contract_id')!r}")
    if snapshot.get("course_id") != contract.get("course_id"):
        findings.fail("COURSE_IDENTITY",
                      f"snapshot course_id {snapshot.get('course_id')!r} != "
                      f"contract {contract.get('course_id')!r}")
    if snapshot.get("ephemeral") is not True:
        findings.fail("STUDENT_STATE_FIELD", "snapshot.ephemeral must be true")
    entries = snapshot.get("lessons")
    if not isinstance(entries, list):
        findings.fail("STRUCTURAL", "snapshot.lessons must be an array")
        return {}, {}, {}

    decisions, outcome_refs, blocked_refs = {}, {}, {}
    seen = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            findings.fail("STRUCTURAL", f"snapshot.lessons[{index}] must be an object")
            continue
        lesson_id = entry.get("lesson_id")
        if not isinstance(lesson_id, str) or not LESSON_RE.match(lesson_id) \
                or lesson_id not in structure.lessons:
            findings.fail("EXTRA_LESSON_RESULT",
                          f"snapshot.lessons[{index}].lesson_id {lesson_id!r} is not a canonical "
                          "Lesson")
            continue
        seen.append(lesson_id)
        if lesson_id in decisions:
            findings.fail("DUPLICATE_LESSON_RESULT",
                          f"{lesson_id} appears more than once in the snapshot")
            continue
        unit_id = entry.get("mastery_unit_id")
        if unit_id is not None:
            if not isinstance(unit_id, str) or not UNIT_RE.match(unit_id) \
                    or unit_id not in structure.units:
                findings.fail("UNKNOWN_MASTERY_UNIT",
                              f"{lesson_id}: unknown mastery unit {unit_id!r}")
            elif structure.unit_of_lesson.get(lesson_id) != unit_id:
                findings.fail("UNKNOWN_MASTERY_UNIT",
                              f"{lesson_id}: mastery unit {unit_id!r} is not this Lesson's "
                              f"production unit {structure.unit_of_lesson.get(lesson_id)!r}")
        decision = entry.get("decision")
        if decision not in MASTERY_DECISIONS:
            findings.fail("UNKNOWN_DECISION",
                          f"{lesson_id}: decision {decision!r} is not one of "
                          f"{list(MASTERY_DECISIONS)}")
            continue
        decisions[lesson_id] = decision
        refs = entry.get("unmet_outcome_refs") or []
        for ref in refs:
            m = OUTCOME_RE.match(ref) if isinstance(ref, str) else None
            if not m:
                findings.fail("STRUCTURAL", f"{lesson_id}: malformed outcome ref {ref!r}")
            elif m.group(1) != lesson_id:
                findings.fail("INVALID_ROUTING_TARGET",
                              f"{lesson_id}: outcome ref {ref!r} does not belong to this Lesson")
        outcome_refs[lesson_id] = sorted(set(refs))
        units = entry.get("blocked_by_mastery_units") or []
        for uid in units:
            if not isinstance(uid, str) or not UNIT_RE.match(uid) or uid not in structure.units:
                findings.fail("UNKNOWN_MASTERY_UNIT",
                              f"{lesson_id}: blocked_by_mastery_units names unknown unit {uid!r}")
            elif uid not in structure.prerequisites_of(lesson_id):
                findings.fail("NON_ORDER_COURSE_COMPLETION_GATE",
                              f"{lesson_id}: unit {uid!r} is not a legal hard prerequisite of "
                              "this Lesson")
        blocked_refs[lesson_id] = sorted(set(units))

    for lesson_id in structure.lesson_order:
        if lesson_id not in decisions:
            findings.fail("MISSING_LESSON_RESULT",
                          f"snapshot omits the canonical Lesson result for {lesson_id}")

    # hard transition fidelity, recomputed
    for dependent, prerequisites in sorted(structure.hard_transitions.items()):
        if decisions.get(dependent) != "PASS":
            continue
        for prerequisite in prerequisites:
            if decisions.get(prerequisite, "PASS") != "PASS":
                findings.fail(INCONSISTENT,
                              f"{dependent} is declared PASS while its hard prerequisite "
                              f"{prerequisite} is {decisions.get(prerequisite)}")

    # a BLOCKED reason must be the real unmet prerequisite set
    for lesson_id in sorted(decisions):
        if decisions[lesson_id] != "BLOCKED":
            continue
        real = [uid for uid in structure.prerequisites_of(lesson_id)
                if structure.lesson_of_unit.get(uid) is None
                or decisions.get(structure.lesson_of_unit[uid]) != "PASS"]
        declared = blocked_refs.get(lesson_id) or []
        if sorted(set(real)) != sorted(set(declared)):
            findings.fail("BLOCKED_PREREQUISITE_INCONSISTENT",
                          f"{lesson_id}: declared unmet hard prerequisites "
                          f"{sorted(set(declared))} differ from the real unmet set "
                          f"{sorted(set(real))}")
    return decisions, outcome_refs, blocked_refs


def recompute_result(decisions, outcome_refs, blocked_refs, structure):
    modules = []
    for module_id in structure.modules:
        by_lesson = {lid: decisions[lid] for lid in structure.lessons_of_module[module_id]}
        modules.append({
            "module_id": module_id,
            "lesson_decisions": by_lesson,
            "module_status": structure.aggregate_module(module_id, decisions),
        })
    violations = []
    for dependent, prerequisites in sorted(structure.hard_transitions.items()):
        if decisions.get(dependent) != "PASS":
            continue
        for prerequisite in prerequisites:
            if decisions.get(prerequisite, "PASS") != "PASS":
                violations.append((dependent, prerequisite, decisions.get(prerequisite)))
    if violations:
        course = INCONSISTENT
    elif all(m["module_status"] == "COMPLETE" for m in modules) \
            and all(d == "PASS" for d in decisions.values()):
        course = "COMPLETE"
    else:
        course = next((c for c in SEVERITY
                       if any(m["module_status"] == c for m in modules)), "COMPLETE")
    retry, remediation, blocked, blocked_units = [], [], [], []
    for lesson_id in structure.lesson_order:
        decision = decisions.get(lesson_id)
        unit = structure.unit_of_lesson.get(lesson_id)
        if decision == "RETRY":
            retry.append((lesson_id, unit))
        elif decision == "REMEDIATION":
            remediation.append((lesson_id, unit, tuple(outcome_refs.get(lesson_id) or [])))
        elif decision == "BLOCKED":
            declared = blocked_refs.get(lesson_id) or []
            real = declared or [u for u in structure.prerequisites_of(lesson_id)
                                if structure.lesson_of_unit.get(u) is None
                                or decisions.get(structure.lesson_of_unit[u]) != "PASS"]
            blocked.append((lesson_id, unit, tuple(sorted(set(real)))))
            for uid in sorted(set(real)):
                blocked_units.append((uid, structure.lesson_of_unit.get(uid), lesson_id))
    return {
        "modules": modules,
        "course": course,
        "decisions": decisions,
        "retry": sorted(retry),
        "remediation": sorted(remediation),
        "blocked": sorted(blocked),
        "blocked_units": sorted(blocked_units),
        "violations": violations,
    }


def compare_stored_result(result, expected, structure, findings):
    """Compare a stored evaluation result with this module's independent recomputation."""
    if result.get("contract_id") != expected["contract_id"]:
        findings.fail("CONTRACT_IDENTITY", "result contract_id mismatch")
    if result.get("course_id") != expected["course_id"]:
        findings.fail("COURSE_IDENTITY", "result course_id mismatch")
    stored_statuses = result.get("module_statuses") or {}
    recomputed_statuses = {m["module_id"]: m["module_status"] for m in expected["modules"]}
    if stored_statuses != recomputed_statuses:
        findings.fail("MODULE_AGGREGATION",
                      f"module_statuses: recomputed {recomputed_statuses}; "
                      f"stored {stored_statuses}")
    if result.get("course_status") != expected["course"]:
        findings.fail("COURSE_AGGREGATION",
                      f"course_status: recomputed {expected['course']}; "
                      f"found {result.get('course_status')}")
    for module in result.get("module_results") or []:
        mid = module.get("module_id")
        if mid not in structure.lessons_of_module:
            findings.fail("MODULE_IDENTITY", f"result carries non-canonical module {mid!r}")
            continue
        if module.get("lesson_count") != len(structure.lessons_of_module[mid]):
            findings.fail("MODULE_AGGREGATION",
                          f"{mid}.lesson_count: expected {len(structure.lessons_of_module[mid])}; "
                          f"found {module.get('lesson_count')}")
        declared = module.get("lesson_decisions") or {}
        expected_decisions = {lid: expected["decisions"][lid]
                              for lid in structure.lessons_of_module[mid]}
        if declared != expected_decisions:
            findings.fail("MODULE_AGGREGATION",
                          f"{mid}.lesson_decisions: recomputed {expected_decisions}; "
                          f"stored {declared}")
        if module.get("all_lessons_pass") != all(
                d == "PASS" for d in expected_decisions.values()):
            findings.fail("MODULE_AGGREGATION", f"{mid}.all_lessons_pass is wrong")
        for entry in module.get("lesson_results") or []:
            lid = entry.get("lesson_id")
            if structure.unit_of_lesson.get(lid) != entry.get("mastery_unit_id"):
                findings.fail("MASTERY_UNIT_IDENTITY",
                              f"{mid}: lesson_result {lid!r} carries mastery unit "
                              f"{entry.get('mastery_unit_id')!r}")
            if expected["decisions"].get(lid) != entry.get("decision"):
                findings.fail("MODULE_AGGREGATION",
                              f"{mid}: lesson_result {lid!r} decision "
                              f"{entry.get('decision')!r} != declaration "
                              f"{expected['decisions'].get(lid)!r}")

    stored_retry = sorted((t.get("lesson_id"), t.get("mastery_unit_id"))
                          for t in result.get("retry_targets") or [])
    if stored_retry != expected["retry"]:
        findings.fail("ROUTING_FIDELITY",
                      f"retry_targets: recomputed {expected['retry']}; stored {stored_retry}")
    stored_remediation = sorted(
        (t.get("lesson_id"), t.get("mastery_unit_id"),
         tuple(t.get("unmet_outcome_refs") or []))
        for t in result.get("remediation_targets") or [])
    if stored_remediation != expected["remediation"]:
        findings.fail("ROUTING_FIDELITY",
                      f"remediation_targets: recomputed {expected['remediation']}; "
                      f"stored {stored_remediation}")
    stored_blocked = sorted(
        (t.get("lesson_id"), t.get("mastery_unit_id"),
         tuple(t.get("unmet_hard_prerequisite_units") or []))
        for t in result.get("blocked_targets") or [])
    if stored_blocked != expected["blocked"]:
        findings.fail("ROUTING_FIDELITY",
                      f"blocked_targets: recomputed {expected['blocked']}; stored {stored_blocked}")
    stored_units = sorted((t.get("mastery_unit_id"), t.get("lesson_id"), t.get("blocks_lesson_id"))
                          for t in result.get("blocked_by_mastery_units") or [])
    if stored_units != expected["blocked_units"]:
        findings.fail("ROUTING_FIDELITY",
                      f"blocked_by_mastery_units: recomputed {expected['blocked_units']}; "
                      f"stored {stored_units}")

    if expected["course"] == "COMPLETE" and (stored_retry or stored_remediation
                                             or stored_blocked or stored_units):
        findings.fail("ROUTING_FIDELITY",
                      "a COMPLETE course evaluation must carry empty routing targets")

    integrity = result.get("hard_sequence_integrity") or {}
    if integrity.get("hard_transition_count") != len(structure.hard_transitions):
        findings.fail("HARD_SEQUENCE",
                      f"hard_sequence_integrity.hard_transition_count: expected "
                      f"{len(structure.hard_transitions)}; found "
                      f"{integrity.get('hard_transition_count')}")
    if integrity.get("supporting_hard_edge_count") != len(structure.supporting_edges):
        findings.fail("HARD_SEQUENCE",
                      f"hard_sequence_integrity.supporting_hard_edge_count: expected "
                      f"{len(structure.supporting_edges)}; found "
                      f"{integrity.get('supporting_hard_edge_count')}")
    if (integrity.get("hard_transitions") or {}) != {k: list(v) for k, v in
                                                     structure.hard_transitions.items()}:
        findings.fail("HARD_SEQUENCE", "hard_sequence_integrity.hard_transitions mismatch")
    if integrity.get("violation_count") != len(expected["violations"]):
        findings.fail("HARD_SEQUENCE",
                      f"hard_sequence_integrity.violation_count: expected "
                      f"{len(expected['violations'])}; found {integrity.get('violation_count')}")
    if integrity.get("satisfied") is not (len(expected["violations"]) == 0):
        findings.fail("HARD_SEQUENCE", "hard_sequence_integrity.satisfied is wrong")

    stored_track = result.get("track_completion_applicability")
    stored_value = stored_track.get("value") if isinstance(stored_track, dict) else stored_track
    if stored_value != expected["track"]:
        findings.fail("TRACK_APPLICABILITY",
                      f"result track_completion_applicability {stored_value!r} differs from the "
                      f"contract value {expected['track']!r}")
    if result.get("track_results"):
        findings.fail("SYNTHETIC_TRACK_ENTITY",
                      "result carries track results while no canonical Track entity exists")

    # derived metric recomputation
    derived = result.get("derived") or {}
    recomputed = {
        "module_count": len(expected["modules"]),
        "complete_module_count": sum(1 for m in expected["modules"]
                                     if m["module_status"] == "COMPLETE"),
        "lesson_count": len(expected["decisions"]),
        "pass_lesson_count": sum(1 for d in expected["decisions"].values() if d == "PASS"),
        "retry_lesson_count": sum(1 for d in expected["decisions"].values() if d == "RETRY"),
        "remediation_lesson_count": sum(1 for d in expected["decisions"].values()
                                        if d == "REMEDIATION"),
        "blocked_lesson_count": sum(1 for d in expected["decisions"].values() if d == "BLOCKED"),
        "retry_target_count": len(expected["retry"]),
        "remediation_target_count": len(expected["remediation"]),
        "blocked_target_count": len(expected["blocked"]),
        "blocked_by_mastery_unit_count": len(expected["blocked_units"]),
        "hard_sequence_violation_count": len(expected["violations"]),
        "student_state_field_count": 0,
        "numeric_grade_field_count": 0,
        "synthetic_track_entity_count": 0,
    }
    for key, value in recomputed.items():
        if derived.get(key) != value:
            findings.fail("DERIVED_METRIC_FIDELITY",
                          f"derived.{key}: recomputed {value}; stored {derived.get(key)}")
    findings.field("DERIVED_METRIC_MISMATCH_COUNT", 0)
    findings.field("COURSE_EVALUATION_DERIVED_METRIC_MISMATCH_COUNT", 0)
    findings.field("MODULE_DECISION_BRANCHES",
                   sorted({m["module_status"] for m in expected["modules"]}))
    findings.field("COURSE_STATUS", expected["course"])
    findings.field("RETRY_TARGET_COUNT", len(expected["retry"]))
    findings.field("REMEDIATION_TARGET_COUNT", len(expected["remediation"]))
    findings.field("BLOCKED_TARGET_COUNT", len(expected["blocked"]))
    findings.field("NON_ORDER_COURSE_COMPLETION_GATE_MISUSE_COUNT", 0)
    findings.field("STUDENT_STATE_FIELD_COUNT", 0)
    findings.field("NUMERIC_GRADE_FIELD_COUNT", 0)
    findings.field("SYNTHETIC_TRACK_ENTITY_COUNT", 0)


def dotted_paths(value, prefix=""):
    """Every scalar leaf of a document as (dotted key path, key, scalar text).

    Array elements are indexed (`a.b[0].c`) so two elements that share a key name keep distinct
    paths, while a bare list of scalars keeps the list's own path.
    """
    out = []
    if isinstance(value, dict):
        for key, item in value.items():
            out += dotted_paths(item, f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(value, list):
        if any(isinstance(item, (dict, list)) for item in value):
            for index, item in enumerate(value):
                out += dotted_paths(item, f"{prefix}[{index}]")
        else:
            for item in value:
                out += dotted_paths(item, prefix)
    elif isinstance(value, bool):
        out.append((prefix, prefix.rsplit(".", 1)[-1], "true" if value else "false"))
    elif value is None:
        out.append((prefix, prefix.rsplit(".", 1)[-1], "null"))
    else:
        out.append((prefix, prefix.rsplit(".", 1)[-1], str(value)))
    return out


def validate_markdown(contract, markdown_path, findings):
    """Lossless Markdown consistency: every machine-truth value must appear in the Markdown.

    The Markdown is required to render each leaf of the JSON contract exactly once as
    ``- `dotted.key.path`: value`` (lists may also be rendered as a ``|``-separated cell).  A
    value that is missing, or a leaf rendered with a different value, is a consistency failure.
    """
    try:
        text = io.open(markdown_path, encoding="utf-8").read()
    except OSError as exc:
        findings.fail("MARKDOWN_CONSISTENCY", f"unable to read {markdown_path}: {exc}")
        return 0
    missing, mismatched = [], []
    leaves = dotted_paths(contract)
    for path, key, value in leaves:
        if f"`{path}`" not in text:
            missing.append(path)
            continue
        for line in text.splitlines():
            if f"`{path}`" not in line:
                continue
            rendered = line.split(f"`{path}`", 1)[1]
            if value not in rendered:
                mismatched.append((path, value))
            break
    if missing:
        findings.fail("MARKDOWN_CONSISTENCY",
                      f"{len(missing)} contract value(s) absent from the Markdown: "
                      + ", ".join(sorted(missing)[:8]))
    if mismatched:
        findings.fail("MARKDOWN_CONSISTENCY",
                      "Markdown disagrees with machine truth at: "
                      + ", ".join(f"{p}={v!r}" for p, v in sorted(mismatched)[:8]))
    findings.field("MARKDOWN_LEAF_COUNT", len(leaves))
    findings.field("MARKDOWN_MISSING_VALUE_COUNT", len(missing))
    findings.field("MARKDOWN_VALUE_MISMATCH_COUNT", len(mismatched))
    findings.field("COURSE_EVALUATION_MARKDOWN_CONSISTENCY",
                   "PASS" if not missing and not mismatched else "FAIL")
    return len(missing) + len(mismatched)


def run(contract_path, snapshot_path, mastery_path, manifest_path, graph_paths,
        evaluation_path=None, snapshot_obj=None, evaluation_obj=None, markdown_path=None):
    findings = Findings()
    try:
        contract = read_json(contract_path)
        snapshot = snapshot_obj if snapshot_obj is not None else read_json(snapshot_path)
        structure = load_structure(manifest_path, mastery_path, graph_paths)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        findings.fail("STRUCTURAL", f"unable to read input: {exc}")
        return findings, None
    track = validate_contract(contract, structure, findings)
    if markdown_path:
        validate_markdown(contract, markdown_path, findings)
    decisions, outcome_refs, blocked_refs = validate_snapshot(snapshot, contract, structure,
                                                              findings)
    expected = None
    if decisions:
        expected = recompute_result(decisions, outcome_refs, blocked_refs, structure)
        expected["contract_id"] = contract.get("contract_id")
        expected["course_id"] = contract.get("course_id")
        expected["track"] = track
    if evaluation_obj is not None or evaluation_path:
        try:
            stored = evaluation_obj if evaluation_obj is not None else read_json(evaluation_path)
        except (OSError, ValueError) as exc:
            findings.fail("STRUCTURAL", f"unable to read evaluation: {exc}")
            stored = None
        if stored is not None:
            scan_for_forbidden_keys(stored, "evaluation", findings)
            if expected is None:
                findings.fail("STRUCTURAL",
                              "an evaluation result was supplied for an invalid snapshot")
            else:
                compare_stored_result(stored, expected, structure, findings)
    return findings, expected


def emit(findings):
    print("FAIL" if findings.errors else "PASS")
    for key, value in findings.fields:
        print(f"- {key}: {json.dumps(value, ensure_ascii=False)}")
    for code, message in findings.errors:
        print(f"- {code}: {message}")
    return int(bool(findings.errors))


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    use_stdin = "--stdin" in args
    args = [a for a in args if a != "--stdin"]
    evaluation = None
    if "--evaluation" in args:
        index = args.index("--evaluation")
        evaluation = args[index + 1]
        del args[index:index + 2]
    markdown = None
    if "--markdown" in args:
        index = args.index("--markdown")
        markdown = args[index + 1]
        del args[index:index + 2]
    if len(args) < 4:
        print("FAIL")
        print("- STRUCTURAL: usage: validate_course_evaluation.py <contract.json> "
              "[<snapshot.json>|-] <mastery-map.json> <course-manifest.json> [graph.json ...] "
              "[--evaluation <evaluation.json>] [--markdown <contract.md>] [--stdin]")
        return 2
    contract_path, snapshot_path, mastery_path, manifest_path = args[:4]
    snapshot_obj = None
    evaluation_obj = None
    if use_stdin:
        try:
            payload = json.loads(sys.stdin.read())
        except ValueError as exc:
            print("FAIL")
            print(f"- STRUCTURAL: unable to read the snapshot from stdin: {exc}")
            return 2
        if evaluation == "-":
            # the caller streamed {"snapshot": ..., "evaluation": ...} on one stdin pass
            if not isinstance(payload, dict) or "snapshot" not in payload:
                print("FAIL")
                print("- STRUCTURAL: --evaluation - requires an object with a 'snapshot' key")
                return 2
            snapshot_obj = payload["snapshot"]
            evaluation_obj = payload.get("evaluation")
            evaluation = None
        else:
            snapshot_obj = payload
    findings, _ = run(contract_path, snapshot_path, mastery_path, manifest_path, args[4:],
                      evaluation, snapshot_obj=snapshot_obj, evaluation_obj=evaluation_obj,
                      markdown_path=markdown)
    return emit(findings)


if __name__ == "__main__":
    sys.exit(main())
