# Jimeng Knowledge Coverage Report（After Gate 2.3-R2）

Gate 2.2 Coverage Assessment 的第四次快照，日期 2026-10-03。使用同一 `knowledge-coverage-policy.md`、`knowledge-coverage.schema.json` 与 `validate_knowledge_coverage.py`。前三次快照（`coverage-assessment.json` 16 项、`coverage-assessment-after-2.3.json` 24 项、`coverage-assessment-after-2.3-r1.json` 41 项）均未被修改。

本快照在 Gate 2.3-R2 全部工作完成后生成，反映两次新增：P16/P17 拆单元后的 2 项 Product Layer 部署知识，以及 P09 材料化后的 2 项 App 版本记录。

## 1. Scope

- 当前生产 Knowledge Item 总数：**45**（JIM-K-0042 ～ JIM-K-0045 共 4 项为本 Gate 新增）。
- 其中 JIM-K-0042/0043 来自新拆出的 P16/P17（Product Layer 上线声明）；JIM-K-0044/0045 来自 P09（即梦 iOS 2.3.0 版本记录）。
- 本轮未新增 CAPABILITY；未修改旧 41 项。
- 领域集合沿用 readiness-assessment.md 的 22 个领域，未改动任何 Criticality 或 Source Ingestion Decision。

## 2. CORE Coverage Matrix

| Domain | Item Count | Coverage Status | Source Decision | Next Action | Gap |
| --- | --- | --- | --- | --- | --- |
| 即梦产品基础结构 | 4 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺模块与功能关系；需 P01/P02 |
| 网页端 | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺界面结构；端级归属需更精确证据 |
| **App** | **2** | **PARTIAL**（原 MISSING） | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺 2.3.5（P04）与其它版本、Android 与操作类知识 |
| Seedance | 11 | PARTIAL | ALLOW_INGESTION | GRAPH_PILOT_ELIGIBLE | 缺实测与账号级开放情况；fast 版无模型层证据 |
| Seedream | 5 | PARTIAL | ALLOW_INGESTION | EXPAND_KNOWLEDGE | 全为模型层 CAPABILITY |
| 图片生成 | 5 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 需 P02/P07 |
| 视频生成 | 7 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺输出规格与模型层对照 |
| 参考图 | 1 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺专项能力项与文件规格 |
| 参考视频/音频 | 5 | PARTIAL | LIMITED_INGESTION | GRAPH_PILOT_ELIGIBLE | 缺音频参数与模型层对照 |
| 模型选择 | 1 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 证据仅一句；不建完整选择表 |
| Prompt | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 需 P07 |
| 编辑功能 | 6 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺 PROCEDURE；C1 未决 |
| 平台内容规则 | 11 | PARTIAL | LIMITED_INGESTION | GRAPH_PILOT_ELIGIBLE | 缺《社区自律公约》与执行阈值 |

**CORE 汇总：PARTIAL 13、MISSING 0、COVERED 0。**

### 本轮重点问题的回答

1. **CORE MISSING 是否仍为 1？** **否——已降为 0。** App 由 MISSING 升为 PARTIAL，这是本工程首次出现 CORE 领域零 MISSING。
2. **App 是否因 P09 进入 PARTIAL？** **是。** P09 材料化成功，新增 JIM-K-0044（iOS 2.3.0 版本条目存在及页面显示日期）与 JIM-K-0045（该版本更新说明记载上线 Seedance 2.0 fast 模型）。
3. **产品版本历史是否因 P09 进入 PARTIAL？** 该领域已在 P16/P17 时由 MISSING 升为 PARTIAL；P09 使其**内容性质改善**：从「只有模型上线声明」变为「含即梦产品自身的版本记录」（JIM-K-0044），项目数 2 → 3。仍为 PARTIAL，因为只有 2.3.0 一条且页面日期不含年份。
4. **模型选择 / 视频生成 / 产品基础结构是否因 P16/P17 改善？** 仅**即梦产品基础结构**改善（2 → 4 项）。模型选择与视频生成未改善：两项上线声明不含可选集合与输出规格。
5. **Graph Pilot Candidates 是否变化？** **未变**，仍 3 个（Seedance、参考视频/音频、平台内容规则）。CORE MISSING 归零并未把任何新领域推入候选——候选标准要求「多个彼此独立 Item + 真实关系潜力 + 不编造知识 + Scope 边界清楚 + 无误导性完整假象」，App（2 项）、产品版本历史（3 项）与其余领域仍不满足。

## 3. Supporting / Dynamic / Optional

- **SUPPORTING**：
  - **产品版本历史**：3 项、PARTIAL —— 首次含即梦产品自身版本记录（K-0044）。
  - **模型版本历史**：**15 项**、PARTIAL —— 含 7 项 VERSION_CONTEXT；其中 K-0045 记载了 Seedance 2.0 fast 这一模型变体的存在事实，但其证据是**产品更新说明**而非模型官方说明。
- **DYNAMIC**：会员、积分、实时价格 —— 均 DEFERRED / DEFER / 0 项。
- **OPTIONAL**：Volcano / Ark API、社区经验、可复现实验 —— 均 DEFERRED / DEFER / 0 项；45 项中仍**无任何 OBSERVED Item**。
- **OUT_OF_SCOPE**：API 服务状态 —— NOT_APPLICABLE。

## 4. Graph Pilot Candidates

仍为 3 个，本轮无变化：

1. **Seedance**（CORE / ALLOW_INGESTION / PARTIAL / 11 Items）
2. **参考视频/音频**（CORE / LIMITED_INGESTION / PARTIAL / 5 Items）
3. **平台内容规则**（CORE / LIMITED_INGESTION / PARTIAL / 11 Items）

均不表示完整 Knowledge Graph Ready，不授权 prerequisite、learning_order 或 curriculum。

## 5. Targeted Ingestion Gaps

`next_action = EXPAND_KNOWLEDGE` 的领域共 **12 个**（CORE 10 个 + SUPPORTING 2 个）。按阻塞性质：

**A. 证据当前不可读（需用户提供正文）**

| Domain | 需要的来源 |
| --- | --- |
| 即梦产品基础结构 | P01、P02 |
| 图片生成 | P02、P07 |
| Prompt | P07 |
| 参考图 | P07 |
| 模型版本历史 | M03–M08；以及 Seedance 2.0 fast 的模型层证据 |
| App | P04（2.3.5 条目） |
| 产品版本历史 | P04 及其它版本条目 |

**B. 属 Readiness 边界或证据本身只到当前粒度**

| Domain | 情况 |
| --- | --- |
| Seedream | 缺产品层证据（Readiness 边界） |
| 视频生成 | 缺输出与运行规格；Readiness 排除精确规格 |
| 参考视频/音频 | 缺音频上传参数；Readiness 明确排除 |
| 编辑功能 | 缺 PROCEDURE；证据只到概念与用途层 |
| 模型选择 | 证据仅一句；Readiness 规定不建完整选择表 |
| 网页端 | 证据只到流程层；端级归属需更精确证据 |

**注意**：上表是审计结论，不是执行授权。

## 6. Return-to-Source Gaps

`next_action = RETURN_TO_SOURCE` 的领域：**none**。13 个 CORE 中 2 个 ALLOW_INGESTION、11 个 LIMITED_INGESTION，无 DEFER/BLOCKED；本轮之后已无 MISSING 领域。unresolved C1 与 C3 继续保留。

## 7. Unmapped Knowledge Items

**none.** `registry_total = 45`，`mapped_item_ids` 45 项，`unmapped_item_ids` 为空，并集精确等于 Registry 全部 knowledge_id 且无重叠。

本轮新增项的映射：

| Item | 映射到的领域 | 未映射到 | 理由 |
| --- | --- | --- | --- |
| JIM-K-0042 | 即梦产品基础结构、产品版本历史 | 网页端 / App / 视频生成 / 模型选择 | 部署句只说「即梦 AI」，不区分端；不含流程、规格或可选集合 |
| JIM-K-0043 | 即梦产品基础结构、产品版本历史 | 同上 | 同上 |
| JIM-K-0044 | **App**、产品版本历史 | 网页端 / 模型版本历史 | 明确为 iOS 中国区 App 2.3.0 条目 |
| JIM-K-0045 | **App**、产品版本历史、模型版本历史 | 视频生成 / 模型选择 / Seedance | 命题是 App 更新说明；不计入视频生成与模型选择以免夸大覆盖；计入模型版本历史是因为它记载了一个模型变体（fast）的存在事实 |

## 8. Coverage Risks

1. **只有 Model Layer 的 CORE 领域**：Seedream、图片生成。未变。
2. **只有 Product Layer 的 CORE 领域**：视频生成、网页端、即梦产品基础结构、平台内容规则、App。**风险上升**：App 与产品版本历史的新增项全为产品层，产品侧单边进一步加重。
3. **knowledge_type 分布**：CAPABILITY 13、PROCEDURE 4、CONCEPT 4、CONSTRAINT 3、POLICY 11、**VERSION_CONTEXT 10**（6 项 Model Layer + 4 项 Product Layer）。骨架 6 类齐备；VERSION_CONTEXT 已成为第二大类。
4. **version_scope 分布**：本轮新增 `iOS 中国区；App 2.3.0`（2 项）。仍未出现 Seedream 分支沿革与 unknown 版本。
5. **是否存在单点被误判 COVERED**：未发现，COVERED 仍为 0。App 虽有 2 项，仍按「只有一条版本记录、页面日期不含年份」保持 PARTIAL。
6. **Item 全部为 draft / DOCUMENTED**：45 项无 validated、无 OBSERVED / INFERRED。
7. **既有风险：POLICY 全部来自同一份协议**（11 项共享 P14）。
8. **新增风险：App 侧知识的单一来源与时点性**。JIM-K-0044/0045 均只来自 P09 一条版本记录，且页面日期只有「7月27日」不含年份；不得据此推断该版本的年份、先后顺序或当前可用性。
9. **新增风险：模型变体的证据层级偏低**。「Seedance 2.0 fast」目前只有产品更新说明这一处证据（P09），没有模型层官方说明。JIM-K-0045 已把这一点写入 scope 与 limitations（不代表模型层技术能力），但仍应避免把它当作 fast 版的完整知识。
10. **既有风险：同一 URL 多单元并存**。P16/M01 与 P17/M02 各共用同一 location，仅 Evidence Scope 不同；引用时必须按单元而不按页面计数。

## 9. Recommendation

```text
overall_recommendation: NEEDS_TARGETED_INGESTION
```

理由：

- **CORE MISSING 已降为 0**，但 13 个 CORE 全部为 PARTIAL、**COVERED 仍为 0**：没有任何 CORE 领域达到「无需虚构缺失知识即可代表主要知识结构」的标准；
- 剩余缺口的根因在 CORE 侧主要是**证据不可读**（P01/P02、P07、P04、M03–M08）与 **Readiness 明确排除**（数值规格、完整选择表），属抽取与证据可达性问题，而非 Readiness 不允许；
- 来源许可整体已存在（13 个 CORE 中 0 个 DEFER/BLOCKED），因此不选 `RETURN_TO_SOURCE_FIRST`；
- 3 个 Graph Pilot 候选领域不足以支撑整个 Track 的图谱试点，故不选 `READY_FOR_GRAPH_PILOT`。

**下一波优先缺口**（需单独授权）：

1. **P04（iOS 2.3.5 条目）**：与 P09 成对后可补足 App 与产品版本历史的版本序列。按 Gate 2.3-R2 §4，该来源保持 BLOCKED，需用户提供正文。
2. **P01/P02**：产品结构 CONCEPT，是「即梦产品基础结构」唯一的实质缺口来源。
3. **P07**：提示词与模型选择的方法类知识。
4. **M03–M08**：Seedance 1.0 与 Seedream 各分支的版本沿革。
5. **Seedance 2.0 fast 的模型层证据**：当前只有产品更新说明；若要把它作为模型知识，需要官方模型侧材料。
6. **端级证据**：网页端与 App 若要获得部署类知识，需要明确区分端的证据。

本文件到此停止：**不进入 Gate 3**，不自行开始新一轮 Ingestion。
