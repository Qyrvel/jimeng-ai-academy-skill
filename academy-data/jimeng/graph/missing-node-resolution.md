# Missing Node Candidate Resolution — Gate 3.0-R1

日期 2026-10-03。处理 Gate 3.0 Seedance Pilot Review 中记录的 `MISSING_NODE_CANDIDATE`。

## 0. 前提校正（重要）

指令 §0/§1 假定 Gate 3.0 只暴露 **2 个** MISSING_NODE_CANDIDATE。核对真实文件后，`seedance-pilot-selection.md` §3 与 `seedance-pilot-review.md` §8 **各记录四项**，两处完全一致。按指令 §2「如果不是恰好两个……STOP_AND_REPORT」，本轮先停止并报告，经用户确认后按以下范围执行：

- **正式处理**：候选 A（= 原记录 #1 流程第三步）与候选 B（= 原记录 #2 流程粒度关系）。指令 §1 与 §5 的概括与这两项的名称、含义一致。
- **记录但不在本 Gate 范围**：原记录 #3、#4。按用户选择，二者在本文件中明确分类为 `BLOCKED_BY_EVIDENCE`，并注明其不属于本 Gate 的处理范围。

## 1. Candidate A — 流程第三步

### 原始 MISSING_NODE_CANDIDATE（逐字）

> 「**流程第三步的独立 PROCEDURE Item**（生成、预览并保存）。当前只有第一步（K-0010）与第二步（K-0011）有独立步骤项，第三步没有，因此 `PROCEDURE_PRECEDES` 只能表达 1→2，无法表达 2→3。」

### 诊断过程

按 §4 要求，不只按 title 搜索，而是比较 statement / domain / scope / version_scope / evidence_refs。当前 Registry 中与 P10 三步流程相关的 PROCEDURE Item 共四项：

| knowledge_id | statement 要点 | 对应步骤 |
| --- | --- | --- |
| JIM-K-0010 | 「生成流程的第一步是进入即梦的AI视频工具并选择Seedance 2.5模型」 | **第一步** |
| JIM-K-0011 | 「把上传素材与输入提示词列为同一步骤：可添加参考图片或视频，并用提示词描述主体、动作、镜头和视觉风格」 | **第二步** |
| JIM-K-0009 | 「把视频生成说明为三个步骤：打开AI视频生成器、上传素材并输入提示词、生成预览并保存；该流程的产物为可下载的AI视频」 | 流程级（含三步与产物） |
| JIM-K-0024 | 「把生成流程组织为三步结构：打开AI视频生成器、上传素材并输入提示词、生成预览并保存」 | 流程级（结构） |

结论：**没有任何 Item 以第三步为命题**。K-0009 与 K-0024 虽在 statement 中提到「生成预览并保存」，但它们是流程级 Item，其命题是整体结构而非该步骤本身；把其中任一当作「第三步 Item」会混淆粒度（正是候选 B 要处理的问题）。

### Resolution Classification

`NEW_ITEM_SUPPORTED`

理由：`materialized/P10.md`（accepted + AVAILABLE）明确记载「第三步 / 生成、预览并保存 / 生成 AI 视频，检查效果并完成必要调整，然后下载成片。」，直接支持建立该步骤 Item。未做 Source Discovery，未使用 candidate 来源。

### 采取的动作

新增 **1 个** Knowledge Item：`JIM-K-0046`（PROCEDURE，Video Generation，Product Layer，evidence = P10）。

按 §4.2 的要求，其 limitations 明确写有：本条表示官方三步流程中的第三步**整体**；不把「生成 / 检查 / 调整 / 下载」分别当作独立的官方步骤；当前 Evidence 不支持更多内部步骤层级。**未**为原子性机械拆成 4 个 Item。

### 是否已解决

**已解决** → 最终状态 `RESOLVED_NEW_ITEM`。

## 2. Candidate B — 流程粒度关系

### 原始 MISSING_NODE_CANDIDATE（逐字）

> 「**「流程整体 vs 流程结构」的关系表达**。K-0009 与 K-0024 是同一流程的不同粒度；Gate 3.0 禁止 PART_OF，也没有对应关系类型，因此该关系在本合同中无表达方式。」

### 诊断过程

按 §5 要求先判断现有关系能否表达。拆成两个不同的关系问题：

**B-1：具体 Procedure Step 属于更高层级 Workflow Procedure**

| 现有关系 | 能否表达 | 原因 |
| --- | --- | --- |
| PREREQUISITE_OF | 不能 | 成员关系不是知识依赖；「该步骤属于该流程」不表示「不懂该步骤就不懂该流程」 |
| PROCEDURE_PRECEDES | 不能 | 只表达两个**步骤**之间的先后，不表达归属 |
| CONSTRAINS | 不能 | from 必须是 CONSTRAINT / POLICY |
| VERSION_CONTEXT_FOR | 不能 | from 必须是 VERSION_CONTEXT |
| SCOPE_PARALLEL_TO | 不能 | 两个 Item 同层同版本，不是跨层平行 |
| VERSION_VARIANT_OF | 不能 | 不是同主题不同版本 |

→ **无法表达，属 `RELATION_GAP`。**

**B-2：K-0009（流程含产物）与 K-0024（流程结构）之间的粒度关系**

Normalization Review 已判该 pair（NR-0004 相邻关系，K-0009 与 K-0024）……实际核对：NR-0005 为 [K-0009, K-0010]、NR-0004 为 [K-0009, K-0011]；K-0024 与 K-0009 的对照记录在 **NR-0018**，relation = `PARTIAL_OVERLAP`、decision = `KEEP_SEPARATE`。

按 `knowledge-graph-policy.md` 的「Graph != Normalization」：`PARTIAL_OVERLAP` **不会**自动生成 Graph Edge。因此该 pair **在正确的图中不需要任何 Edge**——两个流程级 Item 是同一流程的不同表述，正确做法是保留二者独立（Normalization 已如此判定），而不是用图关系把它们连起来。若强行用 `STEP_OF` 连接，会得到一个错误命题（流程不是自己流程的步骤）。

→ **不需要 Edge，属 `NOT_NEEDED`（仅针对 B-2 这部分）。**

### Resolution Classification

`RELATION_GAP`（针对 B-1，即指令 §5 的定义），其中 B-2 子问题为 `NOT_NEEDED`。

### 采取的动作

按 §11 以**附加式变更**新增一个最小关系 `STEP_OF`，并同步更新 Policy / Schema / Validator / tests（详见各自文件）。未重写 Gate 3.0 的 relation contract；Gate 3.0 的禁止关系列表不变。

保留的决定：**K-0024 仍不进入图**。它不是任何步骤的 workflow 归属对象所需（workflow 节点使用已在图中的 K-0009），且它与 K-0009 的关系属 Normalization 范畴，不应图化。该决定记录于此，避免被误读为「补一个节点凑连通」。

### 是否已解决

**已解决** → 最终状态 `RESOLVED_RELATION`。

## 3. 记录但不在本 Gate 范围的两个候选

### #3 Seedance 2.0 fast 的模型层 Item（原始描述逐字）

> 「**Seedance 2.0 fast 的模型层 Item**。当前 fast 只出现在产品更新说明（P09）中，模型层无任何证据，因此无法把它连入模型侧版本骨架。」

**最终状态：`BLOCKED_BY_EVIDENCE`。** 全 Registry 中与 fast 相关的唯一证据是 P09（App Store 2.3.0 更新说明），属 Product Layer 且只有一句；模型层没有任何 accepted + AVAILABLE 证据。本轮不伪造、不扩大来源、不做 Source Discovery。**不在本 Gate 处理范围**（用户已确认）。

### #4 Product Layer 的 Seedance 2.0 能力项（原始描述逐字）

> 「**Product Layer 的 Seedance 2.0 能力项**。现有产品能力项全部来自 2.5 产品页；2.0 只有一条部署声明，导致 K-0043 只能通过版本关系连接，无法参与「能力 ↔ 部署」对照。」

**最终状态：`BLOCKED_BY_EVIDENCE`。** 现有产品层能力项全部来自 Seedance 2.5 产品页；2.0 侧只有一条上线声明（P17），没有任何 2.0 产品能力描述证据。本轮不伪造、不扩大来源。**不在本 Gate 处理范围**（用户已确认）。

## 4. 汇总

| 候选 | 原始编号 | Classification | 最终状态 | 动作 |
| --- | --- | --- | --- | --- |
| A 流程第三步 | #1 | `NEW_ITEM_SUPPORTED` | `RESOLVED_NEW_ITEM` | 新增 1 个 PROCEDURE Item（JIM-K-0046） |
| B 流程粒度关系 | #2 | `RELATION_GAP`（B-2 子问题 `NOT_NEEDED`） | `RESOLVED_RELATION` | 附加新增 `STEP_OF`；K-0024 保持不进图 |
| Seedance 2.0 fast 模型层 Item | #3 | `BLOCKED_BY_EVIDENCE` | `BLOCKED_BY_EVIDENCE` | 无（不在本 Gate 范围） |
| Product Layer Seedance 2.0 能力项 | #4 | `BLOCKED_BY_EVIDENCE` | `BLOCKED_BY_EVIDENCE` | 无（不在本 Gate 范围） |

本 Gate 新增 Knowledge Item 数：**1**（§8 上限为 2）。旧 45 项零修改。

## 5. 边界声明

- 未创建 workflow 级 Item：§7.1 适用——K-0009 已是明确表示「Seedance 2.5 产品页三步生成流程」的 PROCEDURE Item（其 statement 逐字列出三步），直接使用。
- 未为降低 component count 创建任何 Edge：新增的 4 条 Edge 全部有独立语义（3 条步骤归属 + 1 条步骤先后），连通性变化是它们的**结果**而非目的。
- 未做 Source Discovery；未使用 candidate 来源；未修改旧 Item。
