"""Full assessment requirement mapping validation; Python standard library only.

Usage:
  python validate_assessment_mapping.py <full-assessment-mapping.json> <course-manifest.json> \
      <knowledge-registry.json> [graph.json ...]

Outcome references use the compact form "<lesson_id>#<0-based index>" into that lesson's
learner_outcomes, so that every requirement stays machine-checkable without copying prose.

Checks (gate 4.6 section 18):
  Identity     1 requirement_id unique + format, 2 lesson_ids exist, 3 assessment_type valid
  Outcome      4 target_outcomes non-empty, 5 each reference in range,
               6 every canonical learner outcome covered by >= 1 requirement
  Knowledge    7 knowledge_refs non-empty, 8 knowledge_refs subset of the lessons' knowledge_refs
  Completion   9 completion_check_alignment non-empty, 10 alignment_type valid,
               11 the referenced lesson has a non-empty completion_check
  Scope       12 scope not wider than the referenced lesson scope
  Completeness 13 all canonical lessons mapped, 14 no unknown lesson,
               15 no extra outcome, 16 no extra knowledge
  Derived     17 every declared derived metric is recomputed and compared

It never judges whether a requirement is pedagogically well chosen.
"""

import re
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
read_json = runpy.run_path(str(HERE / "validate_source_registry.py"))["read_json"]

TYPES = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
ASSESSMENT_TYPES = ("IDENTIFY", "CLASSIFY", "EXPLAIN_BOUNDARY", "PERFORM_PROCEDURE",
                    "INSPECT_RESULT", "APPLY_RULE", "INTEGRATED_TASK")
ALIGNMENT_TYPES = ("DIRECT", "NARROWER_EQUIVALENT", "COMPOSITE_FROM_MULTIPLE_COMPLETION_CHECKS")
PAIR_REASONS = ("SEQUENCE_PAIR", "INTEGRATED_SKILL")
EVIDENCE_TYPES = ("SELECTION_OR_IDENTIFICATION", "CLASSIFICATION_RESULT", "BOUNDARY_EXPLANATION",
                  "PROCEDURE_EXECUTION", "RESULT_INSPECTION", "RULE_APPLICATION",
                  "CREATED_ARTIFACT", "INTEGRATED_WORK_PRODUCT")
WIDENING_MARKERS = ("所有客户端", "全部客户端", "永久", "所有账号", "全部账号", "所有版本", "任何客户端", "所有地区")
REF_PATTERN = re.compile(r"^(JCA-M[0-9]{2}-L[0-9]{2})#([0-9]+)$")


def load_course(manifest_path):
    manifest = read_json(str(manifest_path))
    root = Path(manifest_path).resolve().parent
    lessons = {}
    for entry in manifest["lesson_files"]:
        lessons[entry["lesson_id"]] = read_json(str((root / entry["json_path"]).resolve()))
    return manifest, lessons


def parse_ref(ref):
    m = REF_PATTERN.match(ref) if isinstance(ref, str) else None
    return (m.group(1), int(m.group(2))) if m else None


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 3:
        print("FAIL")
        print("- Usage: python validate_assessment_mapping.py <full-assessment-mapping.json> "
              "<course-manifest.json> <knowledge-registry.json> [graph.json ...]")
        return 1
    errors = []
    try:
        data = read_json(args[0])
        manifest, lessons = load_course(Path(args[1]).resolve())
        knowledge = read_json(args[2])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("FAIL")
        print(f"- STRUCTURAL: unable to read input: {exc}")
        return 1

    def fail(message):
        errors.append("CONSISTENCY: " + message)

    if "requirements" not in data or not isinstance(data["requirements"], list):
        print("FAIL")
        print("- STRUCTURAL: root.requirements: missing or not a list")
        return 1
    known_knowledge = {item["knowledge_id"] for item in knowledge["items"]}
    reqs = data["requirements"]
    ids = [r.get("requirement_id") for r in reqs]
    if len(set(ids)) != len(ids):
        fail("requirement_id must be globally unique")
    for rid in ids:
        if not isinstance(rid, str) or not re.match(r"^JCA-AR-[0-9]{3}$", rid):
            fail(f"requirement_id {rid!r} must match JCA-AR-###")

    covered = set()
    for req in reqs:
        rid = req.get("requirement_id")
        lesson_ids = req.get("lesson_ids") or []
        for lid in lesson_ids:
            if lid not in lessons:
                fail(f"{rid}: lesson_id {lid!r} is not a canonical lesson")
        if req.get("assessment_type") not in ASSESSMENT_TYPES:
            fail(f"{rid}: assessment_type {req.get('assessment_type')!r} is not allowed")
        if req.get("expected_evidence_type") not in EVIDENCE_TYPES:
            fail(f"{rid}: expected_evidence_type {req.get('expected_evidence_type')!r} is not allowed")
        refs = req.get("target_outcomes") or []
        if not refs:
            fail(f"{rid}: target_outcomes must not be empty")
        for ref in refs:
            parsed = parse_ref(ref)
            if not parsed:
                fail(f"{rid}: target_outcome {ref!r} must look like <lesson_id>#<index>")
                continue
            lid, idx = parsed
            if lid not in lessons:
                fail(f"{rid}: target_outcome references unknown lesson {lid!r}")
                continue
            if lid not in lesson_ids:
                fail(f"{rid}: target_outcome {ref!r} is outside lesson_ids")
                continue
            if idx >= len(lessons[lid]["learner_outcomes"]):
                fail(f"{rid}: target_outcome {ref!r} is out of range for {lid}")
                continue
            covered.add(ref)
        krefs = req.get("knowledge_refs") or []
        if not krefs:
            fail(f"{rid}: knowledge_refs must not be empty")
        allowed = {k for lid in lesson_ids if lid in lessons for k in lessons[lid]["knowledge_refs"]}
        for k in krefs:
            if k not in allowed:
                fail(f"{rid}: knowledge_ref {k!r} is outside the referenced lessons' knowledge_refs")
            if k not in known_knowledge:
                fail(f"{rid}: knowledge_ref {k!r} does not exist in the registry")
        align = req.get("completion_check_alignment") or {}
        if not align.get("lesson_id") or not align.get("source_field"):
            fail(f"{rid}: completion_check_alignment must name lesson_id and source_field")
        elif align["lesson_id"] not in lessons or not lessons[align["lesson_id"]].get("completion_check"):
            fail(f"{rid}: referenced completion_check does not exist")
        if req.get("alignment_type") not in ALIGNMENT_TYPES:
            fail(f"{rid}: alignment_type {req.get('alignment_type')!r} is not allowed")
        if len(lesson_ids) == 2 and req.get("lesson_pair_reason") not in PAIR_REASONS:
            fail(f"{rid}: two-lesson requirements need lesson_pair_reason SEQUENCE_PAIR or INTEGRATED_SKILL")
        lesson_scope = " ".join(lessons[lid]["scope"] for lid in lesson_ids if lid in lessons)
        for marker in WIDENING_MARKERS:
            if marker in str(req.get("scope", "")) and marker not in lesson_scope:
                fail(f"{rid}: scope appears wider than the lesson scope (marker {marker!r})")

    all_outcomes = {f"{lid}#{i}" for lid, lesson in lessons.items()
                    for i in range(len(lesson["learner_outcomes"]))}
    unmapped = sorted(all_outcomes - covered)
    missing_lessons = sorted({lid for lid in lessons} - {lid for r in reqs for lid in (r.get("lesson_ids") or [])})
    if missing_lessons:
        fail("canonical lessons without an assessment requirement: " + ", ".join(missing_lessons))

    derived = data.get("derived")
    if derived is None:
        fail("derived metrics block is required: every declared metric must be recomputable")
    else:
        expected = {
            "requirement_count": len(reqs),
            "mapped_lesson_count": len({lid for r in reqs for lid in (r.get("lesson_ids") or [])}),
            "unmapped_lesson_count": len(missing_lessons),
            "total_learner_outcome_count": len(all_outcomes),
            "mapped_learner_outcome_count": len(covered & all_outcomes),
            "unmapped_learner_outcome_count": len(unmapped),
            "assessment_type_count": len({r.get("assessment_type") for r in reqs}),
            "alignment_type_count": len({r.get("alignment_type") for r in reqs}),
        }
        for key, value in expected.items():
            if derived.get(key) != value:
                fail(f"derived.{key}: expected {value}; found {derived.get(key)}")
    if unmapped:
        fail("learner outcomes without any requirement: " + ", ".join(unmapped))

    print("FAIL" if errors else "PASS")
    for error in errors:
        print("- " + error)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
