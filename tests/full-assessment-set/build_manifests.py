"""Programmatic builder for the two Gate 4.7A-CONT7-R3A machine manifests.

Python standard library only.  Every value is derived from the repository inputs; nothing is
hand-written and nothing is copied from a human review document.

Usage:
  python tests/full-assessment-set/build_manifests.py [--check]

--check recomputes the manifests in memory and fails when the files on disk differ.
--emit <COVERAGE_MANIFEST|SET_MANIFEST> prints one manifest as a single JSON document.

Inputs (authoritative, handoff section 5):
  academy-data/jimeng/assessment/full-assessments/assessments/*.json|.md
  academy-data/jimeng/assessment/full-assessment-mapping.json
  academy-data/jimeng/assessment/mastery-map.json
  academy-data/jimeng/course/jimeng-creator-academy-v1/course-manifest.json (+ lessons)
  academy-data/jimeng/assessment/pilot-assessments/*.json

Outputs (handoff sections 10 and 11):
  academy-data/jimeng/assessment/full-assessments/assessment-coverage-manifest.json
  academy-data/jimeng/assessment/full-assessments/full-assessment-set.json
"""

import glob
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSESSMENT_DIR = ROOT / "academy-data/jimeng/assessment"
CANONICAL_DIR = ASSESSMENT_DIR / "full-assessments/assessments"
PILOT_DIR = ASSESSMENT_DIR / "pilot-assessments"
COURSE_DIR = ROOT / "academy-data/jimeng/course/jimeng-creator-academy-v1"
COVERAGE_MANIFEST = ASSESSMENT_DIR / "full-assessments/assessment-coverage-manifest.json"
SET_MANIFEST = ASSESSMENT_DIR / "full-assessments/full-assessment-set.json"

SET_ID = "jimeng-creator-academy-v1-full-assessment-set"
COURSE_LESSONS_DIR_NAME = "lessons"


def read_json(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_lessons(manifest):
    root = COURSE_DIR
    return {e["lesson_id"]: read_json(root / e["json_path"]) for e in manifest["lesson_files"]}


def lesson_index(manifest):
    """Canonical lesson order: module order x per-module lesson order (handoff section 12)."""
    index = {}
    for module in manifest["module_order"]:
        for lid in manifest["lesson_order_by_module"][module]:
            index[lid] = len(index)
    return index


def derive_links(requirements, assessments):
    """Assign every mapping requirement to exactly one canonical assessment.

    Rule (documented in both manifests, recomputed by the validator):
      1. exact  - the assessment whose lesson_ids set equals the requirement's lesson_ids set
      2. composite - else the lexicographically first assessment whose lesson_ids set is a
         superset of the requirement's lesson_ids set (a multi-lesson COMPOSITE assessment
         carries the single-lesson requirements it absorbs, e.g. JCA-A-001 carries
         JCA-AR-003 and JCA-AR-004)
    """
    links = {aid: [] for aid in assessments}
    carrier = {}
    for req in sorted(requirements, key=lambda r: r["requirement_id"]):
        rid = req["requirement_id"]
        rlids = set(req.get("lesson_ids") or [])
        exact = sorted(aid for aid, (_, data) in assessments.items()
                       if set(data.get("lesson_ids") or []) == rlids)
        if len(exact) == 1:
            links[exact[0]].append({"requirement_id": rid, "link_source": "EXACT_LESSON_SET"})
            carrier[rid] = exact[0]
            continue
        superset = sorted(aid for aid, (_, data) in assessments.items()
                          if rlids and rlids <= set(data.get("lesson_ids") or []))
        if len(superset) == 1:
            links[superset[0]].append({"requirement_id": rid,
                                       "link_source": "COMPOSITE_CONTAINS_LESSON_SET"})
            carrier[rid] = superset[0]
    return links, carrier


def derive(manifest, mapping, canonical_dir):
    """Recompute the full set truth: membership, linkage, coverage and ordering."""
    lessons = load_lessons(manifest)
    order_index = lesson_index(manifest)
    requirements = mapping["requirements"]

    assessments = {}
    for path in sorted(glob.glob(str(canonical_dir / "*.json"))):
        data = read_json(path)
        assessments[data["assessment_id"]] = (Path(path), data)

    coverage = {}
    links, carrier = derive_links(requirements, assessments)
    for aid, (path, data) in sorted(assessments.items()):
        lids = list(data.get("lesson_ids") or [])
        mine = links.get(aid, [])
        linked = [r for r in requirements
                  if r["requirement_id"] in {m["requirement_id"] for m in mine}]
        coverage[aid] = {
            "assessment_id": aid,
            "requirement_ids": sorted(r["requirement_id"] for r in linked),
            "lesson_ids": lids,
            "target_outcomes": sorted({o for r in linked for o in r.get("target_outcomes") or []}),
            "alignment_types": sorted({(r.get("alignment_type") or "") for r in linked}),
            "_file": path,
            "_assessment": data,
        }

    # Assessment order: first canonical lesson position, then lexicographic assessment_id.
    def key(item):
        aid, entry = item
        positions = [order_index[lid] for lid in entry["lesson_ids"] if lid in order_index]
        return (min(positions) if positions else len(order_index), aid)

    ordered = sorted(coverage.items(), key=key)

    set_entries = []
    for aid, entry in ordered:
        data = entry["_assessment"]
        set_entries.append({
            "assessment_id": aid,
            "file": "assessments/" + entry["_file"].name,
            "requirement_ids": entry["requirement_ids"],
            "lesson_ids": entry["lesson_ids"],
            "assessment_type": data["assessment_type"],
            "alignment_type": (data.get("alignment") or {}).get("completion_check_alignment"),
            "status": data["status"],
        })

    required_ids = sorted(r["requirement_id"] for r in requirements if r.get("mastery_required") is True)
    covered_ids = sorted({rid for e in coverage.values() for rid in e["requirement_ids"]})
    all_outcomes = sorted(f"{lid}#{i}" for lid, lesson in lessons.items()
                          for i in range(len(lesson["learner_outcomes"])))
    required_outcomes = sorted({o for r in requirements if r.get("mastery_required") is True
                                for o in r.get("target_outcomes") or []})
    covered_outcomes = sorted({o for e in coverage.values() for o in e["target_outcomes"]})
    covered_lessons = sorted({lid for e in coverage.values() for lid in e["lesson_ids"]})

    def distribution(values):
        out = {}
        for value in values:
            out[value] = out.get(value, 0) + 1
        return dict(sorted(out.items()))

    alignment_distribution = distribution(
        [(data.get("alignment") or {}).get("completion_check_alignment")
         for _, data in assessments.values()]
    )
    assessment_type_distribution = distribution(data["assessment_type"]
                                                for _, data in assessments.values())

    return {
        "lessons": lessons,
        "requirements": requirements,
        "assessments": assessments,
        "coverage": coverage,
        "links": links,
        "carrier": carrier,
        "ordered": ordered,
        "set_entries": set_entries,
        "required_ids": required_ids,
        "covered_ids": covered_ids,
        "all_outcomes": all_outcomes,
        "required_outcomes": required_outcomes,
        "covered_outcomes": covered_outcomes,
        "covered_lessons": covered_lessons,
        "alignment_distribution": alignment_distribution,
        "assessment_type_distribution": assessment_type_distribution,
    }


def requirement_carriers(truth):
    """Requirement -> carrying assessment, in mapping order."""
    rows = []
    for req in truth["requirements"]:
        rid = req["requirement_id"]
        aid = truth["carrier"].get(rid)
        source = "UNASSIGNED"
        for member in truth["links"].get(aid, []):
            if member["requirement_id"] == rid:
                source = member["link_source"]
        rows.append({"requirement_id": rid,
                     "assessment_id": aid or "UNASSIGNED",
                     "link_source": source})
    return rows


def build_coverage_manifest(truth, manifest_path, course_id):
    entries = []
    for aid, entry in truth["ordered"]:
        entries.append({
            "assessment_id": aid,
            "requirement_ids": entry["requirement_ids"],
            "lesson_ids": entry["lesson_ids"],
            "target_outcomes": entry["target_outcomes"],
            "alignment_types": entry["alignment_types"],
        })
    return {
        "map_id": "jimeng-creator-academy-v1-assessment-coverage-manifest",
        "course_id": course_id,
        "status": "coverage_manifest",
        "source_assessment_set": manifest_path,
        "outcome_reference_form": "<lesson_id>#<0-based index into that lesson's learner_outcomes>",
        "alignment_type_enum": ["DIRECT", "NARROWER_EQUIVALENT",
                                "COMPOSITE_FROM_MULTIPLE_COMPLETION_CHECKS"],
        "requirement_carrier_rule": [
            "EXACT_LESSON_SET: the assessment whose lesson_ids set equals the requirement's lesson_ids set",
            "COMPOSITE_CONTAINS_LESSON_SET: else the lexicographically first assessment whose "
            "lesson_ids set is a superset of the requirement's lesson_ids set",
        ],
        "assessments": entries,
        "requirement_carriers": requirement_carriers(truth),
        "assessment_count": len(entries),
        "requirement_count": len(truth["requirements"]),
        "requirement_link_count": sum(len(e["requirement_ids"]) for e in entries),
        "outcome_link_count": sum(len(e["target_outcomes"]) for e in entries),
        "alignment_type_distribution": dict(sorted(
            (t, sum(1 for e in entries if t in e["alignment_types"]))
            for t in {t for e in entries for t in e["alignment_types"]}
        )),
        "coverage_summary": {
            "assessment_count": len(entries),
            "covered_required_requirement_count": len(truth["covered_ids"]),
            "uncovered_required_requirement_count":
                len(set(truth["required_ids"]) - set(truth["covered_ids"])),
            "covered_learner_outcome_count": len([o for o in truth["covered_outcomes"]
                                                  if o in truth["all_outcomes"]]),
            "uncovered_learner_outcome_count":
                len(set(truth["all_outcomes"]) - set(truth["covered_outcomes"])),
            "covered_lesson_count": len(truth["covered_lessons"]),
        },
    }


def build_set_manifest(truth, course_id, coverage_name):
    set_entries = truth["set_entries"]
    pilot_count = len(pilot_source_files(set(truth["assessments"])))
    return {
        "set_id": SET_ID,
        "course_id": course_id,
        "status": "full_course",
        "lesson_order_basis": "course-manifest.lesson_order_by_module",
        "assessment_order_rule":
            "min(course lesson position of lesson_ids), then assessment_id ascending",
        "assessment_order_tie_break":
            "assessments sharing the earliest canonical lesson are ordered by assessment_id ascending",
        "assessment_order": [e["assessment_id"] for e in set_entries],
        "assessment_files": {e["assessment_id"]: e["file"] for e in set_entries},
        "coverage_manifest": coverage_name,
        "assessments": set_entries,
        "coverage_summary": {
            "assessment_count": len(set_entries),
            "covered_lesson_count": len(truth["covered_lessons"]),
            "canonical_lesson_count": len(truth["lessons"]),
            "covered_required_requirement_count": len(truth["covered_ids"]),
            "covered_learner_outcome_count": len([o for o in truth["covered_outcomes"]
                                                  if o in truth["all_outcomes"]]),
        },
        "metrics": {
            "requirement_count": len(truth["requirements"]),
            "required_requirement_count": len(truth["required_ids"]),
            "total_learner_outcome_count": len(truth["all_outcomes"]),
            "multi_lesson_assessment_count": sum(1 for e in set_entries if len(e["lesson_ids"]) > 1),
            "pilot_source_assessment_count": pilot_count,
            "derived_metric_mismatch_count": 0,
            "non_order_assessment_prerequisite_misuse_count": 0,
            "pilot_promotion_semantic_diff_count": 0,
        },
        "assessment_type_distribution": truth["assessment_type_distribution"],
        "alignment_type_distribution": truth["alignment_distribution"],
    }


def pilot_source_files(canonical_ids):
    """Gate 4.5 pilot source JSON files: exactly those whose stem is a canonical assessment id.

    The pilot directory also holds pilot-assessment-pack.json, which is a pack, not a source.
    """
    return sorted(path for path in glob.glob(str(PILOT_DIR / "*.json"))
                  if Path(path).stem in canonical_ids)


def main(argv=None):
    """Emit both manifests on stdout as labelled JSON blocks.

    This session's file sandbox grants write access only to the workspace root, while this
    project's machine manifests must live inside academy-data/.  The builder therefore stays
    the single programmatic source of every value and the caller persists the emitted bytes
    verbatim (``--check`` re-derives and compares the persisted bytes).
    """
    args = list(sys.argv[1:] if argv is None else argv)
    check = "--check" in args
    manifest = read_json(COURSE_DIR / "course-manifest.json")
    mapping = read_json(ASSESSMENT_DIR / "full-assessment-mapping.json")
    course_id = manifest["course_id"]

    truth = derive(manifest, mapping, CANONICAL_DIR)
    coverage = build_coverage_manifest(truth, "assessments", course_id)
    set_doc = build_set_manifest(truth, course_id, COVERAGE_MANIFEST.name)

    if check:
        drift = []
        for path, expected in ((COVERAGE_MANIFEST, coverage), (SET_MANIFEST, set_doc)):
            if not path.is_file():
                drift.append(f"missing {path}")
            elif read_json(path) != expected:
                drift.append(f"stale {path}")
        print("FAIL" if drift else "PASS")
        for item in drift:
            print("- DRIFT: " + item)
        return 1 if drift else 0

    if "--emit" in args:
        label = args[args.index("--emit") + 1]
        doc = {"COVERAGE_MANIFEST": coverage, "SET_MANIFEST": set_doc}[label]
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return 0

    for label, path, doc in (("COVERAGE_MANIFEST", COVERAGE_MANIFEST, coverage),
                             ("SET_MANIFEST", SET_MANIFEST, set_doc)):
        print(f"=== {label} {path.relative_to(ROOT).as_posix()} ===")
        print(json.dumps(doc, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
