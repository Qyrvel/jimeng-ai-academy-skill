"""Gate 4.7B course-evaluation fixture declarations.

This module is the fixture SPEC, not fixture output.  Each fixture states the smallest honest
deviation from the all-PASS snapshot; the runner materialises the snapshot body from frozen
repository truth, runs the real engine and the real validator, and compares everything with the
declaration.  Nothing here is a stored copy of an observation.

Fixture axes
  positive  : the four course-level branches plus three mixed-state (lossless routing) cases
  negative  : the eight required invalid-snapshot cases plus one extra consistency case

A snapshot is inconsistent when a dependent unit is declared *more advanced* than a hard
prerequisite, so only Lessons that are the dependent end of no hard transition may carry a
non-PASS decision while their hard prerequisite stays PASS.  A fixture that needs such a
dependent non-PASS also declares the prerequisite non-PASS.
"""

CONTRACT_ID = "jimeng-creator-academy-v1-course-evaluation"
COURSE_ID = "jimeng-creator-academy-v1"

# fixture name -> declaration
#   valid           : true when the snapshot is a legal evaluation snapshot
#   declared_codes  : diagnostics the snapshot must hit (empty for a valid snapshot)
#   companion_codes : further declared diagnostics the same invalid snapshot legitimately hits
FIXTURES = {
    "valid-complete-course": {
        "valid": True,
        "declared_codes": [],
        "note": "every canonical Lesson declared PASS -> course COMPLETE with empty routing",
        "less": [],
    },
    "valid-retry-course": {
        "valid": True,
        "declared_codes": [],
        "note": "one execution-layer RETRY -> course RETRY_REQUIRED",
        "less": [{"lesson_id": "JCA-M02-L02", "decision": "RETRY"}],
    },
    "valid-remediation-course": {
        "valid": True,
        "declared_codes": [],
        "note": "one outcome-layer REMEDIATION with real unmet outcome refs -> "
                "course REMEDIATION_REQUIRED",
        "less": [{"lesson_id": "JCA-M01-L02", "decision": "REMEDIATION",
                  "unmet_outcome_refs": ["JCA-M01-L02#1", "JCA-M01-L02#2"]}],
    },
    "valid-blocked-course": {
        "valid": True,
        "declared_codes": [],
        "note": "a genuine graph-derived hard prerequisite is unmet while its dependent Lesson "
                "is declared BLOCKED -> course BLOCKED",
        "less": [
            {"lesson_id": "JCA-M02-L01", "decision": "RETRY"},
            {"lesson_id": "JCA-M02-L02", "decision": "BLOCKED",
             "blocked_by_mastery_units": ["JCA-MU-L03"]},
        ],
    },
    "valid-retry-plus-remediation": {
        "valid": True,
        "declared_codes": [],
        "note": "RETRY + REMEDIATION with no BLOCKED -> overall REMEDIATION_REQUIRED, both "
                "routing sets preserved",
        "less": [
            {"lesson_id": "JCA-M02-L02", "decision": "RETRY"},
            {"lesson_id": "JCA-M06-L01", "decision": "REMEDIATION",
             "unmet_outcome_refs": ["JCA-M06-L01#0"]},
        ],
    },
    "valid-remediation-plus-blocked": {
        "valid": True,
        "declared_codes": [],
        "note": "REMEDIATION + BLOCKED -> overall BLOCKED, both routing sets preserved",
        "less": [
            {"lesson_id": "JCA-M02-L01", "decision": "REMEDIATION",
             "unmet_outcome_refs": ["JCA-M02-L01#1"]},
            {"lesson_id": "JCA-M02-L02", "decision": "BLOCKED",
             "blocked_by_mastery_units": ["JCA-MU-L03"]},
        ],
    },
    "valid-retry-remediation-blocked": {
        "valid": True,
        "declared_codes": [],
        "note": "RETRY + REMEDIATION + BLOCKED -> overall BLOCKED with all three routing sets "
                "preserved (lossless). The RETRY sits on JCA-M05-L03, a Lesson that depends on "
                "nothing and that nothing in the hard sequence depends on, so it stays an "
                "independent RETRY that BLOCKED must not swallow.",
        "less": [
            {"lesson_id": "JCA-M05-L03", "decision": "RETRY"},
            {"lesson_id": "JCA-M02-L01", "decision": "REMEDIATION",
             "unmet_outcome_refs": ["JCA-M02-L01#0"]},
            {"lesson_id": "JCA-M02-L02", "decision": "BLOCKED",
             "blocked_by_mastery_units": ["JCA-MU-L03"]},
            {"lesson_id": "JCA-M06-L02", "decision": "REMEDIATION",
             "unmet_outcome_refs": ["JCA-M06-L02#2"]},
        ],
    },

    # ---- invalid snapshots -----------------------------------------------------------
    "invalid-missing-lesson-result": {
        "valid": False,
        "declared_codes": ["MISSING_LESSON_RESULT"],
        "note": "one canonical Lesson result omitted",
        "less": [],
        "omit": ["JCA-M04-L02"],
    },
    "invalid-duplicate-lesson-result": {
        "valid": False,
        "declared_codes": ["DUPLICATE_LESSON_RESULT"],
        "note": "one Lesson declared twice",
        "less": [],
        "duplicate": ["JCA-M01-L01"],
    },
    "invalid-extra-lesson-result": {
        "valid": False,
        "declared_codes": ["EXTRA_LESSON_RESULT"],
        "note": "a non-canonical Lesson id is declared",
        "less": [],
        "add": [{"lesson_id": "JCA-M09-L01", "decision": "PASS"}],
    },
    "invalid-unknown-mastery-unit": {
        "valid": False,
        "declared_codes": ["UNKNOWN_MASTERY_UNIT"],
        "note": "a Lesson carries a mastery unit that does not exist in production mastery",
        "less": [{"lesson_id": "JCA-M01-L01", "decision": "PASS",
                  "mastery_unit_id": "JCA-MU-L99"}],
    },
    "invalid-unknown-decision": {
        "valid": False,
        "declared_codes": ["UNKNOWN_DECISION"],
        "note": "a decision outside the four-value mastery enum",
        "less": [{"lesson_id": "JCA-M02-L02", "decision": "FAILED"}],
    },
    "invalid-hard-prerequisite-inconsistent-pass": {
        "valid": False,
        "declared_codes": ["INCONSISTENT_EVALUATION_SNAPSHOT"],
        "note": "a dependent unit declared PASS while its hard prerequisite is RETRY",
        "less": [{"lesson_id": "JCA-M02-L01", "decision": "RETRY"}],
    },
    "invalid-nonorder-relation-as-course-gate": {
        "valid": False,
        "declared_codes": ["NON_ORDER_COURSE_COMPLETION_GATE"],
        "companion_codes": ["BLOCKED_PREREQUISITE_INCONSISTENT"],
        "note": "a BLOCKED Lesson claims mastery unit JCA-MU-L23, which no PREREQUISITE_OF / "
                "PROCEDURE_PRECEDES relation justifies as its prerequisite, so its declared "
                "unmet set also differs from the real unmet set",
        "less": [{"lesson_id": "JCA-M01-L01", "decision": "BLOCKED",
                  "blocked_by_mastery_units": ["JCA-MU-L23"]}],
    },
    "invalid-student-state-field": {
        "valid": False,
        "declared_codes": ["STUDENT_STATE_FIELD"],
        "note": "the snapshot carries a persistent learner identity field",
        "less": [],
        "top_level": {"student_id": "S-0001"},
    },
    "invalid-blocked-with-unmet-hard-prerequisite": {
        "valid": False,
        "declared_codes": ["BLOCKED_PREREQUISITE_INCONSISTENT"],
        "note": "a BLOCKED Lesson declares an unmet hard prerequisite that is actually PASS, so "
                "the declared prerequisite set is not the real unmet set",
        "less": [{"lesson_id": "JCA-M02-L02", "decision": "BLOCKED",
                  "blocked_by_mastery_units": ["JCA-MU-L03"]}],
    },
}

ORDER = tuple(FIXTURES)

# The eight invalid-snapshot axes the gate requires coverage for.
REQUIRED_INVALID_CASES = {
    "missing-lesson-result": "invalid-missing-lesson-result",
    "duplicate-lesson-result": "invalid-duplicate-lesson-result",
    "extra-lesson-result": "invalid-extra-lesson-result",
    "unknown-mastery-unit": "invalid-unknown-mastery-unit",
    "unknown-decision": "invalid-unknown-decision",
    "hard-prerequisite-inconsistent-pass": "invalid-hard-prerequisite-inconsistent-pass",
    "nonorder-relation-as-course-gate": "invalid-nonorder-relation-as-course-gate",
    "student-state-field": "invalid-student-state-field",
}


def materialise(name, lesson_order):
    """Expand one declaration into a complete snapshot body.

    `lesson_order` is the canonical Lesson order recomputed from the course manifest.
    """
    spec = FIXTURES[name]
    overrides = {entry["lesson_id"]: entry for entry in spec.get("less", [])}
    lessons = []
    for lesson_id in lesson_order:
        if lesson_id in overrides:
            lessons.append(dict(overrides[lesson_id]))
        else:
            lessons.append({"lesson_id": lesson_id, "decision": "PASS"})
    for lesson_id in spec.get("duplicate", []):
        lessons.append(dict(next(e for e in lessons if e["lesson_id"] == lesson_id)))
    for lesson_id in spec.get("omit", []):
        lessons = [e for e in lessons if e["lesson_id"] != lesson_id]
    for entry in spec.get("add", []):
        lessons.append(dict(entry))
    snapshot = {
        "snapshot_id": name,
        "contract_id": CONTRACT_ID,
        "course_id": COURSE_ID,
        "ephemeral": True,
        "lessons": lessons,
    }
    snapshot.update(spec.get("top_level") or {})
    return snapshot
