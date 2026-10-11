# Source Policy — Gate 1.1

## 职责与边界

Source Engine 定义资料准入规则，记录来源身份、位置、版本与日期，分类来源类型和可信级别，标记信息状态与来源生命周期，并检查 Registry 的基础结构与明确的跨字段语义约束。

本阶段仅处理人工录入的本地 JSON，不搜索、抓取、下载或联网核实资料，不提供 RAG、向量数据库、知识抽取、知识图谱、课程生成、AI 教学、MCP 或浏览器自动化。

## 准入原则

每条来源必须具有可识别的 source_id、标题、发布者、来源位置及完整必填字段。位置可以是 URL 或本地文件路径；记录位置不代表已访问或验证。source_id 在同一 Registry 内唯一。

待评估资料可以以 candidate 入库，包括 Tier E。只有人工核对身份、相关性、适用范围及证据后，才可设为 accepted；尚未验证的资料不应标为 accepted。无法确认日期时填 null，无法确认版本时填 unknown，不编造信息。拒绝的来源可保留记录与原因供追溯。

Validator 输出 PASS 仅表示数据符合结构规则与已定义的语义约束，不证明来源真实、内容正确或已经满足准入审核。示例数据不得作为真实知识来源。

## Evidence Unit

Source Registry 不是网页收藏夹。每条 source 记录代表一个可独立引用和审核的证据单元（Evidence Unit），source_id 标识该证据单元。

一个 URL、本地文件或文档：

- 可以只对应一个 Evidence Unit。
- 如果包含不同 information_type、不同版本范围或互相独立的证据，应拆成多个 Evidence Unit。
- 多个 Evidence Unit 可以共享同一个 location，但须各自具有唯一 source_id。

禁止为了方便，给一整份包含不同性质信息的资料统一赋予一个 information_type。

evidence_scope 是必填的非空白字符串，用于说明该证据单元覆盖整份来源还是其中哪一部分。例如 entire source、section: Reference Image、pages 12-18 或 experiment: test case 03。无法获得更精确范围，但整个资料就是一个证据单元时，填写 entire source。

本阶段只记录人工描述的证据范围，不创建复杂文档切片系统，不增加 XPath、CSS selector、DOM locator、hash 或 chunk id。

## 来源五级模型

| 级别 | 定义 | 分类依据 |
| --- | --- | --- |
| Tier A | 官方一手资料 | 目标平台或产品官方发布的文档、帮助、更新记录、课程或公告。 |
| Tier B | 权威一手资料 | 与主题相关的原始论文、正式标准或权威技术主体直接发布的资料。 |
| Tier C | 高质量二手资料 | 具有明确作者、证据引用与专业质量的教材、专业教程或分析。 |
| Tier D | 社区经验 | 社区帖子、论坛讨论或用户实验，适用范围与可复现性需单独核对。 |
| Tier E | 未验证资料 | 身份、依据或质量尚不足以确认的资料。 |

source_type 表示资料形式，trust_tier 表示可信级别，二者不自动映射。视频、书籍等应结合发布者及证据分类；官方身份也不保证所有内容永远正确。

## 信息状态

- DOCUMENTED：官方或权威资料明确记载；应保留直接依据。
- OBSERVED：经过可复现实验观察；应在 notes 中说明实验条件、步骤与结果，或引用本地实验记录。
- INFERRED：基于资料推断，但没有直接证据；应说明推断依据与限制。
- UNVERIFIED：尚未验证。

information_type 与可信级别、生命周期分别记录。专业教程不自动属于 DOCUMENTED，用户实验也只有满足可复现条件才能标为 OBSERVED。若同一资料包含不同性质的信息，应分别记录并说明范围，避免给全部内容统一背书。

## 来源冲突基本原则

- 对同一适用范围，新版本官方资料优先于旧版本官方资料；旧版本资料仍保留其历史适用范围。
- 官方事实与社区经验必须分别保存，不直接混合。
- 实测结果不得自动覆盖官方描述。
- 存在冲突时必须保留双方来源。
- 无法解决的冲突标记 unresolved；在双方 notes 中记录该标记、对方 source_id 与冲突说明，不新增冲突系统。
- 不得为了生成完整课程而隐藏知识缺口；在 notes 中明确缺口与待核实事项。

## 版本与日期原则

所有可能随平台升级发生变化的资料，应在 version_scope 记录适用版本或时间范围。version_scope 必须存在且不能空白；无法确定时填写 unknown。

published_at 为发布日期，last_verified_at 为最近人工核实日期，均填写 YYYY-MM-DD 或 null。不要把录入日期当作发布日期或核实日期。日期必须是实际存在的日历日期。

## 来源生命周期

- candidate：已登记，等待人工评估，尚未正式采纳。
- accepted：已经人工审核，可在明确的版本及证据范围内使用；不代表永久有效。
- stale：可能因版本或时间变化而过时，需要重新核实。
- deprecated：已确认被替代或不再适用于当前范围，保留作历史追溯。
- rejected：不满足准入要求，禁止作为采纳依据；在 notes 记录原因。

生命周期由人工维护，Validator 不自动升级状态或判断时效。

## Registry 与本地校验

Registry 根对象只包含 sources 数组，每个元素遵循 [Source Registry Schema](../assets/source-registry.schema.json)。结构上 notes 可为空字符串，其他文本字段不得为空白；notes 另受下述语义规则约束；未知发布者或语言可显式写 unknown。根对象和来源对象不接受未定义字段，避免拼写错误被静默忽略。

使用 [Validator](../scripts/validate_source_registry.py) 检查 JSON、结构、必填字段、枚举、日期、版本范围及 source_id 唯一性。结构校验通过后，再执行下述语义校验；结构校验失败时先报告结构错误。该脚本仅使用 Python 标准库，不核实 URL 可达性、本地资料存在性或来源内容。

## Semantic Validation

1. status = accepted 时，information_type 不得为 UNVERIFIED。
2. status = accepted 时，trust_tier 不得为 E。
3. status = accepted 时，last_verified_at 不得为 null。
4. information_type = OBSERVED 时，notes 不得为空白，须说明实验条件、步骤、结果或指向实验记录。
5. status = rejected 时，notes 不得为空白，须记录拒绝原因。
6. status = stale 或 deprecated 时，notes 不得为空白，须说明失效或过时原因。

语义错误以 SEMANTIC: 标记。脚本只检查这些可确定的字段组合及 notes 是否非空白，不判断说明是否充分、作者是否权威、URL 是否官方，也不根据域名决定 trust_tier。人工审核仍负责证据真实性与内容质量。
