# Lesson Blueprint Policy — Gate 4.2

本政策定义 **Lesson Blueprint** 层的合同。它位于 Curriculum Policy 之下，**不修改**任何上游层。

```text
Track → Module → Lesson Blueprint
```

Gate 4.2 仍然**不写完整 Lesson 正文**。

## 1. Lesson Blueprint 的职责

Lesson Blueprint 只回答七个问题：

```text
这一课为什么存在？            → purpose + lesson_role
学生完成后能做什么？          → learner_outcomes
这课教哪些已有 Knowledge？    → knowledge_refs
为什么排在这里？              → order_basis + order_rationale
学生要做什么练习？            → practice_intent
什么可观察证据说明这一课完成？  → completion_evidence
适用 scope 是什么？           → scope + limitations
```

它**不回答**：老师具体怎么讲每一句话、完整示例是什么、Quiz 题目是什么、完整操作教程正文是什么。这些属于后续 Gate。

## 2. Lesson 与 Module 的关系

- 一个 Module 展开为若干 Lesson；**每个 Lesson 必须属于一个已存在的 Module**，`module_id` 必须与 `lesson_id` 前缀一致；
- Lesson 不得跨 Module 混用前缀，`lesson_id` 全局唯一；
- 每个 Gate 4.1 Module **恰好**有一个 Module Blueprint；
- Gate 4.2 **不得**增删 Module、重编号或改 Domain Mapping；如发现 Module 结构缺陷，输出 `CURRICULUM_SKELETON_REFINEMENT_REQUIRED` 并停止。

Lesson 数量不设机械配额：目标是**每一课有单一主要学习目的**，同时避免「一个 Knowledge 一个 Lesson」与「一个 Lesson 塞完整个 Module」。

## 3. Knowledge Grounding

- 每个 Lesson `knowledge_refs >= 1`，且所有 ID 必须真实存在于 Knowledge Registry；
- 禁止隐式知识：不得引用未入库的概念、常识或模型记忆；
- **Module Knowledge Preservation Rule**：对每个 Module，

```text
Union(该 Module 全部 lesson.knowledge_refs) ⊇ Gate 4.1 module.knowledge_refs
```

允许同一 Knowledge 被多个 Lesson 使用；**不要求** Lesson 并集等于整个 Knowledge Registry。

## 4. Graph-constrained Lesson Order

Lesson 层与 Module 层不同：Module 层本轮 `GRAPH_CONSTRAINED = 0`，但 **Lesson 层不一定为 0**，必须逐 Module 检查其内部 Knowledge 子图。

只有两类关系构成 Lesson 级硬顺序：

| 关系 | 条件 | 结果 |
| --- | --- | --- |
| `A PREREQUISITE_OF B` | A、B 分属**同一 Module 的不同 Lesson** | 含 A 的 Lesson 必须排在含 B 的 Lesson 之前 |
| `A PROCEDURE_PRECEDES B` | 同上 | 同上 |

**不构成顺序的关系**：`CONSTRAINS`（使用边界）、`STEP_OF`（层级归属）、`VERSION_CONTEXT_FOR`、`SCOPE_PARALLEL_TO`、`VERSION_VARIANT_OF`、`ENFORCEMENT_CONTEXT_FOR`。

**跨 Module 的边不作为 Lesson 顺序约束**：Lesson 顺序只在 Module 内定义（Gate 4.1 已确认 Module 层无跨模块硬依赖）。

### Internal edge 不形成 Lesson order

若某边的 `from` / `to` 落在**同一个 Lesson** 内，它只作为该 Lesson 的 **internal structure**，不形成两个 Lesson 之间的顺序。**不得为了体现 Graph 而拆 Lesson。**

### GRAPH_CONSTRAINED 的准入条件

标 `GRAPH_CONSTRAINED` 的 Lesson 必须同时满足：

1. 至少引用一个真实存在的 edge；
2. 该 edge 的 `from` / `to` Knowledge 分属**不同 Lesson**；
3. Lesson 顺序符合 edge 方向。

**不得**因为「先学简单的再学复杂的」而标 `GRAPH_CONSTRAINED`。

## 5. Pedagogical Lesson Order

Graph 无依赖、但为教学清晰而排序时标 `PEDAGOGICAL`，且 `order_rationale` 必须包含：

```text
PEDAGOGICAL_RATIONALE:
```

并说明为什么对零基础学习者这样安排更清晰。不得声称是知识 prerequisite，**不得回写 Graph**。

## 6. Independent Lesson Order

两个 Lesson 既无 Graph dependency 也无强教学必要性时标 `INDEPENDENT`，并说明它们可以交换、当前顺序只是课程组织选择。

## 7. Practice Blueprint

`practice_intent` 只描述**学生要做什么类型的练习**（例如「在当前已验证 Web scope 中完成一次基础生成并检查结果」）。

禁止：

- 写成完整操作教程；
- 虚构未验证功能；
- 引入未入库的界面步骤、参数或额度条件。

## 8. Completion Evidence

`completion_evidence` 必须是**可观察**的（例如「能指出正确入口并完成一次生成结果检查」「能区分 Product Layer 与 Model Layer 的能力陈述」）。

它不是 Quiz 题目，也不是评分标准。Gate 4.2 不定义 Quiz / Rubric / Exam。

## 9. Scope Inheritance

每个 Lesson 必须继承其 Module 与上游 Knowledge 的 scope，并保留类似标签：

```text
Jimeng Product Layer
ByteDance Seed Model Layer
Jimeng Web
Seedance 2.5
Seedream 5.0 Pro
selected platform usage rules
current verified UI scope
```

禁止把 Model capability 教成 Product availability、把某次观察到的 Web UI 写成永久通用 UI、把建议性数值写成规格、把用户修改要求写成产品保证、把「未单独验证」写成「不支持」。

## 10. Lesson Body Boundary

Gate 4.2 允许写：purpose、outcome、knowledge refs、order rationale、practice intent、completion evidence、scope、limitations。

Gate 4.2 禁止写：讲稿、教程正文、示例正文、Quiz / Homework / Exam 题目、Rubric、Tutor 对话脚本、Student State、RAG、Vector DB、自动授课 Agent。

出现上述任一即 Lesson Body Leakage，Gate 4.2 不得 PASS。

## 11. Lesson Role

`lesson_role` 只允许：

```text
FOUNDATION / CONCEPT / PROCEDURE / APPLICATION / SAFETY / INTEGRATION
```

按真实内容决定，**不要为了角色多样性强行使用全部类型**。

## 12. Learner Outcomes

必须是可观察行为。优先使用「识别 / 区分 / 选择 / 输入 / 生成 / 检查 / 修改 / 执行 / 遵守 / 完成 / 解释边界」。

避免只写「了解 / 熟悉 / 掌握 / 理解」，除非后面接具体可观察行为。

## 13. Upstream Zero-Mutation Rule

```text
Source / Evidence / Knowledge / Normalization / Production Graph / Frozen Graph Contract
Curriculum Readiness Contract / Gate 4.1 Module Skeleton
→ 全部 0 mutation
```

只允许新增：Lesson Blueprint Contract（policy / schema / validator / tests）与 Blueprint artifacts / reviews。

如需修改 Module Skeleton：`STOP_AND_REPORT` + `CURRICULUM_SKELETON_REFINEMENT_REQUIRED`，不得静默拆 Module、重编号或改 Domain Mapping。

## 14. 机器验证与人工审核的分工

`validate_lesson_blueprints.py` 负责结构级检查（身份、Module 完整性、Knowledge 存在性与覆盖、Graph ref 真实性与跨 Lesson 方向、order 标记、证据字段非空）。

Validator **不判断**教学内容质量。以下由 Human Review 负责：Lesson Atomicity、Module Fidelity、Knowledge Grounding、Scope Safety、Model/Product Separation、Order Honesty、Practice Grounding、Completion Evidence、Module Load、Nonblocking Orphans、Lesson Body Leakage。

**fixture PASS ≠ 蓝图合格。**
