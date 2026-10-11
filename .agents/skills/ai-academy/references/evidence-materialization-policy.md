# Evidence Materialization Policy

## 职责边界

Evidence Materialization 把已经审核过的 Evidence Unit 保存为最小、稳定、可重新读取的本地证据材料；目标不是网页存档或整站镜像。

- Source Registry：来源是谁、在哪里、什么版本、什么状态。
- Materialized Evidence：审核时真正看到了什么证据。
- Knowledge Item：这些证据可以安全支持什么知识。

三者分别维护，不得混为一体。材料可读不等于来源 accepted，也不等于知识 validated；读取失败不自动改变来源的历史审核状态。Source Registry Schema 与 Gate 1.3 Readiness 保持不变。

## 最小材料

只保存支持当前 Evidence Unit 所必需的最小正文范围。禁止整站镜像、批量抓取、无关页面复制或默认保存巨大网页全文。仅在 evidence_scope 为 entire source 且资料很短时，才可保存完整文本。

同一 URL 的不同 Evidence Unit 分别保存为 <source_id>.md，不混合范围。允许逐字短摘录，必须标明局部截取、段落位置和遗漏范围；不得把局部材料说成完整覆盖原 evidence_scope。后续只能引用实际保存的内容，不能凭标题、范围标签或记忆补齐上下文。

仅本轮重新读到的原始正文可以新建材料；禁止搜索摘要、缓存摘要、模型记忆、其他教程或替代 URL。遵守引用限制，不将改写摘要冒充原文。范围不足时保留缺口。

## 材料格式与方法

每个 Markdown 使用以下结构，元数据独占一行且填写非空值：

```markdown
# Evidence Material

Source ID: 来源 ID
Original Location: 原始 URL 或本地来源路径
Captured At: YYYY-MM-DD
Evidence Scope: 原 Evidence Unit 审核范围
Materialization Method: DIRECT_READ 或 MANUAL_CAPTURE

## Evidence Extract

本轮实际读到的正文摘录。

## Capture Notes

记录完整或局部截取、具体遗漏、登录要求、动态加载和读取限制；未知项明确标为未知。
```

DIRECT_READ：本轮直接读取原始来源并核对后保存其最小正文。

MANUAL_CAPTURE：用户或审核者在浏览器真实打开原始来源，把 Evidence Scope 对应正文保存到本地。必须记录 Original Location、Captured At、Evidence Scope，不得省略来源。本 Gate 仅定义此方式；没有用户提供的真实正文时不得假装完成。

## Registry 与状态

materialization-registry.json 根对象包含 materials 数组。每项字段：source_id、materialized_path、captured_at、evidence_scope、capture_status、notes。source_id 不重复，必须存在于 Source Registry。日期使用有效 YYYY-MM-DD。

- AVAILABLE：存在可读取的本地材料；是否完整由 Capture Notes 说明。
- BLOCKED：本轮无法重新取得证据。不创建伪造正文，materialized_path 可为 null 或省略；captured_at 记录本轮尝试日期，notes 记录原因。
- STALE：材料存在，但已知与当前来源版本有变化，需复核；notes 说明已知变化。不得当作当前版本证据。

materialized_path 相对本 materialization-registry.json 所在目录解析，也可使用绝对路径，不依赖命令运行目录。AVAILABLE 与 STALE 必须指向可读取的 Markdown；BLOCKED 不因缺文件失败。未取得新材料时不要伪造或覆盖历史正文。

## 离线验证

运行：python .agents/skills/ai-academy/scripts/validate_materialization_registry.py <materialization-registry.json> <source-registry.json>

只用 Python 标准库，检查 JSON、引用 ID、重复、状态、日期、文件和 Markdown 必填标识；核对 Markdown 的 ID、日期、来源地址及范围与 Registry 的一致性。PASS 仅代表机械检查通过，不证明正文真实性、完整性、充分性或网页仍未更新。验证器不联网、不自动比较网页、不改变来源或知识状态。

本 Gate 不开展新的知识入库、图谱、课程或 Gate 2.1。
