# Knowledge Policy — Gate 2.0

## Evidence 与 Knowledge

Evidence Unit 表示来源具体支持的证据；Knowledge Item 是基于这些证据、可安全进入知识体系的一个可教学原子知识。不得将整篇来源直接改名为一个 Item。

## Atomicity 与 Teachable

每个 Item 原则上只表达一个核心概念、能力、明确操作、限制、政策或版本背景。可以独立学习、判断和引用的问题必须拆开；不为减少数量合并整页内容。

statement 回答知识是什么，采用事实性、精确且范围明确的语言，不写“你可以轻松……”等教学或宣传话术。learner_outcome 回答学习后能做什么，使用识别、解释、区分、选择、描述、执行等可观察动作，避免仅写了解、熟悉、掌握。学习结果不得超出证据，例如模型能力简介只能支持识别能力，不能承诺完成实操。

## Provenance

每个 Item 至少引用一个存在且 status=accepted 的 source_id；candidate、stale、deprecated、rejected 均不能作为当前入库依据。同一 Item 内不得重复 source_id。

evidence_refs 的 support_note 说明该证据单元的哪个已审核片段支持 statement 的哪部分，不能只复述标题。来源链接、片段范围和来源版本由 Source Registry 追溯；Knowledge Registry 不复制整页正文。

## Scope Preservation

scope 明示 Product、Model、API 或 Observed 层及适用对象；version_scope 保留证据版本。模型能力不等于产品已部署，API 参数不等于网页参数，产品 UI 不等于模型完整技术能力。不同层的相似能力分别记录，不因文字相似而合并。

## Epistemic Status

通用合同允许 DOCUMENTED、OBSERVED、INFERRED，禁止 UNVERIFIED。DOCUMENTED 至少有一个 accepted / DOCUMENTED 来源；OBSERVED 至少有一个 accepted / OBSERVED 来源。

INFERRED 必须在 limitations 或 support_note 中写明推理依据、适用条件和不能推出的结论。采用显式标记 INFERENCE_BOUNDARY: 后接非空说明，便于最小 Validator 检查。标记及文字存在不代表推理合理，实质边界仍需人工/Agent 审核。

本次 Jimeng Pilot 只创建 DOCUMENTED，全部 status=draft。draft 表示仍待知识实体验收；validated 必须另经内容、原子性和范围审核，不能由脚本 PASS 自动升级。deprecated 用于保留已不再适用的知识实体；不豁免本 Validator 的引用检查。

## No Hidden Completion

证据只支持部分结论时，只记录该部分。不根据常识、模型记忆、类似平台、API或新旧版本推演补全；无法确认的部分写入 limitations 和报告，不塞入 statement。

原始页面本轮无法读取时，将相关来源入库标记为 INGESTION_BLOCKED 并退回 Source Engine，不使用搜索摘要、页面标题或历史记忆代替，不寻找替代来源。独立可读取且已 accepted 的证据可继续处理，报告必须标明未完成的试点边界。

## Marketing Language

最好、电影级、革命性、专业级、领先、惊艳、高质量等宣传词不转成客观能力结论。只保留正文明确支持、可辨认的能力；必要宣传描述只能作为明确归属于发布方的 attribution，不能作效果保证。官方能力声明不等于独立实验结果。

## Readiness Boundary

遵守 [Source Readiness Policy](source-readiness-policy.md) 和当前 Track 的 readiness-assessment.md。BLOCKED / DEFER 不入库，LIMITED_INGESTION 只取明示许可部分。scope、version_scope 与 limitations 一并限定 statement，不能利用模型层许可绕过产品层限制。

## 字段与 ID

Registry 根对象只含 items 数组，遵循 [Knowledge Registry Schema](../assets/knowledge-registry.schema.json)。主要文本及 support_note 必须非空白。limitations 必须存在，确无额外限制时填写 none identified within current evidence scope，不使用 null。

knowledge_id 稳定、可读、标识知识实体。Jimeng 使用 JIM-K-0001 等编号，编号不表示章节或教学顺序。本 Gate 不添加 prerequisite、depends_on、parent、child、graph、learning_order 字段，不建立课程结构。

## 验证与人工审核

[Validator](../scripts/validate_knowledge_registry.py) 仅使用标准库，检查结构、唯一性、来源存在性及 accepted 状态、信息类型对应与推理边界标记。先校验 Knowledge 结构，再复用既有 Source Validator 检查输入来源表，之后进行引用与认知状态检查。

脚本不联网，不判断自然语言是否被正文支持，也不自动判断原子性、跨层外推、Readiness、营销语言或学习结果质量。这些检查须记录在 ingestion report。结构通过不等于内容通过；本 Gate 不进入图谱、前置关系、课程、测验或学习状态系统。

## Addendum — Enumerated Policy Atomicity

Added after Gate 2.3-R1。本增补节不重写 Gate 2.0 的既有设计，只补充枚举型 POLICY 条款的原子性判定规则；与上文冲突时，以本增补节为准处理枚举型条款。

### 适用范围

仅适用于「一条款 + 枚举子项」形态的 POLICY 证据（典型为协议或规则中以（1）（2）（3）……列举的情形）。

### 允许条款级 POLICY Item 的条件

如果一个条款同时满足以下四点：

1. 只有一个主要规范动作或模态（例如「不得」「应当」「可以」）；
2. 枚举子项共享同一个 actor、action、modality 与 condition；
3. 子项主要是该规范下的类别、示例或对象集合；
4. 子项不存在独立例外、独立处罚条件或独立适用主体；

则允许只建立一个**条款级 POLICY Item**，不要求为每个子项分别建立 Knowledge Item。

### 必须拆分子项的条件

只有当某个子项满足以下任一条件时，才需要为它单独拆分：

- 改变义务、禁止或权利的性质；
- 带有该条款其它子项不具备的独立条件；
- 带有独立例外；
- 带有独立的处罚或后果；
- 可以独立发生版本变化或独立产生冲突。

### 记录要求

采用条款级 POLICY Item 时：

- statement 只表达该条款的规范与对象类别，不逐项复述子项；
- limitations 必须注明「本条不复述子项，具体子项以材料原文为准」，并说明该条不解释各项的判定标准；
- 不得因为子项模板同构而把不同条款判为重复；规范对象不同（例如违法违规内容、不良内容、欺骗性与高危险性内容）属于不同 POLICY 命题。

### 与 Normalization 的关系

本增补节与 [Knowledge Normalization Policy](knowledge-normalization-policy.md) 配合使用：子项共享同一 actor/action/modality/condition 时，条款级 Item 之间不构成 EXACT_DUPLICATE；判定关系时仍须比较 scope、version_scope、knowledge_type 与 statement 的规范对象，而不是句式的相似度。

本增补节不授权把整份协议压成一条 POLICY，也不授权把带有独立条件的子项合并进条款级 Item。
