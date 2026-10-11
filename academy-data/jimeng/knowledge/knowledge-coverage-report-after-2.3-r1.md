# Jimeng Knowledge Coverage Report（After Gate 2.3-R1）

Gate 2.2 Coverage Assessment 的第三次快照，日期 2026-10-03。使用同一 `knowledge-coverage-policy.md`、`knowledge-coverage.schema.json` 与 `validate_knowledge_coverage.py`。Gate 2.2 与 Gate 2.3 的历史快照（`coverage-assessment.json`、`coverage-assessment-after-2.3.json` 及其报告）未被修改。

本轮快照在 Gate 2.3-R1 完成时点生成，反映该 Gate 全部新增：11 项 POLICY（P14）+ 6 项 VERSION_CONTEXT（M01、M02），共 17 项。

## 1. Scope

- 当前生产 Knowledge Item 总数：**41**（Gate 2.3-R1 新增 17 项：JIM-K-0025 ～ JIM-K-0041）。
- 其中 POLICY 11 项来自 P14 第 4.1–4.8 节；VERSION_CONTEXT 6 项来自 M01（Seedance 2.5 发布页）与 M02（Seedance 2.0 发布页）。
- 本轮未新增 CAPABILITY，未修改旧 24 项。
- 领域集合沿用 readiness-assessment.md 的 22 个领域，未改动任何 Criticality 或 Source Ingestion Decision。

## 2. CORE Coverage Matrix

| Domain | Item Count | Coverage Status | Source Decision | Next Action | Gap |
| --- | --- | --- | --- | --- | --- |
| 即梦产品基础结构 | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 需 P01/P02 正文 |
| 网页端 | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺界面结构；P11 candidate |
| App | 0 | MISSING | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 需 P04/P09/P15 正文 |
| Seedance | 11 | PARTIAL | ALLOW_INGESTION | GRAPH_PILOT_ELIGIBLE | 缺实测与账号级开放情况；版本背景见模型版本历史 |
| Seedream | 5 | PARTIAL | ALLOW_INGESTION | EXPAND_KNOWLEDGE | 全为模型层 CAPABILITY |
| 图片生成 | 5 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 需 P02/P07 正文 |
| 视频生成 | 7 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺输出规格与模型层对照 |
| 参考图 | 1 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺专项能力项与文件规格 |
| 参考视频/音频 | 5 | PARTIAL | LIMITED_INGESTION | GRAPH_PILOT_ELIGIBLE | 缺音频参数与模型层对照 |
| 模型选择 | 1 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 证据仅一句 |
| Prompt | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 需 P07 正文 |
| 编辑功能 | 6 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺 PROCEDURE；C1 未决 |
| **平台内容规则** | **11** | **PARTIAL**（原 MISSING） | LIMITED_INGESTION | **GRAPH_PILOT_ELIGIBLE** | 缺《社区自律公约》与执行阈值 |

CORE 汇总（与 Gate 2.2 / 2.3 对比）：

| 状态 | Gate 2.2（16 项） | Gate 2.3（24 项） | Gate 2.3-R1（41 项） |
| --- | --- | --- | --- |
| COVERED | 0 | 0 | **0** |
| PARTIAL | 11 | 11 | **12** |
| MISSING | 2 | 2 | **1** |

CORE 状态变化：**平台内容规则 MISSING → PARTIAL**，使 CORE MISSING 由 2 个减至 1 个（仅剩 App）。COVERED 仍为 0，因为没有任何 CORE 领域达到「无需虚构缺失知识即可代表主要知识结构」的标准。

## 3. Supporting / Dynamic / Optional

- **SUPPORTING**：产品版本历史（0 项、MISSING、EXPAND_KNOWLEDGE，需 P04/P09）；模型版本历史（**14 项**、PARTIAL、EXPAND_KNOWLEDGE，**含 6 项 VERSION_CONTEXT**，见 4.4）。
- **DYNAMIC**：会员、积分、实时价格 —— 均 DEFERRED / DEFER / 0 项，与前两次快照一致。
- **OPTIONAL**：Volcano / Ark API、社区经验、可复现实验 —— 均 DEFERRED / DEFER / 0 项；41 项中仍**无任何 OBSERVED Item**。
- **OUT_OF_SCOPE**：API 服务状态 —— NOT_APPLICABLE。

## 4. Graph Pilot Candidates

`next_action = GRAPH_PILOT_ELIGIBLE` 的领域由 Gate 2.3 的 2 个增至 **3 个**：

### 4.1 Seedance（CORE / ALLOW_INGESTION / PARTIAL / 11 Items）

Model Layer 3 项与 Product Layer 8 项并存，含 CONCEPT、CONSTRAINT、CAPABILITY、PROCEDURE 四类；可讨论关系包括同层流程包含、跨层「模型具备 ↔ 产品提供」对照、概念与其用途边界的界定。

### 4.2 参考视频/音频（CORE / LIMITED_INGESTION / PARTIAL / 5 Items）

含 CONCEPT（JIM-K-0017）、CONSTRAINT（JIM-K-0022、JIM-K-0023）与 CAPABILITY（JIM-K-0014、JIM-K-0015）；可讨论概念与用途边界的界定关系。

### 4.3 平台内容规则（CORE / LIMITED_INGESTION / PARTIAL / 11 Items）

Gate 2.3-R1 新增的候选。11 项 POLICY 分别对应协议第 4.1–4.8 节，**按节分立且各自表达一条规则**，因此存在真实的、无需编造的领域内关系：同一节派生的规则之间（4.1 → 0025/0026；4.2 → 0027/0028；4.3 → 0029/0030）、以及各节规则与平台处理权（4.8 → 0035）之间的关系。scope 明确（全部 Jimeng Product Layer、同一协议版本），缺口（《社区自律公约》、执行阈值、子项粒度）已在 limitations 与本节显式记录，不会造成完整政策假象。

**三者均不表示完整 Knowledge Graph Ready**：只允许在这三个领域内做小规模关系试点，不授权 prerequisite、learning_order、curriculum 或任何课程结构。

### 4.4 模型版本历史（非 Graph Pilot 候选，但本轮具备可讨论的版本沿革结构）

该领域为 SUPPORTING / LIMITED_INGESTION，next_action 仍为 EXPAND_KNOWLEDGE，不列入 Graph Pilot 候选。但它是本轮第二处实质变化：Gate 2.3-R1 新增的 6 项 VERSION_CONTEXT——JIM-K-0036（Seedance 2.5 于 2026-07-31 发布及其定位）、JIM-K-0037（2.5 延续 2.0 的架构、2.0 已发布）、JIM-K-0038（Seedance 2.0 于 2026-02-12 发布及其定位）、JIM-K-0039（2.0 采用统一多模态音频视频联合生成架构并支持文字/图片/音频/视频/标签输入）、JIM-K-0040（2.0 与 1.5 版本的承接比较）、JIM-K-0041（该架构在 2.0 与 2.5 之间的延续）——让它从「8 项单版本能力声明、零版本沿革」变为「含 2.5 / 2.0 / 1.5 三个版本与架构延续关系」。仍为 PARTIAL，因为覆盖只在 Seedance 一侧，Seedream 全部分支与 Seedance 1.0 仍缺。

## 5. Targeted Ingestion Gaps

`next_action = EXPAND_KNOWLEDGE` 的领域共 **12 个**（CORE 10 个 + SUPPORTING 2 个）。按阻塞性质分类：

**A. 证据当前不可读（需用户在浏览器打开并复制正文）**

| Domain | 需要的来源 |
| --- | --- |
| App | P04、P09、P15 |
| 产品版本历史 | P04、P09 |
| 模型版本历史 | M02（以及 M03–M08）；M01 已材料化 |
| 即梦产品基础结构 | P01、P02 |
| 图片生成 | P02、P07 |
| Prompt | P07 |
| 参考图 | P07 |

**B. 已有可读证据，但属于 Readiness 边界或尚未抽取**

| Domain | 情况 |
| --- | --- |
| Seedream | 5 项均为模型层；缺产品层证据（Readiness 边界） |
| 视频生成 | 缺输出与运行规格；Readiness 排除精确规格（边界，非漏抽） |
| 参考视频/音频 | 缺音频上传参数；Readiness 明确排除（边界） |
| 编辑功能 | 缺 PROCEDURE 操作知识；证据只到概念与用途层 |
| 模型选择 | 证据仅一句；Readiness 规定不建完整选择表 |
| 网页端 | 证据只到流程层；P11 candidate |

**注意**：上表是审计结论，不是执行授权。

## 6. Return-to-Source Gaps

`next_action = RETURN_TO_SOURCE` 的领域：**none**。13 个 CORE 中 2 个 ALLOW_INGESTION、11 个 LIMITED_INGESTION，无 DEFER/BLOCKED；剩余 MISSING 领域（App）持有 accepted Evidence，其缺口是证据当前不可读 + 尚未抽取。unresolved C1 与 C3 继续保留，限制未来表述边界。

## 7. Unmapped Knowledge Items

**none.** `registry_total = 41`，`mapped_item_ids` 41 项，`unmapped_item_ids` 为空，并集精确等于 Registry 全部 knowledge_id 且无重叠。

映射说明：11 项 POLICY（JIM-K-0025 ～ JIM-K-0035）只映射到「平台内容规则」——它们都是即梦协议条款，不属于图/视频生成或编辑等功能领域。6 项 VERSION_CONTEXT（JIM-K-0036 ～ JIM-K-0041）按其 Model Layer scope 只映射到「模型版本历史」，**未**同时计入 Seedance 或任何产品领域（JIM-K-0041 引用 M02+M01 也仍属模型层）；也没有因两份发布页末段提到即梦而映射到「产品版本历史」（那句超出 Evidence Scope，未入库）。

## 8. Coverage Risks

1. **只有 Model Layer 的 CORE 领域**：Seedream、图片生成（各 5 项全部模型层）。未改变。
2. **只有 Product Layer 的 CORE 领域**：视频生成、网页端、即梦产品基础结构、平台内容规则；参考图、模型选择、Prompt 各 1–2 项且均产品层。**本轮该风险上升**：平台内容规则新增 11 项全部为产品层，使「产品层单侧」的领域数与 Item 数都增加。
3. **knowledge_type 分布**：CAPABILITY 13、PROCEDURE 4、CONCEPT 4、CONSTRAINT 3、**POLICY 11**、**VERSION_CONTEXT 6**。骨架 6 类**已全部具备**，且版本沿革不再只覆盖单一版本：现有 2.5 / 2.0 / 1.5 三个版本与一条架构延续关系。但 VERSION_CONTEXT 仍只覆盖 Seedance 一侧，Seedream 分支沿革为空。
4. **version_scope 仍偏窄**：41 项的 version_scope 取值集中在 `Seedance 2.5`、`Seedream 5.0 Pro`、`Seedance 2.5；2026-10-03 公开产品页`、`2025-08-25 更新；2025-09-01 生效`（协议），本轮新增 `Seedance 2.0；发布于 2026-02-12`、`Seedance 2.0；2026-02-12 发布页`、`Seedance 2.0 与 1.5 版本`、`Seedance 2.0（M02）与 Seedance 2.5（M01）`。仍无 Seedream 分支沿革、无 1.0、无 unknown。该风险明显缓解但未消除。
5. **是否存在单点被误判 COVERED**：未发现，COVERED 仍为 0。平台内容规则虽有 11 项且覆盖 4.1–4.8 全部小节，仍按「缺《社区自律公约》、缺执行阈值、子项未逐条原子化」保持 PARTIAL。
6. **Item 全部为 draft / DOCUMENTED**：41 项无 validated、无 OBSERVED / INFERRED。覆盖只成立于官方文档层。
7. **新增风险：POLICY 全部来自同一份协议的同一节区**。11 项共享同一 Evidence Unit（P14）与同一版本范围，来源多样性极低；若做关系试点，其关系的证据基础单一，输出不得暗示多来源交叉验证。
8. **新增风险：条款版本时效**。协议版本为 2025-09-01 生效，而评估日为 2026-10-03；该节条文是否在期间修订未核验。POLICY Item 的 version_scope 已如实标注该版本范围，但读者不应把其当作最新条款保证。

## 9. Recommendation

```text
overall_recommendation: NEEDS_TARGETED_INGESTION
```

理由：

- 13 个 CORE 中 COVERED 仍为 0（PARTIAL 12 / MISSING 1）；
- VERSION_CONTEXT 已增至 6 项，模型版本历史首次具备 2.5 / 2.0 / 1.5 三个版本与架构延续关系；但**产品版本历史仍为 MISSING**（P04/P09 未取得），Seedream 分支沿革亦为空。两个领域的根因仍是**证据不可读**而非抽取不足；
- 来源许可整体已存在（13 个 CORE 中 0 个 DEFER/BLOCKED），因此不选 `RETURN_TO_SOURCE_FIRST`；
- 3 个 Graph Pilot 候选领域仍不足以支撑整个 Track 的图谱试点，CORE COVERED 仍为 0，故不选 `READY_FOR_GRAPH_PILOT`。

**下一波优先缺口**（需单独授权）：

1. **产品版本历史**（CORE MISSING）：需要 **P04/P09**（App Store 版本记录）。
2. **模型版本沿革补充**：M02 已材料化；仍需 **M03/M04**（Seedance 1.5 pro / 1.0）与 **M05–M08**（Seedream 各分支）。
3. **产品端上线事实**：M01 与 M02 的末段都写着该版本「已上线即梦 AI」，但两句都**超出各自 evidence_scope**，本轮未入库。若要记录该产品端事实，需先由 Source Engine 决定是否为其拆出新的 Product Layer Evidence Unit。
4. 产品结构 CONCEPT：需要 **P01/P02**。
5. PROCEDURE 深化：需要 **P07**。
6. POLICY 细化：若要把 4.4/4.5/4.6 的子项逐条原子化，需要确认该粒度是否符合预期（当前以节为粒度，对应归一化复核中的 NR-0016 NEEDS_REVIEW）。

本文件到此停止：**不进入 Gate 3**，不自行开始新一轮 Ingestion。
