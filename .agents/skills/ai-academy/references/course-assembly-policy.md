# Course Assembly Policy — Gate 4.4B2

本政策定义 **Canonical Course Package** 的组装合同。组装层位于 Lesson 之下，**不修改任何上游层**。

```text
Track → Module → Lesson Blueprint → Lesson → Course Package
```

## 1. Canonical Course Package

正式课程包目录：

```text
academy-data/jimeng/course/jimeng-creator-academy-v1/
├── course-manifest.json
├── course-outline.md
├── lessons/    24 × .json + 24 × .md
└── reviews/    组装评审
```

该目录是**完整课程的唯一发布边界**。课程包**不得**通过引用历史位置（`curriculum/pilot-lessons/`、`curriculum/role-expansion/`、临时目录、探针文件）来拼接——引用历史路径即组装失败。

非课程产物（环境探针、权限恢复记录、诊断脚本、评审笔记）**不属于**课程包内容，不得进入 manifest，也不计入课程产物统计。

## 2. Manifest Responsibilities

`course-manifest.json` 是课程包的唯一机器可读清单，负责声明：

- 身份（`course_id` / `curriculum_id` / `blueprint_id` / `version` / `status` / `scope`）；
- 结构（`module_order` / `lesson_order_by_module`）；
- 成员与文件身份（`lesson_files`）；
- 汇总（`coverage_summary` / `sequence_summary` / `grounding_summary` / `role_coverage_summary`）；
- 组装元数据（`assembly_metadata`）。

`status` 终点值为 `assembled_v1`。Manifest **不重述** Lesson 教学内容，只引用已存在且已校验的 canonical 文件。

## 3. Module / Lesson Ordering

- `module_order` 必须与 Curriculum Skeleton 的 `module_order` **完全一致**；
- `lesson_order_by_module[module]` 必须与 Lesson Blueprint 的 `lesson_order` **完全一致**。

**不得**为了课程大纲好看而重排。组装是**只读**行为：它记录顺序，不生产顺序。

## 4. Lesson Membership

- manifest 的 lesson ID 集合必须与 Blueprint 的 lesson ID 集合 **exact set equality**；
- 不允许用「数量相等」代替集合相等；
- 每课恰好一个 canonical pair（一个 `.json` + 一个 `.md`）。

## 5. Canonical File Identity

`lesson_files` 的每一项只允许：

```text
lesson_id, json_path, markdown_path, module_id, role
```

并须满足：文件存在；JSON 内的 `lesson_id` / `module_id` / `lesson_role` 与 manifest 一致；JSON 的 `status = full_course`；该 Lesson 通过 `validate_lesson.py`。

## 6. Completeness

```text
Module:  curriculum.module_order  ↔ manifest.module_order      缺/多/重复 = 0
Lesson:  blueprint lesson IDs     ↔ manifest lesson IDs        缺/多/重复 = 0
Files:   每课 JSON 与 Markdown 各 1                             缺失 = 0
```

## 7. Grounding Preservation

组装**不改变**任何 grounding：`knowledge_refs`、`graph_support_refs`、teaching point 的引用、`scope`、`learner_outcomes` 均来自已校验的 canonical Lesson。

组装层**禁止**：新增引用、删除引用、改写 scope、增删 outcome。

## 8. Sequence Preservation

- Module 级硬顺序维持 Gate 4.1 的结论：`GRAPH_CONSTRAINED = 0`；
- Lesson 级硬顺序由 production graph 的 `PREREQUISITE_OF` 与 `PROCEDURE_PRECEDES` 决定，**仅当两端分属同一 Module 的不同 Lesson 时**成立；
- 组装**不得**新增、删除或反转硬顺序。

## 9. Scope Preservation

课程包的总 scope 必须由各 Lesson 的 scope 收敛而来，**不得**比其中任何一课的 scope 更宽。禁止把局部验证范围（特定客户端 / 时点 / 账号）泛化成通用声明。

## 10. Role Coverage

课程包中各 Lesson 的 `lesson_role` 集合必须与 Blueprint 的 role 集合 **exact set equality**：

```text
Missing Role Set = ∅    Untested Blueprint Role Count = 0
```

## 11. Upstream Immutability

组装**不得**修改：

```text
Source / Evidence / Knowledge / Normalization / Production Graph / Frozen Graph Contract
Curriculum Readiness / Curriculum Skeleton / Lesson Blueprint
任何 canonical Lesson 的 JSON 或 Markdown 内容
```

Canonical Lesson 的不可变性用**内容指纹**证明（pre/post 哈希比较），**不得**用文件修改时间作为主要证据。

## 12. Assembly-only Boundary

本层**只**生产：组装合同（policy / schema / validator / fixtures）、`course-manifest.json`、`course-outline.md`、组装评审。

本层**不**生产：Lesson 内容、Knowledge、Graph、Assessment、Quiz、Homework、Rubric、Tutor Engine、Student State、RAG、Vector DB。

如果组装暴露 Requirement 是 Lesson 内容错误 → `LESSON_REVISION_REQUIRED` + `GATE_4_4: BLOCKED`，**不得**静默改 Lesson。
如果合同无法表达当前课程 → `COURSE_ASSEMBLY_CONTRACT_REVISION_REQUIRED`，**不得**改 Curriculum 或 Lesson 去迎合 validator。

## 13. Final Course Status

课程包状态只允许：

```text
assembled_v1      完整组装并通过组装校验
```

组装层**不**声明 Assessment / Tutor / Student State 就绪；它只声明**课程内容与结构**已完整、已校验、可交付。
