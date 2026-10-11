# Pilot Ingestion Report

## Scope

Gate 2.0；核查日期2026-10-03。合同与来源验证器实现完成，Gate 2.0 首轮真实试点仅完成模型层，产品层当轮未完成（下节 Scope 记录该轮事实）。处理Domain：Seedance、Seedream、编辑功能。实际引用accepted来源M09、M10，两者均为DOCUMENTED。产品层已于 Gate 2.0-R1 补测完成，见 Product Layer Pilot Ingestion 与 Cross-Layer Retest。

本轮只读取预先accepted的原始页面，未进行Source Discovery。M09/M10正文可读；P10/P12/P13共用的即梦产品页读取超时，标记INGESTION_BLOCKED，退回Source Engine。未使用其上轮页面内容、搜索摘要或替代来源。M01/M05未用于本轮Item。

来源：[M09](https://seed.bytedance.com/en/seedance2_5)、[M10](https://seed.bytedance.com/en/seedream5_0_pro)；阻塞页面：[P10/P12/P13](https://jimeng.jianying.com/tools/seedance-2-5)。仅取Registry规定的说明段，不使用示例长Prompt、标题或宣传口号独立立项。

遵守现有readiness-assessment：Seedance/Seedream只记录官方模型描述；编辑功能只取明确的模型层用途，保持LIMITED_INGESTION。全部8个Item为DOCUMENTED / draft。没有修改Source Registry、Gate 1政策或Readiness判断；一次读取失败不自动推翻既有来源身份或历史审核。

## Items Created

| knowledge_id | title | knowledge_type | scope | evidence_refs |
| --- | --- | --- | --- | --- |
| JIM-K-0001 | Seedance音视频联合生成 | CAPABILITY | Model；Seedance 2.5；不代表产品部署 | M09 |
| JIM-K-0002 | Seedance参考视频的构图信息 | CAPABILITY | Model；Seedance 2.5；不代表产品部署 | M09 |
| JIM-K-0003 | Seedance绿幕编辑能力 | CAPABILITY | Model；Seedance 2.5；不代表产品部署 | M09 |
| JIM-K-0004 | Seedream文字密集图像生成 | CAPABILITY | Model；Seedream 5.0 Pro；不代表产品部署 | M10 |
| JIM-K-0005 | Seedream空间标注引导 | CAPABILITY | Model；Seedream 5.0 Pro；不代表产品部署 | M10 |
| JIM-K-0006 | Seedream草图引导 | CAPABILITY | Model；Seedream 5.0 Pro；不代表产品部署 | M10 |
| JIM-K-0007 | Seedream图层分离 | CAPABILITY | Model；Seedream 5.0 Pro；不代表产品部署 | M10 |
| JIM-K-0008 | Seedream多语言图像生成 | CAPABILITY | Model；Seedream 5.0 Pro；不代表产品部署 | M10 |

## Atomicity Review

8个Item分别围绕一个能力判断。音视频联合生成是一个模型生成模态定位，不同时讲解两个独立流程；参考构图与绿幕编辑分别立项。空间标注、草图引导、图层分离可独立识别与引用，分别立项。没有将整页或整个Interactive Editing章节压成一个Item。

learner_outcome均采用可观察的识别、指出等动作；模型描述只支持能力辨认，不承诺学习者据此执行未被来源说明的实际操作。

## Provenance Review

每项有一个非重复source_id及说明正文支持关系的support_note。M09/M10在现有来源表均为accepted / DOCUMENTED；未引用candidate或不存在的来源。support_note定位已审核说明段，不仅重复标题。

Validator检查结构、引用和信息类型条件；Agent另对照本轮正文核对statement及learner_outcome，移除营销修饰。通过测试不自动把draft升级validated。

## Cross-Layer Review

全部8项scope明确为ByteDance Seed Model Layer，没有Product或API Item，也没有把Seedream 5.0 Pro描述为已在即梦部署。C3跨层部署映射仍未知。

实际Product与Model并存时能否保持分离尚未完成验证：P10/P12/P13为INGESTION_BLOCKED。不能把“本轮没有产品Item”当成跨层混合试点已通过。待原始产品页可读后返回Source Engine复核，再按后续授权补测；本Gate不自行继续。Gate 2.0-R1 已按此约定重读同一 URL，仍不可读，结论见下节 Cross-Layer Retest。

## Unsupported Claims

以下均未入库：

- 即梦已为所有账号开放Seedream 5.0 Pro，或模型能力等同产品UI能力：无产品部署与权限证据。
- 即梦按钮位置、完整模型菜单、上传格式及素材上限：超出Readiness许可范围。
- 图层数量、API字段和输出文件规格：M10所选说明段未支持，且API领域为DEFER。
- 稳定保持人物一致、精确复现构图、电影级画质等效果保证：营销或比较性描述不能替代独立实测。
- 多语言完整清单及文字准确率：所选说明段不足以支持。
- 绿幕编辑的操作机制和详细步骤：正文只列能力，不能根据常识补全。
- 即梦模型选择、参考上传及局部编辑的产品层知识：Gate 2.0 首轮因原文不可读按 INGESTION_BLOCKED 排除，不声称其内容本身已被否定；该阻塞已在 Gate 2.0-R1 通过用户 MANUAL_CAPTURE 解除，产品层 Item 见下节。

## Duplicates / Overlap

JIM-K-0005与JIM-K-0006同属交互编辑且共享证据段，分别对应空间标注与草图引导，保留为两个原子能力。JIM-K-0007涉及独立的图层分离能力。其他Item未发现同层、同版本、同一结论的重复。未建立任何关联字段或图结构。

Gate 2.0-R1 新增的产品层 Item 中，JIM-K-0015与模型层 JIM-K-0002 同涉及参考视频、JIM-K-0016与模型层 JIM-K-0003/0005/0006/0007 同涉及编辑能力，均属不同知识层，按 TEST C 分别保留，不视为重复。

## Validation

三份测试均与真实Source Registry配合：valid预期PASS；invalid包含重复ID、非法类型、空statement和空evidence_refs；provenance-invalid结构合法，包含缺失来源、candidate来源及OBSERVED引用DOCUMENTED的类型不匹配。

实际执行：valid为PASS（退出码0），invalid为FAIL（退出码1），provenance-invalid为FAIL（退出码1），真实Pilot为PASS（退出码0），均符合预期；该结果只验证机器可判定规则。测试不修改真实Source Registry。额外边界检查覆盖非法JSON、错误根结构、缺字段、空文本、重复引用及INFERRED边界标记。

Gate 2.0-R1 实际执行：Source Validator 为 PASS（退出码0）；Materialization Validator 在 P10/P12/P13 由 BLOCKED 转为 AVAILABLE 后为 PASS（退出码0）；Knowledge Validator 在新增 8 个产品层 Item 后为 PASS（退出码0）。三个 PASS 均只代表 Registry 与 Markdown 的机械一致性；原子性、provenance 质量、分层保持、营销语言与未支持声明由本报告的人工/Agent 审核承担，尤其 support_note 已逐条对照 `materialized/P10.md`、`P12.md`、`P13.md` 的实际保存文字。

## Product Layer Pilot Ingestion

Gate 2.0-R1；核查日期2026-10-03。前置条件已满足：P10/P12/P13 经用户 MANUAL_CAPTURE 材料化为 AVAILABLE，Materialization Validator 为 PASS。本轮读取的唯一材料为 `materialized/P10.md`、`P12.md`、`P13.md`，未做 Source Discovery，未使用搜索摘要、模型记忆、第三方教程或类似产品信息。

### Items Created

| knowledge_id | title | knowledge_type | scope | evidence_refs |
| --- | --- | --- | --- | --- |
| JIM-K-0009 | Seedance 2.5产品页三步生成流程 | PROCEDURE | Product；Seedance 2.5公开产品页；不代表模型完整能力 | P10 |
| JIM-K-0010 | Seedance 2.5流程的入口与模型选择 | PROCEDURE | Product；Seedance 2.5公开产品页；不代表模型完整能力 | P10 |
| JIM-K-0011 | Seedance 2.5流程中的素材与提示词输入 | PROCEDURE | Product；Seedance 2.5公开产品页；不代表模型完整能力 | P10 |
| JIM-K-0012 | Seedance 2.5文字与图片输入方式 | CAPABILITY | Product；Seedance 2.5公开产品页；不代表模型完整能力 | P12 |
| JIM-K-0013 | Seedance 2.5多模态素材组合创作 | CAPABILITY | Product；Seedance 2.5公开产品页；不代表模型完整能力 | P12 |
| JIM-K-0014 | Seedance 2.5带声音视频与音画协同创作 | CAPABILITY | Product；Seedance 2.5公开产品页；不代表模型完整能力 | P12 |
| JIM-K-0015 | Seedance 2.5参考视频控制复杂动作 | CAPABILITY | Product；Seedance 2.5公开产品页；不代表模型完整能力 | P12 |
| JIM-K-0016 | Seedance 2.5局部编辑 | CAPABILITY | Product；Seedance 2.5公开产品页；不代表模型完整能力 | P13 |

新增 8 项，全部 information_type=DOCUMENTED、status=draft，scope 均明确为 Jimeng Product Layer，evidence_refs 全部为 Product Evidence（P10/P12/P13），没有任何一项仅由 Mxx 支持。既有 JIM-K-0001～JIM-K-0008 未修改。

### Atomicity Review

三项流程 Item 分别对应流程整体、第一步（入口与模型选择）、第二步（素材与提示词），各自可独立识别与引用；第三步与产物并入流程整体，不另立重复 Item。P12 的一句话答复涉及两类不同知识，已拆为“文字与图片输入方式”（JIM-K-0012）与“多模态素材组合创作”（JIM-K-0013），未把一句话压成一个 Item。音画协同（JIM-K-0014）、参考视频用途（JIM-K-0015）、局部编辑（JIM-K-0016）分别立项。learner_outcome 使用复述、指出、区分等可观察动作，未写“了解/熟悉/掌握”，也未承诺实操生成效果。

### Provenance Review

每项仅引用一个非重复 source_id，且该来源在 Source Registry 为 accepted / DOCUMENTED；support_note 定位到材料中实际保存的具体段落或句子，而非复述标题。所有 support_note 指向的文字均可在对应 materialized Markdown 中逐字找到，未引用材料之外的内容，也未引用页面未保存部分。

### Marketing Language 与 Unsupported Claims 处理

- P10 开篇“只需三个简单步骤”属于发布方便利性表述，未转成客观结论，只在流程 Item 中保留为发布方说明。
- P12“准确控制复杂动作”中的“准确”未被放大为效果保证；JIM-K-0015 的 limitations 明确记录为发布方产品层说明，不作精确复现承诺。
- P13“无需重新生成整段视频”“同时保留原有构图、光影、音频、动作和时间线连续性”按发布方声明记录，未当作实测一致性结论。
- 未入库：各账号/地区/设备端的开放差异、素材数值上限与格式、按钮位置与界面布局、生成耗时与队列、局部编辑的选区与参数、效果与一致性保证、模型层与 API 层能力映射。

## Cross-Layer Retest

Gate 2.0-R1；核查日期2026-10-03。目标是验证同一 Knowledge Registry 中 Jimeng Product Layer 与 ByteDance Seed Model Layer 能否保持知识实体、证据和 scope 分离。本轮只使用既有 accepted Evidence Units P10/P12/P13 的材料与既有 M09/M10 材料，未做 Source Discovery，未寻找替代来源。

### 读取结果

P10/P12/P13 共用 `https://jimeng.jianying.com/tools/seedance-2-5`。Gate 2.0-R1 首次直接读取失败，过程记录（该次失败事实保留在 Materialization Registry 的 notes 中）：

| 尝试 | 结果 |
| --- | --- |
| 读取层抓取该 URL | 拒绝：hostname 解析为非公网地址 |
| DNS 解析 | 成功，A 记录 198.18.0.33（非公网地址） |
| TCP 443 | 可连接 |
| HTTPS 请求（直接读取原始页） | TLS 阶段失败（schannel SEC_E_NO_CREDENTIALS） |
| HTTP 入口 | 301 跳转到同一 HTTPS 地址，随后同样失败 |

Harness 网络环境无法直接读取后，改由用户本人于 2026-10-03 在浏览器真实打开该原始官方页面，人工读取并复制对应 Evidence Scope 的正文；P10/P12/P13 以 MANUAL_CAPTURE 材料化成功，材料文件为 `materialized/P10.md`、`P12.md`、`P13.md`，capture_status 已由 BLOCKED 转为 AVAILABLE。外部检索通道虽有响应，但返回的是第三方教程、社区帖与托管副本，按合同不得作为替代正文，因此未采纳其中任何内容。

### TEST A：Product Item 不得仅由 Mxx 支持

通过。JIM-K-0009～0016 的 evidence_refs 分别为 P10（3项）、P12（4项）、P13（1项），无一项引用 Mxx，因此不存在仅由 Model Evidence 支持的产品层 Item。

### TEST B：Model Item 不得因新增 Product Evidence 改写成产品部署

通过。JIM-K-0001～0008 未做任何修改：scope 仍为“ByteDance Seed Model Layer；仅官方模型能力说明，不代表即梦产品已部署或开放”，version_scope 仍为 Seedance 2.5 / Seedream 5.0 Pro，evidence_refs 仍为 M09/M10。新增产品证据没有被用来回填或改写模型层 Item。

### TEST C：相似能力的 Product / Model Item 分别保留，不合并

通过。以下相似能力全部成对保留为不同知识实体，未合并、未互相引用、未建立任何关联字段：

| 产品层 Item（Pxx） | 模型层 Item（Mxx） |
| --- | --- |
| JIM-K-0012 文字与图片输入方式 | JIM-K-0004 文字密集图像生成、JIM-K-0008 多语言图像生成（同为生成输入/输出主题） |
| JIM-K-0013 多模态素材组合创作 | JIM-K-0002 参考视频的构图信息（同为多模态参考主题） |
| JIM-K-0014 带声音视频与音画协同创作 | JIM-K-0001（模型定位） |
| JIM-K-0015 参考视频控制复杂动作 | JIM-K-0002（参考信息理解） |
| JIM-K-0016 局部编辑 | JIM-K-0003 绿幕编辑、JIM-K-0005 空间标注引导、JIM-K-0006 草图引导、JIM-K-0007 图层分离 |

理由：模型具备能力与即梦产品公开提供该能力不是同一个知识实体。JIM-K-0015 与 JIM-K-0002 均涉及参考视频，一为产品层用途（动作控制），一为模型层信息理解（framing），分别在各自 limitations 中注明分层关系且保持独立。JIM-K-0016 与模型层四项编辑能力同为编辑主题，也分别记录。

### TEST D：不得推断全账号 / 全地区 / 全设备端 / 全历史版本开放

通过。8 个新增 Item 的 scope 一致声明“不代表底层模型完整能力，也不代表所有账号、地区或设备端已开放相同能力”，其中 JIM-K-0009/0010/0011 另声明不代表实时界面一致。未出现任何全量开放、全平台一致或版本通用性推断。

### 7 项必须报告项

1. Product Knowledge Items 数量：8（JIM-K-0009～0016）。
2. Model Knowledge Items 数量：8（JIM-K-0001～0008，未改动）。
3. 是否存在 Product statement 只引用 Model Evidence：没有。8 项产品 Item 全部引用 Pxx。
4. 是否存在 Model statement 被改写成 Product deployment：没有。模型层 Item 的 scope 与 version_scope 未修改。
5. 是否存在相似 Product / Model Item 被错误合并：没有。TEST C 表中 5 组相似能力均分别保留。
6. 是否存在跨层推断（模型能力→产品权限、API 能力→产品参数、产品入口→底层完整模型能力）：没有新增。产品层 Item 只陈述产品页文字，未声称对应某个模型分支或其完整能力；API 领域本轮完全未使用（A01–A07 仍为 candidate / DEFER）；unresolved C1/C3 继续保留。
7. Unsupported Claims：本轮未入库的项列在上一节“Marketing Language 与 Unsupported Claims 处理”中；未有新 statement 超出所引用材料。

### 仍未验证的边界

本轮验证了“产品层与模型层能在同一 Registry 中分别立项、分别引用、互不改写”，但没有验证产品页所述能力与具体模型版本之间的部署映射（unresolved C3），也没有验证各账号、地区与设备端的实际开放差异。这些仍属未支持结论，不得由本轮 PASS 推导。

## Recommendation

KNOWLEDGE_CONTRACT: PASS

MODEL_LAYER_PILOT: PASS

PRODUCT_LAYER_PILOT: PASS

CROSS_LAYER_PILOT: PASS

GATE_2_0: PASS

产品层本轮以用户 MANUAL_CAPTURE 材料化后完成入库，Product 与 Model 在同一 Registry 中并存并保持知识实体、证据与 scope 分离，TEST A–D 全部通过。所有 Product Item 为 DOCUMENTED / draft，仍需后续内容验收才能升级 validated。

Gate 1.4 与 Gate 2.0-R1 首轮的直接读取失败事实保留在 Materialization Registry 的 notes 中；两次失败不属于 Schema、Policy、Atomicity、Provenance 或 Scope Preservation 的设计错误，因此不使用 KNOWLEDGE_CONTRACT_NEEDS_REVISION。

材料真实性边界：P10/P12/P13 的正文由用户人工采集，Harness 无法独立复核该页面当前内容；Validator PASS 只代表 Registry 与 Markdown 的机械一致性。

Gate 2.0 已完成本轮定义的试点范围，不进入 Gate 2.1；未创建知识图谱、前置关系、课程、测验或学习状态结构。
