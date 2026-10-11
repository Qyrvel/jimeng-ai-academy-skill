# Architecture

The project separates factual provenance, pedagogical structure, and learner evaluation.

```text
Source Registry / Evidence Scope
        ↓
Atomic Knowledge Items
        ↓
Knowledge Graph
        ↓
Curriculum + Lesson Blueprint
        ↓
Canonical Lessons
        ↓
Assessment Requirements → Concrete Assessments
        ↓
Mastery Units
        ↓
Course Evaluation
```

## Layers

**Source** records where a claim comes from, its publisher, trust tier, version/client scope, evidence scope, and verification state.

**Knowledge** turns accepted evidence into atomic, scope-preserving claims.

**Graph** captures relationships such as prerequisites, procedure order, constraints, version context, scope parallels, variants, steps, and enforcement context.

**Curriculum** selects and orders what a beginner should learn. Pedagogical ordering is not automatically treated as a factual prerequisite.

**Lesson** is the canonical teaching unit.

**Assessment** maps required observable outcomes to concrete evidence tasks.

**Mastery** decides `PASS`, `RETRY`, `REMEDIATION`, or `BLOCKED` for a supplied evidence snapshot.

**Course Evaluation** composes lesson-level decisions into `COMPLETE`, `RETRY_REQUIRED`, `REMEDIATION_REQUIRED`, or `BLOCKED` while preserving routing targets.

## Non-goals in V1

There is no persistent learner database, gradebook, GPA, Tutor Engine, or adaptive learner model.
