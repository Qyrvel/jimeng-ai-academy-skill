# Jimeng Knowledge Coverage Report（After Gate 2.3）

Gate 2.2 Coverage Assessment 的重跑版本，日期 2026-10-03。使用同一 `knowledge-coverage-policy.md`、`knowledge-coverage.schema.json` 与 `validate_knowledge_coverage.py`。Gate 2.2 的历史快照（`coverage-assessment.json`、`knowledge-coverage-report.md`）未被修改，保留其当时结论。

## 1. Scope

- 当前生产 Knowledge Item 总数：**24**（Gate 2.3 新增 8 项：JIM-K-0017 ～ JIM-K-0024）。
- 本轮仍不新增知识：本文件只是 Gate 2.3 之后的覆盖审计。
- 领域集合沿用 readiness-assessment.md 的 22 个领域，未改动任何 Criticality 或 Source Ingestion Decision。
- 覆盖判断只依据当前 Registry 中真实存在的 Item。

## 2. CORE Coverage Matrix

| Domain | Item Count | Coverage Status | Source Decision | Next Action | Gap |
| --- | --- | --- | --- | --- | --- |
| 即梦产品基础结构 | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺产品模块与功能关系；需 P01/P02（BLOCKED） |
| 网页端 | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺界面结构与入口关系；P11 candidate |
| App | 0 | MISSING | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 需 P04/P09/P15（BLOCKED） |
| Seedance | 11 | PARTIAL | ALLOW_INGESTION | **GRAPH_PILOT_ELIGIBLE** | 缺 VERSION_CONTEXT（M01/M02 BLOCKED）与实测 |
| Seedream | 5 | PARTIAL | ALLOW_INGESTION | EXPAND_KNOWLEDGE | 全为模型层 CAPABILITY；产品映射缺失 |
| 图片生成 | 5 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 只有模型层一侧；需 P02/P07（BLOCKED） |
| 视频生成 | 7 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺输出与运行规格；无模型层对照项 |
| 参考图 | 1 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺参考图专项能力项与文件规格 |
| 参考视频/音频 | 5 | PARTIAL | LIMITED_INGESTION | **GRAPH_PILOT_ELIGIBLE** | 缺音频参数与模型层对照项 |
| 模型选择 | 1 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 证据仅一句；不建完整选择表 |
| Prompt | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺结构与方法；A07 candidate |
| 编辑功能 | 6 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺 PROCEDURE 操作知识；C1 影响画布 UI |
| 平台内容规则 | 0 | MISSING | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 需 P14（POLICY，BLOCKED） |

CORE 汇总：PARTIAL 11、MISSING 2、COVERED 0。

与 Gate 2.2 相比：CORE 状态计数**没有变化**（COVERED 仍为 0）。变化发生在结构层而非状态层：

- **参考视频/音频** Item 数 2 → 5，并从「全为 CAPABILITY」变为含 CONCEPT 与 CONSTRAINT，因此新增为 Graph Pilot 候选；
- **视频生成** 5 → 7（新增 CONCEPT 与 PROCEDURE）；
- **编辑功能** 4 → 6（新增 CONCEPT 与 CONSTRAINT，不再是全 CAPABILITY）；
- **Prompt** 1 → 2（新增首个 CONCEPT）；
- **Seedance** 9 → 11（新增 CONCEPT 与 CONSTRAINT）。

## 3. Supporting / Dynamic / Optional

- **SUPPORTING**：产品版本历史（0 项、MISSING、LIMITED_INGESTION、EXPAND_KNOWLEDGE，需 P04/P09 正文）；模型版本历史（8 项、PARTIAL、LIMITED_INGESTION、EXPAND_KNOWLEDGE，仍无任何 VERSION_CONTEXT，需 M01–M08 正文）。
- **DYNAMIC**：会员、积分、实时价格 —— 均 DEFERRED / DEFER / DEFER / 0 项，与 Gate 2.2 一致。
- **OPTIONAL**：Volcano / Ark API、社区经验、可复现实验 —— 均 DEFERRED / DEFER / DEFER / 0 项。24 项中仍**无任何 OBSERVED Item**。
- **OUT_OF_SCOPE**：API 服务状态 —— NOT_APPLICABLE。

## 4. Graph Pilot Candidates

`next_action = GRAPH_PILOT_ELIGIBLE` 的领域由 Gate 2.2 的 1 个增至 **2 个**：

### 4.1 Seedance（CORE / ALLOW_INGESTION / PARTIAL / 11 Items）

Model Layer 3 项（JIM-K-0001 音视频联合生成定位、JIM-K-0002 参考视频信息理解、JIM-K-0003 绿幕编辑）与 Product Layer 8 项（JIM-K-0009、0010、0012、0013、0014、0015、0017、0023）。Gate 2.3 补入 JIM-K-0017（参考生视频概念）与 JIM-K-0023（参考生视频用途边界），使该领域同时含 CONCEPT、CONSTRAINT、CAPABILITY、PROCEDURE 四类，可讨论的真实关系包括：同层流程包含关系、跨层「模型具备能力 ↔ 产品提供能力」对照、以及概念与其用途边界之间的界定关系。已知最大缺口（部署映射 unresolved C3）已在相关 Item 的 limitations 中显式标注，不会造成完整结构假象。

### 4.2 参考视频/音频（CORE / LIMITED_INGESTION / PARTIAL / 5 Items）

JIM-K-0014（带声音视频与音画协同）、JIM-K-0015（参考视频控制复杂动作）、JIM-K-0017（参考生视频概念）、JIM-K-0022（参考素材作用边界）、JIM-K-0023（参考生视频用途边界）。该领域现已含 CONCEPT 与 CONSTRAINT，可讨论的关系包括概念与用途边界的界定、用途与能力之间的支撑关系。缺口（音频参数、模型层对照项）已在 limitations 与本节显式记录。

**两者均不表示完整 Knowledge Graph Ready**：本结论只允许在这两个领域内做小规模关系试点，不授权 prerequisite、learning_order、curriculum 或任何课程结构，也不表示其余 20 个领域已就绪。

## 5. Targeted Ingestion Gaps

`next_action = EXPAND_KNOWLEDGE` 的领域共 **13 个**（CORE 11 个 + SUPPORTING 2 个），全部为 **Knowledge ingestion gap**（来源许可已存在，知识抽取未完成或证据本轮不可读）。

Gate 2.3 后剩余缺口按「阻塞性质」分为两类：

**A. 证据本轮不可读（需要用户在浏览器打开并复制正文后才能推进）**

| Domain | 需要的来源 |
| --- | --- |
| 平台内容规则 | P14（用户协议第 4.1–4.8） |
| 产品版本历史 | P04、P09 |
| 模型版本历史 | M01–M08 |
| App | P04、P09、P15 |
| 即梦产品基础结构 | P01、P02 |
| 图片生成 | P02、P07 |
| Prompt | P07 |
| 参考图 | P07 |

**B. 已有可读证据但本轮未抽取（骨架目标之外或优先级较低）**

| Domain | 情况 |
| --- | --- |
| Seedream | 5 项均为模型层；缺产品层证据（非「未抽取」而是证据不可读） |
| 视频生成 | 缺输出与运行规格；现有可读材料不含这些数值，Readiness 亦排除精确规格 → 属 Readiness 边界，不是漏抽 |
| 参考视频/音频 | 缺音频上传参数；Readiness 明确排除上传参数 → 同上 |
| 编辑功能 | 缺 PROCEDURE 操作知识；证据只到概念与用途层 |
| 模型选择 | 证据仅一句；Readiness 明确不建完整选择表 |
| 网页端 | 证据只到流程层；P11 candidate |

**注意**：上表是审计结论，不是执行授权。本轮未创建任何新 Item 之后的新增；下一波 Ingestion 需单独授权。

## 6. Return-to-Source Gaps

`next_action = RETURN_TO_SOURCE` 的领域：**none**。

没有任何 CORE 领域的阻塞被判定为「Source Readiness 不允许」：13 个 CORE 中 2 个 ALLOW_INGESTION、11 个 LIMITED_INGESTION，无 DEFER/BLOCKED。3 个 MISSING 领域（App、平台内容规则、产品版本历史）均持有 accepted Evidence，其缺口是**证据当前不可读 + 尚未抽取**，属于 ingestion 侧问题；但若长期无法取得这些正文，它们会实际转化为 Evidence 可达性问题——该风险记录在此，不作为本轮判定依据。

仍保留的 Source 层风险：unresolved C1（画布新旧 UI 与灰度）与 C3（Pro/Flash 命名与产品开放映射），继续限制未来表述边界。

## 7. Unmapped Knowledge Items

**none.** `registry_total = 24`，`mapped_item_ids` 24 项，`unmapped_item_ids` 为空，并集精确等于 Registry 全部 knowledge_id 且无重叠。

新增 8 项的映射：JIM-K-0017（Seedance、参考视频/音频）、JIM-K-0018（视频生成）、JIM-K-0019（编辑功能）、JIM-K-0020（Prompt）、JIM-K-0021（编辑功能）、JIM-K-0022（参考视频/音频）、JIM-K-0023（Seedance、参考视频/音频）、JIM-K-0024（视频生成）。

未滥映射示例：JIM-K-0022 虽涉及参考图片，但核心命题是参考素材的作用边界，已映射到「参考视频/音频」，未计入「参考图」；JIM-K-0017 未计入「视频生成」，因为其命题是参考生视频这一方式的概念。

## 8. Coverage Risks

1. **只有 Model Layer 的 CORE 领域**：Seedream、图片生成（各 5 项全部模型层）。Gate 2.3 未改变该结构。
2. **只有 Product Layer 的 CORE 领域**：视频生成、网页端、即梦产品基础结构；参考图、模型选择、Prompt 各 1–2 项且均产品层。**风险较 Gate 2.2 略升**：Prompt 从 1 项增至 2 项，参考视频/音频从 2 项增至 5 项，但两者仍是单层（产品层），新增的结构知识没有带来模型层对照。
3. **knowledge_type 分布改善但仍偏斜**：CONCEPT 4、CONSTRAINT 3、CAPABILITY 13、PROCEDURE 4、POLICY 0、VERSION_CONTEXT 0。骨架类型从 0/6 增至 2/6，但**政策类与版本沿革类仍完全空缺**，这是当前最严重的结构缺口。
4. **version_scope 仍然过窄**：24 项只覆盖 `Seedance 2.5`、`Seedream 5.0 Pro` 与 `Seedance 2.5；2026-10-03 公开产品页` 三种取值，无任何历史版本、无 unknown。Gate 2.3 未能改善（VERSION_CONTEXT 证据全部 BLOCKED）。
5. **是否存在单点被误判 COVERED**：未发现，因为 COVERED 仍为 0。参考视频/音频虽已达 5 项并含两类骨架，仍按「缺音频参数与模型层对照」保持 PARTIAL，未升级为 COVERED。
6. **Item 全部为 draft / DOCUMENTED**：24 项无 validated、无 OBSERVED / INFERRED。覆盖只成立于官方文档层。
7. **新增风险：两个 Graph Pilot 候选都建立在同一个 URL 与同一版本上**。Seedance 与参考视频/音频的可读证据主要来自同一份 P12 与 P10（Seedance 2.5 产品页），若做关系试点，其关系的来源多样性有限；报告与试点输出都必须避免让读者以为这是多来源交叉验证的结果。

## 9. Recommendation

```text
overall_recommendation: NEEDS_TARGETED_INGESTION
```

理由：

- 13 个 CORE 中仍为 COVERED 0 / PARTIAL 11 / MISSING 2；
- **POLICY 与 VERSION_CONTEXT 仍为 0**，两个 CORE/SUPPORTING 领域（平台内容规则、产品版本历史）仍完全空置，其根因不是抽取不足而是**证据不可读**（P14、P04/P09、M01–M08 本轮全部 MATERIALIZATION_BLOCKED）；
- 来源许可整体已存在（13 个 CORE 中 0 个 DEFER/BLOCKED），因此仍不选 `RETURN_TO_SOURCE_FIRST`；
- 现有 2 个 Graph Pilot 候选领域不足以支撑整个 Track 的图谱试点，故不选 `READY_FOR_GRAPH_PILOT`。

**下一波优先缺口（按价值排序，需单独授权）**：

1. POLICY 骨架 —— 需要 **P14** 正文（用户协议第 4.1–4.8 用户行为规范），可按节建立原子 POLICY Item。
2. VERSION_CONTEXT 骨架 —— 需要 **P04/P09**（App 版本记录）与 **M01–M08**（模型发布与报告），可建立版本发布与历史版本存在类 Item。
3. 产品结构 CONCEPT —— 需要 **P01/P02** 正文。
4. PROCEDURE 深化 —— 需要 **P07** 正文（提示词、额度、模型选项 FAQ）。

以上四项都卡在同一处：本会话无法直接读取任何外部来源。与 P10/P12/P13 相同，由你在浏览器真实打开并复制正文即可解锁。

本文件到此停止：**不进入 Gate 3**，不自行开始 Gate 2.3-R1，不创建 Knowledge Graph、prerequisite、learning_order、curriculum、module、lesson、quiz、student state、RAG 或向量数据库。

## 10. 快照性质说明

Gate 2.2 的 `coverage-assessment.json` 与 `knowledge-coverage-report.md` 保留为 **2026-10-03 当时 16 项**的历史快照，未被修改。需要明确的是：该快照的 `item_accounting` 是**当时**的守恒关系，因此用当前 24 项的 Registry 去校验旧快照会（正确地）失败：

```
validate_knowledge_coverage.py coverage-assessment.json pilot-knowledge-registry.json
FAIL — registry_total: expected 24; found 16，且 JIM-K-0017 ～ JIM-K-0024 未纳入 accounting
```

这不是旧文件损坏，而是覆盖评估天然是快照。可核验的配对是：旧快照 ↔ 16 项时的 Registry（历史结论），新快照 `coverage-assessment-after-2.3.json` ↔ 当前 24 项 Registry（本轮 PASS）。
