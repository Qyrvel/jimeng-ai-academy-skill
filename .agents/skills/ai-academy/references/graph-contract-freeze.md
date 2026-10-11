# Graph Contract Freeze — Baseline v1

Baseline Version: 1.0
Freeze Gate: Gate 3.3
Baseline: Graph Contract v1.0
Status: FROZEN_BASELINE

## 冻结范围

通用 AI Academy 合同，依据 [Knowledge Graph Policy](knowledge-graph-policy.md) 及其增补。R2 替代早期将课程泄漏交给 Integrity 的实现分工；不改变关系语义。

根对象仅 graph_id、scope、nodes、edges，全部必填；前二者非空白字符串，后二者数组，无 minItems。Node 仅 knowledge_id。Edge 仅 edge_id、from、relation、to、epistemic_status、rationale、limitations，全部必填、非空白字符串，枚举依合同；对象禁止额外字段。Graph 不复制完整 Knowledge Item。

Graph does not create Knowledge. 禁止 hidden concept、implicit user/platform/action、enum child、synthetic bridge node；须先由 Knowledge Engine 建立正式 Item。缺节点记 MISSING_NODE_CANDIDATE，不补隐式节点。

## Relation Semantic Snapshot

| Relation | 含义与方向 | 非含义 | 端点类型 | DAG | 机器检查 / 语义审核 |
| --- | --- | --- | --- | --- | --- |
| PREREQUISITE_OF | 前置知识 → 依赖其理解或执行的知识 | 教学偏好 | 无额外限制 | 独立 DAG | 环与共享规则 / 真实知识依赖；KNOWLEDGE_DEPENDENCY: 不必填且不是证明 |
| PROCEDURE_PRECEDES | 真实流程前一步 → 后一步 | 教学顺序 | PROCEDURE → PROCEDURE | 独立 DAG | 类型、环、已知父集合不相交需 CROSS_WORKFLOW_ORDER_JUSTIFICATION: / 真实顺序及跨流程依据 |
| CONSTRAINS | 规则 → 被约束的行为、输入、输出或使用边界 | 处理后果、任意广播 | from 为 CONSTRAINT 或 POLICY | 否 | from 类型 / 具体直接约束与跨层证据 |
| VERSION_CONTEXT_FOR | 版本背景 → 适用知识 | 版本替代 | from 为 VERSION_CONTEXT | 否 | from 类型 / 版本背景适用性 |
| SCOPE_PARALLEL_TO | 跨 Layer / Scope 平行；对称，仅存一个方向 | 合并、模型能力推出产品可用 | 无额外限制 | 否 | 禁双向，Normalization SCOPE_PARALLEL 或 NORMALIZATION_JUSTIFICATION: / 真实范围平行 |
| VERSION_VARIANT_OF | 同主题不同版本；对称，仅存一个方向 | 替代、下线、优劣 | 无额外限制 | 否 | 禁双向，Normalization VERSION_VARIANT 或 VERSION_JUSTIFICATION: / 主题与版本匹配 |
| STEP_OF | 明确步骤 → 所属 workflow | 通用 PART_OF、先后、课程层级 | PROCEDURE → PROCEDURE | 独立 DAG | 类型、环、禁双向 / 明确步骤归属及方向 |
| ENFORCEMENT_CONTEXT_FOR | 处理措施 → 被违反或可能违反的规则 | 因果、自动处罚、法律/合规结论、前置 | POLICY → POLICY | 否 | 类型、禁成对反向、组引用及 pair 规则 / 单边真实方向、集合成员和处理条件 |

## 共享 epistemic / integrity 规则

所有关系叠加以下规则；标记存在不证明语义成立。

- DOCUMENTED：证据明确支持关系本身，不能因两节点 DOCUMENTED 就认定边成立。INFERRED：rationale 给推理依据，limitations 含 INFERENCE_BOUNDARY: 并解释推论边界；机器只检查格式。
- Node ID 在 Registry 存在且在图中唯一；边端点须在 nodes 声明，edge_id 唯一，无 self-edge。现有实现没有对不同 edge_id 的相同 (from, relation, to) 做独立去重；不得声称已有该 guard，冗余须审核。对称双向重复与 STEP_OF / Enforcement 成对反向另行拒绝。
- Normalization CONFLICT_CANDIDATE 无向 pair 禁止入图。DISTINCT / PARTIAL_OVERLAP / EXACT_DUPLICATE 不自动建边。
- 同一有向 pair 的 PREREQUISITE_OF 或 STEP_OF 与 VERSION_VARIANT_OF 或 SCOPE_PARALLEL_TO 组合，要求该 pair 任一 rationale 有 PAIR_RELATION_JUSTIFICATION:；理由充分性由审核判断。
- Enforcement 与 VERSION_VARIANT_OF 或 SCOPE_PARALLEL_TO 在同一无向 pair 硬拒绝，没有 justification 例外。
- 三个 DAG 分别检查，不检查混合关系联合环。环报告 PREREQUISITE_CYCLE_REVIEW / PROCEDURE_ORDER_CYCLE_REVIEW / STEP_OF_CYCLE_REVIEW，不自动删边。
- PROCEDURE_PRECEDES 两端已有 STEP_OF 父集合且不相交，须 CROSS_WORKFLOW_ORDER_JUSTIFICATION:；缺父信息不证明同流程。
- A→B→C 加 A→C 的 prerequisite 产生 POTENTIAL_TRANSITIVE_REDUNDANCY warning，不 hard fail；审核 KEEP_DIRECT / REMOVE_REDUNDANT / NEEDS_REVIEW。
- Enforcement 同一 from fan-out >=3，机器要求每条 rationale 有 DOCUMENTED_GROUP_REFERENCE:。语义审核对所有多边（包括 2 条）要求证据组引用、可枚举成员和推论限制；禁止全平台广播，无 fan-in 上限。
- DOCUMENTED Enforcement 要求 DOCUMENTED_GROUP_REFERENCE: 或 DIRECT_REFERENCE:；证据实际为组引用，即使只选一条也用组标记。fan-out 数量不决定 epistemic 状态。

## Review 与生产验收

Review 根仅 reviews。每条仅 edge_id、status、review_reason、directness、curriculum_leakage；覆盖所有图边且无重复或未知边。reason 非空白，leakage 为 boolean。status 为 KEEP / MODIFY / REMOVE / NEEDS_REVIEW；directness 为 DIRECT / TRANSITIVE / NOT_APPLICABLE。TRANSITIVE + KEEP 要求 reason 有 DIRECT_DEPENDENCY_JUSTIFICATION:，充分性仍需审核。

默认 validate_edge_review.py <review> <graph> 检查格式、覆盖和上述标记，允许中间审核状态；默认 PASS 不是生产接受。

Production / accepted Graph 必须 Graph PASS、Integrity PASS、Review default PASS、Review --final PASS、Evidence-backed Semantic Review PASS：

```text
python .agents/skills/ai-academy/scripts/validate_edge_review.py <review> <graph> --final
```

每条保留边 KEEP、curriculum_leakage=false、NEEDS_REVIEW=0。Enforcement 还须审核为 DIRECT。--final 只检查已记录状态，不推导自然语言真值。不确定边 OMIT；REMOVE / MODIFY / NEEDS_REVIEW 不能随最终图通过。修改后重新审核，历史审核独立保存。

## Machine / Semantic Boundary

Machine Validation ≠ Semantic Truth。Evidence-backed Agent/Human Review 是正式合同组成部分。Marker presence ≠ semantic truth；仅检查正式 marker / format token，不得把 KNOWLEDGE_DEPENDENCY: 当证明。

生产 Validator 禁止中文/英文语义关键词、正则语义黑名单、Knowledge ID / Source ID special case、platform-name、Jimeng-only、Seedance-only、P14-only 分支判断自然语言关系。

Graph 是知识结构，不因课程应先教 A 建 prerequisite。未来 Curriculum 根据 Graph + Teaching Policy + Learner State 决定教学顺序；本 Gate 不进入 Curriculum。

## 非冻结范围与版本

Contract Frozen ≠ Graph Data Frozen。不冻结 Knowledge Registry、Source Registry、新 Knowledge Items、nodes/edges 数量、新领域 Graph、Jimeng coverage、future evidence、future versions。Curriculum 不在冻结范围。

变更遵循 [Expansion Policy](graph-expansion-policy.md)，允许受控 v1.1 additive extension，不引入复杂发布系统。[Manifest](../assets/graph-contract-baseline.json) 中 Pilot 路径相对项目根，Validator 文件名相对 scripts。Baseline checker 检查枚举和回归，不保证识别任意语义漂移；代码、Policy 与证据审核仍然必须执行。
