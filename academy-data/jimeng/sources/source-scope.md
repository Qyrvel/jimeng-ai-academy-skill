# Jimeng Source Scope

审计日期：2026-10-03。目标是可信教材来源地图，不是课程或知识抽取。

## 四层来源模型

| Layer | 范围 | 优先来源 |
| --- | --- | --- |
| A — Jimeng Product Layer | 网页端、App、产品功能、UI、会员/积分、平台实际支持模型、操作入口、上传与生成限制、平台规则、版本更新 | 即梦官网、官方帮助、公告、教程、App 官方版本记录，以及身份可靠确认的官方社交账号 |
| B — ByteDance Seed Model Layer | Seedance、Seedream、底层模型能力与版本、模型介绍、技术博客、Technical Report、官方 Benchmark | seed.bytedance.com、Seed 官方 Blog、原始技术报告 |
| C — Volcano / Ark API Layer | API、模型 ID、Prompt Guide、开发者参数、输入输出规格、调用限制、API 版本及服务状态 | 火山引擎文档中心与火山方舟官方资料 |
| D — Observed / Community Layer | 用户实验、真实表现、Bug、异常行为、稳定性、Prompt 实测、官方未说明的限制 | 自有可复现实验、高质量专业教程、社区讨论；不得覆盖前三层官方事实 |

Layer 表示适用范围，Tier A–E 表示可信级别，二者不是同一分类。官方模型或 API 资料也可为 Tier A，但不能因此成为产品层证据。

## 禁止跨层推断

1. Seed 模型支持某项能力，不自动等于即梦产品已经开放该能力。
2. 火山 API 支持某项参数，不自动等于即梦网页端具有同样参数。
3. 即梦 UI 出现某项功能，不自动证明底层模型的完整技术能力。
4. 社区观察到某种行为，不得直接升级成官方规则。
5. 同一个事实横跨多个层时，应分别保留来源，并标明端、地区、版本及核查范围。

## 证据与准入

每条记录是可独立引用与审核的 Evidence Unit，不是网站收藏。不同信息性质、版本范围或独立证据应拆开，可共享 location。evidence_scope 指明章节、条目或评论范围；本轮不做自动切片。

所有新来源先按 candidate 处理，检查发布主体、来源链路、版本范围及指定片段后才设 accepted。不能仅凭域名、账号名称、搜索排名或平台托管身份采纳。社交账号必须有官方回链、认证主体等可核实依据；本轮没有 accepted 社交账号。

沿用既有 JSON Schema，不增加 layer 字段；P/M/A/O 的 source_id 前缀及 notes 中 Layer 分别对应 Product/Model/API/Observed。官方博客为 Tier A；原始研究报告按 Tier B 记录；非官方且身份未明的资料保留 Tier E。

## 时间与审核边界

published_at 仅记录明确发布日期，未知为 null；更新日、模型 ID 日期和搜索抓取日不冒充发布日期。last_verified_at 表示本轮检查日期，candidate 的该日期不代表全部内容核验成功。version_scope 无法确认时为 unknown；已知历史版本仍可 accepted，不自动标 stale 或 deprecated。

动态页面与搜索索引不一致、跨端权限不同、版本分支映射不明时，保留双方并在 notes 标 unresolved。accepted 仅采纳已检查的片段，不代表全文、当前账号权限或独立性能验证。

本 Gate 允许有限联网调查，覆盖 Gate 1.1 文档中的阶段性离线限制；不修改其通用文件。禁止爬虫、整站下载、MCP、RAG、数据库、Knowledge Item、知识图谱、前置关系、课程与教学。本轮只生成本目录三个文件。
