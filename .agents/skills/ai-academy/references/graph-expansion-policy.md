# Graph Expansion Policy — Baseline v1

治理 [Graph Contract v1.0](graph-contract-freeze.md) 后续扩展；Freeze 是版本基线，不是永久禁止变化。

## Type A — Data Expansion

只新增 nodes、edges、新 domain graph，遵循基线，不改 Schema / Relation Contract。节点引用 Knowledge Engine 已正式建立且有证据的 Item；Graph 不创造 Knowledge，不补 hidden concept、implicit user/platform/action、enum child、synthetic bridge node。缺节点退回 Knowledge Engine，不确定边 OMIT。

必须 Graph PASS、Integrity PASS、Review default PASS、Review --final PASS、Evidence-backed Semantic Review PASS。生产边 KEEP、curriculum_leakage=false、NEEDS_REVIEW=0；Enforcement 须 DIRECT、正确方向和组成员证据。图允许不完整，不允许伪精确。

## Type B — Contract Expansion

仅当现有八种关系无法准确表达真实、必要、证据支持的结构关系（EXPRESSION_GAP），才提出 RELATION_GAP_CANDIDATE。图不漂亮、减少边、泛泛相关、AI 感觉、课程顺序或名称不完美均不是 gap。

固定流程不得跳步：

1. RELATION_GAP_CANDIDATE：记录必要关系与范围。
2. Evidence Re-check：证据支持关系本身。
3. Existing Relation Fit Test：逐一检查 PREREQUISITE_OF、PROCEDURE_PRECEDES、CONSTRAINS、VERSION_CONTEXT_FOR、SCOPE_PARALLEL_TO、VERSION_VARIANT_OF、STEP_OF、ENFORCEMENT_CONTEXT_FOR，记录不适用原因。
4. Generality Test：通用知识结构；JIMENG_SPECIAL_*、SEEDANCE_ONLY_*、P14_*、K0035_* 等特例判 RELATION_TOO_SPECIFIC，拒绝。
5. Minimal Relation Definition：含义、非含义、方向、端点、认知与完整性规则。
6. Additive Schema Proposal：最小兼容提案。
7. Machine/Semantic Boundary Design：明确可靠机械检查和证据审核。
8. Positive Tests。
9. Negative Tests：分别记录机械和语义预期。
10. Bounded Real-world Pilot。
11. Edge Review：含 default / --final。
12. Integrity Review。
13. Regression：两个基线 Pilot、Curriculum Leakage、Enforcement、Core Integrity 和 baseline checker。
14. Generalization Review：通用性，无语言/平台/ID 特例，无课程混入。
15. Contract Version Decision：类别、兼容性、变更文件、审核结论和版本；未通过不能合入基线。

## 变更分类

- ADDITIVE_CHANGE：新增 relation 或兼容 guard，不改变既有合法图语义与合法性；须 bounded pilot、full regression、baseline version update（例如 1.0 → 1.1），同步 Policy / Schema / Validator / Tests / Manifest。
- CLARIFICATION：只澄清措辞、例子或机器/语义边界，不改变合法性或 meaning；记录变更。
- BREAKING_CHANGE：删除 relation、改 meaning/direction、改 Node/Edge required fields、原合法变非法或原非法语义变合法。CONTRACT_REVISION_REQUIRED；停止普通 expansion，进入独立 migration / compatibility Gate。新增 guard 若使原合法图非法也属于 breaking。

## Governance

权威顺序：Frozen Contract / Policy > Schema > Validator > Tests > Pilot Data。冲突 STOP_AND_REPORT。禁止 Policy 不变而 Validator 偷改语义、Schema 不变而 Tests 暗定新语义，或实现重新解释 Review 字段。

Python 只验证可机械可靠判断的结构、正式 marker / format。不用 keyword、regex blacklist、Knowledge ID、Source ID、platform 或 language semantics；禁止 marker-as-proof。自然语言关系由 Evidence-backed Semantic Review 判断，这是正式合同组成部分。

默认 Review PASS 不等于最终接受。REMOVE / MODIFY / NEEDS_REVIEW 不能通过 production --final；--final 只检查已记录状态，不证明审核正确。修改边重新审核，历史记录独立保存。Baseline checker 不替代 Policy、代码和证据审查。

## Curriculum 边界

知识依赖不是教学偏好，流程顺序不是教学顺序。未来 Curriculum 根据 Graph + Teaching Policy + Learner State 工作；本政策不启动课程。覆盖率与合同冻结独立；Gate 3.3 只报告 Curriculum Readiness Audit 资格，不自动执行下一 Gate。
