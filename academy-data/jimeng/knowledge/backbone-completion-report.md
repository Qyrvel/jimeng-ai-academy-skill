# Gate 2.3-R1 Backbone Completion Report

## Scope

本轮只补两个骨架类型：**POLICY** 与 **VERSION_CONTEXT**。

- 不允许新 Source Discovery、替代来源、candidate 来源、第三方教程或社区内容。
- 不允许新增 CAPABILITY。
- 不允许修改旧 24 个 Knowledge Item。
- 不进入 Knowledge Graph。

分三次收到用户提供的正文，各自只处理对应部分：

| 用户提供 | 收到的类型 | 处理结果 |
| --- | --- | --- |
| **P14 RAW**（即梦AI用户服务协议第 4.1–4.8 节） | POLICY | 新增 **11** 项 POLICY（JIM-K-0025 ～ JIM-K-0035） |
| **M01 RAW**（Seed 官方 Seedance 2.5 发布页） | VERSION_CONTEXT | 新增 **2** 项 VERSION_CONTEXT（JIM-K-0036、JIM-K-0037） |
| **M02 RAW**（Seed 官方 Seedance 2.0 发布页） | VERSION_CONTEXT | 新增 **4** 项 VERSION_CONTEXT（JIM-K-0038 ～ JIM-K-0041） |
| P04 / P09 | — | 未提供，保持 BLOCKED |

本轮合计新增 **17** 项，其中 CAPABILITY 新增 **0** 项（刻意不扩张）。两个目标骨架类型均已补齐，因此 §12 判定为 **BACKBONE_COMPLETION: PASS**。

## Materialization

| Source | 目标类型 | 最终状态 | 说明 |
| --- | --- | --- | --- |
| **P14** | POLICY | **AVAILABLE** | 用户于 2026-10-03 真实打开协议页面并复制第 4.1–4.8 节；`materialized/P14.md`，MANUAL_CAPTURE |
| **M01** | VERSION_CONTEXT | **AVAILABLE** | 同上方式；`materialized/M01.md`（只含标题、日期行、开篇段） |
| **M02** | VERSION_CONTEXT | **AVAILABLE** | 同上方式；`materialized/M02.md`（含标题、日期行、开篇三段与核心亮点四段——均在 M02 已审核的 evidence_scope 内） |
| P04 | VERSION_CONTEXT | **BLOCKED** | 未提供正文；Harness 直读 TLS 失败；未用替代来源 |
| P09 | VERSION_CONTEXT | **BLOCKED** | 同上 |

### M01 / M02 的范围处理（重要）

两份发布页在 Source Registry 中具有**不同的 evidence_scope**，因此可保存的范围不同：

| Source | 已审核 evidence_scope | 保存内容 | 范围外（记录为遗漏） |
| --- | --- | --- | --- |
| M01 | section: 发布日期及开篇模型版本介绍 | 标题、日期行、开篇段 | 核心亮点三段（30 秒与多轮延长、多模态参考 30/10/10 数值、编辑能力）、末段（上线平台与 API 计划） |
| M02 | sections: 发布日期、Key highlights 与官方评测章节入口 | 标题、日期行、开篇三段、核心亮点四段 | 末段「Seedance 2.0 已上线即梦 AI、豆包等平台」 |

处理原则：按 `evidence-materialization-policy.md`「只保存支持当前 Evidence Unit 所必需的最小正文范围」，超出各自 evidence_scope 的段落未纳入材料、未据其建立任何 Item，并在 Capture Notes 中逐项记录为遗漏范围。未修改 Source Registry 的 evidence_scope，也未新建 Evidence Unit。

M02 另有一项如实记录：本页**未出现**官方评测章节的正文，而该 Evidence Unit 的范围是「……与官方评测章节入口」——因此材料到入口为止，未据任何评测内容建立 Item。

覆盖影响：两份发布页的末段都写着该版本「已上线即梦 AI」，但这两句都在各自 evidence_scope 之外，因此**本轮仍未建立任何「产品端上线」类 VERSION_CONTEXT**，产品版本历史领域仍为 MISSING。若要记录该事实，需先由 Source Engine 决定是否为该段拆出独立的 Product Layer Evidence Unit。

## New POLICY Items

来自 **P14** 第 4.1–4.8 节，共 11 项。全部：`DOCUMENTED / draft / POLICY / Jimeng Product Layer / evidence_refs=[P14] / version_scope = 2025-08-25 更新；2025-09-01 生效`。

| knowledge_id | title | 依据节 | 核心命题 |
| --- | --- | --- | --- |
| JIM-K-0025 | 禁止输入或分享未经授权的信息 | 4.1 | 不得输入、分享未经授权的个人信息、保密信息及其他未授权信息 |
| JIM-K-0026 | 输入内容须合法且不侵害他人权益 | 4.1 | 输入内容须合法、为本人所有或已获授权，且不得侵害所列他人权益 |
| JIM-K-0027 | AI内容标识的添加规则 | 4.2 | 平台有权依法规与强制性国家标准对 AI 内容添加标识 |
| JIM-K-0028 | 禁止遮挡或删除AI内容标识 | 4.2 | 不得以任何方式遮挡、涂抹、修改或删除平台添加的标识 |
| JIM-K-0029 | 真实身份认证作为生成与发布的前提 | 4.3 | 完成真实身份信息认证后，才可使用生成、制作、发布功能 |
| JIM-K-0030 | 内容合规与特定信息须标注来源 | 4.3 | 内容须合法；涉及时事、公共政策、社会事件时须准确标注来源 |
| JIM-K-0031 | 禁止输入或传播违法违规内容 | 4.4 | 禁止该节列举的十二类违法违规内容 |
| JIM-K-0032 | 禁止输入或传播不良内容 | 4.5 | 禁止该节列举的十一项不良内容，并应主动抵制其传播 |
| JIM-K-0033 | 禁止欺骗性与高危险性内容 | 4.6 | 禁止欺骗性、高危险性、危害身心健康的内容（该节列四类） |
| JIM-K-0034 | 禁止扰乱平台经营秩序的信息 | 4.7 | 禁止垃圾信息、商业招揽、过度营销、无关联信息及规避技术审核的信息 |
| JIM-K-0035 | 平台对违规行为的处理权 | 4.8 | 有合理理由认为违规时，平台可警示、限制功能、暂停或终止服务并追责 |

自审：节内不同义务分别立项（4.1 → 0025/0026；4.2 → 0027/0028；4.3 → 0029/0030）；4.4/4.5/4.6 各以「禁止该节列举的 N 类内容」为一条命题，limitations 注明不复述子项、以材料原文为准。未做法律解释、合规保证、把局部条款写成完整平台政策、从一条政策推导其他未写规则。4.2 末句的责任承担与 4.8 的《社区自律公约》未单独立项。

## New VERSION_CONTEXT Items

### 来自 M01（Seedance 2.5 发布页的日期行与开篇段），2 项

| knowledge_id | title | scope | version_scope | 核心命题 |
| --- | --- | --- | --- | --- |
| JIM-K-0036 | Seedance 2.5 的正式发布与发布日期 | Model Layer | Seedance 2.5；发布于 2026-07-31 | 官方发布页记载该版本于 2026-07-31 正式发布，并称其为新一代视频创作模型 |
| JIM-K-0037 | Seedance 2.5 与 2.0 的版本承接关系 | Model Layer | Seedance 2.5 与 Seedance 2.0（依据 2026-07-31 发布页表述） | 发布页记载该版本延续 Seedance 2.0 统一的多模态视频联合生成架构，并提到 Seedance 2.0 已经发布 |

### 来自 M02（Seedance 2.0 发布页的日期行、开篇段与核心亮点），4 项

| knowledge_id | title | scope | version_scope | 核心命题 |
| --- | --- | --- | --- | --- |
| JIM-K-0038 | Seedance 2.0 的正式发布与发布日期 | Model Layer | Seedance 2.0；发布于 2026-02-12 | 官方发布页记载该版本于 2026-02-12 正式发布，并称其为新一代视频创作模型 |
| JIM-K-0039 | Seedance 2.0 的架构与输入支持 | Model Layer | Seedance 2.0；2026-02-12 发布页 | 该页记载 2.0 采用统一的多模态音频视频联合生成架构，支持文字、图片、音频、视频和标签输入 |
| JIM-K-0040 | Seedance 2.0 与 1.5 版本的承接关系 | Model Layer | Seedance 2.0 与 1.5 版本（依据 2026-02-12 发布页表述） | 该页以「相比 1.5 版本」作对比，据此记载 1.5 已存在并把 2.0 描述为质量提升的版本 |
| JIM-K-0041 | 统一多模态架构在 2.0 与 2.5 之间的延续 | Model Layer | Seedance 2.0（M02）与 Seedance 2.5（M01） | 两份发布页分别记载 2.0 采用该架构、2.5 延续该架构，共同支持架构延续这一事实 |

自审与边界：

- 6 项全部为 Model Layer、`DOCUMENTED / draft`，version_scope 与材料一致；仅 JIM-K-0041 同时引用 M02 与 M01（同一 Model Layer 内的两份官方发布页），未跨层。
- 严格未推断：新版完全替代旧版、旧版已下线、所有端同步、所有账号同步、模型版本等于产品版本。JIM-K-0037 与 JIM-K-0040 的 limitations 均明确写出「不推断……已下线或被替代」。
- 未把「生成质量大幅提升」「可用率达到业界 SOTA」「工业级」等比较性与宣传性表述转成客观结论：JIM-K-0040 明确标注其为**发布方的比较性陈述**、不作独立评测，且不把「1.5 版本」细化为具体分支名（如 1.5 pro）。
- 未把 M02 核心亮点里的具体规格（9 张图片 / 3 段视频 / 3 段音频、15 秒多镜头、双声道）建成 CAPABILITY Item——本轮不扩张 CAPABILITY，这些规格也未进入任何 VERSION_CONTEXT 的 statement。
- 未把 M01 与 M02 末段的「已上线即梦 AI」写成产品端事实（见上一节的 scope 处理）。
- 未使用 Source Registry 的 `published_at` 元数据作为证据。

## Unsupported Claims

以下因为证据不足、证据缺失或超出 Evidence Scope 而**未入库**：

| 未入库的结论 | 原因 |
| --- | --- |
| 单次生成 30 秒、支持多轮延长；单次最多 30 张图片 / 10 段视频 / 10 段音频；遮罩编辑、视频编辑、精准时间控制 | 位于 M01 的「核心亮点」段，超出该 Evidence Unit 的 evidence_scope；且属能力与规格结论，本轮不扩张 CAPABILITY |
| Seedance 2.0 的 9 张图片 / 3 段视频 / 3 段音频混合模态上限、15 秒多镜头生成、双声道音频、可用率业界 SOTA | 虽在 M02 的 evidence_scope 内，但属能力与规格结论；本轮不扩张 CAPABILITY，也未写入任何 VERSION_CONTEXT 的 statement，留待后续授权的 CAPABILITY 波次 |
| **Seedance 2.5 正式上线即梦 AI、豆包专业版等平台**（M01 末段）与 **Seedance 2.0 已上线即梦 AI、豆包等平台**（M02 末段） | 两句均为官方原文，但都在各自 Evidence Unit 的 evidence_scope 之外。因此未建立产品端上线 Item，产品版本历史领域仍为 MISSING。需先由 Source Engine 决定是否拆出独立的 Product Layer Evidence Unit |
| Seedance 2.5 的 API 将在近期上线火山方舟 | 同上；且 API 领域在 Readiness 中为 DEFER |
| 官方评测章节的评测结论（M02） | 该 Evidence Unit 的范围只到「官方评测章节入口」，本页未出现评测正文；未据此推断任何评测结论 |
| 「1.5 版本」的具体分支名称（如 1.5 pro）与发布日期 | M02 只写「1.5 版本」，未给分支名与日期；M03/M04 未材料化 |
| Seedance 1.0 的历史存在与分支关系 | M04 BLOCKED，非本轮范围 |
| iOS App 2.3.5 / 2.3.0 版本存在与时间关系 | P04/P09 BLOCKED |
| Seedream 各版本关系 | M05–M08 BLOCKED；§7 明确不为其扩大来源 |
| 「新版替代旧版」「旧版已下线」「所有端/所有账号同步」「模型版本 = 产品版本」 | 无证据支持，且 §3 明确禁止 |
| 违规责任承担规则（4.2 末句） | 属后果与责任分配表述，非行为规则，未单独立项 |
| 平台处理措施的执行顺序与申诉途径；各条款的执行阈值与审核机制 | 证据不含，未推断 |
| 《“即梦AI”社区自律公约》条文 | 未纳入 P14 材料范围 |

## Type Balance

| knowledge_type | Before（24 项） | After（41 项） | 变化 |
| --- | --- | --- | --- |
| CONCEPT | 4 | 4 | 0 |
| CAPABILITY | 13 | 13 | **0（刻意不扩张）** |
| PROCEDURE | 4 | 4 | 0 |
| CONSTRAINT | 3 | 3 | 0 |
| **POLICY** | **0** | **11** | **+11** |
| **VERSION_CONTEXT** | **0** | **6** | **+6** |
| **合计** | **24** | **41** | **+17** |

骨架类型完成度：**6 / 6 全部具备**（CONCEPT、CAPABILITY、PROCEDURE、CONSTRAINT、POLICY、VERSION_CONTEXT）。

## Normalization Check on New Items

本轮新增 17 项集中在两类，且 POLICY 全部来自同一 Evidence Unit、VERSION_CONTEXT 六项同源于两份发布页，因此做了归一化复核，并把 Gate 2.3 的 8 项一并补齐。`normalization-review.json` 现为 **28 条 Review，覆盖全部 41 个 Item**：

- DISTINCT 12、PARTIAL_OVERLAP 13、SCOPE_PARALLEL 3；
- KEEP_SEPARATE 27、**NEEDS_REVIEW 1**。
- 本轮新增 4 条复核：`NR-0025`（K-0038/0039，DISTINCT）、`NR-0026`（K-0038/0040，DISTINCT）、`NR-0027`（K-0039/0041，PARTIAL_OVERLAP / KEEP_SEPARATE）、`NR-0028`（K-0037/0041，PARTIAL_OVERLAP / KEEP_SEPARATE）；`NR-0024`（K-0036/0037，DISTINCT）在收到 M01 时已建立。

（更正记录：在只收到 M01 的那一步，收尾摘要里曾写「25 条 Review」，校验后实为 24 条；本报告与 Registry 的计数以校验输出为准。）

唯一 NEEDS_REVIEW 仍是 **NR-0016（JIM-K-0031 / 0032 / 0033）**：三者命题同构（都是「禁止……该节列举的内容」），共享同一条禁止性结构，独立的是不同类别清单（4.4 十二类 / 4.5 十一项 / 4.6 四类）→ PARTIAL_OVERLAP + NEEDS_REVIEW。这是粒度设计问题（按节 vs 逐项原子化 27 条），本 Gate 不擅自裁决，留待决定。

其余 VERSION_CONTEXT 之间的复核结果均为 KEEP_SEPARATE：K-0039 与 K-0041（同一架构事实，但一为单版本架构与输入、一为跨版本延续）、K-0037 与 K-0041（同一「延续」表述，但证据面不同：M01 单独 vs M02+M01）被判为 PARTIAL_OVERLAP，未合并。

## Recommendation

```text
BACKBONE_COMPLETION_PASS
```

对照 §12 全部条件：至少新增 1 个真实 POLICY ✔（11 个）；至少新增 1 个真实 VERSION_CONTEXT ✔（2 个）；所有 Validator PASS ✔；旧 24 项零改动 ✔；无跨层混淆 ✔（POLICY 全 Product Layer 且只引用 P14；VERSION_CONTEXT 全 Model Layer 且只引用 M01）；无版本替代推断 ✔。

## Post-2.3-R1 Coverage

已重跑 Gate 2.2 的 Coverage Assessment，生成新快照（不覆盖旧报告）：

- `coverage-assessment-after-2.3-r1.json`（37 项版）
- `knowledge-coverage-report-after-2.3-r1.md`

变化：**平台内容规则** MISSING → PARTIAL（11 项 POLICY）；**模型版本历史** PARTIAL 但首次含 VERSION_CONTEXT（2 项），从「无任何版本沿革知识」变为「已有 2 项版本背景」。`overall_recommendation` 仍为 **NEEDS_TARGETED_INGESTION**，因为 CORE COVERED 仍为 0、产品版本历史仍 MISSING，且剩余缺口的根因仍是证据不可读。
