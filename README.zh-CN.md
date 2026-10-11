# Jimeng AI Academy Skill

> 一个以证据为基础、可验证、可测试的即梦 AI 系统学习 Skill：从来源治理、知识结构，一直到课程、考核、Mastery 与课程级完成判断。

[English](README.md) · [架构](docs/architecture.md) · [贡献指南](CONTRIBUTING.md) · [路线图](ROADMAP.md)

## 项目是什么

这是一个**非官方社区项目**。当前公开基线包含面向零基础普通创作者的 **Jimeng Creator Academy V1**。它不是让模型在聊天时临时编一套课程，而是把课程真值、Lesson、Assessment、Mastery 与 Course Evaluation 固化为可读、可校验的仓库资产。

```text
Source / Evidence
  → Knowledge Items
  → Knowledge Graph
  → Curriculum / Blueprint
  → 24 Canonical Lessons
  → 23 Concrete Assessments
  → 24 Mastery Units
  → Course Evaluation
```

当前基线：

- 8 个模块
- 24 个 canonical Lessons
- 23 个 concrete Assessments
- 24 个 Mastery Units
- Mastery 分支：`PASS / RETRY / REMEDIATION / BLOCKED`
- Course 分支：`COMPLETE / RETRY_REQUIRED / REMEDIATION_REQUIRED / BLOCKED`
- 核心 validator/evaluator 只使用 Python 标准库
- Skill 入口：`.agents/skills/ai-academy/SKILL.md`

## 核心原则

项目特别强调不要把以下内容混为一谈：

- 产品声明 vs 模型声明
- 历史发布记录 vs 当前可用状态
- 模型能力 vs 某账号/地区/客户端是否开放
- DOCUMENTED / OBSERVED / INFERRED / UNVERIFIED

## 如何开始

克隆仓库后，把仓库根目录作为支持项目级 Agent Skills 的工作区打开。然后可以直接提出系统学习意图，例如：

```text
我完全不会即梦 AI，请从第一课开始系统教我。
按讲解 → 练习 → 作答 → 批改 → 达标后继续的方式推进。
```

Skill 的触发范围经过正负场景设计：系统学习、正式课程、练习/考核、Mastery 判断应该触发；普通广告文案、单次提示词润色和无关代码任务不应被强行接管。

详细安装与验证见 [docs/install-codex.md](docs/install-codex.md)。

## 课程结构

1. 产品、模型、版本与创作入口认知
2. 第一次基础图片生成
3. 视频生成流程与产物
4. Prompt 基础表达与调整
5. 参考素材输入与用途区分
6. 编辑与局部修正
7. 平台使用规则与生成准入
8. 综合独立创作

权威课程目录：`academy-data/jimeng/course/jimeng-creator-academy-v1/course-outline.md`。

## 为什么公开版没有原始网页逐字摘录

冻结开发基线中保留了最小 Evidence Material，用于内部可追溯审计，其中部分是第三方官网、App Store 页面或服务协议的逐字摘录。公开版**不会再分发这些第三方逐字材料**，只保留来源 URL、Evidence Scope 与来源元数据。贡献者需要根据原始来源自行复核，并遵循 Evidence Materialization Policy 只保存必要的最小证据。

参见 [THIRD_PARTY_SOURCES.md](THIRD_PARTY_SOURCES.md) 与 [docs/evidence-model.md](docs/evidence-model.md)。

## Phase 1 明确不包含

- 持久 Student State
- Tutor Engine
- Adaptive Learning
- GPA / gradebook / 课程百分制毕业线
- 自动判断某个真实账号当下是否开放具体产品能力

## 开发与测试

```bash
python scripts/run_public_smoke.py
```

## 参与共建

欢迎贡献来源核验、版本更新、课程改进、翻译、本地化、测试用例、validator 强化，以及基于同一架构构建新的 Academy。提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

本公开导出中由项目贡献者原创的代码、schema、policy、课程结构、测试与教育内容默认采用 **Apache License 2.0**；第三方名称、商标、链接及其原始内容不因本仓库的 License 而改变权利归属。参见 [LICENSE](LICENSE)、[NOTICE](NOTICE)、[THIRD_PARTY_SOURCES.md](THIRD_PARTY_SOURCES.md)。

## 非官方声明

本项目为社区独立开发，**不隶属于、未受赞助、也未获得即梦 AI、字节跳动、剪映/CapCut、Seed、Apple、火山引擎或其关联方的官方背书**。所有商标及产品名称归各自权利人所有。
