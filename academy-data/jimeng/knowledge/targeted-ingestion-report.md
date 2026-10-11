# Gate 2.3 Targeted Knowledge Ingestion Report

## 1. Scope

本轮目标：**补知识结构骨架，不是扩张能力清单。**

依据 Gate 2.2 的结论（16 Items、13 个 CORE 中 COVERED = 0、类型严重偏斜），本 Gate 优先补充 CONCEPT / CONSTRAINT / POLICY / VERSION_CONTEXT，必要时少量 PROCEDURE，原则上不扩张 CAPABILITY。

本轮实际新增 **8 个** Knowledge Item（JIM-K-0017 ～ JIM-K-0024），其中 **CAPABILITY 新增 0 个**。未修改现有 16 个 Item 的任何字段，未删除、未合并、未标 deprecated。

来源边界：只使用 Source Registry 中 `status = accepted` 且材料化 AVAILABLE 的 Evidence Unit。实际使用 3 个：P10、P12、P13（均为 Product Layer）。本轮未做 Source Discovery，未联网读取成功任何新来源，未使用 candidate、搜索摘要、模型记忆或第三方来源。

## 2. Materialization Results

### 本轮尝试材料化的 accepted Sources

按 §4 允许的范围，本轮对「已 accepted 但未材料化」的 Evidence Unit 逐一尝试有限材料化，**全部失败**：所有 HTTPS 请求在 TLS 阶段即失败（`SEC_E_NO_CREDENTIALS`），与 P10/P12/P13 首轮失败同因（hostname 解析为非公网地址）。用户本轮未提供这些来源的真实正文，因此未做、也不得假装 MANUAL_CAPTURE。

| source_id | 层 | 目标用途 | 结果 |
| --- | --- | --- | --- |
| P14 | Product | POLICY（用户行为规范第 4.1–4.8 节） | **BLOCKED** |
| P07 | Product | CONCEPT / CONSTRAINT / PROCEDURE（视频生成器 FAQ） | **BLOCKED** |
| P04 | Product | VERSION_CONTEXT（iOS 2.3.5 版本记录） | **BLOCKED** |
| P09 | Product | VERSION_CONTEXT（iOS 2.3.0 版本记录） | **BLOCKED** |
| P01 | Product | CONCEPT（官网视频创作概述） | **BLOCKED** |
| P02 | Product | CONCEPT（图片与智能画布概述） | **BLOCKED** |
| P15 | Product | CONCEPT（iOS 开发者功能简介） | **BLOCKED** |
| M01 | Model | VERSION_CONTEXT（Seedance 2.5 发布，2026-07-31） | **BLOCKED** |
| M02 | Model | VERSION_CONTEXT（Seedance 2.0 发布，2026-02-12） | **BLOCKED** |
| M03 | Model | VERSION_CONTEXT（Seedance 1.5 pro） | **BLOCKED** |
| M04 | Model | VERSION_CONTEXT（Seedance 1.0） | **BLOCKED** |
| M05 | Model | VERSION_CONTEXT（Seedream 5.0 Pro 发布，2026-07-08） | **BLOCKED** |
| M06 | Model | VERSION_CONTEXT（Seedream 5.0 Lite 发布，2026-02-13） | **BLOCKED** |
| M07 | Model | VERSION_CONTEXT（Seedream 4.5 模型页） | **BLOCKED** |
| M08 | Model | VERSION_CONTEXT（Seedream 4.0/4.5 报告元数据） | **BLOCKED** |

### 本轮实际可用的材料

| source_id | 材料化状态 | 材料文件 | 本轮是否引用 |
| --- | --- | --- | --- |
| P10 | AVAILABLE（MANUAL_CAPTURE） | materialized/P10.md | 是（JIM-K-0020、JIM-K-0024） |
| P12 | AVAILABLE（MANUAL_CAPTURE） | materialized/P12.md | 是（JIM-K-0017、JIM-K-0018、JIM-K-0022、JIM-K-0023） |
| P13 | AVAILABLE（MANUAL_CAPTURE） | materialized/P13.md | 是（JIM-K-0019、JIM-K-0021） |
| M09 | AVAILABLE（DIRECT_READ） | materialized/M09.md | 否（其内容为模型层能力说明，与本轮骨架目标不符） |
| M10 | AVAILABLE（DIRECT_READ） | materialized/M10.md | 否（同上） |

### 未处理的来源

P03、P05、P08、P11（Product candidate）、A01–A07（API candidate）、O01/O02（Observed candidate）：非 accepted，本 Gate 不得使用，本轮未尝试读取。

**materialization-registry.json 本轮未修改**（无新增 AVAILABLE 条目），因此其 Validator 结果与 Gate 2.0-R1 一致，仍为 PASS。

## 3. New Knowledge Items

| knowledge_id | title | domain | knowledge_type | scope | version_scope | evidence_refs |
| --- | --- | --- | --- | --- | --- | --- |
| JIM-K-0017 | 参考生视频的产品概念 | 参考视频/音频 | CONCEPT | Jimeng Product Layer | Seedance 2.5；2026-10-03 公开产品页 | P12 |
| JIM-K-0018 | 文生视频与图生视频的产品概念 | 视频生成 | CONCEPT | Jimeng Product Layer | Seedance 2.5；2026-10-03 公开产品页 | P12 |
| JIM-K-0019 | 局部编辑的产品概念 | 编辑功能 | CONCEPT | Jimeng Product Layer | Seedance 2.5；2026-10-03 公开产品页 | P13 |
| JIM-K-0020 | 提示词在产品生成流程中的角色 | Prompt | CONCEPT | Jimeng Product Layer | Seedance 2.5；2026-10-03 公开产品页 | P10 |
| JIM-K-0021 | 局部编辑的修改与保留边界 | 编辑功能 | CONSTRAINT | Jimeng Product Layer | Seedance 2.5；2026-10-03 公开产品页 | P13 |
| JIM-K-0022 | 参考视频与参考图片的作用边界 | 参考视频/音频 | CONSTRAINT | Jimeng Product Layer | Seedance 2.5；2026-10-03 公开产品页 | P12 |
| JIM-K-0023 | 参考生视频的用途边界 | 参考视频/音频 | CONSTRAINT | Jimeng Product Layer | Seedance 2.5；2026-10-03 公开产品页 | P12 |
| JIM-K-0024 | 产品端三步生成流程的结构 | 视频生成 | PROCEDURE | Jimeng Product Layer | Seedance 2.5；2026-10-03 公开产品页 | P10 |

8 项全部为 `information_type = DOCUMENTED`、`status = draft`，全部为 Product Layer，全部只引用 Pxx，没有任何一项引用 Mxx 或跨层混用。

内容自审结果：

- **Atomicity**：8 项各表达一个核心命题。4 个 CONCEPT 分别定义「参考生视频」「文生/图生」「局部编辑」「提示词角色」四个不同概念；3 个 CONSTRAINT 分别限定「局部编辑的修改与保留范围」「参考素材的作用位置」「参考生视频的用途范围」；1 个 PROCEDURE 只描述流程结构。没有把同一事实拆成多条，也没有把多个概念压成一条。
- **Provenance**：每条 support_note 均指向对应材料中实际保存的文字，并说明该文字支持 statement 的哪一部分。
- **Scope Preservation**：全部限定在 Jimeng Product Layer，且逐条声明不代表底层模型完整能力、不代表所有账号/地区/设备端已开放。
- **Marketing Language**：未把「准确控制」「只需三个简单步骤」等表述转成客观结论；JIM-K-0023 的 limitations 明确记录「准确」只作发布方产品层说明。
- **Unsupported Claims**：未入库任何超出材料的内容（详见第 6 节）。

## 4. Type Balance Before / After

| knowledge_type | Before | After | 变化 |
| --- | --- | --- | --- |
| CONCEPT | 0 | **4** | +4 |
| CAPABILITY | 13 | 13 | 0 |
| PROCEDURE | 3 | **4** | +1 |
| CONSTRAINT | 0 | **3** | +3 |
| POLICY | 0 | **0** | 0（TYPE_GAP_REMAINS） |
| VERSION_CONTEXT | 0 | **0** | 0（TYPE_GAP_REMAINS） |
| **合计** | **16** | **24** | **+8** |

达成 §8 的理想结果中：CONCEPT（≥2）✔、CONSTRAINT（≥2）✔、PROCEDURE 少量增加 ✔；POLICY（≥1）与 VERSION_CONTEXT（≥2）**未达成**。

**TYPE_GAP_REMAINS: POLICY, VERSION_CONTEXT**

根因说明（不是数量不足，而是证据不可达）：

- POLICY 只能来自明确政策/协议/规则 Evidence（§9）。唯一此类 accepted 来源是 P14，本轮材料化 BLOCKED，且禁止替代来源、禁止法律推断，因此无法建立任何原子 POLICY Item。
- VERSION_CONTEXT 只能记录明确证据支持的版本发布、能力新增、历史版本存在或版本时间关系（§10）。此类证据位于 P04/P09（App 版本记录）与 M01–M08（模型发布/报告），全部 BLOCKED。现有已材料化内容只支持「当前版本说明」，不构成版本沿革证据，因此不建立任何 VERSION_CONTEXT Item，也没有把「当前版本」推断成「替代旧版本」。

本 Gate 未为达到类型配额伪造任何 Item：POLICY 与 VERSION_CONTEXT 保持为 0，而不是把能力或适用范围改写成这两类。

## 5. Domain Delta

| Domain | Before | After | 新增 Items |
| --- | --- | --- | --- |
| 参考视频/音频 | 2 | 5 | JIM-K-0017、JIM-K-0022、JIM-K-0023 |
| 视频生成 | 5 | 7 | JIM-K-0018、JIM-K-0024 |
| 编辑功能 | 4 | 6 | JIM-K-0019、JIM-K-0021 |
| Prompt | 1 | 2 | JIM-K-0020 |
| Seedance | 9 | 11 | 其中 JIM-K-0017、JIM-K-0023 亦映射到该领域 |
| 其它 17 个领域 | 不变 | 不变 | 无 |

新增 Item 数：**8**（§13 建议 8～16，取建议区间下限，未通过过度拆分凑数）。按 Domain 计的映射：参考视频/音频 +3、视频生成 +2、编辑功能 +2、Prompt +1。

## 6. Unsupported / Deferred

本轮想建立但**因证据原因未入库**的知识：

| 想建立的知识 | 目标类型 | 阻塞原因 |
| --- | --- | --- |
| 用户行为规范 / 内容规则（分条原子化） | POLICY | Materialization BLOCKED（P14）；禁止替代来源与法律推断 |
| 即有具体条文，也不得扩张为「即梦完整内容政策」 | POLICY | 同上；即使拿到 P14，也只能按节建立具体规范 Item |
| iOS App 基础功能概述 | CONCEPT | Materialization BLOCKED（P15）；App 领域非本轮骨架目标 |
| iOS 2.3.5 / 2.3.0 版本条目 | VERSION_CONTEXT | Materialization BLOCKED（P04/P09） |
| Seedance 2.5 / 2.0 / 1.5 pro / 1.0 发布与版本关系 | VERSION_CONTEXT | Materialization BLOCKED（M01–M04） |
| Seedream 5.0 Pro / 5.0 Lite / 4.5 / 4.0 版本关系 | VERSION_CONTEXT | Materialization BLOCKED（M05–M08） |
| 产品模块与画布结构概念 | CONCEPT | Materialization BLOCKED（P01/P02）；仅凭 P10 不足以定义产品结构 |
| 参考素材文件规格与数量上限 | CONSTRAINT | 证据本身不含数值规格；Readiness 亦明确排除录入上限，故不是「漏抽」而是不允许 |
| 提示词结构、字数与方法 | PROCEDURE / CONSTRAINT | 需 P07（BLOCKED）；且 A07 仍为 candidate |
| 编辑操作入口与选区方式 | PROCEDURE | 证据只到概念与用途层；C1 影响画布 UI |
| 模型选择完整列表与默认项 | CONCEPT / CONSTRAINT | 只有 P10 第一步一句；Readiness 明确不建完整选择表 |

未入库的原因分类：**Materialization / Evidence 不足**（多数）、**Readiness 不允许**（数值上限、完整选择表）、**Scope 不明确**（产品结构概念）、**Version 不明确**（版本沿革）。没有一项是因为「写起来麻烦」而放弃。

## 7. Cross-Layer Review

- **Product / Model 未被混合**：本轮 8 项全部为 Jimeng Product Layer，只引用 P10/P12/P13；M09/M10 虽 AVAILABLE 但本轮未使用，因此不存在用模型证据支撑产品层的可能。既有 8 项模型层 Item 未被触碰。
- **API 未外推产品**：本轮完全未使用 A01–A07（全部 candidate）；没有把任何 API 参数写成产品参数或产品权限。
- **Policy 未被扩张**：POLICY 为 0 项，不存在「即梦完整内容政策」类扩张；也未做任何法律推断或法律建议。
- **Version Context 未被写成替代关系**：VERSION_CONTEXT 为 0 项；未出现「旧版已下线」「新版完全替代旧版」「所有端同步上线」「所有账号已切换」等推断。JIM-K-0017 ～ 0024 的 version_scope 只标注其证据对应的版本与页面日期，不宣称该版本是当前唯一可用版本。
- **Capability 未被改名伪装**：三项 CONSTRAINT 均为真正的适用范围/用途边界（修改对象与保留要素、参考素材的作用位置、参考生视频的用途），不是「支持某能力」的改写；四项 CONCEPT 均为材料中明确出现的产品概念，未发明术语、未建抽象 ontology。

## 8. Recommendation

```text
TARGETED_INGESTION_PASS
```

理由：Knowledge Validator PASS；Manifest Validator PASS；Materialization Validator（本轮未修改该 Registry，仍为 PASS）；未修改既有 16 个 Item；至少新增一种此前为 0 的类型（CONCEPT 与 CONSTRAINT 同时从 0 变为 4 与 3）；新 Item 全部基于 accepted 且已材料化的 Evidence；Product / Model scope 保持分离；未为追求类型平衡制造任何伪知识（POLICY 与 VERSION_CONTEXT 保持 0 并如实上报 TYPE_GAP_REMAINS）。

**下一波优先缺口**（供后续授权参考，本轮不执行）：

1. **POLICY**：需要 P14 的用户行为规范正文。取得后可按节建立若干原子 POLICY Item。
2. **VERSION_CONTEXT**：需要 P04/P09（App 版本记录）与 M01–M08（模型发布/报告）的正文。取得后可建立版本发布与历史版本存在类 Item。
3. **产品结构 CONCEPT**：需要 P01/P02 正文。
4. **PROCEDURE 深化**：需要 P07（FAQ）正文以支持提示词与模型选择相关方法类知识。

环境限制记录：本轮网络对上述来源全部不可达（TLS 阶段失败），未尝试自行修复 ACL、DNS、Proxy、TLS、PATH、环境变量、注册表或网络适配器。若需补齐上述类型，需要用户提供对应来源的真实正文（MANUAL_CAPTURE），与 P10/P12/P13 的处理方式一致。

## 9. Post-2.3 Coverage

本轮结束后按 §21 重跑 Gate 2.2 的 Coverage Assessment（不修改旧快照）：

- `coverage-assessment-after-2.3.json`
- `knowledge-coverage-report-after-2.3.md`

结论：`overall_recommendation` 仍为 **NEEDS_TARGETED_INGESTION**，因此不进入 Gate 3，也不自行开始 Gate 2.3-R1。
