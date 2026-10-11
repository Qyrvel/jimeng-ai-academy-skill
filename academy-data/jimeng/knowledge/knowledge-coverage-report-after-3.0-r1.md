# Jimeng Knowledge Coverage Report（After Gate 3.0-R1）

Gate 2.2 Coverage Assessment 的第五次快照，日期 2026-10-03。使用同一 `knowledge-coverage-policy.md`、`knowledge-coverage.schema.json` 与 `validate_knowledge_coverage.py`。此前四次快照（16 / 24 / 41 / 45 项）均未被修改。

本快照在 Gate 3.0-R1 之后生成，反映的唯一新增是 `JIM-K-0046`（Seedance 2.5 产品页三步流程的第三步）。

## 1. Scope

- 当前生产 Knowledge Item 总数：**46**（Gate 3.0-R1 新增 1 项：JIM-K-0046）。
- 该 Item 为 PROCEDURE / 视频生成 / Jimeng Product Layer，evidence = P10（accepted + AVAILABLE）。
- 本轮未新增 CAPABILITY；未修改旧 45 项。
- P04 按 Gate 3.0-R1 §18 **不在本 Gate 处理**，保留在 Coverage Backlog。

## 2. CORE Coverage Matrix

| Domain | Item Count | Coverage Status | Source Decision | Next Action | Gap |
| --- | --- | --- | --- | --- | --- |
| 即梦产品基础结构 | 4 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺模块与功能关系；需 P01/P02 |
| 网页端 | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺界面结构；端级归属需更精确证据 |
| App | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺 2.3.5（P04，backlog） |
| Seedance | **12** | PARTIAL | ALLOW_INGESTION | GRAPH_PILOT_ELIGIBLE | 缺实测与账号级开放情况；fast 无模型层证据 |
| Seedream | 5 | PARTIAL | ALLOW_INGESTION | EXPAND_KNOWLEDGE | 全为模型层 CAPABILITY |
| 图片生成 | 5 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 需 P02/P07 |
| 视频生成 | **8** | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺输出规格与模型层对照 |
| 参考图 | 1 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺专项能力项与文件规格 |
| 参考视频/音频 | 5 | PARTIAL | LIMITED_INGESTION | GRAPH_PILOT_ELIGIBLE | 缺音频参数与模型层对照 |
| 模型选择 | 1 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 证据仅一句 |
| Prompt | 2 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 需 P07 |
| 编辑功能 | 6 | PARTIAL | LIMITED_INGESTION | EXPAND_KNOWLEDGE | 缺 PROCEDURE；C1 未决 |
| 平台内容规则 | 11 | PARTIAL | LIMITED_INGESTION | GRAPH_PILOT_ELIGIBLE | 缺《社区自律公约》与执行阈值 |

CORE 汇总：PARTIAL 13、MISSING 0、COVERED 0（与 Gate 2.3-R2 相同）。

## 3. Supporting / Dynamic / Optional

- **SUPPORTING**：产品版本历史 3 项、PARTIAL（P04 在 backlog）；模型版本历史 15 项、PARTIAL。
- **DYNAMIC**：会员、积分、实时价格 —— 均 DEFERRED / DEFER / 0 项。
- **OPTIONAL**：Volcano / Ark API、社区经验、可复现实验 —— 均 DEFERRED / DEFER / 0 项；46 项中仍**无任何 OBSERVED Item**。
- **OUT_OF_SCOPE**：API 服务状态 —— NOT_APPLICABLE。

## 4. Graph Pilot Candidates

仍为 3 个，无变化：Seedance、参考视频/音频、平台内容规则。

说明：Gate 3.0-R1 的图形工作**没有改变任何领域的覆盖状态**，也没有改变候选名单。它改变的是**图的表达能力**（新增 `STEP_OF`）与 Pilot 图的完整度（多一个真实节点、多四条真实 Edge），这两者属于 Graph Contract 层，不属于 Coverage 层。不应把「图连成一个分量」误读为「覆盖变好」。

## 5. 本轮唯一实质变化

| 项目 | 变化 |
| --- | --- |
| Knowledge Item 总数 | 45 → **46** |
| 视频生成领域 | 7 → **8** 项；首次包含流程收尾步骤（生成、预览并保存） |
| Seedance 领域 | 11 → **12** 项 |
| PROCEDURE 类型总数 | 4 → **5** |
| Coverage 状态计数 | 不变（PARTIAL 15 / DEFERRED 6 / NOT_APPLICABLE 1） |
| overall_recommendation | 不变（NEEDS_TARGETED_INGESTION） |

## 6. Unmapped Knowledge Items

**none.** `registry_total = 46`，`mapped_item_ids` 46 项，`unmapped_item_ids` 为空，并集精确等于 Registry 全部 knowledge_id 且无重叠。

JIM-K-0046 映射到 **视频生成** 与 **Seedance** 两个领域；未映射到网页端（与第二步 K-0011 的处理保持一致）、即梦产品基础结构（单个流程步骤不构成结构知识）、Prompt（不含提示词内容）或模型版本历史（不是版本沿革知识）。

## 7. Coverage Risks

1. **只有 Model Layer 的 CORE 领域**：Seedream、图片生成。未变。
2. **只有 Product Layer 的 CORE 领域**：视频生成、网页端、即梦产品基础结构、平台内容规则、App。未变。
3. **knowledge_type 分布**：CAPABILITY 13、PROCEDURE 5、CONCEPT 4、CONSTRAINT 3、POLICY 11、VERSION_CONTEXT 10。骨架 6 类齐备。
4. **version_scope 分布**：未变（本轮新增项沿用 `Seedance 2.5；2026-10-03 公开产品页`）。
5. **是否存在单点被误判 COVERED**：未发现，COVERED 仍为 0。
6. **Item 全部为 draft / DOCUMENTED**：46 项无 validated、无 OBSERVED / INFERRED。
7. **既有风险：POLICY 全部来自同一份协议**；产品侧知识集中在 2.5 产品页。
8. **新增风险：产品流程知识的粒度治理成本**。现在同一流程有 5 个 PROCEDURE Item（K-0009 流程含产物、K-0024 流程结构、K-0010 第一步、K-0011 第二步、K-0046 第三步）。它们由 Normalization Review 分别判定（NR-0004/0005/0018/0036/0037/0038），并非重复；但后续若继续在同一流程上新增 Item，必须先确认是否真的缺少某个**官方步骤**，而不是把同一步骤的内部动作拆出来。

## 8. Recommendation

```text
overall_recommendation: NEEDS_TARGETED_INGESTION
```

理由：

- 13 个 CORE 中 COVERED 仍为 0（PARTIAL 13、MISSING 0）；
- 本轮只补了一个流程步骤，未改变任何领域的覆盖性质；
- 剩余 CORE 缺口的根因仍是**证据不可读**（P01/P02、P07、P04）与 **Readiness 明确排除**（数值规格、完整选择表）；
- 3 个 Graph Pilot 候选领域仍不足以支撑整个 Track 的图谱试点。

**下一波优先缺口**（需单独授权）：

1. **P04（iOS 2.3.5 条目）**：仍在 Coverage Backlog；按 Gate 3.0-R1 §18 本轮不处理。
2. **P01/P02**：产品结构 CONCEPT。
3. **P07**：提示词与模型选择的方法类知识。
4. **M03–M08**：Seedance 1.0 与 Seedream 各分支的版本沿革。
5. **Seedance 2.0 fast 的模型层证据**：当前仍 `BLOCKED_BY_EVIDENCE`（Gate 3.0-R1 候选 #3）。
6. **Product Layer 的 Seedance 2.0 能力项**：当前仍 `BLOCKED_BY_EVIDENCE`（候选 #4）。

本文件到此停止：**不进入 Gate 3.1 或 Curriculum**，不自行开始新一轮 Ingestion。
