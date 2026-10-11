# Course Evaluation Contract — Jimeng Creator Academy V1

Gate 4.7B machine truth: `course-evaluation-contract.json` in this directory.
This Markdown is a **lossless** expression of that JSON: every leaf value below is the machine
value, rendered as `` `dotted.key.path`: value``. The JSON is the machine truth; if the two ever
disagree, the JSON wins and the validator fails (`COURSE_EVALUATION_MARKDOWN_CONSISTENCY: FAIL`).

---

## 1. Identity

- `contract_id`: jimeng-creator-academy-v1-course-evaluation
- `course_id`: jimeng-creator-academy-v1
- `status`: course_evaluation_contract
- `outcome_reference_form`: `<lesson_id>#<0-based index into that lesson's learner_outcomes>`
- `purpose`: 把已冻结的 24 个 canonical Lesson mastery 决策、8 个 Module 结构与 4 个 hard Lesson transition 聚合成一个确定性、可验证的课程级评价合同。不生成新的教学内容，不存储学习者状态，不产生数字成绩。

## 2. Decision enum and precedence

- `decision_enum`: COMPLETE | RETRY_REQUIRED | REMEDIATION_REQUIRED | BLOCKED
- `forbidden_decisions`: FAILED | GRADUATED | FINAL_GRADE
- `precedence`: BLOCKED > REMEDIATION_REQUIRED > RETRY_REQUIRED > COMPLETE

## 3. Lesson mastery input contract

- `lesson_mastery_input_contract.source`: academy-data/jimeng/assessment/mastery-map.json
- `lesson_mastery_input_contract.decision_enum`: PASS | RETRY | REMEDIATION | BLOCKED
- `lesson_mastery_input_contract.lesson_to_module_decision.PASS`: COMPLETE
- `lesson_mastery_input_contract.lesson_to_module_decision.RETRY`: RETRY_REQUIRED
- `lesson_mastery_input_contract.lesson_to_module_decision.REMEDIATION`: REMEDIATION_REQUIRED
- `lesson_mastery_input_contract.lesson_to_module_decision.BLOCKED`: BLOCKED
- `lesson_mastery_input_contract.rule`: 课程级评价不重新发明 Lesson mastery，只消费 production mastery 的合法输出并聚合。

## 4. Module aggregation rule

- `module_aggregation_rule.unit`: MODULE
- `module_aggregation_rule.input`: 该 Module 的全部 canonical Lesson mastery 决策，每个 Lesson 恰好一个
- `module_aggregation_rule.ordered_conditions[0].condition`: any_lesson_decision_is
- `module_aggregation_rule.ordered_conditions[0].value`: BLOCKED
- `module_aggregation_rule.ordered_conditions[0].module_status`: BLOCKED
- `module_aggregation_rule.ordered_conditions[1].condition`: any_lesson_decision_is
- `module_aggregation_rule.ordered_conditions[1].value`: REMEDIATION
- `module_aggregation_rule.ordered_conditions[1].module_status`: REMEDIATION_REQUIRED
- `module_aggregation_rule.ordered_conditions[2].condition`: any_lesson_decision_is
- `module_aggregation_rule.ordered_conditions[2].value`: RETRY
- `module_aggregation_rule.ordered_conditions[2].module_status`: RETRY_REQUIRED
- `module_aggregation_rule.ordered_conditions[3].condition`: every_lesson_decision_is
- `module_aggregation_rule.ordered_conditions[3].value`: PASS
- `module_aggregation_rule.ordered_conditions[3].module_status`: COMPLETE
- `module_aggregation_rule.first_match_wins`: true
- `module_aggregation_rule.illegal_module_input`: MISSING_LESSON_RESULT | DUPLICATE_LESSON_RESULT | EXTRA_LESSON_RESULT | UNKNOWN_MASTERY_UNIT | UNKNOWN_DECISION
- `module_aggregation_rule.illegal_module_input_rule`: 缺失、重复、越界或未知决策都属于非法 evaluation snapshot，必须报错，不得默认为 incomplete。

## 5. Course completion rule

- `course_completion_rule.unit`: COURSE
- `course_completion_rule.complete_iff`: every_canonical_lesson_mastery_unit_is_PASS | every_module_status_is_COMPLETE | all_hard_lesson_transitions_satisfied | production_mastery_prerequisite_semantics_consistent | no_non_order_relation_promoted_into_a_course_gate
- `course_completion_rule.otherwise`: 按 precedence 取严重度最高的状态
- `course_completion_rule.precedence`: BLOCKED > REMEDIATION_REQUIRED > RETRY_REQUIRED
- `course_completion_rule.complete_implies_empty_routing`: true
- `course_completion_rule.no_numeric_grade`: true
- `course_completion_rule.no_hidden_graduation_logic`: 不得引入「80% 即通过」「完成 X 个模块即可结业」等未由冻结 upstream 支持的规则。

## 6. Hard sequence rule

- `hard_sequence_rule.source`: production mastery map hard_prerequisite_units + authoritative graph set order edges
- `hard_sequence_rule.legal_order_relations`: PREREQUISITE_OF | PROCEDURE_PRECEDES
- `hard_sequence_rule.counts_are_recomputed`: true
- `hard_sequence_rule.reported`: hard_transition_count | supporting_hard_edge_count | hard_transitions
- `hard_sequence_rule.later_unit_declared_pass_while_hard_prerequisite_not_pass`: INCONSISTENT_EVALUATION_SNAPSHOT
- `hard_sequence_rule.inconsistent_snapshot_rule`: 不得静默改写为 BLOCKED；必须作为非法 snapshot 报错，validator FAIL。BLOCKED 只能由 production mastery 决策本身真实输出。

## 7. Routing rule

- `routing_rule.retry_targets`: 只包含当前 decision = RETRY 的 Lesson / mastery unit / assessment evidence 需求；不得重新打开已 PASS 的无关 Lesson。
- `routing_rule.remediation_targets`: 包含当前 decision = REMEDIATION 的 Lesson / mastery unit，以及 production mastery 真实指出的 unmet learner outcome refs；不得泛化为重学整个 Course。
- `routing_rule.blocked_targets`: 包含当前 decision = BLOCKED 的 Lesson / mastery unit，以及未满足的合法 hard prerequisite mastery unit。
- `routing_rule.blocked_by_mastery_units`: 未满足的合法 hard prerequisite mastery unit，逐条给出 blocked lesson 归属。
- `routing_rule.non_order_relation_rule`: 任何 non-order relation 都不得成为 module gate、course gate、track gate 或 completion prerequisite。
- `routing_rule.lossless`: overall_status = 最高严重度，但 retry / remediation / blocked 三组 routing target 全部保留真实集合。
- `routing_rule.complete_rule`: course_status = COMPLETE 时四个 routing 集合必须全部为空。

## 8. Track applicability

- `track_completion_applicability.value`: NOT_APPLICABLE
- `track_completion_applicability.basis`: CANONICAL_TRACK_ENTITY_COUNT = 0：当前 canonical project 中不存在真实 Track entity。
- `track_completion_applicability.rule`: 不得为满足 track completion 字样发明 synthetic Track 层级；validator 必须要求无 synthetic track result。

## 9. Invalid snapshot semantics

- `invalid_snapshot_semantics.codes`: MISSING_LESSON_RESULT | DUPLICATE_LESSON_RESULT | EXTRA_LESSON_RESULT | UNKNOWN_MASTERY_UNIT | UNKNOWN_DECISION | INCONSISTENT_EVALUATION_SNAPSHOT | BLOCKED_PREREQUISITE_INCONSISTENT | NON_ORDER_COURSE_COMPLETION_GATE | INVALID_ROUTING_TARGET | STUDENT_STATE_FIELD
- `invalid_snapshot_semantics.rule`: 非法 snapshot 必须 exit != 0 并命中对应 code，不得被解释为 incomplete，也不得被降级为 BLOCKED。

## 10. Derived metric policy

- `derived_metric_policy.rule`: 任何保留的 *_count / distribution / summary 必须由 validator 现场从源字段重算并比对，mismatch = FAIL。
- `derived_metric_policy.contract_stores_no_upstream_bulk_data`: true

## 11. No student state boundary

- `no_student_state_boundary.ephemeral_snapshot_only`: true
- `no_student_state_boundary.forbidden_fields`: student_id | user_id | learner_id | learner_profile | history | attempt_history | timestamp | progress | saved_progress | database_key | session_id
- `no_student_state_boundary.rule`: evaluation snapshot 只能是一次输入；不得包含学生身份、持久历史、attempt 序列或数据库键。

## 12. No numeric grade boundary

- `no_numeric_grade_boundary.forbidden_fields`: percentage | gpa | final_score | letter_grade | weighted_score
- `no_numeric_grade_boundary.rule`: 本 V1 课程完成合同基于 mastery completeness 与 hard-sequence integrity，不创建数字成绩。

## 13. Governance mandate

- `governance_mandate.interfaces_between`: LESSON-GRADE | STAGE-GRADE
- `governance_mandate.not_responsible_for`: content generation | content storage | learner state | numeric grading
- `governance_mandate.note`: 本课程级评价合同位于 Lesson 级 mastery 决策之上、Stage 级治理之下；它只做确定性聚合、路由与一致性校验，不对内容生成、内容存储、学习者状态或数字评分负责。

## 14. Input references

- `input_refs.course_manifest`: academy-data/jimeng/course/jimeng-creator-academy-v1/course-manifest.json
- `input_refs.mastery_map`: academy-data/jimeng/assessment/mastery-map.json
- `input_refs.assessment_mapping`: academy-data/jimeng/assessment/full-assessment-mapping.json
- `input_refs.graph_set`: academy-data/jimeng/graph/seedance-pilot-graph-r2.json | academy-data/jimeng/graph/policy-pilot-graph-r1.json | academy-data/jimeng/graph/curriculum-readiness-core-graph-r2.json
- `input_refs.full_assessment_set`: academy-data/jimeng/assessment/full-assessments/full-assessment-set.json
- `input_refs.coverage_manifest`: academy-data/jimeng/assessment/full-assessments/assessment-coverage-manifest.json
- `input_refs.engine`: .agents/skills/ai-academy/scripts/evaluate_course_completion.py
- `input_refs.validator`: .agents/skills/ai-academy/scripts/validate_course_evaluation.py
- `input_refs.schema`: .agents/skills/ai-academy/assets/course-evaluation.schema.json
- `input_refs.policy`: .agents/skills/ai-academy/references/course-evaluation-policy.md

## 15. Recomputed counts policy

These numbers are the validator's live recomputation targets, not copied upstream data.

- `recomputed_counts_policy.module_count`: 8
- `recomputed_counts_policy.canonical_lesson_count`: 24
- `recomputed_counts_policy.canonical_mastery_unit_count`: 24
- `recomputed_counts_policy.mastery_hard_transition_count`: 4
- `recomputed_counts_policy.mastery_supporting_hard_edge_count`: 5
- `recomputed_counts_policy.canonical_track_entity_count`: 0
- `recomputed_counts_policy.note`: 这些数字是 validator 现场重算的比对对象，不是合同复制的大块 upstream 数据；合同不保存任何 Lesson / Assessment / outcome 清单。
