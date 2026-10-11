# Jimeng AI Academy Skill

> An evidence-grounded, testable AI learning Skill for systematic Jimeng/即梦 AI learning — from source provenance to lessons, assessments, mastery routing, and course-level evaluation.

[中文说明](README.zh-CN.md) · [Architecture](docs/architecture.md) · [Contributing](CONTRIBUTING.md) · [Roadmap](ROADMAP.md)

## What this project is

Jimeng AI Academy Skill is an **unofficial community project** that turns evidence-backed product knowledge into a structured learning system. The current public baseline contains **Jimeng Creator Academy V1** for beginner creators.

The implemented pipeline is:

```text
Source / Evidence
  → Knowledge Items
  → Knowledge Graph
  → Curriculum / Blueprint
  → 24 Canonical Lessons
  → 23 Concrete Assessments
  → 24 Mastery Units
  → Course Evaluation
```

Current baseline:

- 8 modules
- 24 canonical lessons
- 23 concrete assessments
- 24 mastery units
- Mastery decisions: `PASS`, `RETRY`, `REMEDIATION`, `BLOCKED`
- Course decisions: `COMPLETE`, `RETRY_REQUIRED`, `REMEDIATION_REQUIRED`, `BLOCKED`
- Python validators/evaluators use the standard library only
- Designed for native project-level Agent Skill discovery via `.agents/skills/ai-academy/`

## Why this repository is different

The project deliberately separates:

- **Product claims** from **model claims**
- historical **release records** from current availability
- model capability from account/client/region availability
- documented evidence from observation, inference, and unverified information

The course is not generated ad hoc during a chat. The Skill reads canonical lessons, assessments, mastery contracts, and course-evaluation contracts stored in the repository.

## Repository layout

```text
.agents/skills/ai-academy/
  SKILL.md
  references/       # policies and contracts
  assets/           # JSON schemas / graph baseline
  scripts/          # validators and evaluators

academy-data/jimeng/
  sources/           # public source registry (raw third-party captures omitted)
  knowledge/         # normalized knowledge artifacts
  graph/             # graph artifacts
  curriculum/        # V1 curriculum + blueprint
  course/            # canonical course + 24 lessons
  assessment/        # assessments, mastery map, course evaluation

tests/               # reusable validators/fixtures
docs/                # contributor documentation
```

## Install / use with Codex-compatible project Skills

Clone the repository and open the repository root as your project/workspace. The Skill lives at:

```text
.agents/skills/ai-academy/SKILL.md
```

A learning request can be as simple as:

```text
I am completely new to Jimeng AI. Teach me systematically from the first lesson,
with explanations, practice, assessment, and mastery checks.
```

The Skill is intentionally scoped **not** to take over ordinary copywriting, one-off prompt rewrites, or unrelated coding tasks.

See [docs/install-codex.md](docs/install-codex.md) for a fuller workflow.

## Course map

1. Product, model, version, and entry-point concepts
2. First image-generation workflow
3. Video-generation workflow and output
4. Prompt fundamentals and revision
5. Reference-material inputs and boundaries
6. Editing and local correction
7. Platform-use rules and generation prerequisites
8. Independent end-to-end creation

The authoritative outline is `academy-data/jimeng/course/jimeng-creator-academy-v1/course-outline.md`.

## Evidence and copyright model

The public repository keeps source URLs and provenance metadata, but **does not redistribute the frozen project's verbatim captured excerpts from third-party webpages or terms**. Contributors should re-check original sources and materialize only minimal evidence when necessary. See [THIRD_PARTY_SOURCES.md](THIRD_PARTY_SOURCES.md) and [docs/evidence-model.md](docs/evidence-model.md).

## Project boundaries

Phase 1 intentionally does **not** implement persistent Student State, a Tutor Engine, adaptive learning, a gradebook/GPA, or account-level product availability detection. Mastery is a decision over a supplied evidence snapshot, not a permanent claim about a learner.

## Development

Most validators are standalone Python scripts under `.agents/skills/ai-academy/scripts/`. No third-party Python package is required for the core validators.

Run the public smoke checks:

```bash
python scripts/run_public_smoke.py
```

## Contributing

Contributions are welcome: source verification, version updates, localization, curriculum improvements, test fixtures, validator hardening, and new Academy topics that respect the architecture are all useful. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

Original project code, schemas, policies, course structures, tests, and original educational content in this public export are licensed under the **Apache License 2.0**, except where a file or referenced third-party source says otherwise. Third-party product names, trademarks, source materials, and linked content remain the property of their respective owners. See [LICENSE](LICENSE), [NOTICE](NOTICE), and [THIRD_PARTY_SOURCES.md](THIRD_PARTY_SOURCES.md).

## Unofficial project / trademarks

This project is community-developed and is **not affiliated with, sponsored by, or endorsed by Jimeng/即梦 AI, ByteDance, Jianying/CapCut, Seed, Apple, Volcengine, or their affiliates**. All trademarks and product names belong to their respective owners.
