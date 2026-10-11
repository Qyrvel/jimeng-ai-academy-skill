# Gate 2.3 — Targeted Knowledge Ingestion Plan（Backbone Wave）

计划日期：2026-10-03。本文件在任何新 Knowledge Item 之前写成。

## 0. 本轮原则

- 目标不是尽量多抽知识，而是补齐未来 Knowledge Graph 所需的骨架类型：CONCEPT / CONSTRAINT / POLICY / VERSION_CONTEXT，必要时少量 PROCEDURE。
- 原则上不扩张 CAPABILITY。
- 禁止新 Source Discovery：只使用 Source Registry 中 `status = accepted` 的 Evidence Unit，且其材料化必须为 AVAILABLE 或可在本轮合法完成。
- 只保存支持目标 Item 的最小证据范围。

## 1. 来源可用性核查（本轮实际状态）

### 1.1 已 AVAILABLE、可直接使用的材料

| source_id | 状态 | Evidence Materialization | 材料文件 | 层 |
| --- | --- | --- | --- | --- |
| M09 | accepted | AVAILABLE | materialized/M09.md | Model（Seedance 2.5） |
| M10 | accepted | AVAILABLE | materialized/M10.md | Model（Seedream 5.0 Pro） |
| P10 | accepted | AVAILABLE（MANUAL_CAPTURE） | materialized/P10.md | Product（Seedance 2.5 产品页） |
| P12 | accepted | AVAILABLE（MANUAL_CAPTURE） | materialized/P12.md | Product |
| P13 | accepted | AVAILABLE（MANUAL_CAPTURE） | materialized/P13.md | Product |

可直接支撑本轮骨架抽取的只有以上 5 个 Evidence Unit。

### 1.2 本轮尝试材料化但被阻塞的 accepted 来源

Gate 2.3 的 §4 允许对「已 accepted 但未材料化」的 Evidence Unit 做一次有限材料化。本轮逐一尝试读取，**全部失败**：HTTPS 请求在 TLS 阶段即失败（schannel `SEC_E_NO_CREDENTIALS`），与本会话此前 P10/P12/P13 首轮失败同因（hostname 解析为非公网地址）。用户本轮未提供这些来源的真实正文，因此不得假装 MANUAL_CAPTURE。

| source_id | 层 | 目标用途 | 材料化结果 |
| --- | --- | --- | --- |
| P14 | Product（用户协议第 4.1–4.8 用户行为规范） | POLICY | MATERIALIZATION_BLOCKED |
| P04 | Product（iOS 开发者与 2.3.5 版本记录） | VERSION_CONTEXT | MATERIALIZATION_BLOCKED |
| P09 | Product（iOS 2.3.0 历史版本记录） | VERSION_CONTEXT | MATERIALIZATION_BLOCKED |
| P07 | Product（AI 视频生成器 FAQ：提示词、额度、模型选项） | CONCEPT / CONSTRAINT / PROCEDURE | MATERIALIZATION_BLOCKED |
| P01 | Product（官网视频创作概述） | CONCEPT | MATERIALIZATION_BLOCKED |
| P02 | Product（官网图片与智能画布概述） | CONCEPT（编辑） | MATERIALIZATION_BLOCKED |
| P15 | Product（iOS 开发者功能简介） | CONCEPT（App） | MATERIALIZATION_BLOCKED |
| M01 | Model（Seedance 2.5 官方发布，2026-07-31） | VERSION_CONTEXT | MATERIALIZATION_BLOCKED |
| M02 | Model（Seedance 2.0 官方发布，2026-02-12） | VERSION_CONTEXT | MATERIALIZATION_BLOCKED |
| M03 | Model（Seedance 1.5 pro Technical Report） | VERSION_CONTEXT | MATERIALIZATION_BLOCKED |
| M04 | Model（Seedance 1.0 Technical Report） | VERSION_CONTEXT | MATERIALIZATION_BLOCKED |
| M05 | Model（Seedream 5.0 Pro 官方发布，2026-07-08） | VERSION_CONTEXT | MATERIALIZATION_BLOCKED |
| M06 | Model（Seedream 5.0 Lite 官方发布，2026-02-13） | VERSION_CONTEXT | MATERIALIZATION_BLOCKED |
| M07 | Model（Seedream 4.5 官方模型页） | VERSION_CONTEXT | MATERIALIZATION_BLOCKED |
| M08 | Model（Seedream 4.0/4.5 Technical Report 元数据） | VERSION_CONTEXT | MATERIALIZATION_BLOCKED |

### 1.3 明确不可用的来源

P03、P05、P08、P11（Product candidate）、A01–A07（API candidate）、O01/O02（Observed candidate）：**非 accepted，本 Gate 不得使用**，本轮未使用。

## 2. Target Domains

| # | Domain | 为什么本轮优先 | 目标 knowledge_type | 可用 accepted source_id | Materialization 状态 | 本轮允许 ingestion |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 平台内容规则 | 两个 CORE MISSING 领域之一；POLICY 类型全域为 0 | POLICY | P14 | **BLOCKED** | **否** —— 唯一 POLICY 证据不可读，无替代来源，保持未入库并记录 MATERIALIZATION_BLOCKED |
| 2 | 产品版本历史 | 另一个 CORE（SUPPORTING）MISSING 领域；VERSION_CONTEXT 为 0 | VERSION_CONTEXT | P04、P09 | **BLOCKED** | **否** —— 同上 |
| 3 | Seedance | CORE READY 领域，且是唯一 Graph Pilot 候选，最缺结构骨架 | CONCEPT / CONSTRAINT / VERSION_CONTEXT | M09、P10、P12、P13（VERSION_CONTEXT 需 M01/M02，BLOCKED） | M09/P10/P12/P13 AVAILABLE | **部分允许** —— CONCEPT / CONSTRAINT 可做；VERSION_CONTEXT 本轮不可做 |
| 4 | 视频生成 | CORE PARTIAL，只有流程与能力，缺概念与边界 | CONCEPT / CONSTRAINT / PROCEDURE | P10、P12 | AVAILABLE | **是** |
| 5 | 参考视频/音频 | CORE PARTIAL，两项均为 CAPABILITY，缺概念与边界 | CONCEPT / CONSTRAINT | P12 | AVAILABLE | **是** |
| 6 | Prompt | CORE PARTIAL，仅 1 项且为流程侧 | CONCEPT / CONSTRAINT / PROCEDURE | P10（流程第二步提示词要素） | AVAILABLE | **部分允许** —— 只做证据明示的提示词角色，不从 P07 补方法（BLOCKED） |
| 7 | 编辑功能 | CORE PARTIAL，4 项全为 CAPABILITY | CONCEPT / CONSTRAINT | P13 | AVAILABLE | **是** |
| 8 | 模型版本历史 | 第二优先级；VERSION_CONTEXT | VERSION_CONTEXT | M01–M08 | **BLOCKED** | **否** |
| 9 | 模型选择 | 第二优先级；CONCEPT / CONSTRAINT | CONCEPT / CONSTRAINT | P10（仅第一步选择说明） | AVAILABLE | **有限** —— 仅在证据支持范围内建 CONCEPT |
| 10 | 即梦产品基础结构 | 第二优先级；CONCEPT | CONCEPT | P01、P02（BLOCKED）、P10 | 部分 BLOCKED | **否** —— 缺 P01/P02 正文，证据不足以定义产品结构概念，本轮不做 |

## 3. Planned Items（按证据可达性）

可从 1.1 的 5 份材料真实支持的骨架 Item：

| 计划 ID | knowledge_type | 目标 Domain | 证据 | 核心命题（草案） |
| --- | --- | --- | --- | --- |
| JIM-K-0017 | CONCEPT | 参考视频/音频 | P12 | 参考生视频的产品语义：上传参考视频作为参照来控制动态细节的生成方式 |
| JIM-K-0018 | CONCEPT | 视频生成 | P12 | 文生视频与图生视频是两种并列输入方式的产品概念 |
| JIM-K-0019 | CONCEPT | 编辑功能 | P13 | 局部编辑的产品语义：修改局部而非重新生成整段 |
| JIM-K-0020 | CONCEPT | Prompt | P10 | 提示词在产品流程中的角色与描述要素 |
| JIM-K-0021 | CONSTRAINT | 编辑功能 | P13 | 局部编辑的修改对象边界与保留要素边界 |
| JIM-K-0022 | CONSTRAINT | 参考视频/音频 | P12 | 参考视频/参考图片在生成中的作用边界（提供参照与控制，不替代其他输入） |
| JIM-K-0023 | CONSTRAINT | 参考视频/音频 | P12 | 参考生视频主要传达动态信息这一用途边界 |
| JIM-K-0024 | PROCEDURE | 视频生成 | P10 | 产品端生成流程的三步结构 |

计划新增 8 项：CONCEPT 4、CONSTRAINT 3、PROCEDURE 1，无新增 CAPABILITY。

## 4. Type Targets vs Reachability（诚实告知）

§8 的理想结果为「CONCEPT ≥2、CONSTRAINT ≥2、POLICY ≥1、VERSION_CONTEXT ≥2」。按 1.2 的材料化结果：

| 目标类型 | 本轮可达？ | 原因 |
| --- | --- | --- |
| CONCEPT | 可达（4 项） | P10/P12/P13 明文支持 |
| CONSTRAINT | 可达（3 项） | P12/P13 含明确的用途与保留范围边界 |
| POLICY | **不可达** | 唯一证据 P14 材料化 BLOCKED，禁止替代来源与法律推断 |
| VERSION_CONTEXT | **不可达** | 需 P04/P09 或 M01–M08 的发布/版本正文，全部 BLOCKED；现有材料只有「当前版本说明」，不构成版本沿革证据 |

因此本轮预计上报 **TYPE_GAP_REMAINS（POLICY、VERSION_CONTEXT）**，并说明其根因是 **Materialization 阻塞**，不是 Schema、Atomicity 或 Prose 设计错误。

## 5. Do Not Ingest

因以下原因明确不在本轮处理的领域：

| Domain | 不处理的原因 |
| --- | --- |
| 平台内容规则 | Materialization BLOCKED（P14 不可读）；无替代来源，禁止法律推断 |
| 产品版本历史 | Materialization BLOCKED（P04/P09 不可读） |
| 模型版本历史 | Materialization BLOCKED（M01–M08 不可读） |
| 即梦产品基础结构 | 主要证据 P01/P02 材料化 BLOCKED；仅凭 P10 不足以定义产品结构概念 |
| App | 证据 P04/P09/P15 全部 BLOCKED；非本轮骨架目标 |
| 网页端 | 现有可读证据只有流程侧，且 P11 为 candidate；非本轮骨架目标 |
| Seedream | 已有 5 项 CAPABILITY，本轮不扩张 CAPABILITY |
| 图片生成 | 同上；且缺产品层证据 |
| 参考图 | 只有流程侧一项；P07（含参考素材说明）BLOCKED |
| 模型选择 | 仅 P10 第一步一句；除 CONCEPT 外无法扩展，第二大优先级 |
| 会员 / 积分 / 实时价格 | Dynamic，Readiness 为 DEFER |
| Volcano / Ark API | Optional，Readiness 为 DEFER；A01–A07 全为 candidate |
| API 服务状态 | OUT_OF_SCOPE |
| 社区经验 / 可复现实验 | Optional，Readiness 为 DEFER；O01/O02 为 candidate |

## 6. 边界与合规声明

- 现有 16 个 Knowledge Item 的 statement / learner_outcome / scope / version_scope / evidence_refs / limitations / status 一律不改；新 ID 从 JIM-K-0017 顺序使用。
- 不把能力描述改名为约束（§11）：本计划的三项 CONSTRAINT 均为「用途/修改范围与保留边界」这类真正的适用范围限制，不是「支持某能力」的改写。
- CONCEPT 项均对应材料中明确出现的产品概念，不发明术语、不建抽象 ontology（§12）。
- 不跨 Product / Model / API / Observed 层：本轮计划中的 Item 全部为 Product Layer（P10/P12/P13），不使用 M09/M10 支撑产品层 Item。
- POLICY 保持缺席而不伪造；VERSION_CONTEXT 不写成替代关系（§10）：本轮不建任何 VERSION_CONTEXT，因此不存在「旧版已下线」类推断风险。
- 环境安全：本轮未修改 ACL、所有者、防火墙、DNS、Proxy、TLS、PATH、环境变量、注册表或网络适配器；网络不可达仅被记录，未尝试自行修复。
