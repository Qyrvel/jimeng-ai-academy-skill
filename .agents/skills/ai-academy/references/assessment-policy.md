# Assessment Policy — Gate 4.5

本政策定义 **Assessment Spec** 的合同。它位于 Lesson 之下，**不修改任何上游层**。

```text
Lesson outcome + completion_check + taught knowledge
        ↓
  observable task → expected evidence → scoring rule
```

核心命题只有一句：**我们教过什么，就只测什么；学生是否通过可观察行为证明已达到 Lesson outcome？**

## 1. Assessment Grounding

每个 Assessment 的重要 claim 必须可追溯：`Lesson → Knowledge`。Assessment **自身不得新增任何产品事实**、不得引入 Registry 之外的知识、不得查 Web 补洞。

若发现必须依赖未入库事实 → `ASSESSMENT_KNOWLEDGE_GAP_DISCOVERED` + `STOP_AND_REPORT`。

## 2. Outcome Alignment

`target_outcomes` 必须是被引用 Lesson 的 `learner_outcomes` 的**子集**。不得创造 Lesson 没教过的 outcome，也不得把 outcome 改写成更容易测的样子。

## 3. Completion-check Alignment

每个 Assessment 必须显式记录 `Lesson completion_check → Assessment expected_evidence` 的关系，只允许：

```text
DIRECT
NARROWER_EQUIVALENT
COMPOSITE_FROM_MULTIPLE_COMPLETION_CHECKS
```

禁止 `UNRELATED`。**这是本 Gate 的核心检查。**

## 4. Knowledge Boundary

`knowledge_refs` 必须是被引用 Lesson `knowledge_refs` 的**并集子集**。Assessment 不得引用课程之外 Knowledge。

## 5. Scope Inheritance

Assessment 的 `scope` 必须 **≤ Lesson scope**（相等或更窄）。不得扩大客户端 / version / model / UI / 账号范围。

## 6. Assessment Item Types

顶层语义类型只允许 7 种：

```text
IDENTIFY / CLASSIFY / EXPLAIN_BOUNDARY / PERFORM_PROCEDURE
INSPECT_RESULT / APPLY_RULE / INTEGRATED_TASK
```

**禁止**把 `MULTIPLE_CHOICE` / `TRUE_FALSE` / `ESSAY` 当作顶层类型——它们是**呈现形式**，不是测量对象。本 Gate 先验证测量对象；delivery format 留待后续。

## 7. Expected Evidence

必须明确写出「学生提交什么证据，才能判断已达到 outcome」：正确入口识别 / 操作结果 / 屏幕或产物 / 分类结果 / 边界解释 / 规则应用理由。

不得要求课程没教过的证据。

## 8. Scoring Criteria

必须 criterion-based。每条至少：

```text
criterion_id / description / evidence_source / weight / pass_condition
```

`max_score` 与 `pass_score` 由 criteria **程序化计算**（`max_score = Σ weight`），不得手算写死。

## 9. Scoring Scale

Pilot 使用 criterion score，不建立复杂 mastery 模型：

```text
0 = 未满足      1 = 部分满足      2 = 满足
```

某 criterion 若本质二元，允许只用 `0 / 2`，但必须在 `partial_credit_policy` 中解释。

## 10. Partial Credit

必须允许 partial credit，除非该 criterion 本质是原子二元动作。**不得**因为最终结果失败就把中间已正确完成的已教步骤全部判 0。

## 11. No Trick Question Rule

禁止：用课程没教过的 UI 名称做陷阱；用旧版本按钮骗学生；把 Model capability 与 Product availability 混淆当难题；把 unknown 当 unsupported；用模糊 wording 测阅读陷阱。

Assessment 测能力，不测猜题。

## 12. Sequence Safety

- Assessment 可以引用一个 Lesson，或一个**已验证的 Lesson pair**（`SEQUENCE_PAIR`）或已教能力的组合（`INTEGRATED_SKILL`）；不得任意跨课拼题，不得创建跨 Module 综合考试。
- 跨 Lesson 的 assessment 必须**分别报告**：

```text
ASSESSMENT_HARD_TRANSITION_COUNT
ASSESSMENT_SUPPORTING_HARD_EDGE_COUNT
```

不得把 transition 计数与 edge 计数合并成一个数字。

## 13. Feedback Boundary

只定义「评分后可以告诉学生什么」：哪个 criterion 未达标、对应 Lesson、建议重学哪一课、scope/boundary 提醒。

禁止：自动生成新知识事实、引入 Registry 外答案、推断长期 mastery。

## 14. Pilot-only Boundary

本 Gate **只做小规模 Pilot**。禁止创建：全课程 quiz bank、24 课全量 assessment、final/graduation exam、gradebook、mastery engine、student state、spaced repetition、adaptive learning、tutor engine、RAG、vector DB、用户画像、自动评分模型、全课程认证体系。

## 15. Upstream Zero-mutation

不得修改：Source / Evidence / Knowledge / Normalization / Graph / Curriculum Skeleton / Lesson Blueprint / Canonical Lessons / Course Manifest / Course Outline。

若 Assessment 暴露 **Lesson outcome 不可测** → `LESSON_OUTCOME_REFINEMENT_REQUIRED` + `STOP_AND_REPORT`，**不得**静默改 Lesson。
若问题在合同侧 → `ASSESSMENT_CONTRACT_REVISION_REQUIRED` + `STOP_AND_REPORT`。

## 16. 审美边界

创作类 Lesson 不得用「好看 / 高级 / 电影感 / 专业」作为无定义评分标准。若必须判断结果质量，只能评分**已教且可观察**的 criterion（是否满足指定修改目标、是否保留已要求边界、是否按流程完成）。
