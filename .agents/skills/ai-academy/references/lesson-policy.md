# Lesson Policy — Gate 4.3

本政策定义 **Lesson**（真实教学单元）的合同。它位于 Lesson Blueprint 之下，**不修改**任何上游层。

```text
Track → Module → Lesson Blueprint → Lesson
```

Gate 4.3 只为 Pilot 生成少量 Lesson，**不生成全课程**。

## 1. Lesson 的职责

Lesson 是学生真正读到、练到、被检查的最小教学单元。它负责把**已经存在的 Knowledge** 组织成可教的形式：

```text
目标 → 讲解 → 引导练习 → 独立练习 → 完成检查 → 边界提醒
```

## 2. Lesson Body 与 Blueprint 的关系

Blueprint 回答"这一课为什么存在、要教哪些知识、排在哪里"；Lesson Body 回答"这一课具体怎么教"。

必须一致（§12 Blueprint Fidelity）：`lesson_id` / `module_id` / `title` / `lesson_role` / `scope` / `learner_outcomes` / `knowledge_refs` / `graph_support_refs` 全部来自 Gate 4.2 Blueprint。

- 允许 `scope` **更窄**；
- **不允许** `scope` 更宽；
- **不得**新增 Blueprint 中不存在的核心 learner outcome。

## 3. Knowledge Grounding

- 每个 `teaching_point` 的 `knowledge_refs >= 1`，且必须是本 Lesson `knowledge_refs` 的子集；
- `explanation` 只能解释已有 Knowledge 的 statement 与 limitations，不得扩大 claim；
- Lesson 的 `knowledge_refs` 必须覆盖 Blueprint 为这一课列出的全部引用（Gate 4.2 的"核心 refs"判定即"该课被分配的全部 refs"）。

## 4. 允许与禁止

Lesson **可以**：改写成易懂语言、分步骤解释、比较、给教学例子、提醒边界。

Lesson **不可以**：

- 扩大 claim；
- 补写未验证按钮；
- 补写价格或积分；
- 补写动态版本状态；
- 把 Model capability 写成 Product availability；
- 把 Product UI 写成 Model technical limit。

出现任何 Knowledge / Evidence 无法支持的产品事实 → `NEEDS_REVISION`，**先改 Lesson，不得改 Knowledge 去适配 Lesson**。

## 5. Scope Inheritance

`scope` 必须继承 Blueprint 与上游 Knowledge 的 scope，只能更窄。禁止出现把局部验证范围泛化的表述（如"所有客户端""永久""全部账号"）。

## 6. teaching_point

每个 teaching point 必须含：

```text
point_id
knowledge_refs
explanation
scope_note
```

`scope_note` 用于说明该点适用的范围或"不能推出什么"。

## 7. Pedagogical Example Contract

允许创建教学例子，但**任何非 Evidence 原文的例子**必须显式标注：

```text
PEDAGOGICAL_EXAMPLE
```

并满足：不作为产品事实、不引入新功能 claim、不引入动态参数、不引入未验证 UI、不改变 Knowledge scope。

例（合法）：

> `PEDAGOGICAL_EXAMPLE`：假设你想把人物上衣改成蓝色，其他保持不变……

例（非法）：

> "Seedream 永远可以只修改衣服且其它完全不变。"（这是把用户的修改要求写成了产品保证）

## 8. guided_practice

每课必须有。只描述**学生在引导下完成什么动作**，必须映射本课 learner outcome。操作型 Lesson 应尽量使用当前已验证 Product Scope；不得创建未验证操作步骤。

## 9. independent_practice

每课必须有。比 guided practice **少一个层级的提示**，仍不得引入新功能。它不是 Homework 系统。

## 10. completion_check

每课必须定义**可观察**完成标准。它不是 Quiz Bank，不定义题目、评分或 rubric。

## 11. boundaries_and_misconceptions

每课至少包含一项边界或易混点，来源必须是 Knowledge limitations 或 Curriculum review，例如：易混 scope、version/UI 边界、model/product 边界、"unknown ≠ unsupported"、policy 使用边界、workflow 边界。

**不得凭空制造"常见错误事实"。**

## 12. Graph Order

- Lesson 顺序遵循 Gate 4.2 的 `lesson_order` 与 Lesson 级硬顺序；
- `PREREQUISITE_OF` 与 `PROCEDURE_PRECEDES` 在跨 Lesson 时构成硬顺序；
- `CONSTRAINS` / `STEP_OF` / `VERSION_CONTEXT_FOR` / `VERSION_VARIANT_OF` / `SCOPE_PARALLEL_TO` / `ENFORCEMENT_CONTEXT_FOR` **不得**被写成顺序或 prerequisite；
- **不得**为了"看起来更严谨"把教学偏好包装成 Graph constraint。

## 13. Lesson 不得创造事实

Lesson 是教学表达层，不是知识生产层。它不得新增 Knowledge Item、不得新增 Graph edge、不得发起新的 source discovery。

如果教学中发现必须依赖新事实：

```text
CURRICULUM_KNOWLEDGE_GAP_DISCOVERED
STOP_AND_REPORT
```

## 14. 上游零修改

```text
Source / Evidence / Knowledge / Normalization / Production Graph / Frozen Graph Contract
Curriculum Readiness / Gate 4.1 Skeleton / Gate 4.2 Blueprint
→ 全部 0 mutation
```

只允许新增：Lesson Contract（policy / schema / validator / tests）、Pilot Lesson artifacts 与 Pilot Reviews。

## 15. 机器验证与人工审核的分工

`validate_lesson.py` 负责结构级检查（身份与 Blueprint 一致性、引用子集关系、Graph ref 真实性、Practice / Check 非空、scope 不能更宽、Pack 内硬顺序）。

Validator **不判断**教学内容是否真实、易懂或教学有效。以下由 Human Review 负责：Knowledge Grounding、Scope Fidelity、Model/Product Separation、Version/UI Boundary、Unsupported Claim、Pedagogical Example Labels、Practice Grounding、Completion Check Alignment、Lesson Body Leakage。
