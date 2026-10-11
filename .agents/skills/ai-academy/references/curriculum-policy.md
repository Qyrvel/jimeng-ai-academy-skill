# Curriculum Policy — Gate 4.1

本政策定义 AI Academy 的 **Curriculum Engine** 合同。它建立在既有三个引擎之上，且**不修改它们**。

```text
Source Engine        → 事实证据
Knowledge Engine     → 知识命题
Knowledge Graph      → 知识结构 / dependency / scope / relation
Curriculum Engine    → 为学习者组织「教什么、按什么顺序、达到什么能力」
```

进入本政策的前提是 Curriculum Readiness：`blocking_gaps = []`、`track_verdict = READY_FOR_CURRICULUM_DESIGN`、全部 FOUNDATIONAL / CORE 域为 `READY`。

## 1. Curriculum 的职责

Curriculum **负责**：

- Track goal → 学习路径；
- Ready domains → Module；
- Knowledge Items → 教学覆盖；
- Graph dependencies → **硬顺序约束**；
- Scope / limitations → 教学边界；
- 学习结果 → 可观察能力。

Curriculum **不负责创造事实**。任何 Module 的知识依据必须来自已存在且已 READY 的 Knowledge Item；不得在课程层补造、扩写或"顺手修正"上游命题。

## 2. Curriculum 的最小层级

Gate 4.1 只使用两级：

```text
Track
→ Module
```

**不创建 Lesson Entity**。Lesson、练习、检查、测验、评分、Tutor 行为、Student State、学习者长期记忆、RAG 与 Vector DB 全部属于后续 Gate，本阶段禁止。

## 3. Module 的定义

Module 必须同时满足：

| 要求 | 含义 |
| --- | --- |
| 有清晰 purpose | 一句话说明该 Module 让学习者获得什么 |
| 支持一个或多个 Ready Domain competency | `target_domain_ids` 必须指向真实存在且 READY 的域 |
| 有明确 observable learner outcome | 用可观察动词描述（完成 / 识别 / 选择 / 输入 / 生成 / 检查 / 修改 / 区分 / 解释 / 遵守） |
| 引用真实 Knowledge | `knowledge_refs` 至少 1 项，且 ID 必须存在于 Knowledge Registry |
| 保留 scope | 继承 Knowledge / Evidence 的已知 scope 与 limitations |
| 不跨层偷换 | Model 能力不得教成 Product 可用性；不把某客户端 UI 写成永久通用 UI |
| 在课程中有合理位置 | `order_basis` + `order_rationale` 必填且真实 |
| 不只是「某页面资料合集」 | 必须有教学目的与能力目标 |

不得按 Domain 一对一机械建 Module；不得为凑数量拆分或合并。目标区间 5～10 个 Module，最终由真实 competency 聚类决定。

## 4. 顺序合同：Graph Dependency ≠ Curriculum Order

Curriculum 可以决定教学顺序，但**顺序类型必须显式标注**：

| order_basis | 含义 | 要求 |
| --- | --- | --- |
| `GRAPH_CONSTRAINED` | 顺序由真实 Graph knowledge dependency 决定 | `order_rationale` 必须引用对应 Graph edge；`graph_support_refs` 至少 1 项 |
| `PEDAGOGICAL` | Graph 无 dependency，但为了零基础教学选择先后 | `order_rationale` 必须含 `PEDAGOGICAL_RATIONALE:` 并说明为何更易学；**不得声称是知识 prerequisite** |
| `INDEPENDENT` | 两个 Module 无必要顺序 | 必须说明可交换，当前顺序只是课程组织选择 |

**硬规则**：课程不得因为教学便利而把 `A PREREQUISITE_OF B` 回写 Graph。Graph 是 FROZEN_V1，Curriculum 只读取、不写入。

只有 `PREREQUISITE_OF` 与 `PROCEDURE_PRECEDES` 能构成顺序约束；`CONSTRAINS` 是使用边界、`STEP_OF` 是层级归属、`VERSION_*` 与 `SCOPE_PARALLEL_TO` 是范围关系，**都不是顺序约束**。

## 5. Scope Safety

每个 Module 必须继承并保留已知 scope，例如：

```text
Jimeng Product Layer
ByteDance Seed Model Layer
Jimeng Web
Seedance 2.5
Seedream 5.0 Pro
selected platform usage rules
current verified UI scope
```

禁止：

- 把 **Model capability** 教成 **Jimeng product availability**；
- 把**某次观察到的 Web UI** 写成**所有客户端永久通用 UI**；
- 把**建议性数值**（如像素建议、生成张数、耗时表述）写成强制规格或承诺；
- 把**用户提出的修改要求**写成产品保证；
- 把**未单独验证**写成**不支持**。

## 6. Dynamic / Optional 处理

Readiness 中 decision 为 `DEFER_DYNAMIC` / `DEFER_OPTIONAL` 的域：

- 不得为了课程「看起来完整」升级为必修核心；
- 不得出现在任何 Module 的 `target_domain_ids` 中；
- 只允许作为 `deferred_domains` 条目，并写明 disposition；
- 不得成为当前 Track 的毕业必备 outcome。

## 7. 字段合同

**根字段只允许**（`curriculum.schema.json` 为唯一事实源）：

```text
curriculum_id, track, version, status, track_goal, entry_profile, exit_profile,
scope, module_order, modules, deferred_domains, coverage_summary
```

`status` 在 Gate 4.1 只允许 `skeleton`。

**Module 字段只允许**：

```text
module_id, title, purpose, target_domain_ids, learner_outcomes, knowledge_refs,
graph_support_refs, scope, order_basis, order_rationale, limitations, status
```

`module_id` 格式为 `JCA-M##`，稳定且顺序唯一。

`graph_support_refs` 只引用真实 production graph 中的 `edge_id`；不依赖任何边时允许 `[]`，**不得为了让字段非空制造关系**。

## 8. 机器验证与人工审核的分工

`validate_curriculum.py` 负责**结构级**检查：schema 形状、ID 存在性、域覆盖、顺序枚举与标记、outcome 与 scope 非空、graph ref 真实性、`coverage_summary` 与真实 readiness 的一致性。

Validator **不判断**自然语言是否「教学得好」，也不判断 module 聚类是否最优。以下由 **Human Curriculum Review** 负责：

- Track Goal 忠实度；
- Core Coverage 完整性；
- Knowledge Grounding（是否存在只靠常识的 Module）；
- Scope Safety 与 Version/UI Safety；
- GRAPH_CONSTRAINED 与 PEDAGOGICAL 的区分是否正确；
- Overfragmentation / Overcompression；
- Deferred Leakage；
- Lesson Leakage（本 Gate 不允许出现教学正文）。

**fixture PASS ≠ 课程设计合格**：fixture 只证明 Validator 的机械规则生效。

## 9. 覆盖判定

Coverage Matrix 的 Coverage Verdict 只允许：

```text
COVERED
PARTIALLY_MAPPED
UNMAPPED
```

Gate 4.1 PASS 要求：FOUNDATIONAL / CORE 域的 `UNMAPPED = 0`，且不存在 blocking 的 `PARTIALLY_MAPPED`。

## 10. 上游零修改

Gate 4.1 默认：

```text
Source: 0 mutation
Evidence: 0 mutation
Knowledge: 0 mutation
Normalization: 0 mutation
Graph: 0 mutation
```

只创建 Curriculum Engine 合同与 Curriculum artifacts。如果发现必须修改上游层，输出 `STOP_AND_REPORT` + `UPSTREAM_REVISION_REQUIRED`，不得顺手改。

## 11. 边界声明

Curriculum Contract PASS **不表示**：Lesson 已写完、Tutor Engine Ready、Quiz Ready、Assessment Ready、Student State Ready 或完整 Jimeng 课程已生成。它只表示：Curriculum Contract 稳定，且第一版 Jimeng Creator Academy V1 的模块级骨架可以被现有 Source / Knowledge / Graph 安全支撑。
