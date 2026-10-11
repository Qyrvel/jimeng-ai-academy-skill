# Course Evaluation Policy — Jimeng Creator Academy V1

Gate 4.7B. This policy defines how the frozen 24 canonical Lessons, 8 Modules and 4 hard Lesson
transitions are aggregated, routed and validated at course level. It creates no teaching content,
no assessment item, no Lesson, no Module, no graph edge and no learner state.

```text
COURSE_EVALUATION_POLICY: full_course
```

---

## 1. Scope

In scope:

```text
24 canonical Lesson mastery decisions (the production mastery contract)
8 canonical Modules
4 hard Lesson transitions and 5 supporting hard edges
course-level aggregation, routing and validation
one ephemeral evaluation snapshot as the only input
```

Out of scope, and forbidden in this Gate:

```text
Student State Engine        Learner Profile          Gradebook
persistent mastery history  student_id records       progress timeline
attempt history             spaced repetition        adaptive tutor
Tutor Engine                RAG                      Vector DB
online proctoring           user behaviour tracking
Final Exam                  Graduation Exam          numeric final grade
new assessment item         new Lesson               new Curriculum
new mastery unit            new Graph edge           synthetic Track level
```

---

## 2. Input boundary

The course evaluator reads, and never writes:

```text
course-evaluation-contract.json                     (this contract, machine truth)
one ephemeral evaluation snapshot                     (the only per-evaluation input)
academy-data/jimeng/assessment/mastery-map.json       (production mastery contract)
academy-data/jimeng/course/<course>/course-manifest.json  (canonical course structure)
the authoritative graph set actually used by production mastery
```

The snapshot carries exactly:

```text
snapshot_id
contract_id
course_id
one declared decision per canonical Lesson (mandatory, exactly one each)
optional unmet_outcome_refs        (REMEDIATION only)
optional blocked_by_mastery_units  (BLOCKED only)
```

The snapshot must **not** carry any of:

```text
student_id  user_id  learner_id  learner_profile  profile
history  attempt_history  attempt_sequence  attempts
timestamp  timestamps  created_at  updated_at  saved_at
progress  saved_progress  progress_timeline  timeline
database_key  db_key  record_id  persistent_id  session_id
grade  score  percentage  gpa  final_score  letter_grade
```

A snapshot carrying any of these fields is an invalid snapshot (`STUDENT_STATE_FIELD` or
`NUMERIC_GRADE_FIELD`) and must be rejected; it is never silently ignored.

```text
NO_STUDENT_STATE_ENGINE: PASS
```

---

## 3. Output decisions

Course-level and Module-level decisions are drawn only from:

```text
COMPLETE
RETRY_REQUIRED
REMEDIATION_REQUIRED
BLOCKED
```

These values are **not** used at any level:

```text
FAILED   GRADUATED   FINAL_GRADE
```

Severity / precedence:

```text
BLOCKED  >  REMEDIATION_REQUIRED  >  RETRY_REQUIRED  >  COMPLETE
```

---

## 4. Lesson mastery input

The course evaluator does **not** re-invent Lesson mastery. It consumes the production mastery
decision contract and maps it one-to-one:

```text
PASS         -> the Lesson contributes COMPLETE
RETRY        -> RETRY_REQUIRED
REMEDIATION  -> REMEDIATION_REQUIRED
BLOCKED      -> BLOCKED
```

There is no second mastery semantics, no re-scoring and no promotion:

```text
REMEDIATION is never promoted to PASS
BLOCKED     is never rewritten to RETRY
```

---

## 5. Module aggregation

A Module's status is the highest severity among its canonical Lessons, taking the first matching
condition in this exact order:

```text
if any Lesson = BLOCKED:        Module = BLOCKED
else if any Lesson = REMEDIATION: Module = REMEDIATION_REQUIRED
else if any Lesson = RETRY:       Module = RETRY_REQUIRED
else every Lesson must be PASS:   Module = COMPLETE
```

Illegal Module input — missing, duplicate, extra, unknown-unit or unknown-decision — is an
**invalid evaluation snapshot**, not an incomplete Module:

```text
MISSING_LESSON_RESULT     DUPLICATE_LESSON_RESULT   EXTRA_LESSON_RESULT
UNKNOWN_MASTERY_UNIT      UNKNOWN_DECISION
```

The evaluator must never default an illegal snapshot to "incomplete".

---

## 6. Course aggregation

```text
COURSE = COMPLETE
iff
1. every canonical Lesson mastery unit is PASS
2. every Module status is COMPLETE
3. all hard Lesson transitions are satisfied
4. the production mastery prerequisite semantics are consistent
5. no non-order relation has been promoted into a course gate
```

Otherwise the Course status is the highest severity present, using the precedence of §3.

```text
course_status = COMPLETE  ==>  every routing target array is empty
```

No numeric grade is produced at any point:

```text
percentage  GPA  weighted final score  letter grade  ->  forbidden
```

Reason: completion is decided by mastery completeness plus hard-sequence integrity, which is
already sufficient truth. No hidden common-sense graduation logic may be added ("80% passes",
"skip a Lesson", "finish X Modules and graduate", "average above Y") unless a frozen upstream
contract explicitly requires it. None does, so:

```text
NUMERIC_GRADE_REQUIREMENT_DISCOVERED: NOT FOUND
NUMERIC_GRADE_FIELD_COUNT = 0
```

---

## 7. Hard-sequence integrity

The evaluator recomputes, programmatically and never from a hardcoded literal:

```text
hard Lesson transitions        (from production mastery hard_prerequisite_units)
supporting hard edges          (from the authoritative graph set)
```

Only these relations are legal hard ordering:

```text
PREREQUISITE_OF
PROCEDURE_PRECEDES
```

A snapshot that declares a later unit `PASS` while its hard prerequisite unit is not `PASS`
cannot legally exist:

```text
INCONSISTENT_EVALUATION_SNAPSHOT
```

It is reported as an invalid snapshot and makes the validator `FAIL`. It is **never** silently
converted into `BLOCKED`. A `BLOCKED` state must come from the production mastery decision itself,
and a Lesson declared `BLOCKED` must name exactly the hard prerequisite units that its own
snapshot leaves unsatisfied:

```text
BLOCKED_PREREQUISITE_INCONSISTENT
```

---

## 8. Non-order relation guard

These relations may never become a Module gate, a Course gate, a Track gate or a completion
prerequisite:

```text
CONSTRAINS   STEP_OF   VERSION_CONTEXT_FOR   VERSION_VARIANT_OF
SCOPE_PARALLEL_TO   ENFORCEMENT_CONTEXT_FOR
```

Legal hard ordering comes only from `PREREQUISITE_OF` and `PROCEDURE_PRECEDES`, exactly as the
frozen graph / mastery contract already approves. Any snapshot that claims a prerequisite unit no
order relation justifies is rejected:

```text
NON_ORDER_COURSE_COMPLETION_GATE
NON_ORDER_COURSE_COMPLETION_GATE_MISUSE_COUNT = 0
```

---

## 9. Routing

The evaluator emits four deterministic, separately-sorted routing collections:

```text
retry_targets
remediation_targets
blocked_targets
blocked_by_mastery_units
```

### RETRY

Routes only to the Lessons / mastery units that are currently `RETRY`, together with the
assessment-evidence requirement. It never reopens an unrelated Lesson that already passed.

### REMEDIATION

Routes to the Lessons / mastery units that are currently `REMEDIATION`, carrying the unmet
learner outcome references the production mastery decision really points at. It is never
generalised into "retake the whole course".

### BLOCKED

Routes to the unmet legal hard prerequisite mastery units, per blocked Lesson. It never routes to
a non-order relation.

### COMPLETE

All four routing collections must be empty.

---

## 10. Mixed-state precedence and lossless routing

When `RETRY`, `REMEDIATION` and `BLOCKED` coexist:

```text
overall_status = highest severity   (BLOCKED wins)
```

but the other real routing targets are **not** dropped:

```text
retry_targets         preserved (real non-empty set)
remediation_targets   preserved (real non-empty set)
blocked_targets       preserved (real non-empty set)
```

Routing is therefore lossless: severity decides the headline status, and no route is lost.

---

## 11. Track applicability

```text
CANONICAL_TRACK_ENTITY_COUNT = 0
TRACK_COMPLETION_APPLICABILITY = NOT_APPLICABLE
```

No canonical Track entity exists in the current project, so no Track aggregation is performed and
no synthetic Track level may be invented to satisfy the phrase "track completion". The validator
requires:

```text
no synthetic track result        (track_results must be empty)
SYNTHETIC_TRACK_ENTITY_COUNT = 0
```

If a real Track entity is later added to canonical truth, applicability becomes `APPLICABLE` and
aggregation must use real Track membership.

---

## 12. Invalid snapshot semantics

Every one of these conditions makes the evaluator exit non-zero with the named code, and makes
the validator `FAIL`:

```text
MISSING_LESSON_RESULT                  a canonical Lesson result is absent
DUPLICATE_LESSON_RESULT                a Lesson is declared twice
EXTRA_LESSON_RESULT                    a non-canonical Lesson is declared
UNKNOWN_MASTERY_UNIT                   an unknown or mismatched mastery unit
UNKNOWN_DECISION                       a decision outside the four-value enum
INCONSISTENT_EVALUATION_SNAPSHOT       a later unit PASS under an unmet hard prerequisite
BLOCKED_PREREQUISITE_INCONSISTENT      declared unmet set != real unmet set
NON_ORDER_COURSE_COMPLETION_GATE       a non-order relation used as a prerequisite
INVALID_ROUTING_TARGET                 an outcome ref outside its own Lesson
STUDENT_STATE_FIELD                    a persistent learner identity field
NUMERIC_GRADE_FIELD                    a grade field
```

No invalid snapshot is ever reinterpreted as "incomplete" and none is downgraded to `BLOCKED`.

---

## 13. Derived metric policy

Any `*_count`, `summary`, `distribution` or `coverage` value that is retained in a machine
artifact must be recomputed from source fields and compared with the stored value:

```text
recompute from source  ->  compare stored  ->  mismatch = FAIL
COURSE_EVALUATION_DERIVED_METRIC_MISMATCH_COUNT = 0
```

The contract itself stores no bulk upstream data: it references the course manifest, mastery map,
graph set, full assessment set and coverage manifest, and never copies the 24 Lessons, 23
Assessments or 59 outcomes into itself.

---

## 14. Determinism

The evaluator is a pure deterministic function: Python standard library only, no network, no
database, no filesystem write, no randomness, no clock. Every emitted collection is sorted by a
total key (`lesson_id`, then `mastery_unit_id`), so the same snapshot always yields byte-identical
output.

---

## 15. No student state

```text
ephemeral snapshot only: true
NO_STUDENT_STATE_ENGINE: PASS
STUDENT_STATE_FIELD_COUNT = 0
```

The snapshot is an evaluation input, never a record. Nothing is persisted per learner, and no
attempt, timeline, grade or identity is stored anywhere in this Gate.
