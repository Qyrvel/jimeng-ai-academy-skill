# Jimeng Knowledge Coverage Report

## 1. Scope

Gate 2.2 — Knowledge Coverage Audit；评估日期 2026-10-03；Track：Jimeng Creator Academy V1。

- 当前生产 Knowledge Item 总数：**16**（JIM-K-0001 ～ JIM-K-0016；Model Layer 8 / Product Layer 8；DOCUMENTED 16；全部 draft）。
- 本轮**不新增任何知识**：未新建、未修改、未删除任何 Knowledge Item，未修改 Source Registry、Readiness、Materialized 材料或 Normalization Review。
- 审计对象仅为当前生产 Registry 中真实存在的 Item 及其字段；未根据来源内容、模型记忆或未来计划假想「应该已经有」的知识，也未把 Source Evidence 本身当成 Knowledge Item。
- 领域集合沿用 `readiness-assessment.md` 的 22 个领域，未改动任何 Criticality 或 Source Ingestion Decision。
- 本轮运行 Knowledge Validator 与 Coverage Validator，均为 PASS。

Source Readiness 与 Knowledge Coverage 严格分开记录：本报告只回答「已经形成了多少可用 Knowledge Item」，不改写 Readiness 结论。

## 2. CORE Coverage Matrix

13 个 CORE 领域：

| Domain | Item Count | Coverage Status | Source Decision | Next Action | Gap |
| --- | --- | --- | --- | --- | --- |
| 即梦产品基础结构 | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺产品模块与功能关系类知识（工作台/画布边界、图与视频模块关系、分享与项目管理） |
| 网页端 | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺网页端界面结构与入口关系；P11 仍 candidate，当前 UI 与灰度未核验 |
| App | 0 | MISSING | LIMITED_INGESTION | EXPAND_KNOWLEDGE | App 侧知识完全未落成 Item（iOS 概述与 2.3.5/2.3.0 条目均未入库） |
| Seedance | 9 | PARTIAL | ALLOW_INGESTION | **GRAPH_PILOT_ELIGIBLE** | 缺实测与账号级开放情况；产品页能力与具体模型版本的部署映射未核验（C3） |
| Seedream | 5 | PARTIAL | ALLOW_INGESTION | EXPAND_KNOWLEDGE | 全部为模型层 CAPABILITY；缺产品层知识，产品分支映射未核验 |
| 图片生成 | 5 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 只有模型层一侧；缺产品端生成流程、输入输出规格与模型对应关系 |
| 视频生成 | 5 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺输出与运行规格（时长、分辨率、队列）；产品层与模型层对应关系未核验 |
| 参考图 | 1 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺参考图产品层能力项与文件规格（格式、尺寸、数量） |
| 参考视频/音频 | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺音频独立上传、格式、时长与数量类知识 |
| 模型选择 | 1 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺完整模型列表、默认项、可选分支与地域权限 |
| Prompt | 1 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺提示词结构与方法；图片专项与完整模型指南缺失，A07 candidate |
| 编辑功能 | 4 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 全部为 CAPABILITY；缺操作入口、选区与参数（PROCEDURE）及限制（CONSTRAINT）；C1 影响画布 UI |
| 平台内容规则 | 0 | MISSING | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 无任何 POLICY 类知识；P14 为 accepted 但未落成 Item |

CORE 汇总：PARTIAL 11、MISSING 2、COVERED 0、DEFERRED 0。

**没有任何 CORE 领域被判为 COVERED。** 这不是悲观措辞，而是审计结论：11 个 PARTIAL 各有明确的已知子范围缺口，2 个 MISSING 完全无 Item。判定未使用数量阈值——例如「模型选择」只有 1 项却仍算 PARTIAL（而非 MISSING），因为它确实存在一个相关 Item；而「Seedream」有 5 项也未判 COVERED，因为 5 项全是模型层能力声明，缺少产品层与结构类知识。

## 3. Supporting / Dynamic / Optional

### SUPPORTING（1 个领域）

| Domain | Item Count | Status | Source Decision | Next Action | Gap |
| --- | --- | --- | --- | --- | --- |
| 产品版本历史 | 0 | MISSING | LIMITED_INGESTION | EXPAND_KNOWLEDGE | P04/P09 为 accepted 但未落成 Item；网页与 Android 版本史亦缺 |
| 模型版本历史 | 8 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 8 项均带明确 version_scope，但都是单版本能力声明，不是版本沿革知识；M01–M08 的发布与分支关系未落成 Item，无 VERSION_CONTEXT 类型 |

说明：模型版本历史的 8 项之所以计入，是因为它们都携带明确 `version_scope`（Seedance 2.5 / Seedream 5.0 Pro），可作为版本化知识的载体；但它们不代表版本沿革，故为 PARTIAL。

### DYNAMIC（3 个领域）

会员、积分、实时价格：均为 `coverage_status = DEFERRED`、`source_ingestion_decision = DEFER`、`next_action = DEFER`、Item 数 0。三者在 Readiness 中因 P05/P08 仍为 candidate、渠道与时效未对齐而 DEFER。本阶段不应要求 Knowledge Engine 覆盖，动态信息不冻结稳定领域。

### OPTIONAL（3 个领域）

Volcano / Ark API、社区经验、可复现实验：均为 `DEFERRED` / `DEFER` / `DEFER` / Item 数 0（A01–A07、O01/O02 全为 candidate；无合格实验记录）。此外当前 16 项全部为 `DOCUMENTED`，没有任何 `OBSERVED` Item，可复现实验领域因此连观察类知识也不存在。

### OUT_OF_SCOPE（1 个领域）

API 服务状态：`NOT_APPLICABLE` / `NOT_APPLICABLE` / `NOT_APPLICABLE`，不纳入本 Creator Track。

## 4. Graph Pilot Candidates

`next_action = GRAPH_PILOT_ELIGIBLE` 的领域只有 **1 个**：

### Seedance（CORE，ALLOW_INGESTION，PARTIAL，9 Items）

为什么当前可以在未来小规模 Graph Pilot 中使用（逐条对照 Policy §Graph Pilot Eligibility）：

1. **存在多个彼此独立的 Knowledge Item**：Model Layer 3 项（JIM-K-0001 音视频联合生成定位、JIM-K-0002 参考视频信息理解、JIM-K-0003 绿幕编辑）与 Product Layer 6 项（JIM-K-0009 三步流程、JIM-K-0010 入口与模型选择、JIM-K-0012 文字与图片输入、JIM-K-0013 多模态素材组合、JIM-K-0014 带声音视频与音画协同、JIM-K-0015 参考视频控制复杂动作）。这些 Item 已在 Gate 2.1 与 2.1-R1 中被确认彼此不重复（K-0009 与 K-0010/K-0011 为部分重叠，K-0015 与 K-0002 为跨层平行）。
2. **存在真实、可讨论的关系潜力**：至少存在两类无需编造即可讨论的关系——同层内的流程包含关系（整体流程与其中一步），以及跨层的「模型具备能力」与「产品提供该能力」对照关系（K-0001/K-0002 对 K-0014/K-0015）。这两类关系正是 Gate 2.1-R1 已用夹具验证过分类能力的类型。
3. **不需要编造知识**：上述关系全部由现有 9 个 Item 的 statement 与 scope 直接支撑，无需虚构中间节点。
4. **Scope 边界清楚**：9 项的 scope 分别明确写为 ByteDance Seed Model Layer 与 Jimeng Product Layer，并在 limitations 中互相声明不合并、不外推。
5. **已知重大缺口不会造成误导性完整假象**：本领域最大的缺口是「产品页能力与具体模型版本的部署映射」（unresolved C3）与账号级开放差异。二者都已在相关 Item 的 limitations 与 Source Registry notes 中显式标注为未核验，因此 Pilot 即便只呈现现有 9 项，也不会被误读为完整结构。

未入选的领域及理由：**编辑功能**（4 项，跨 Seedance 产品层与 Seedream 模型层两个模型分支，跨层关系的语义基础弱于 Seedance，且全为 CAPABILITY）；**视频生成**（5 项，全为产品层，无同领域模型层对照项）；**Seedream**（5 项，全为模型层，无产品层对照项）；其余领域 Item 数为 0 或仅 1 项，不足以形成关系网络。

**Graph Pilot Eligibility 不等于完整 Knowledge Graph Ready**：本结论只允许在 Seedance 领域内做小规模关系试点，不授权建立 prerequisite、learning_order、curriculum 或任何课程结构，也不表示其他 21 个领域已就绪。

## 5. Targeted Ingestion Gaps

`next_action = EXPAND_KNOWLEDGE` 的领域共 **14 个**（13 个 CORE 中的 12 个 + SUPPORTING 中的 2 个）。以下说明每个领域已有哪些 Item、还缺什么类型的 Knowledge、以及是否已有 Source Readiness 许可。所有缺口均为 **Knowledge ingestion gap**（来源许可已存在，知识抽取未完成），不是 Source evidence gap。

| Domain | 已有 Items | 还缺的 Knowledge 类型 | Source 许可 |
| --- | --- | --- | --- |
| 即梦产品基础结构 | K-0009、K-0012 | CONCEPT/CONSTRAINT：产品模块与功能关系、工作台与画布边界、分享与项目管理 | LIMITED_INGESTION 已允许「仅图/视频、编辑、分享等公开功能关系」 |
| 网页端 | K-0009、K-0010 | CONCEPT/CONSTRAINT：网页端界面结构与入口关系（排除按钮布局与实时规格） | LIMITED_INGESTION 已允许「仅产品页明示流程」 |
| App | 无 | CONCEPT/CAPABILITY：iOS 基础功能概述；VERSION_CONTEXT：2.3.5 / 2.3.0 条目 | LIMITED_INGESTION 已允许「仅简介及对应历史版本条目，不绑定二者」 |
| Seedream | K-0004 ～ K-0008 | PRODUCT 层 Item；CONCEPT/CONSTRAINT：产品分支映射与输入输出规格 | ALLOW_INGESTION（仅该模型官方说明，不含即梦部署结论） |
| 图片生成 | K-0004 ～ K-0008 | Product 层 CAPABILITY/PROCEDURE：产品端流程与输入输出；产品与模型对应关系 | LIMITED_INGESTION 已允许「产品概述与模型说明分开，排除精确限制」 |
| 视频生成 | K-0009、K-0012 ～ K-0015 | CONSTRAINT：时长、分辨率、队列等输出与运行规格；Model 层对照项 | LIMITED_INGESTION 已允许「仅公开创作流程与版本化描述」 |
| 参考图 | K-0011 | CAPABILITY：参考图产品层用途；CONSTRAINT：格式、尺寸、数量边界 | LIMITED_INGESTION 已允许「仅明示参考用途和流程，不录入上限」 |
| 参考视频/音频 | K-0014、K-0015 | CONSTRAINT：音频独立上传、格式、时长、数量 | LIMITED_INGESTION 已允许「仅官方参考类型与用途，排除上传参数」 |
| 模型选择 | K-0010 | CONCEPT/CONSTRAINT：可用模型集合与默认项（不建完整选择表） | LIMITED_INGESTION 已允许「仅 2.5 产品页选择说明与 App 版本条目」 |
| Prompt | K-0011 | PROCEDURE/CONSTRAINT：提示词结构与要素指导 | LIMITED_INGESTION 已允许「仅官方 FAQ 及流程中的提示词指导」 |
| 编辑功能 | K-0005 ～ K-0007、K-0016 | PROCEDURE：编辑操作入口与步骤；CONSTRAINT：可编辑范围与限制 | LIMITED_INGESTION 已允许「版本与层分别保存，仅明示编辑用途」 |
| 平台内容规则 | 无 | POLICY：用户行为规范与内容规则条文 | LIMITED_INGESTION 已允许「仅所读条文，排除完整合规承诺与法律推断」 |
| 产品版本历史 | 无 | VERSION_CONTEXT：iOS 2.3.5 与 2.3.0 条目 | LIMITED_INGESTION 已允许「仅两条明确版本记录」 |
| 模型版本历史 | K-0001 ～ K-0008 | VERSION_CONTEXT：各版本发布与分支关系（M01–M08 元数据） | LIMITED_INGESTION 已允许「仅已核实发布/报告元数据」 |

**重要提醒**：上表是审计结论，不是执行授权。本轮未创建任何新 Item；Targeted Knowledge Ingestion 需要单独授权，且必须遵守各领域的 LIMITED_INGESTION 边界（例如参考图领域不得录入数值上限，平台内容规则不得作法律推断，模型版本历史不得把模型发布推导为产品开放）。

## 6. Return-to-Source Gaps

`next_action = RETURN_TO_SOURCE` 的领域：**none**。

没有任何 CORE 领域的阻塞根因来自 Source Readiness 或 Evidence 不足：

- 13 个 CORE 中，2 个是 ALLOW_INGESTION（Seedance、Seedream），11 个是 LIMITED_INGESTION，**没有一个是 DEFER 或 BLOCKED**；
- 3 个 MISSING 领域（App、平台内容规则、产品版本历史）都已有 accepted Evidence（P04/P09/P15、P14、P04/P09），因此其缺口属于知识抽取未完成，已归入上表的 EXPAND_KNOWLEDGE；
- 真正被 Source Engine 拦住的是 DYNAMIC / OPTIONAL 领域（会员、积分、实时价格、API、社区经验、可复现实验），它们的 next_action 是 DEFER 而非 RETURN_TO_SOURCE。

但必须同时记录两类仍然存在、且**不能靠本次入库解决的 Source 层风险**（它们不改变上述判定，但会影响未来 Pilot 的表述边界）：

- unresolved C1：P02/P03/P11 的新旧界面与灰度关系未知 → 阻止画布 UI 与迁移结论；
- unresolved C3：M05/M10、A04、P03/P11 的 Pro/Flash 命名与实际产品开放映射未核验 → 阻止跨层等价与全量开放结论。

## 7. Unmapped Knowledge Items

**none.**

`item_accounting` 结果：`registry_total = 16`，`mapped_item_ids` 16 项，`unmapped_item_ids` 为空数组，两者并集精确等于 Registry 全部 knowledge_id 且无重叠。

16 项全部至少映射到一个领域，映射分布（同一 Item 可出现在多个领域，此处按 Item 列出其领域数）：

| Item | 映射到的领域 |
| --- | --- |
| JIM-K-0001 | Seedance；模型版本历史 |
| JIM-K-0002 | Seedance；模型版本历史 |
| JIM-K-0003 | Seedance；模型版本历史 |
| JIM-K-0004 | Seedream；图片生成；模型版本历史 |
| JIM-K-0005 | Seedream；图片生成；编辑功能；模型版本历史 |
| JIM-K-0006 | Seedream；图片生成；编辑功能；模型版本历史 |
| JIM-K-0007 | Seedream；图片生成；编辑功能；模型版本历史 |
| JIM-K-0008 | Seedream；图片生成；模型版本历史 |
| JIM-K-0009 | 即梦产品基础结构；网页端；Seedance；视频生成 |
| JIM-K-0010 | 网页端；Seedance；模型选择 |
| JIM-K-0011 | 参考图；Prompt |
| JIM-K-0012 | 即梦产品基础结构；Seedance；视频生成 |
| JIM-K-0013 | Seedance；视频生成 |
| JIM-K-0014 | Seedance；视频生成；参考视频/音频 |
| JIM-K-0015 | Seedance；视频生成；参考视频/音频 |
| JIM-K-0016 | 编辑功能 |

未把任何 Item 强行塞入领域：例如 JIM-K-0016（局部编辑）未被映射到 Seedream 或图片生成，因为它的 scope 是 Seedance 2.5 产品层，与 Seedream 5.0 Pro 模型说明不构成同一领域的代表；JIM-K-0005 ～ K-0007 未被映射到视频生成，因为它们是 Seedream 图像侧编辑能力。

## 8. Coverage Risks

### 风险 1：多个 CORE 领域只有 Model Layer，没有 Product Layer

- **Seedream**（5 项全部 Model Layer，产品层 0 项）；
- **图片生成**（5 项全部为 Seedream 模型层说明，产品端 0 项）。

这两个领域存在「模型具备能力被误读为产品已提供」的风险。缓解：相关 Item 的 scope 已统一写明「不代表即梦产品已部署或开放」，limitations 亦逐条声明不外推产品开放范围。但覆盖结构本身确实缺产品一侧。

### 风险 2：多个 CORE 领域只有 Product Layer，没有 Model Layer

- **视频生成**（5 项全部产品层，同领域模型层对照项 0 个）；
- **网页端**、**即梦产品基础结构**（均为产品层流程知识）；
- **参考图**、**模型选择**、**Prompt**（各 1 项，均产品层）。

风险：这些领域目前无法呈现「模型能力 vs 产品能力」的对照，未来若做图谱容易出现单侧结构。

### 风险 3：knowledge_type 分布严重偏斜

| knowledge_type | 数量 |
| --- | --- |
| CAPABILITY | 13 |
| PROCEDURE | 3 |
| CONCEPT | 0 |
| CONSTRAINT | 0 |
| POLICY | 0 |
| VERSION_CONTEXT | 0 |

16 项中 13 项为 CAPABILITY、3 项为 PROCEDURE，其余四类完全为 0。这意味着当前知识体系几乎没有「限制条件」「政策规范」「版本沿革」「结构概念」类知识。直接后果：**平台内容规则**领域（POLICY）与**模型版本历史**领域（VERSION_CONTEXT）虽有 accepted 来源却完全无法覆盖。这也是本报告不建议现在进入完整图谱的关键结构性质因。

### 风险 4：version_scope 过窄且高度集中

16 项的 version_scope 只有三种取值：`Seedance 2.5`（3 项）、`Seedream 5.0 Pro`（5 项）、`Seedance 2.5；2026-10-03 公开产品页`（8 项）。没有任何 Item 覆盖 Seedance 2.0 / 1.5 pro / 1.0、Seedream 5.0 Lite / 4.5 / 4.0，也没有 unknown 版本项。风险：当前知识被压缩在「最新两个版本」上，版本沿革与历史适用范围完全空缺；若未来做课程，容易把「当前版本行为」误当作通用规律。

### 风险 5：是否存在 CORE 领域实际只有一两个知识点却被误判 Covered

**未发现此类误判，因为本轮没有任何 CORE 领域被标为 COVERED。** 13 个 CORE 的最佳情况是 PARTIAL（11 个），其中「模型选择」「Prompt」「参考图」各只有 1 项，审查后确认不足以代表领域，因此保持 PARTIAL 而非升级为 COVERED。数量阈值未被使用：Seedream 与视频生成各有 5 项，同样因结构单侧而保持 PARTIAL。

### 风险 6：Item 全部为 draft / DOCUMENTED

16 项 status 全为 `draft`、information_type 全为 `DOCUMENTED`。没有任何 `validated` Item，也没有任何 `OBSERVED` / `INFERRED` Item。风险：当前覆盖完全建立在官方文档层，缺少实测与推理类知识；本报告的任何「已覆盖」表述都只适用于官方文档层，不代表知识已经过内容验收。

## 9. Recommendation

```text
overall_recommendation: NEEDS_TARGETED_INGESTION
```

理由：

- 13 个 CORE 领域中 **0 个 COVERED、11 个 PARTIAL、2 个 MISSING**，多数 CORE 领域的 Knowledge Item 尚不足以形成有意义的结构；
- 来源许可已存在：12 个 CORE 领域为 ALLOW_INGESTION 或 LIMITED_INGESTION，因此下一步应先做 **Targeted Knowledge Ingestion**，而不是回 Source Engine；
- 当前**没有**任何一个 CORE 领域的真正阻塞来自 Source Readiness 或 Evidence 不足（`RETURN_TO_SOURCE` 为 none），故不选 `RETURN_TO_SOURCE_FIRST`；
- 存在 1 个可在未来小规模试点的领域（Seedance），但单凭 1 个领域不足以支撑整个 Track 的图谱试点，且知识类型分布严重偏斜（CAPABILITY 13 / PROCEDURE 3，其余为 0），故不选 `READY_FOR_GRAPH_PILOT`。

本 Gate 到此停止：**不进入 Gate 2.3 或 Gate 3**，不创建 Knowledge Graph、prerequisite、learning_order、curriculum、module、lesson、quiz、student state、RAG 或向量数据库。Targeted Knowledge Ingestion 需另行授权，且不得超出各领域的 LIMITED_INGESTION 边界。
