# Jimeng Creator Academy V1 — Mastery Map（人类可读渲染）

> 机器事实以 `mastery-map.json` 为准。本文件只定义**判定规则**，不存储任何学习者状态。

## 判定合同

```text
decision_enum: PASS / RETRY / REMEDIATION / BLOCKED
```

固定分支顺序（**顺序即合同**）：

```text
① hard prerequisite 未满足    → BLOCKED / BLOCKED_BY_HARD_PREREQUISITE
② 全部 required outcome 满足   → PASS / PASS_ALL_REQUIRED_OUTCOMES
③ 缺口含 boundary/concept 误解 → REMEDIATION / REMEDIATE_BOUNDARY_MISCONCEPTION
④ 证据未提交                   → RETRY / RETRY_EVIDENCE_INCOMPLETE
⑤ execution criterion 未达标   → RETRY / RETRY_EXECUTION_INCOMPLETE
⑥ 仍有 outcome 缺口            → REMEDIATION / REMEDIATE_OUTCOME_GAP
```

④⑤ 必须排在 ⑥ 之前，否则 RETRY 永远不可达。

## 24 个 LESSON mastery unit

`outcomes` 列为该 unit 需覆盖的 outcome 数（必须等于其 Lesson 的全部 learner outcome）。

| Unit | Lesson | Requirement | Outcomes | Hard Prerequisite |
| --- | --- | --- | --- | --- |
| MU-L01 | M01-L01 | AR-001 | 3 | — |
| MU-L02 | M01-L02 | AR-002 | 4 | — |
| MU-L03 | M02-L01 | AR-003, AR-004 | 2 | — |
| MU-L04 | M02-L02 | AR-004 | 2 | MU-L03 |
| MU-L05 | M02-L03 | AR-005 | 2 | — |
| MU-L06 | M03-L01 | AR-006 | 2 | — |
| MU-L07 | M03-L02 | AR-007 | 2 | MU-L06 |
| MU-L08 | M03-L03 | AR-008 | 2 | MU-L07 |
| MU-L09 | M04-L01 | AR-009 | 2 | — |
| MU-L10 | M04-L02 | AR-010 | 2 | — |
| MU-L11 | M04-L03 | AR-011 | 2 | — |
| MU-L12 | M05-L01 | AR-012 | 3 | — |
| MU-L13 | M05-L02 | AR-013 | 3 | — |
| MU-L14 | M05-L03 | AR-014 | 3 | MU-L12 |
| MU-L15 | M06-L01 | AR-015 | 3 | — |
| MU-L16 | M06-L02 | AR-016 | 4 | — |
| MU-L17 | M07-L01 | AR-017 | 2 | — |
| MU-L18 | M07-L02 | AR-018 | 2 | — |
| MU-L19 | M07-L03 | AR-019 | 3 | — |
| MU-L20 | M07-L04 | AR-020 | 2 | — |
| MU-L21 | M08-L01 | AR-021 | 2 | — |
| MU-L22 | M08-L02 | AR-022 | 2 | — |
| MU-L23 | M08-L03 | AR-023 | 3 | — |
| MU-L24 | M08-L04 | AR-024 | 2 | — |

**未创建任何 `SEQUENCE_PAIR` unit**：4 个 hard gate 已由后置 LESSON unit 的 `hard_prerequisite_units` 表达，额外建 pair unit 没有真实 necessity，只会重复计数。

## 硬顺序汇总

```text
mastery_hard_transition_count:       4
mastery_supporting_hard_edge_count:  5
non_order_mastery_gate_misuse_count: 0
```

## 规则命名

unit 的 `pass_rule` / `retry_rule` / `remediation_rule` 引用 `rule_definitions` 中的 `LESSON_PASS` / `LESSON_RETRY` / `LESSON_REMEDIATION`，避免 24 份重复文本互相漂移。

## 决策夹具（`tests/mastery-decisions/`）

```text
pass-all.json                 → PASS / PASS_ALL_REQUIRED_OUTCOMES
retry-execution.json          → RETRY / RETRY_EXECUTION_INCOMPLETE
remediation-outcome-gap.json  → REMEDIATION / REMEDIATE_OUTCOME_GAP
blocked-prerequisite.json     → BLOCKED / BLOCKED_BY_HARD_PREREQUISITE
```

四者只含 `assessment evidence snapshot`，不含 `student_id`、历史或持久状态。
