# JCA-A-011 — 视频提示词的组织与主体不清楚时的修订

> 机器事实以 `JCA-A-011.json` 为准。本文件是该 JSON 的无损人类可读渲染：合同字段文字逐字保留，仅允许引号字形与 Markdown 排版差异。

| assessment_type | lesson_ids | max / pass | alignment |
| --- | --- | --- | --- |
| PERFORM_PROCEDURE | JCA-M04-L02 | 10 / 8 | DIRECT |

**Purpose**：测量 JCA-M04-L02 的两条 outcome：学生要按官方建议组织一条视频提示词，并在主体表达不清楚时完成一次修订。

**Target Outcomes**
- 输入按官方建议组织的视频提示词
- 在主体表达不清楚时补充描述并完成一次修订

**Knowledge Refs**：JIM-K-0047, JIM-K-0048

**Scope**：Jimeng Product Layer；官方视频生成器 FAQ 的基础表达建议（组织方法与主体不清时的补足）。

## Task

写出两条视频提示词：第一条按官方建议用主体、场景、动作、运镜和光线组织；第二条是在第一条出现主体不清楚时的修订版本，修订方式为补足主体的外观和位置。然后说明这两条建议的适用边界。

## Expected Evidence

①第一条提示词中五个组织要素均可见；②第二条提示词中补足了主体的外观与位置；③一句说明该建议未给出适用模型或版本、不是效果结论、不保证一次成功。

## Scoring Criteria

| criterion | 描述 | 证据来源 | 权重 | 通过条件 |
| --- | --- | --- | --- | --- |
| A011-C1 | 按五要素组织出视频提示词 | 写出的提示词 | 2 | 主体、场景、动作、运镜、光线五项在提示词中均可辨认 |
| A011-C2 | 完成一次主体不清楚的修订 | 修订后的提示词 | 2 | 修订以补足主体外观与位置的方式作出，而非整句重写 |
| A011-C3 | 说明建议的适用边界 | 手写说明 | 2 | 指出未给出适用模型或版本、不是效果结论、不保证一次成功 |
| A011-C4 | 不把建议写成承诺或公式 | 整体作答 | 2 | 没有任何一处把五要素写成固定顺序或必填公式，也没有效果保证 |
| A011-C5 | 修订可辨认 | 两版提示词对照 | 2 | 两版之间的差异可被指出，且差异仅在主体描述部分 |

**Partial Credit**：允许 partial credit：每条 0/1/2。五要素漏一项得 1、漏两项及以上得 0；修订方向正确但未说明补足内容得 1。不因用词与官方建议不同扣分。

**Allowed Support**：lesson notes / course outline
**Disallowed Support**：external web search / unverified community tutorial / another person's completed answer

## Feedback Boundary

评分后只可告知：哪条 criterion 未达标、对应 Lesson（JCA-M04-L02）、以及「官方建议 ≠ 效果承诺」这一 boundary 提醒。不得补充字数、语法或完整 Prompt 技法。

## Limitations

只覆盖 2026-10-04 读取的官方 FAQ 基础建议；未给出适用模型或版本；不是效果结论、不保证一次成功；不含教学示例原文、完整 Prompt 技法、UI 操作或输入参数；一次评估不代表长期掌握。
