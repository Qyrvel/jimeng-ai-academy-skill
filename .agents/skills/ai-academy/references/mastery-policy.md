# Mastery Policy — Gate 4.6

本政策定义 **Mastery Contract**：给定一组 assessment evidence，**应该如何判定**。它不存储任何学生状态。

## 1. Mastery 的含义

> Mastery = 学习者对一个明确 mastery unit 的所有 required outcomes，均产生满足 assessment requirement 的可观察 evidence。

Mastery **不是**：一次考试的百分比分数、学生永久能力、模型对学生的心理推断、长期记忆状态。

## 2. Mastery Unit

本 Gate 只允许两种：

```text
LESSON
SEQUENCE_PAIR
```

暂不创建 `MODULE` / `TRACK` 级 graduation mastery——当前 evidence 最稳定的锚点仍是 Lesson outcome / completion_check。

默认 `1 canonical Lesson → 1 LESSON mastery unit`。只有真实 necessity 才额外建 `SEQUENCE_PAIR` unit；**不得为了体现 graph 强行创建**（本 Gate 未创建任何 SEQUENCE_PAIR unit）。

## 3. Unit 字段

`mastery_unit_id`（`JCA-MU-L##`）/ `unit_type` / `lesson_ids` / `required_requirement_ids` / `required_outcomes` / `hard_prerequisite_units` / `pass_rule` / `retry_rule` / `remediation_rule` / `limitations`。

`required_outcomes` 使用 `<lesson_id>#<index>` 形式引用该课 `learner_outcomes` 的 0-based 索引。

规则文本用 `rule_definitions` 中的命名规则引用（`LESSON_PASS` / `LESSON_RETRY` / `LESSON_REMEDIATION`），避免 24 份重复文本互相漂移。

## 4. Hard Sequence Gating

- 只有 `PREREQUISITE_OF` 与 `PROCEDURE_PRECEDES` 在**跨 Lesson** 时形成 mastery gate；
- 当前为 **4 个 transition 级 gate**，由 **5 条** hard edge 支撑；
- 一个 transition 即使被 2 条边支撑，仍只算 **1 个 gate / 1 个 prerequisite**，不得重复制造两个 prior unit；
- 两个计数**必须分开报告**。

## 5. 非顺序关系不得做 Gate

`CONSTRAINS` / `STEP_OF` / `VERSION_CONTEXT_FOR` / `VERSION_VARIANT_OF` / `SCOPE_PARALLEL_TO` / `ENFORCEMENT_CONTEXT_FOR` **不得**生成 `hard_prerequisite_units`。

```text
NON_ORDER_RELATION_MASTERY_GATE_MISUSE_COUNT = 0
```

## 6. Pass Rule

不得只用 `total_score >= 百分比` 作为 mastery 定义。Lesson mastery PASS 至少要求：

```text
A. 所有 mastery_required requirement 都已有 evidence；
B. 每一个 required learner outcome 都被满足；
C. 所有 critical criterion（如存在）满足其 pass_condition；
D. hard_prerequisite_units 已先满足。
```

允许同时有分数阈值，但**分数不得覆盖 outcome 缺口**。

**Critical criterion**：只有对安全、顺序或核心 procedure 完成不可缺失的 criterion 才可标 critical；不得把所有 criterion 都标 critical。本 Gate 未新增任何批 critical 字段——它是 Mastery 解释层概念，不改 Gate 4.5 的 assessment schema。

## 7. Retry

`RETRY` 表示：学习者已具备必要基础，但本次 task execution / evidence 不完整，可在**不重新教学全部内容**的情况下再次尝试。

条件：hard prerequisites 已满足 + 无概念/边界误解 + 主要缺失在 execution / evidence / result quality 层。

## 8. Remediation

`REMEDIATION` 表示：evidence 显示某个 required outcome **本身**尚未达到，需要回到明确 Lesson / teaching point / practice。

必须输出：`target_lesson_id` / `target_outcome` / `reason` / `recommended_review_scope`。**不得**生成课程外新教学内容。

## 9. Retry 与 Remediation 必须可判定

禁止「失败了就随便标 RETRY」或「一律 REMEDIATION」。判定使用固定分支顺序（见 `mastery-map.json` 的 `decision_contract.evaluation_order`）：

```text
① hard prerequisite 未满足        → BLOCKED / BLOCKED_BY_HARD_PREREQUISITE
② 全部 required outcome 满足       → PASS / PASS_ALL_REQUIRED_OUTCOMES
③ 缺口含 boundary/concept 误解     → REMEDIATION / REMEDIATE_BOUNDARY_MISCONCEPTION
④ 证据未提交                       → RETRY / RETRY_EVIDENCE_INCOMPLETE
⑤ execution criterion 未达标       → RETRY / RETRY_EXECUTION_INCOMPLETE
⑥ 仍有 outcome 缺口                → REMEDIATION / REMEDIATE_OUTCOME_GAP
```

分支 ④⑤ 必须排在 ⑥ 之前：这样「执行/证据层缺失」才判 RETRY，「outcome 本身未达到」才判 REMEDIATION。若把 ⑥ 放前面，RETRY 将**永远不可达**，两级区分形同虚设。

**分支顺序即合同**：`validate_mastery.py --decision` 与实现必须一致。

## 10. Decision Enum

只允许：

```text
PASS / RETRY / REMEDIATION / BLOCKED
```

`BLOCKED_BY_HARD_PREREQUISITE` 时**不得**判 PASS / RETRY / REMEDIATION。这不是 Student State，只是 decision contract。

## 11. Derived Metric 硬规则

> 任何写入 machine artifact 的 derived metric，如果保留，就必须由 validator 根据 source fields 重新计算并逐字段核对；否则不要写这个字段。

禁止「人工填一个 count 但 validator 不验证」。`full-assessment-mapping.json` 与 `mastery-map.json` 的 `derived` 块均由对应 validator 重算比对。

## 12. 不建立 Student State

本层只定义 decision contract。**不得**创建或存储：`student_id`、学习历史、进度时间线、持久 mastery 状态、gradebook、learner profile。

Decision fixture 只模拟 `assessment evidence snapshot` 输入。

## 13. Upstream Zero-mutation

不得修改 Source / Evidence / Knowledge / Normalization / Graph / Curriculum Skeleton / Lesson Blueprint / Canonical Lesson / Course Manifest / Course Outline / Gate 4.5 Pilot Assessment 内容。

若 mapping 暴露 outcome 不可测 → `LESSON_OUTCOME_REFINEMENT_REQUIRED`；若需要课程外事实 → `ASSESSMENT_KNOWLEDGE_GAP_DISCOVERED`；若合同无法表达某课 → `ASSESSMENT_CONTRACT_REVISION_REQUIRED` / `ASSESSMENT_TYPE_CONTRACT_REVISION_REQUIRED`。以上任一情形均 `STOP_AND_REPORT`，**不得静默改上游**。
