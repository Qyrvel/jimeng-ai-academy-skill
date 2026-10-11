---
name: ai-academy
description: 构建、维护、教学并评估本仓库中的 AI Academy。用户要求系统学习即梦/Jimeng、从零开始课程、继续课程、课程练习/考核、Mastery/课程完成判断，或维护 Academy 的 Source→Knowledge→Graph→Curriculum 流程时使用；依据 canonical 仓库真值并保持产品/模型/版本边界。不用于普通广告文案、单次提示词优化或无关代码任务。
---

# AI Academy

## Skill 的目标

用户只需指定一个平台、软件、学科或知识领域，例如即梦、DaVinci Resolve、Premiere Pro 或 Blender，即可作为未来学院的学习主题。

长期目标是基于可信资料建立完整知识体系，将知识拆成原子知识点，建立前置依赖关系与知识图谱，再生成从零开始的结构化课程。通过讲解、练习、作业、测验、复习和学习状态追踪，逐步帮助学习者达到能够独立实践的水平。

Jimeng Creator Academy V1 Phase 1 已实现，可依据 canonical 课程开展教学、Assessment、Mastery 决策与 Course Evaluation。其它主题的学院建设仍是扩展方向；持久 Student State、Tutor Engine 与自适应学习不属于 Phase 1。

当前课程入口为项目根目录下 `academy-data/jimeng/course/jimeng-creator-academy-v1/course-manifest.json` 与同目录 `course-outline.md`，包含 24 个 canonical Lessons。`academy-data/jimeng/assessment/` 下的 `full-assessments/full-assessment-set.json`（23 个 Assessments）、`full-assessment-mapping.json`、`mastery-map.json`（24 个 units）与 `course-evaluation/course-evaluation-contract.json` 为评估入口。教学与考核读取这些真值及对应 Lesson/Assessment，不现场另编课程；需要解释合同或执行判定时，按需读取 `references/` 中对应 policy 与 `scripts/` 中现有 evaluator/validator。

## 适用场景

- 用户希望围绕指定主题建立系统学习路径，而非只解决一个零散问题。
- 用户希望从零开始，逐步掌握基础知识、操作技能和独立实践能力。
- 讨论通用 AI 学院的学习目标、资料标准与后续建设范围。

## 不适用场景

- 一次性知识问答、单个操作答疑或临时故障排查。
- 仅要求代做成品、代完成作业，且没有学习目标的任务。
- 要求持久学习状态、Tutor Engine 或自适应学习；这些不属于当前 Phase 1，不自动扩展实现范围。

## 核心原则

- 可信且可追溯：优先采用官方文档、权威教材与可靠的一手资料，保留来源和适用版本；区分已证实内容、推断与待核实信息。
- 知识原子化：每个知识点围绕一个可解释、可练习、可检验的学习目标，明确其前置条件。
- 循序渐进：按前置依赖组织学习路径，结合学习者基础调整进度，避免跳过必要基础。
- 实践与反馈：以能够独立实践为目标，通过练习、作业和测验发现薄弱点，再安排复习；不把完成阅读等同于掌握。
- 主题通用：不绑定单一平台或软件，尊重具体领域的资料、版本与实践要求。
- 范围克制：当前使用已实现的 canonical 课程与评估合同；不扩展实现网络爬虫、知识图谱算法或课程生成算法，不安装额外 Python 包，不接入 MCP，不创建复杂数据库，不复制任何第三方 Skill 内容。

## 学院建设的大致阶段

1. 明确学习主题、目标、学习者基础和适用版本。
2. 收集并核实可信资料，界定知识体系的覆盖范围与缺口。
3. 拆解原子知识点，标明前置依赖，形成知识图谱。
4. 按依赖关系组织从零开始的课程与阶段实践目标。
5. 开展讲解、练习、作业与测验，根据反馈安排复习。
6. 依据当前 evidence 检验独立实践能力；持久学习状态追踪与自适应路径为未来范围。

## 当前实现与后续范围

- 本仓库已有 Jimeng 的 Source、Knowledge、Graph、Curriculum、Blueprint 与 canonical 课程；不将这些已实现内容说成未来规划。
- canonical Lesson 支持讲解与练习；Assessment、Mastery 与 Course Evaluation 支持基于一次 evidence snapshot 的评估，不代表永久掌握状态。
- 自动资料更新、其它主题课程建设、个性化学习路径、学习状态持久化与进度追踪仍属后续范围。

`references/`、`scripts/` 和 `assets/` 已包含 policy、validator/evaluator 与 schema；项目的 `academy-data/` 和 `tests/` 已包含课程真值与测试。以实际文件为准，按任务读取。
