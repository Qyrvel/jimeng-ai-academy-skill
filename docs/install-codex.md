# Install / use in Codex-compatible project Skill discovery

## Repository layout

The Skill entry is:

```text
.agents/skills/ai-academy/SKILL.md
```

Open the cloned repository as the project/workspace. On environments that support native project-level `.agents/skills` discovery, no duplicate Skill copy is required.

## Positive trigger examples

```text
I am completely new to Jimeng AI. Teach me systematically from the first lesson.
```

```text
Use the course's formal practice and assessment system to check whether I understand product/model/version boundaries.
```

## Negative trigger examples

These should remain ordinary tasks and should not force Academy mode:

```text
Write a short ad about Jimeng AI.
```

```text
Rewrite this single video prompt to sound more natural.
```

```text
Write a Python utility that prints JSON keys.
```

## Verification

Run:

```bash
python scripts/run_public_smoke.py
```

Then start a fresh agent session and try both positive and negative trigger examples.
