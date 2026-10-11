# Knowledge Normalization Report

## Scope

Gate 2.1 — Knowledge Normalization & Deduplication；核查日期 2026-10-03。

处理范围：`pilot-knowledge-registry.json` 中当前存在的全部 **16 个 Knowledge Item**（JIM-K-0001 ～ JIM-K-0016），无新增、无删除、无修改。其中 ByteDance Seed Model Layer 8 项（JIM-K-0001～0008），Jimeng Product Layer 8 项（JIM-K-0009～0016）。

本轮只读取既有 Item、既有 Materialized 材料与既有 Report，未联网、未读取新 Source、未进行 Source Discovery、未新建 Knowledge Item。未使用 embeddings、vector search、模糊匹配包、聚类框架或任何第三方库；全部 16 项由人工 / Agent 全量语义比较。

方法顺序：先比较 scope / Layer，再比较 version_scope，再比较 knowledge_type，最后比较 statement 语义。层或版本一旦不同，关系即在 SCOPE_PARALLEL 或 VERSION_VARIANT 处确定，不再向下判为重复。

Item 覆盖情况：16 个 Item 全部至少参与一条 Review，无遗漏。共生成 **12 条 Review**（NR-0001 ～ NR-0012），每条 Review 给出 relation 与 decision，并由 `validate_normalization_review.py` 检查合同合法性。

## Relation Summary

| Relation | 数量 | Review |
| --- | --- | --- |
| DISTINCT | 5 | NR-0001、NR-0002、NR-0003、NR-0011、NR-0012 |
| EXACT_DUPLICATE | 0 | none |
| PARTIAL_OVERLAP | 4 | NR-0004、NR-0005、NR-0006、NR-0007 |
| VERSION_VARIANT | 0 | none |
| SCOPE_PARALLEL | 3 | NR-0008、NR-0009、NR-0010 |
| CONFLICT_CANDIDATE | 0 | none |

| Decision | 数量 |
| --- | --- |
| KEEP_SEPARATE | 12 |
| MERGE_CANDIDATE | 0 |
| NEEDS_REVIEW | 0 |

说明：本轮没有任何 EXACT_DUPLICATE，因此 MERGE_CANDIDATE 与 NEEDS_REVIEW 均为 0；12 条 Review 全部为 KEEP_SEPARATE，与「本 Gate 不执行合并」一致。

VERSION_VARIANT 为 0 的原因：当前 Registry 中不存在同层同主题但版本不同的 Item 对。产品层 8 项同为 Seedance 2.5 公开产品页；模型层 8 项中 Seedance 2.5（JIM-K-0001～0003）与 Seedream 5.0 Pro（JIM-K-0004～0008）主题与版本同时不同，属于不同主题而非同主题不同版本，因此按 DISTINCT 处理。若将来 Seedance 2.0 或 Seedream 5.0 Lite 等版本入库，同类比较应转为 VERSION_VARIANT。

## Merge Candidates

**none.**

没有 EXACT_DUPLICATE。以下是被重点审查、最终确认「不可合并」的同层同版本项及其理由：

| Review | Item 对 | 同层同版本？ | 为何不是 EXACT_DUPLICATE |
| --- | --- | --- | --- |
| NR-0004 | JIM-K-0009 ⊃ JIM-K-0011 | 是 | 整体流程（含第二、三步与产物）与第二步输入细节：一为整体一为局部，属部分重叠。 |
| NR-0005 | JIM-K-0009 ⊃ JIM-K-0010 | 是 | 整体流程与第一步入口/模型选择：部分重叠。 |
| NR-0006 | JIM-K-0012 / JIM-K-0013 | 是 | 同一句 FAQ 的前半句（文字/图片输入）与后半句（多模态素材组合）：素材类型不同，各自独立。 |
| NR-0007 | JIM-K-0012 / JIM-K-0014 / JIM-K-0015 | 是 | 输入方式、产物特征、参考视频用途三类不同知识，共享上位主题。 |
| NR-0011 | JIM-K-0005 / JIM-K-0006 | 是 | 共享同一说明段，但空间标注与草图引导是可独立识别与引用的两种引导方式。 |
| NR-0012 | JIM-K-0004 / JIM-K-0008 | 是 | 共享同一模型页，但文字密集生成与多语言生成是两种不同能力。 |

上表六组均满足 scope、version_scope、knowledge_type 相同，是最容易误判为重复的组合；逐条比较 statement 后确认各自表达不同知识，因此全部 KEEP_SEPARATE，无一进入 MERGE_CANDIDATE。本 Gate 未执行任何 merge，也未修改任何 Item。

## Scope Parallel Review

以下 Product Layer 与 Model Layer 项表面相似，经审查后保持分离：

| Review | Product Layer | Model Layer | 相似点 | 保持分离的理由 |
| --- | --- | --- | --- | --- |
| NR-0008 | JIM-K-0015 参考视频控制复杂动作 | JIM-K-0002 参考视频的构图信息 | 均涉及参考视频 | 产品页声明该能力可用；模型说明只声明可理解参考信息的类型。产品提供能力与模型具备能力不是同一知识实体。 |
| NR-0009 | JIM-K-0014 带声音视频与音画协同创作 | JIM-K-0001 音视频联合生成 | 均涉及音视频关系 | 产品层功能声明与模型层模态定位分属不同层；模型能力不等于产品已部署该能力。 |
| NR-0010 | JIM-K-0016 局部编辑 | JIM-K-0003 绿幕编辑、JIM-K-0005 空间标注引导、JIM-K-0006 草图引导、JIM-K-0007 图层分离 | 均涉及编辑 | 产品层编辑用途与模型层编辑能力分别记录；产品版本（Seedance 2.5）与模型分支（Seedream 5.0 Pro）也不可互相映射。 |

Scope Parallel 数量：**3 条 Review**，共涉及 **9 个不同 Item**：产品层 3 项（JIM-K-0014、JIM-K-0015、JIM-K-0016），模型层 6 项（JIM-K-0001、JIM-K-0002、JIM-K-0003、JIM-K-0005、JIM-K-0006、JIM-K-0007）。其中 NR-0010 一条 Review 即包含 5 项（1 项产品层 + 4 项模型层）。

其余跨层对照（JIM-K-0009/0010/0011 对 JIM-K-0001）因内容本身完全不同（产品操作流程 vs 模型模态定位）判为 DISTINCT，而非 SCOPE_PARALLEL，见 NR-0001～NR-0003。跨层项中**没有任何一组**被判定为 EXACT_DUPLICATE。

产品 / Model 相似知识没有被误合并：8 个产品层 Item 与 8 个模型层 Item 在本轮审查后仍各自独立，Item 总数保持 16。

## Version Variants

**none.**

当前没有任何同主题不同版本的 Item 对。产品层全部为 Seedance 2.5 公开产品页；模型层中 Seedance 2.5 与 Seedream 5.0 Pro 属不同主题。跨版本合并风险本轮不存在，但 Version Preservation 原则与 VERSION_VARIANT / KEEP_SEPARATE 约束已写入 Policy 并由 Validator 强制执行（VERSION_VARIANT + MERGE_CANDIDATE 会被判 FAIL，见测试项 NR-B-0007）。

## Partial Overlap

| Review | Item | 共享部分 | 各自独立部分 | Decision |
| --- | --- | --- | --- | --- |
| NR-0004 | JIM-K-0009 / JIM-K-0011 | 生成流程中的第二步主题 | K-0009 另有完整三步与可下载产物；K-0011 另有输入类型与提示词四要素 | KEEP_SEPARATE |
| NR-0005 | JIM-K-0009 / JIM-K-0010 | 第一步「打开 AI 视频生成器」 | K-0009 另有第二、三步与产物；K-0010 另有入口与模型选择表述 | KEEP_SEPARATE |
| NR-0006 | JIM-K-0012 / JIM-K-0013 | 同一条 FAQ 答复、同属生成输入主题 | K-0012 为文字/图片基础输入；K-0013 为脚本/视频/音频/风格素材组合 | KEEP_SEPARATE |
| NR-0007 | JIM-K-0012 / JIM-K-0014 / JIM-K-0015 | 同属产品页声明的生成能力 | 分别为输入方式、产物声音特征、参考视频对动作的控制 | KEEP_SEPARATE |

四条均为 KEEP_SEPARATE，无 NEEDS_REVIEW：各项的独立知识都有对应 Evidence 支持，且各自 limitations 已明确边界，不存在需要回退审查的设计问题。

## Conflict Candidates

**none.**

未发现任何 CONFLICT_CANDIDATE。审查依据 §10-E 的三项条件：

1. 相同 scope：仅在设计、同层同版本的项之间检查冲突。跨层项（NR-0008～NR-0010）按 Layer Preservation 排除，不同版本项本轮不存在。
2. 相同或可比较 version_scope：上述同层同版本项 satisfied，但它们的 statement 之间不存在互斥表述（例如 JIM-K-0009 的流程描述与 JIM-K-0011 的第二步描述是包含关系，不是矛盾）。
3. 相同语义主题下的不兼容陈述：未出现。产品页未对模型层能力作反向陈述；模型说明也未对产品可用性作陈述，因此不存在同范围内的不一致。

既有 unresolved C1（P02/P03/P11 新旧界面与灰度）、C2（P05/P08 渠道与时效）、C3（M05/M10、A04、P03/P11 的 Pro/Flash 命名与产品开放映射）继续保留在 Source 与 Readiness 层，本轮未将其当作 Item 间冲突，也未宣布解决。冲突候选没有被静默消解：本轮不存在可消解对象，且 Policy 已规定 CONFLICT_CANDIDATE 必须配 NEEDS_REVIEW，Validator 会拒绝 KEEP_SEPARATE（见测试项 NR-B-0008）。

## Contract Validation

```
python .agents/skills/ai-academy/scripts/validate_knowledge_registry.py academy-data/jimeng/knowledge/pilot-knowledge-registry.json academy-data/jimeng/sources/source-registry.json
PASS（退出码 0）

python .agents/skills/ai-academy/scripts/validate_normalization_review.py academy-data/jimeng/knowledge/normalization-review.json academy-data/jimeng/knowledge/pilot-knowledge-registry.json
PASS（退出码 0）

tests/knowledge-normalization/valid-normalization-review.json   → PASS（退出码 0）
tests/knowledge-normalization/invalid-normalization-review.json → FAIL（退出码 1，12 条预期错误全部命中）
```

Validator 只检查机械规则（结构、字段、ID 存在性、关系与决策合法性及其组合约束），PASS 不证明关系判定在语义上成立；语义结论由本报告的人工 / Agent 审核承担。

## Item 状态变化

无。没有任何 Item 被修改、删除、标 deprecated 或合并；`pilot-knowledge-registry.json` 在本 Gate 中保持只读，Knowledge Item 总数仍为 16。

## Recommendation

NORMALIZATION_CONTRACT_PASS

理由：Knowledge Registry 仍 PASS；Normalization Review PASS；Product 与 Model 相似知识未被误合并（12 条 Review 全部 KEEP_SEPARATE）；不同版本未被误合并（本轮无版本对照，且约束已由 Validator 强制）；本轮无 EXACT_DUPLICATE，因此不存在理由不充分的重复判定；无 CONFLICT_CANDIDATE 被静默消解。

本轮不进入 Gate 2.2 或 Gate 3：未创建 Knowledge Graph、prerequisite、learning_order、curriculum、module、lesson、quiz、student state、RAG 或向量数据库。

## 边界声明

- 本 Gate 只识别关系、生成 Review、验证合同，不执行合并，不修改任何 Knowledge Item 字段。
- 12 条 Review 中 KEEP_SEPARATE 占全部，说明当前 16 项尚未出现真正的重复；这不表示未来新增 Item 后仍无重复，也不表示 Item 的语义内容已经过 validated 验收（全部仍为 draft）。
- normalized_label 仅用于识别知识主题，不是图谱节点、不是 ontology、不是 prerequisite，也不含任何教学顺序。
- 部分重叠与跨层平行关系将来如需处理，必须先满足 Provenance Preservation：被合并项的全部 accepted source_id 与 support_note 的段落信息完整保留。
