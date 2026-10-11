# Knowledge Normalization Policy — Gate 2.1

## 职责与边界

本 Policy 定义 Knowledge Normalization 与 Deduplication 的判断原则。它补充 [Knowledge Policy](knowledge-policy.md)，不替代来源准入、Evidence Unit、Readiness、Materialization、Schema 或任何既有 Validator。

Normalization 的目标是：判断两个或多个既有 Knowledge Item 之间是什么关系，并在不破坏 Provenance、Version Scope 与 Layer 边界的前提下记录该关系。

本 Gate 只做三件事：识别关系、生成 Review、验证 Normalization Contract。

本 Policy 不授权：修改 statement、修改 learner_outcome、修改 scope、修改 version_scope、修改 evidence_refs、删除 Item、把 Item 标为 deprecated、合并 Item、新建 Item、建立 prerequisite、graph、learning_order 或 curriculum。

## 不以标题判断重复

标题相似不等于知识相同。标题只用于显示与检索，不能作为重复依据。

比较任意两个 Item 时，必须同时比较以下字段：

- statement
- knowledge_type
- scope
- version_scope
- information_type
- evidence_refs
- limitations

只有这些字段共同表明“表达同一个知识”时，才允许判定重复。任何单一字段相同（包括标题、domain、信息来源 URL 相同）都不构成重复证据。

同一来源被拆成多个 Evidence Unit 或同一个 Item 引用同一来源，也不自动构成重复：证据相同而知识不同，仍是不同知识实体。

## Layer Preservation

以下层各自独立，即使 statement 表面相似，也默认不得合并：

- Jimeng Product Layer
- ByteDance Seed Model Layer
- Volcano / API Layer
- Observed / Community Layer

典型例子：

- “模型支持参考视频”（Model Layer）
- “即梦产品页提供参考视频能力”（Product Layer）

二者属于不同知识实体：模型具备能力与产品公开提供该能力，不是同一个知识。

因此跨层相似项一律标 SCOPE_PARALLEL 并 KEEP_SEPARATE。只有内容本身完全不同（仅是措辞或主题偶然接近）时才标 DISTINCT。绝对不得因为“都提到参考视频”“都提到编辑”就把跨层两项判为 EXACT_DUPLICATE。

API 层与 Observed/Community 层同理。API 参数不等于网页参数，实测观察不等于官方描述。

## Version Preservation

不同明确版本默认保留为不同 Item。例如 Seedance 2.0 与 Seedance 2.5 不得因为主题相同而合并。Seedream 5.0 Pro 与 Seedream 5.0 Lite、4.5、4.0 是不同分支，不得互相覆盖。

如果一个 Item 的 version_scope 为 unknown，另一个为明确版本，不得自动视为相同；unknown 不匹配任何明确版本，也不因“可能相同”而合并。

主题相近但版本不同时标 VERSION_VARIANT 并 KEEP_SEPARATE。

## Provenance Preservation

即使两个 Item 最终被认定为重复，也不得丢失任何 accepted Evidence。

未来如真正执行合并，必须先保证：被合并项引用的全部 accepted source_id 及其 support_note 的信息被完整保留，来源范围与版本不被压缩成更宽或更窄的表述。

本 Gate 的 Pilot 暂不实际合并，因此 Provenance 的完整保留要求记录为条件，而不是本轮执行动作。任何 Item 的 evidence_refs 在本轮都不得被修改。

## 关系类型

两个或多个 Knowledge Item 之间只能使用以下关系，不使用其他分类：

| Relation | 含义 |
| --- | --- |
| DISTINCT | 语义不同，应保持独立。 |
| EXACT_DUPLICATE | 在相同 scope、version_scope、knowledge_type 下，核心 statement 实际表达同一个知识。 |
| PARTIAL_OVERLAP | 存在共享信息，但至少一方还有独立知识，不能直接合并。 |
| VERSION_VARIANT | 主题相近，但版本不同。 |
| SCOPE_PARALLEL | 主题相近，但属于不同 Layer / Scope，典型为 Product vs Model。 |
| CONFLICT_CANDIDATE | 两个 Item 在相同适用范围内存在可能不一致的陈述，仅表示“需要进一步审查”。 |

判定顺序建议：先比较 scope / Layer，再比较 version_scope，再比较 knowledge_type，最后才比较 statement 语义。层或版本一旦不同，关系已在 SCOPE_PARALLEL 或 VERSION_VARIANT 处确定，不再向下判为重复。

## 决策类型

每个 Review 只能给出以下决策之一：

| Decision | 含义 |
| --- | --- |
| KEEP_SEPARATE | 保持两个 Item 独立，不做任何修改。 |
| MERGE_CANDIDATE | 记录为将来可能合并的候选，本轮不执行合并。 |
| NEEDS_REVIEW | 需要回到 Evidence / Source 层进一步审查，本轮不下结论。 |

约束：

- EXACT_DUPLICATE 只能给 MERGE_CANDIDATE 或 NEEDS_REVIEW。本轮不得自动执行 merge。
- SCOPE_PARALLEL 必须给 KEEP_SEPARATE。
- VERSION_VARIANT 必须给 KEEP_SEPARATE。
- CONFLICT_CANDIDATE 必须给 NEEDS_REVIEW，不得自动判定谁正确，也不得静默消解冲突。
- DISTINCT 应为 KEEP_SEPARATE；给 MERGE_CANDIDATE 视为判断矛盾，需人工复核。
- PARTIAL_OVERLAP 通常为 KEEP_SEPARATE；只有确实存在设计问题时才给 NEEDS_REVIEW。

## 冲突判定边界

只有在相同 scope、相同或可比较 version_scope、相同语义主题下出现不兼容陈述时，才可标 CONFLICT_CANDIDATE。

不得把 Product 与 Model 的表面差异、不同版本之间的差异、不同 Evidence Unit 的范围差异错误当成冲突。冲突候选不是错误结论，而是待审查标记；发现冲突候选时必须回到 Evidence 与 Source 层，不在本 Gate 内解决。

## normalized_label 的定位

normalized_label 只用于帮助识别“这些 Item 大致属于哪个知识主题”，例如 参考视频、局部编辑、多模态参考。

它不是 Knowledge Graph 节点、不是 ontology、不是 prerequisite、不是 curriculum topic、不是教学顺序。不得在其上附加层级、编号顺序或依赖关系，也不得为了统一标签而改写任何 Item。

## 方法与工具限制

Item 数量较小时允许人工 / Agent 全量语义比较。本 Gate 不引入 embeddings、vector search、模糊匹配包、聚类框架或任何第三方库；Validator 只使用 Python 标准库。

Validator 只检查合同中的机械规则：结构、字段、ID 存在性、关系与决策合法性及其组合约束。Validator 不判断自然语言语义是否真的重复，该判断由人工 / Agent 审核承担，并记录在 normalization report。

## 与 Validator 的关系

Normalization Review 遵循 [Normalization Review Schema](../assets/normalization-review.schema.json)，并由 [Validator](../scripts/validate_normalization_review.py) 离线检查。

PASS 只表示 Review 文件符合合同并正确引用现有 Item；不证明关系判定在语义上成立。结构通过不等于内容通过。

本 Gate 不进入 Gate 2.2、Gate 3、图谱、课程或学习状态系统。
