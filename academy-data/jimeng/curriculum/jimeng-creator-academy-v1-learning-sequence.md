# Jimeng Creator Academy V1 — Learning Sequence Summary

日期：2026-10-04。对象：`jimeng-creator-academy-v1-blueprint.json`。本文件只总结顺序与边界，**不含任何 Lesson 内容**。

## 1. Module 顺序（8）

```text
JCA-M01 产品、模型与创作入口认知          HEAVY_BUT_COHESIVE
JCA-M02 第一次基础图片生成                COHESIVE
JCA-M03 视频生成流程与产物                COHESIVE
JCA-M04 Prompt 基础表达与调整             COHESIVE
JCA-M05 参考素材输入与用途区分            COHESIVE
JCA-M06 编辑与局部修正                    COHESIVE
JCA-M07 平台使用规则与生成准入            HEAVY_BUT_COHESIVE
JCA-M08 综合独立创作                      HEAVY_BUT_COHESIVE
```

Module 层顺序类型（承接 Gate 4.1 Order Review）：`GRAPH_CONSTRAINED = 0`、`PEDAGOGICAL = 6`、`INDEPENDENT = 1`。**Module 层没有任何硬顺序约束**，全部为教学或课程组织选择。

## 2. 每个 Module 的 Lesson 顺序（24 Lessons）

```text
JCA-M01  L01 产品声明、模型声明与版本记录的区别 → L02 创作入口、准入条件与客户端范围
JCA-M02  L01 图片生成流程与提示输入 → L02 查看生成结果与导出 → L03 模型能力与产品流程的范围分离
JCA-M03  L01 视频生成三步流程与第一步 → L02 第二步：素材与提示词输入 → L03 第三步：生成、预览与保存
JCA-M04  L01 提示词在生成流程中的角色 → L02 视频提示词组织与主体不清楚时的修订 → L03 图片提示词对象组织与歧义修订
JCA-M05  L01 参考生视频的方式与参考素材类型 → L02 参考内容的加入路径与总量提示 → L03 参考用途与使用边界
JCA-M06  L01 局部编辑的能力与保留边界 → L02 图片修改任务的执行与交付
JCA-M07  L01 输入内容的义务与权属要求 → L02 AI 内容标识规则 → L03 内容合规要求与禁止内容类型 → L04 平台处理上下文与生成动作的准入前提
JCA-M08  L01 创作准备：入口、准入与任务目标 → L02 独立完成一次图片创作流程 → L03 独立完成一次视频创作流程并加入参考素材 → L04 修正与交付
```

Lesson Role 分布（按真实内容决定，未强凑类型）：FOUNDATION 2、CONCEPT 3、PROCEDURE 11、APPLICATION 1、SAFETY 4、INTEGRATION 4。

## 3. 哪些顺序是 Graph constrained

**4 个 Lesson transition 为硬顺序**（`SWAPPABLE: false`）：

| Transition | 依据 edge | 两端 Knowledge |
| --- | --- | --- |
| JCA-M02-L01 → L02 | `CRR2-E-0004` | K-0052 → K-0053 |
| JCA-M03-L01 → L02 | `JIM-E-0004` | K-0010 → K-0011 |
| JCA-M03-L02 → L03 | `JIM-E-0026` | K-0011 → K-0046 |
| JCA-M05-L02 → L03 | `JIM-E-0001`、`JIM-E-0003` | K-0017 → K-0015、K-0017 → K-0023 |

这四条边在 **Module 层**落在单一 Module 内部（故 Module 层为 0），在 **Lesson 层**因 from/to 被分配到不同 Lesson 而成为硬顺序。两层结论不矛盾，见 `jimeng-creator-academy-v1-lesson-order-review.md` 第 10 节。

## 4. 哪些只是 pedagogical

**7 个 transition**，均带 `PEDAGOGICAL_RATIONALE:`，**不是**知识 prerequisite：

```text
M01-L01 → L02   先分层判断，再落到入口与准入
M04-L01 → L02   先讲提示词位置与要素，再讲写法
M05-L01 → L02   先讲参考方式与素材类型，再讲界面路径
M06-L01 → L02   先讲能力与边界，再执行修改
M07-L03 → L04   先学并列规则，再把规则落到动作上
M08-L01 → L02   先做创作准备，再进入创作
M08-L03 → L04   先有产出物，再做修正
```

## 5. 哪些可交换

**12 个 transition 可交换**（4 个 GRAPH_CONSTRAINED 不可交换，其余全部可交换）：

```text
INDEPENDENT（完全可交换，5 个）：
  M02-L02 → L03  范围分离课可前置或后置
  M04-L02 → L03  视频/图片提示词方法课可互换
  M07-L01 → L02  输入义务课与标识课可互换
  M07-L02 → L03  标识课与禁止内容课可互换
  M08-L02 → L03  图片链路与视频链路可互换

PEDAGOGICAL（可交换，代价是学习便利，7 个）：见第 4 节。
```

## 6. 关键 scope boundary

| 边界 | 内容 |
| --- | --- |
| 客户端 | 实践环境为 **Jimeng Web**；2026-10-04 观察到的未登录创作首页、已登录图片生成界面、已登录视频生成 / 全能参考界面、已登录图片修改任务界面。iOS / Android 与其它地区/账号**未验证** |
| 模型 | 产品层可见行为限 **Seedance 2.5** 与 **Seedream 5.0 Pro**；Model Layer 能力**不**教成产品可用性 |
| 平台规则 | 限 **P14 所保存的第 4.1–4.8 节命题**；不含《社区自律公约》、阈值或法律解释 |
| 未验证项（保持 NOT_VERIFIED，不写成 UNSUPPORTED） | 独立音频上传路径；结果页「局部重绘」「去画布编辑」等子工具的**内部步骤**；Seedance 视频编辑（本轮证据未验证） |
| 不承诺项 | 建议性像素数值不是规格；生成张数与耗时表述不是承诺；「其他保持不变」是用户修改要求而非产品保证；不保证修改结果保真度 |
| 非必修范围 | CRD-10（future_extension）、CRD-11（deferred_dynamic）、CRD-12（deferred_optional）、CRD-13（out_of_scope）未进入任何 Module 或 Lesson |
| 未使用知识 | `JIM-K-0002`、`JIM-K-0018` 保持 `UNMAPPED_NONBLOCKING_KNOWLEDGE` |

## 7. 上游状态

```text
Source / Evidence / Knowledge / Normalization / Production Graph
Frozen Graph Contract / Curriculum Readiness Contract / Gate 4.1 Module Skeleton
→ 全部 0 mutation
```

本文件为新增总结，未修改任何上游文件、Gate 4.1 Skeleton 或 Blueprint 本身。
