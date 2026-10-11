# Source Readiness Policy

## 核心原则

Source Completeness 不等于 Knowledge Ingestion Readiness。资料不必达到 100% 完整才开始知识入库；必须按 Track、领域、版本和证据范围判断，不能只给整个平台一个 READY / NOT_READY。

本规则补充 [Source Policy](source-policy.md)，不替代来源准入、Evidence Unit、JSON Schema 或语义校验。Readiness 是人工证据判断，不新增数据库或算法。

## 范围重要性

| Criticality | 含义 |
| --- | --- |
| CORE | 当前 Track 必需的核心领域；缺可信证据时阻止该领域入库。 |
| SUPPORTING | 帮助完整理解的背景；缺失不阻止已有证据支持的核心范围入库。 |
| DYNAMIC | 价格、积分、套餐、实时配额、促销和服务状态等易变信息；独立维护，不阻止稳定知识入库。 |
| OPTIONAL | 高级、扩展或特定人群内容，不是当前主学习路径的必要部分。 |
| OUT_OF_SCOPE | 明确不属于当前 Track。 |

分类依据学习对象与目标，不以已有资料多少决定。LAB 可作说明标签，但不是第六种 Criticality。若某项背景是特定核心结论的必要依据，其缺失仍阻止该结论；不得用分类掩盖实际依赖。

## 领域状态与决策

| Status | 判定 | 可用 Decision |
| --- | --- | --- |
| READY | accepted 证据足以支持明确版本与范围的知识抽取。 | ALLOW_INGESTION；非当前优先范围可 DEFER |
| PARTIAL | 有可靠证据但范围不全；能明确区分已支持和未知部分。 | LIMITED_INGESTION；无法隔离缺口或暂不纳入时 DEFER |
| BLOCKED | 没有足够可靠证据，或关键冲突无法与拟入库部分隔离。 | DEFER |
| NOT_APPLICABLE | 不属于当前 Track。 | NOT_APPLICABLE |

ALLOW_INGESTION 表示该限定领域具备进入 Gate 2 的证据条件；LIMITED_INGESTION 只允许明确 Evidence Units 支持的部分；DEFER 留在 Source Engine。决策不是自动执行后续 Gate 的授权。

## 最小证据合同

每个领域记录 Domain、Criticality、Evidence、Status、Version Scope、Gap、Decision，并说明分类理由及允许/禁止抽取的边界。

1. 用 source_id 引用 accepted Evidence Units；candidate、stale、deprecated、rejected 不能充当本轮当前范围的入库依据。
2. 核对来源身份、指定片段、版本与适用层；数量不作为门槛，元数据或入口不能替代未读正文。
3. 版本未知仍记 unknown。可限定为核查日页面的概述性描述，但不能声称其是当前完整参数、权限或通用规则；关键版本无法隔离时 BLOCKED。
4. 模型声明、产品描述、API 参数和实测分别保留，不跨层外推。官方展示不等于独立效果验证。
5. LIMITED_INGESTION 必须列出具有实际用途的受支持子范围与排除项；不能仅有来源标题或宣传口号就认定核心领域可用。
6. 保留 unresolved 冲突并关联双方。冲突涉及的结论暂停入库；其他可独立核验的部分可以继续。
7. 动态信息缺少渠道、日期或有效范围时 DEFER，不补猜；不由此冻结稳定领域。
8. Schema 与 Validator PASS 是结构及已定义语义规则通过，不证明领域就绪；不得为获得 READY 升级未经核验的来源。

## Track 级汇总

CORE_READY：全部主要 CORE 为 READY / ALLOW_INGESTION，或 PARTIAL / LIMITED_INGESTION 且受支持部分有实际用途、关键缺口已隔离。

CORE_NOT_READY：存在关键 CORE BLOCKED，或 CORE 仍为 DEFER、限定范围不足以支持其核心目的。列出具体阻塞领域，不能隐藏或改分类以取得 CORE_READY。

同时报告 EXTENDED_GAPS：SUPPORTING、DYNAMIC、OPTIONAL 的未覆盖内容；OUT_OF_SCOPE 单列。CORE_READY 仅表示能够开始构建明确范围的核心知识体系，不表示平台知识完整、课程可发布或用户已能独立实践。

每次评估记录日期与 Track 范围。来源变更、版本变化或新冲突影响已许可范围时，只重审相关领域。历史评估保留其当时范围，不悄然改写。
