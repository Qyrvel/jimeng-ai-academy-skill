# Knowledge Graph Policy — Gate 3.0

## 职责与边界

本 Policy 定义 Knowledge Graph 的合同：Node、Edge、关系类型、认知状态、跨层与版本规则。它补充 [Knowledge Policy](knowledge-policy.md) 与 [Knowledge Normalization Policy](knowledge-normalization-policy.md)，不替代来源准入、Readiness、Materialization、Normalization 或任何既有 Validator。

Graph 的职责只有一件：**表达已经存在的 Knowledge Item 之间可利用的知识关系**。

Graph 不创造知识，不生成课程，不定义教学顺序，不复制 Item 内容。

## Graph 不创造知识

Node 必须引用 `pilot-knowledge-registry.json` 中真实存在的 `knowledge_id`。禁止：

- 创建隐式知识节点；
- 创建课程节点；
- 创建 lesson / module；
- 用自然语言补出一个「缺失概念」再放进图中。

如果表达某个关系需要一个当前不存在的节点，必须记录为 `MISSING_NODE_CANDIDATE`，并在当轮 Gate 中**不创建**它。MISSING_NODE_CANDIDATE 记录在 selection 与 review 文档中，用于说明当前合同的表达边界，不得作为 Node 写入图。

## Node Contract

Graph 不复制完整 Knowledge Item。Node 只允许一个字段：

```json
{ "knowledge_id": "JIM-K-0001" }
```

title、statement、knowledge_type、scope、version_scope、evidence_refs、limitations 全部以 Knowledge Registry 为唯一事实源。Graph 不复制任何一项，避免双重真相源。

## Edge Contract

每条 Edge 只允许以下七个字段，不得增加其它字段：

```json
{
  "edge_id": "JIM-E-0001",
  "from": "JIM-K-xxxx",
  "relation": "PREREQUISITE_OF",
  "to": "JIM-K-yyyy",
  "epistemic_status": "INFERRED",
  "rationale": "...",
  "limitations": "..."
}
```

`rationale` 与 `limitations` 必须非空。`from` 与 `to` 都必须出现在同一份图的 nodes 中，且 `from != to`。

## Relation Types

Gate 3.0 只允许以下六种关系。

### PREREQUISITE_OF

`from` 所表达的知识是合理理解或执行 `to` 的前置知识条件。这是**知识依赖**，不是课程顺序，也不是教学建议。

禁止仅因为「我想先教 A 再教 B」而建立该关系。判定方法：若移除 `from`，学习者是否仍能合理理解 `to`？若答案是「可以完全理解」，则它不是 prerequisite。

### PROCEDURE_PRECEDES

两个 PROCEDURE Item 属于同一明确流程，`from` 对应步骤发生在 `to` 之前。只能来自真实 Procedure Evidence 或已有 Procedure Items 的明确语义，不是教学顺序。

### CONSTRAINS

`from` 为 CONSTRAINT 或 POLICY，并对 `to` 的适用、使用、输入、输出或行为边界形成限制。

不得因为某条 Policy「大概适用于整个平台」就批量连向所有 Product Item。必须能说明为什么**这条具体规则**与**这个具体知识 Item** 有直接关系。

### VERSION_CONTEXT_FOR

`from` 为 VERSION_CONTEXT，它提供理解 `to` 的明确版本背景（例如某版本的发布或部署事实）。**不表示版本替代。**

### SCOPE_PARALLEL_TO

两个 Item 主题相近但属于不同 Layer / Scope，应保持平行而非合并。典型为 Model capability 对 Product deployment / Product capability。此关系为**对称**关系：不得同时保存 A→B 与 B→A。

要求：Normalization Review 已对该 pair 判为 `SCOPE_PARALLEL`，或在 `rationale` 中写明 `NORMALIZATION_JUSTIFICATION:` 并给出理由。

### VERSION_VARIANT_OF

两个 Item 属于同一主题但明确版本不同。此关系为**对称**关系：不得同时保存 A→B 与 B→A。

要求：Normalization Review 已对该 pair 判为 `VERSION_VARIANT`，或在 `rationale` 中写明 `VERSION_JUSTIFICATION:`。

不得解释为 replaces、supersedes 或 deprecated_by。

## 当前禁止的关系

Gate 3.0 禁止：CAUSES、IMPROVES、BETTER_THAN、REPLACES、SUPERSEDES、DEPRECATED_BY、PART_OF、RELATED_TO、SIMILAR_TO、ENABLES、RECOMMENDED_BEFORE、LEARNING_ORDER。

原因：这些关系要么过于模糊，要么容易把营销、推断或教学顺序混进 Knowledge Graph。未来 Gate 可单独增加。

## Edge Epistemic Status

只允许 `DOCUMENTED` 与 `INFERRED`。

- **DOCUMENTED**：只有当 Evidence 或 Knowledge statement **明确支持该关系本身**时才使用。例如官方明确写「2.5 延续了 2.0 的统一多模态架构」，且存在对应两个 Item 时，这种版本关系可有 DOCUMENTED edge。
- **INFERRED**：当关系基于已有 Knowledge Item 的语义、明确的 scope / version / type 与合理的知识依赖判断推导出来时使用。INFERRED Edge 的 `limitations` 必须包含 `INFERENCE_BOUNDARY:`，其后写明推理依据与**不能推出什么**。

## Cross-Layer Rules

- Product Layer 与 Model Layer 的相似能力**必须**以 `SCOPE_PARALLEL_TO` 表达平行关系，不得合并，也不得用 `PREREQUISITE_OF` 掩盖跨层关系。
- 不得把 Model capability 写成 Product availability：模型发布、模型架构、模型能力声明都不能变成「产品已开放」。
- CONSTRAINT / POLICY 的 `CONSTRAINS` edge 默认作用于同层 Item；跨层 CONSTRAINS 必须有直接证据理由，并显式说明其层次。
- 不允许一条 POLICY 批量连向大量节点（Policy Overlinking）。

## Version Rules

- VERSION_CONTEXT Item 可以作为关系骨架：用 `VERSION_CONTEXT_FOR` 为其所描述的版本的其它知识提供背景。
- `VERSION_VARIANT_OF` 只表示「同主题不同版本」，绝不表示替代、下线或优劣。
- 不得把 Model 版本与 Product 版本视为同一对象，也不得把产品版本条目当作模型版本能力。
- 不得由版本先后推断版本替代。

## No Hidden Node

图中出现的每个 `knowledge_id` 都必须同时在该图的 nodes 中列出，且在 Knowledge Registry 中存在。不允许「边引用了节点但节点未声明」，也不允许把 Registry 中不存在的 ID 当作节点。

## Graph != Curriculum

Graph 不是课程：不定义学习顺序、不划分阶段、不产生 lesson / module / prerequisite chain 的教学解释。

`PREREQUISITE_OF` 表达知识依赖，不表达教学顺序；`PROCEDURE_PRECEDES` 表达流程步骤先后，也不表达教学顺序。任何以「课程应该先教 A」为理由建立的 Edge 都违反本 Policy。

Graph 可以在完全不生成 Curriculum 的情况下独立成立。

## Graph != Normalization

Normalization 判断知识是否重复、重叠、不同版本、跨 Scope 平行或冲突候选；Graph 表达可利用的知识关系。两者目的不同：

- `SCOPE_PARALLEL` 与 `VERSION_VARIANT` 可以有对应的 Graph Edge；
- `DISTINCT`、`PARTIAL_OVERLAP`、`EXACT_DUPLICATE`、`CONFLICT_CANDIDATE` **不会**自动生成 Graph Edge。

`CONFLICT_CANDIDATE` 的 pair 在当前合同中不进入图（Gate 3.0 没有审查类关系）。冲突必须在 Source 与 Normalization 层解决，不得用 Graph Edge 静默消解。

## 验证与人工审核

Graph 遵循 [Graph Schema](../assets/knowledge-graph.schema.json)，并由 [Validator](../scripts/validate_knowledge_graph.py) 离线检查：Node 存在性与唯一性、Edge 字段与枚举、类型规则、对称性、Normalization 支撑与冲突安全。

Validator **不判断** PREREQUISITE 的语义是否真的合理，也不判断 rationale 是否充分。这些必须由人工 / Agent Review 承担，并记录在 pilot review 文档中。

Validator PASS 只表示合同成立，不表示图的内容正确。

## 质量优先

不要求图连通，不要求每个节点都有多条边，不设定「边越多越好」。禁止为了「看起来像图」而添加弱关系。只有 8 条高质量 Edge 时，允许只有 8 条。

本 Gate 不进入 Curriculum、Tutor、Assessment、Student State 或全量 Jimeng Graph。

## Addendum — STEP_OF

Added after Gate 3.0。本增补节为**附加式变更**：不重写 Gate 3.0 的 Relation Contract，只在原有六种关系之外增加第七种，用于表达 Procedure 粒度。

### 新增背景

Gate 3.0 的 Seedance Pilot 暴露一个 `RELATION_GAP`：无法表达「一个具体 Procedure Step 属于一个更高层级 Workflow Procedure」。现有六种关系都不适用——`PREREQUISITE_OF` 是知识依赖而非成员关系；`PROCEDURE_PRECEDES` 只表达两个步骤之间的先后，不表达归属；`VERSION_*` 与 `SCOPE_*` 与主题无关。因此新增 `STEP_OF`，且只服务该问题。

### STEP_OF 含义

`from` 表示一个明确的 PROCEDURE step，`to` 表示一个明确的 PROCEDURE workflow，且 `from` 是 `to` 在 Evidence 或 Knowledge statement 中**明确包含**的步骤。

### 语义边界

`STEP_OF` 不是：

- `PREREQUISITE_OF`（成员关系不是知识依赖）；
- `PROCEDURE_PRECEDES`（不表达步骤先后）；
- `PART_OF` 的通用替代；
- Curriculum order。

它只表达：「这个 Procedure Knowledge Item 是那个 Workflow Procedure Knowledge Item 的明确步骤组成」。

### Type Rule

`STEP_OF`：

- `from` 的 `knowledge_type` 必须为 `PROCEDURE`；
- `to` 的 `knowledge_type` 必须为 `PROCEDURE`。

### Evidence / Inference

如果已有 Knowledge statement 或 Evidence 明确说明「该 Workflow 由若干步骤组成，且该 Item 是其中某一步」，可标 `DOCUMENTED`。否则标 `INFERRED`，且 `limitations` 必须包含 `INFERENCE_BOUNDARY:`。

### 方向性

`STEP_OF` 是**方向性**关系，不是对称关系：A 是 B 的步骤，不等于 B 是 A 的步骤。因此：

- 不得同时保存 A→B 与 B→A；
- 保存反向边视为语义矛盾，Validator 必须拒绝（这与 `SCOPE_PARALLEL_TO` / `VERSION_VARIANT_OF` 的「对称关系只存一次」不同，后者的两个方向语义等价，`STEP_OF` 的两个方向语义不等价且后者为假）。

### 禁止泛化

不允许把 `STEP_OF` 扩展成：

- 任意概念层级；
- 任意 feature component；
- 任意 parent-child 关系。

它只服务 Procedure Workflow 的粒度问题。若未来需要其它粒度关系，必须单独提出新的 Addendum，不得复用本关系。

### 与 Normalization 的关系

`STEP_OF` 表达的是流程成员关系，不替代 Normalization 判定。Workflow 级 Item 与 Step 级 Item 之间通常为 `PARTIAL_OVERLAP` 或 `DISTINCT`，**不得**因为同源就判 `EXACT_DUPLICATE`；`PARTIAL_OVERLAP` 本身仍不自动生成 Graph Edge。

### 关系总数

Gate 3.0-R1 之后，允许的关系为七种：`PREREQUISITE_OF`、`PROCEDURE_PRECEDES`、`CONSTRAINS`、`VERSION_CONTEXT_FOR`、`SCOPE_PARALLEL_TO`、`VERSION_VARIANT_OF`、`STEP_OF`。Gate 3.0 的「当前禁止的关系」列表不变，仍然全部禁止。

## Addendum — Graph Integrity Rules

Added after Gate 3.0-R1。本增补节不重写任何既有关系合同，只定义图的**结构完整性**与**关系语义完整性**规则。这些规则由 [Integrity Validator](../scripts/validate_graph_integrity.py) 机械检查，其无法判断的部分由人工审计承担。

### DAG Rule — PREREQUISITE_OF

`PREREQUISITE_OF` 必须形成有向无环图。禁止 `A→B` 与 `B→A`，也禁止 `A→B→C→A` 这类更长环路。原因：知识前置关系不能形成「必须先理解彼此」的闭环。

若出现环：**不得自动删除任意一条**，必须标记 `PREREQUISITE_CYCLE_REVIEW`，逐条审查哪一条 Edge 不是真正的 prerequisite。

### DAG Rule — PROCEDURE_PRECEDES

`PROCEDURE_PRECEDES` 必须无环。禁止两步互为先后，也禁止更长顺序环。若出现，标记 `PROCEDURE_ORDER_CYCLE_REVIEW`，说明当前流程建模错误。

### DAG Rule — STEP_OF

`STEP_OF` 不允许形成层级环：既禁止 `A STEP_OF B` 与 `B STEP_OF A` 并存，也禁止 `A STEP_OF B → B STEP_OF C → C STEP_OF A`。`STEP_OF` 的反向关系不能自动生成（反向边语义为假，见上面的方向性条款）。

### STEP_OF + PROCEDURE_PRECEDES Consistency

若 `A STEP_OF W` 与 `B STEP_OF W`（同一 workflow），则 `A PROCEDURE_PRECEDES B` 是合法的同一 workflow 内顺序。

若 `A STEP_OF W1` 与 `B STEP_OF W2` 而 W1 / W2 没有明确同一流程关系，则 `A PROCEDURE_PRECEDES B` 必须在 `rationale` 中写明 `CROSS_WORKFLOW_ORDER_JUSTIFICATION:`；否则不得建立。

### Redundant Prerequisite Review

若同时存在 `A PREREQUISITE_OF B`、`B PREREQUISITE_OF C`、`A PREREQUISITE_OF C`：**不得自动删除 A→C**，但必须标记 `POTENTIAL_TRANSITIVE_REDUNDANCY`，由人工判断 A 是 C 的**直接必要前置**，还是仅通过 B 间接成立。

输出只允许：`KEEP_DIRECT`、`REMOVE_REDUNDANT`、`NEEDS_REVIEW`。该标记**不是 Validator hard fail**，只作为 warning 报告。

### Pair Relation Compatibility

同一有向 pair `A→B` 禁止同时出现明显互斥的关系。至少检查以下组合，它们默认标记 `PAIR_RELATION_CONFLICT`：

- `PREREQUISITE_OF` 与 `VERSION_VARIANT_OF`
- `PREREQUISITE_OF` 与 `SCOPE_PARALLEL_TO`
- `STEP_OF` 与 `VERSION_VARIANT_OF`
- `STEP_OF` 与 `SCOPE_PARALLEL_TO`

某些 pair 可能合法拥有多个关系，但必须明确说明：在 `rationale` 中写明 `PAIR_RELATION_JUSTIFICATION:` 并给出理由，否则视为未解决的 pair 冲突。本 Gate 不创建通用多关系本体。

### Curriculum Leakage Rule

任何 `PREREQUISITE_OF` Edge，如果 `rationale` 出现「课程里应该先教」「建议先学」「教学顺序上更自然」「为了课程结构」这类逻辑，而没有知识依赖依据，则标记 `CURRICULUM_LEAKAGE`，**必须删除或改写**。

Graph 只表达知识依赖，不表达教学策略。

### Epistemic Status Audit

**DOCUMENTED Edge** 必须能从 Knowledge statement、Evidence 支持的 relation 或已明确发布的关系**直接得到**。不得仅因为两个节点都 DOCUMENTED 就把 Edge 标 DOCUMENTED。

**INFERRED Edge** 必须在 `rationale` 给出推理依据，并在 `limitations` 含 `INFERENCE_BOUNDARY:` 且写明不能推出什么。

### 与既有 Validator 的分工

| 检查 | 归属 |
| --- | --- |
| Node 存在性、Edge 字段与枚举、类型规则、对称性、Normalization 支撑、冲突安全 | [Graph Validator](../scripts/validate_knowledge_graph.py)（Gate 3.0 / R1） |
| 三类环、STEP_OF 反向、workflow 顺序一致性、pair 关系冲突、课程泄漏、认知状态标记、冗余前置 warning | [Integrity Validator](../scripts/validate_graph_integrity.py)（Gate 3.1） |
| prerequisite 语义是否真的合理、rationale 是否充分、扩展就绪判断 | 人工 / Agent 审计 |

## Addendum — Enforcement Context & Documented Group Reference

Added after Gate 3.2。本增补节为**附加式变更**：不重写原 Relation Contract，只增加第八种关系，并为其定义组引用例外。Gate 3.0 / 3.1 / 3.2 的既有条款全部继续有效。

### 新增背景

Gate 3.2 的 Policy Pilot 暴露一个 `RELATION_GAP_CANDIDATE`：平台处理条款（协议第4.8节）与其所执行的整组规则之间的关系无法表达。用 `CONSTRAINS` 会把「后果」写成「边界」（并有把处置升级为法律结论的风险）；用 `PREREQUISITE_OF` 则需对整组规则逐一连接而构成广播。因此新增 `ENFORCEMENT_CONTEXT_FOR`。

### ENFORCEMENT_CONTEXT_FOR 含义

`from` 描述平台处理措施的 POLICY Item 为 `to` 所表达规则的违反或可能违反提供明确的**处理 / 执行上下文**。

只表示：官方政策文本明确将某处理措施与某规则或规则集合的违反 / 可能违反**联系起来**。

### 不等同于因果

禁止把 `E ENFORCEMENT_CONTEXT_FOR R` 解释成「违反 R 一定导致 E」。本关系不表示：

- 一定处罚、自动处罚、处罚概率或处罚预测；
- 法律责任、法律因果；
- 违法认定、合规结论。

不得为此另设 `CAUSES`、`TRIGGERS`、`PUNISHES`、`SANCTIONS`、`VIOLATION_CAUSES` 等强因果关系。

### Type Rule 与方向

- `from` 与 `to` 的 `knowledge_type` 都必须为 `POLICY`；
- `from != to`（处理条款不得指向自身）；
- 方向**不可反转**：只能 enforcement → rule；反向关系必须在证据语义审查中拒绝。
- 当前 Knowledge / Node Contract 没有 enforcement-role 字段。不得凭 ID、语言、关键词或 statement 措辞判定真实角色，也不为此新增领域专属字段。
- Graph Validator 检查 POLICY → POLICY、端点存在、无 self-edge 以及成对反向边不得并存；单条边的真实方向由 Evidence-backed Semantic / Edge Review 判断。机械 PASS 不等于方向语义 PASS。
- 不自动生成反向 Edge。最终保留边必须经逐边语义审核，明确 from 描述处理措施、to 描述被覆盖的规则，并在 Edge Review 中为 KEEP / DIRECT / curriculum_leakage=false；NEEDS_REVIEW 不得随最终图通过验收。

### 与 CONSTRAINS 的分工

`CONSTRAINS`：规则 A 对行为 / 输入 / 输出 / 使用边界形成限制。
`ENFORCEMENT_CONTEXT_FOR`：处理条款 E 说明当规则 R 被违反或可能违反时，平台拥有某种处理上下文。

两者不得混用。处理条款不因「它提到了某规则」而对该规则的**行为面**形成边界。

### DOCUMENTED_GROUP_REFERENCE

Policy Overlinking Rule 继续有效，但新增一个**严格例外**：

如果官方 Evidence 明确使用「上述约定」「前述规则」「以下各项」「本节规定」等**对一个可明确枚举的规则集合**的组引用，则允许一个 Policy Item 对该集合中的多个 Policy Item 产生 fan-out。这不属于过度广播。

### 组引用的必要条件

若同一个 `from` 产生多条 `ENFORCEMENT_CONTEXT_FOR`，每条 `rationale` 必须包含 `DOCUMENTED_GROUP_REFERENCE:`，并说明：

1. Evidence 中的组引用原文语义；
2. 当前 target 为什么属于该组（须指明对应哪一条款）；
3. 不能推出什么。

### 防无限扩张

组引用例外**不能**扩张到「整个平台所有 POLICY」「所有 Product Item」或「所有 Graph Node」，只允许 Evidence 文本可明确枚举的组。

若未来来源写「违反本协议任何条款」是否允许全协议 fan-out，**不在本增补节解决**，记录为未来 contract question。

守则由人工 / Agent 审计承担：Integrity Validator 在同一 from 的 fan-out >=3 时强制每条 rationale 含组引用标记；语义审查对所有多边 fan-out（包括 2 条）执行组引用要求，并逐条验证集合成员资格，不能把标记存在当作证据成立。

### Epistemic Status

若 Evidence 明确写出「违反或可能违反上述约定 → 平台有权采取处理措施」，则该 Edge 可标 `DOCUMENTED`——关系本身被证据直接表达。**不得因为 fan-out 较多而自动降为 INFERRED。**

`DOCUMENTED` 的 `ENFORCEMENT_CONTEXT_FOR`，其 `rationale` 必须明确写出组引用（`DOCUMENTED_GROUP_REFERENCE:`）或单条直接引用（`DIRECT_REFERENCE:`）。只有来源确实单独引用该规则时才使用 DIRECT_REFERENCE；即使只选一条边，依据为组引用时仍标 DOCUMENTED_GROUP_REFERENCE。

INFERRED 继续遵守既有 INFERENCE_BOUNDARY 规则，不因 fan-out 数量自动改变认知状态。

该关系适用于平台规则、社区规范、软件使用政策及组织制度中的处理条款与被引用规则，不依赖具体平台或条款编号。它表达处理上下文，不表达执行顺序、因果或知识前置。

### Pair 兼容性

`ENFORCEMENT_CONTEXT_FOR` 与 `VERSION_VARIANT_OF` 或 `SCOPE_PARALLEL_TO` 出现在**同一 pair**（任一方向）时，视为 pair conflict 并**硬拒绝**（不适用 `PAIR_RELATION_JUSTIFICATION:` 逃生口）。

### DAG

`ENFORCEMENT_CONTEXT_FOR` **不参与** DAG 检查（它不是知识依赖或流程顺序）。

### 关系总数

Gate 3.2-R1 之后允许的关系为八种：`PREREQUISITE_OF`、`PROCEDURE_PRECEDES`、`CONSTRAINS`、`VERSION_CONTEXT_FOR`、`SCOPE_PARALLEL_TO`、`VERSION_VARIANT_OF`、`STEP_OF`、`ENFORCEMENT_CONTEXT_FOR`。Gate 3.0 的「当前禁止的关系」列表不变，仍然全部禁止。

## Addendum — Curriculum Leakage Validation Boundary

Added after Gate 3.2-R1；Gate 3.2-R2。此澄清替代上文将课程泄漏分配给 Integrity 脚本判断的实现分工，不改变任何 Relation semantics。

Curriculum Leakage prohibition remains unchanged. Graph 表达知识结构，任何关系都不得仅因课程编排偏好而建立。PREREQUISITE_OF 必须表示真实知识理解依赖；PROCEDURE_PRECEDES 表示程序步骤顺序，不表示教学先后。

Python Validator 不用中文、英文关键词、正则黑名单、ID、平台名称或 marker 与关键词组合判断自然语言语义。Integrity 保留 DAG、类型、pair 冲突、认知状态等机械规则，不再据课程词语判定泄漏。

KNOWLEDGE_DEPENDENCY: 只记录作者声称存在知识依赖，不证明依赖成立，也不是本 Gate 新增的必填标记。marker presence ≠ semantic truth；既有正式必需标记仍按原合同检查格式。

Evidence-backed Edge Review 必须逐边判断：真实依赖是否成立、理由是否仅为课程偏好、否定句是否在排除泄漏，以及任意语言的 rationale 是否与 marker 相符。不得用 marker 或脚本 PASS 代替证据审查。

机器层检查 Review 覆盖、字段、boolean 类型及已记录的最终状态，不分析 review_reason 的自然语言。validate_edge_review.py 默认模式保持原有审核记录格式检查，允许记录 REMOVE / MODIFY / NEEDS_REVIEW；默认 PASS 不代表最终图可以接受。

production / accepted Graph 必须运行 validate_edge_review.py <review.json> <graph.json> --final，并同时通过 Graph、Integrity 与证据语义审查。最终每条保留边必须 status=KEEP、curriculum_leakage=false，NEEDS_REVIEW=0。--final 只验证已记录状态，不推导审核结论。

若发现 leakage=true，记录 REMOVE 或 MODIFY；从最终图移除，或修改后重新审核，不得带入最终验收。不确定边 OMIT。保留独立的历史审核记录，最终 review 只对应最终图的边。

Graph / Knowledge / Node / Edge 不新增 curriculum_role 等字段；继续使用既有 Review 字段。Enforcement 方向继续由证据语义审查判断，不恢复关键词逻辑。
