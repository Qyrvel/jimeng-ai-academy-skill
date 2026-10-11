# Contributing

Thank you for helping improve Jimeng AI Academy Skill. The project values **evidence quality, scope discipline, reproducibility, and learner usefulness** over adding features quickly.

## Good contribution areas

- Verify/update official Jimeng product sources and version context.
- Improve lesson clarity without changing unsupported facts.
- Add or harden validator fixtures.
- Improve assessment alignment and mastery routing.
- Translate documentation while preserving canonical IDs and semantics.
- Propose new Academy topics using the same Source → Knowledge → Graph → Curriculum architecture.

## Evidence rules

1. Prefer first-party/official sources.
2. Record source URL, publisher, verification date, evidence scope, version/client scope, and trust tier.
3. Separate Product / Model / API / Observed layers.
4. Do not infer account availability from model capability.
5. Do not commit full webpages or large verbatim excerpts from third-party sources. Use minimal excerpts only when redistribution is appropriate; otherwise keep only metadata and ask reviewers to verify the original URL.
6. Never turn search snippets or model memory into `DOCUMENTED` evidence.

## Change discipline

A change to a lesson may require corresponding updates to the blueprint, assessment mapping, concrete assessment, mastery map, and tests. Preserve canonical IDs unless the change explicitly includes a migration plan.

## Tests

Run:

```bash
python scripts/run_public_smoke.py
```

For validator changes, also run the relevant fixture suite under `tests/`.

## Pull requests

Explain:

- what changed;
- which canonical artifacts are affected;
- evidence/source IDs supporting factual changes;
- what tests were run;
- any version/client/region limitations.

## Scope boundaries

Phase 1 does not include persistent Student State, Tutor Engine, adaptive learning, a gradebook, or automatic account-level availability checks. Proposals for these belong in a future phase and should not silently alter the V1 contract.
