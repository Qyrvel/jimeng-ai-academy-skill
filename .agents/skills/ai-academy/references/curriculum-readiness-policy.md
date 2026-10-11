# Curriculum Readiness Policy

本政策只判断 Track 是否具备课程设计条件，不生成 Course、Module、Lesson、Quiz、Homework、Teaching sequence 或 Student State。

## 分层与评估单位

Source Readiness、Knowledge Readiness、Graph Readiness、Curriculum Readiness 相互独立。Trusted Sources → Safe Knowledge → Sufficient Competency Coverage → Usable Knowledge Structure → Curriculum Readiness，不得跳层。资料数量、Item 数量或 Validator PASS 不能证明教学充分。

Curriculum Readiness Domain 是达成 Track 目标所需的一类能力或理解领域，优先由既有 Track、Source domains、Knowledge coverage、backbone 归纳，不新建知识 ontology。

## Criticality / Status / Decision

复用 Source criticality，增加 FOUNDATIONAL 作为课程层对基础 CORE 的细分，不改 Source 分类。

- FOUNDATIONAL：缺失将阻断大量后续理解或基础入口。
- CORE：独立完成 Track 主要目标必需。
- SUPPORTING：辅助理解，非当前核心依赖。
- DYNAMIC：价格、会员、积分等独立更新信息。
- OPTIONAL：Track 不依赖的 API、社区、高级实验等。
- OUT_OF_SCOPE：明确排除。

READY 表示限定能力满足下列六项；PARTIAL 表示有可用部分但尚有缺口；BLOCKED 表示关键动作/理解无法支撑；NOT_APPLICABLE 仅对应 OUT_OF_SCOPE。Source PARTIAL 可以支撑限定能力 READY；Source accepted 也可能因材料或程序知识不足而 Curriculum BLOCKED。

决策为 ALLOW_CURRICULUM_DESIGN、TARGETED_INGESTION_FIRST、GRAPH_DATA_EXPANSION_FIRST、DEFER_DYNAMIC、DEFER_OPTIONAL、NOT_APPLICABLE。Domain 许可不是整个 Track 许可，更不是执行下一 Gate 的授权。

## READY 的六项检查

1. Knowledge Presence：原子知识覆盖目标能力，不能只有主题名称。
2. Provenance：核心命题可回溯 accepted 且实际可读的证据范围；缺本地材料不凭历史 accepted 代替正文。
3. Scope Stability：无影响目标的混层、版本歧义、未决冲突。
4. Procedural Sufficiency：实际操作有足够 PROCEDURE / CAPABILITY / CONSTRAINT；仅识别能力名称不能支持独立执行。
5. Graph Usability：依赖、流程、约束、版本结构已可用，或明确能依冻结合同安全扩图；关键结构须预先补齐时记 GRAPH_DATA_EXPANSION_FIRST。
6. Critical Missing Knowledge：不存在使学习者仍无法完成该目标动作的关键缺口。

draft 不自动升级 validated；可审核其已限定内容以判断设计准备度，不能据此发布教学或承诺实操。机器只检查记录一致性，证据充分性由 Agent/Human 审计。

## 缺口与 Track verdict

SOURCE_GAP → SOURCE_ENGINE：证据不存在、不足或未材料化，先回 Source；不必然需要新来源发现。
KNOWLEDGE_INGESTION_GAP → KNOWLEDGE_ENGINE：已有足够可读证据但缺必要 Item。
GRAPH_DATA_GAP → GRAPH_DATA_EXPANSION：Item 已在 Registry，缺必要实际结构，使用 Frozen Baseline，不改合同。

每个 blocking gap 记录缺失能力、阻断理由、预期知识类型、现有来源支持、所需引擎和独立验收条件。JSON 保存最小字段；详细证据与验收写 Markdown。非阻断缺口放 known_gaps，不混入 blocking_gaps。

READY_FOR_CURRICULUM_DESIGN：FOUNDATIONAL / CORE 全部 READY，剩余仅非阻断支持/动态/可选事项。
READY_AFTER_TARGETED_INGESTION：方向明确，有有限可枚举的核心阻断；先 targeted ingestion / graph expansion，再复审。
NOT_READY_FOR_CURRICULUM_DESIGN：目标或基础体系仍广泛缺失，无法界定有限修复集。

有核心阻断时不得边设计课程边补知识。输出最小阻断集合与修复顺序，不用 wishlist 代替验收。Dynamic/Optional 若是实际核心依赖则不能用 defer 隐藏；非依赖分别 DEFER_DYNAMIC / DEFER_OPTIONAL。

## 版本、分层与 Graph 边界

稳定概念和 workflow 优先；版本知识用 VERSION_CONTEXT，按钮位置不作为永久基础。动态 UI 可以局部延期，但核心入口或产品逻辑无法确定仍应 PARTIAL/BLOCKED。Product、Model、API 分层，不把模型能力直接当产品开放。

局部平台规则只支持 selected usage rules，不代表完整法律政策或合规保证。Full Graph 不是准备度必要条件；合同就绪不代表数据充分。关键结构无法安全建立才阻断。现有无独立 tuple 去重 guard 的限制不自动阻断；实际数据受影响才记录质量缺口。

教学顺序疑问记 CURRICULUM_ORDER_QUESTION，不回写知识边。发现真正合同缺陷 STOP_AND_REPORT / GRAPH_CONTRACT_REVISION_REQUIRED，不修改 Frozen v1。

## 机器格式与验证

使用 [Schema](../assets/curriculum-readiness.schema.json) 和 [Validator](../scripts/validate_curriculum_readiness.py)。拒绝未知字段、重复 ID、非法枚举、空白文本、悬空 gap、状态/决策/引擎不一致。READY 无 blocking gap；BLOCKED 必须有 gap；blocking decision 必须对应 gap 类型；defer 与 criticality 一致；OUT_OF_SCOPE 必须 NOT_APPLICABLE。READY track 的核心域须 READY 且无 blocking gap；targeted verdict 须存在核心 blocking gap。

Validator 不搜索关键词判断能力充分，不验证自然语言真值。完成审计即停止；只有 READY 才可建议 Gate 4.1，其余有限缺口建议 Gate 4.0-R1，不自动执行。
