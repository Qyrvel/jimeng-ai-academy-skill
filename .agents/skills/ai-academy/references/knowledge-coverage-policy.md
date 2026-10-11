# Knowledge Coverage Policy — Gate 2.2

## 职责与边界

本 Policy 定义 Knowledge Coverage Audit 的判断原则。它补充 [Knowledge Policy](knowledge-policy.md)、[Source Readiness Policy](source-readiness-policy.md) 与 [Knowledge Normalization Policy](knowledge-normalization-policy.md)，不替代来源准入、Evidence Unit、Readiness、Materialization、Normalization、Schema 或任何既有 Validator。

Gate 2.2 是审计，不是补知识：只回答「当前真实 Knowledge Item 覆盖了哪些领域、哪些领域不足、下一步应先做什么」，不新增、不修改、不删除任何 Knowledge Item，不联网，不进行 Source Discovery。

## Source Readiness ≠ Knowledge Coverage

两者必须分开记录，不得混为一谈：

- **Source Readiness** 表示「这个领域是否已有足够证据，可以安全抽取知识」，取值来自 readiness-assessment.md 的 Decision（ALLOW_INGESTION / LIMITED_INGESTION / DEFER / NOT_APPLICABLE）。
- **Knowledge Coverage** 表示「这个领域目前已经实际形成了多少可用 Knowledge Item」，取值来自本 Gate 的审计结论。

一个领域完全可以 Source = READY 而 Knowledge Coverage = MISSING：来源已准备好，但尚未进行实际抽取。反之，Knowledge Coverage 好也绝不代表来源已完整。

因此本 Gate 禁止：

- 用 Source Decision 直接推出 Coverage Status；
- 用 Coverage Status 反推或升级 Source Decision（`source_ingestion_decision` 必须照抄当前 readiness-assessment.md，不得自行升级或降级）；
- 把 Source Evidence 本身当成 Knowledge Item；
- 根据来源内容、模型记忆或未来计划假想「应该已经有」的知识。

## 只审计当前 Registry

覆盖判断只能依据当前生产 Knowledge Registry 中真实存在的 Item 及其字段（statement、knowledge_type、scope、version_scope、information_type、evidence_refs、limitations）。任何未落成 Item 的知识，无论来源是否已 READY，都只能记为缺口，不得计入覆盖。

## Domain Coverage Status

每个领域只能使用以下一种状态：

### COVERED

当前明确允许的知识范围内，已有足够独立 Knowledge Items，能够代表该领域的主要知识结构，且不需要为了后续分析虚构缺失知识。

COVERED 不代表平台全部知识完整，也不代表课程或实操教学就绪。

### PARTIAL

已有至少一个相关 Knowledge Item，但存在已知重要子范围未形成 Knowledge Item。

### MISSING

当前没有可用 Knowledge Item，但该领域属于当前 Track 且理论上可以存在知识实体。

### DEFERRED

该领域在 Source Readiness 中仍为 DEFER / BLOCKED，当前不应要求 Knowledge Engine 覆盖。

### NOT_APPLICABLE

不属于当前 Track。

## Next Action

每个领域只能选择以下一种下一步动作：

### GRAPH_PILOT_ELIGIBLE

当前已有足够真实 Knowledge Items，可以在未来小规模 Graph Pilot 中使用。不代表完整课程图谱就绪。

### EXPAND_KNOWLEDGE

Source Readiness 已允许（ALLOW_INGESTION 或 LIMITED_INGESTION），但当前 Knowledge Coverage 仍不足。未来应做 Targeted Knowledge Ingestion。

### RETURN_TO_SOURCE

知识缺口的根因是缺乏足够 accepted Evidence，或 Source Readiness 仍不允许入库。必须先回 Source Engine。

### DEFER

当前属于 Dynamic / Optional，且不影响 Creator Track 核心路径。

### NOT_APPLICABLE

不属于当前 Track。

## 不用纯数量决定覆盖

禁止使用简单阈值，例如「≥3 Item = COVERED」。判定时必须检查：

- Knowledge Item 是否真正属于该 Domain，而不是关键词偶然相同；
- knowledge_type 分布是否只有 CAPABILITY；
- statement 是否覆盖不同子知识，还是同一事实的不同表述；
- scope / version_scope 是否过窄；
- 是否只有宣传性能力说明而缺少可教学结构。

数量只能作为辅助信息，且必须在 coverage_rationale 中说明数量之外的判断依据。

## Knowledge Item 映射原则

一个 Item 可以映射到多个 Domain（例如参考视频类 Item 同属 视频生成 与 参考视频/音频），但不得滥映射：只有在 Item 的 statement 与该领域的核心问题直接相关时才计入。

每个领域都必须在 coverage_rationale 中说明为什么所列 Item 足以或不足以代表该领域。若一个 Item 无法合理映射到任何当前 Domain，必须放入 `unmapped_item_ids`，不得强行塞入某个领域；反之也不得为了凑覆盖把领域外 Item 拉入。

映射必须满足总量守恒：`mapped ∪ unmapped` 精确等于真实 Registry 的全部 knowledge_id，且两者不重叠。

## Graph Pilot Eligibility

一个 Domain 可标 GRAPH_PILOT_ELIGIBLE，仅当同时满足：

1. 至少存在多个彼此独立的 Knowledge Items；
2. Item 之间存在真实、可讨论的知识关系潜力；
3. 不需要编造不存在的知识才能形成关系；
4. Product / Model 等 Scope 边界清楚；
5. 已知重大缺口不会让该 Pilot 产生误导性的「完整结构」假象。

Graph Pilot Eligibility 不等于完整 Knowledge Graph Ready，也不授权建立 prerequisite、learning_order 或 curriculum。

## Mechanical Semantic Rules

以下规则可机械判断，并由 Validator 强制执行：

1. coverage_status = MISSING → knowledge_item_ids 必须为空数组。
2. coverage_status = COVERED 或 PARTIAL → knowledge_item_ids 必须非空。
3. coverage_status = DEFERRED → source_ingestion_decision 必须为 DEFER。
4. coverage_status = NOT_APPLICABLE → source_ingestion_decision 必须为 NOT_APPLICABLE 且 next_action = NOT_APPLICABLE。
5. next_action = GRAPH_PILOT_ELIGIBLE → coverage_status 只能为 COVERED 或 PARTIAL。
6. source_ingestion_decision = DEFER → next_action 不得为 GRAPH_PILOT_ELIGIBLE。
7. source_ingestion_decision = ALLOW_INGESTION 或 LIMITED_INGESTION，且 coverage_status = MISSING → next_action 优先应为 EXPAND_KNOWLEDGE；若人为选择 RETURN_TO_SOURCE，必须在 coverage_rationale 中明确写出新的 Source 阻塞原因（Validator 只检查该说明非空，不判断是否合理）。

## Gap 分类

报告必须把缺口明确分为两类，不得混用：

- **Knowledge ingestion gap**：来源已允许入库，但知识抽取尚未完成或不足 → EXPAND_KNOWLEDGE。
- **Source evidence gap**：真正的阻塞来自 accepted Evidence 不足或 Readiness 不允许入库 → RETURN_TO_SOURCE。

## Validator 的边界

Coverage 评估遵循 [Coverage Schema](../assets/knowledge-coverage.schema.json)，并由 [Validator](../scripts/validate_knowledge_coverage.py) 离线检查结构、引用、accounting 守恒与上述可机械判断的规则。

Validator 不判断 COVERED 是否真的合理、Domain 映射是否语义正确、Graph Eligibility 是否内容上充分；这些由 Agent / 人工审核并记录在 coverage report。

PASS 只表示合同与守恒关系成立，不证明覆盖判断正确。

## 与后续 Gate 的关系

本 Gate 只输出审计与建议，不自动开始下一 Gate：不进入 Gate 2.3 或 Gate 3，不创建 Knowledge Graph、prerequisite、learning_order、curriculum、module、lesson、quiz、student state、RAG 或向量数据库。

若审计结论为需要补知识，也必须等待单独授权后才能执行 Targeted Knowledge Ingestion。
