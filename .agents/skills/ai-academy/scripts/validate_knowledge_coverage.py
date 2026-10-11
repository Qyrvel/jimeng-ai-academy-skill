"""Gate 2.2 offline knowledge coverage validation; Python standard library only."""

import re
import runpy
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE.parent / "assets/knowledge-coverage.schema.json"
SOURCE = runpy.run_path(str(HERE / "validate_source_registry.py"))
read_json = SOURCE["read_json"]

ROOT_FIELDS = ("track", "assessment_date", "domains", "item_accounting", "overall_recommendation")
DOMAIN_FIELDS = ("domain", "criticality", "source_ingestion_decision", "knowledge_item_ids", "coverage_status", "coverage_rationale", "known_gap", "next_action")
ACCOUNTING_FIELDS = ("registry_total", "mapped_item_ids", "unmapped_item_ids")
CRITICALITY = ("CORE", "SUPPORTING", "DYNAMIC", "OPTIONAL", "OUT_OF_SCOPE")
SOURCE_DECISIONS = ("ALLOW_INGESTION", "LIMITED_INGESTION", "DEFER", "NOT_APPLICABLE")
COVERAGE_STATUSES = ("COVERED", "PARTIAL", "MISSING", "DEFERRED", "NOT_APPLICABLE")
NEXT_ACTIONS = ("GRAPH_PILOT_ELIGIBLE", "EXPAND_KNOWLEDGE", "RETURN_TO_SOURCE", "DEFER", "NOT_APPLICABLE")
OVERALL = ("READY_FOR_GRAPH_PILOT", "NEEDS_TARGETED_INGESTION", "RETURN_TO_SOURCE_FIRST")
INGESTION_ALLOWED = ("ALLOW_INGESTION", "LIMITED_INGESTION")


def text(value):
    return isinstance(value, str) and bool(value.strip())


def valid_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def known_item_ids(knowledge):
    ids = []
    if isinstance(knowledge, dict) and isinstance(knowledge.get("items"), list):
        for item in knowledge["items"]:
            if isinstance(item, dict) and text(item.get("knowledge_id")):
                ids.append(item["knowledge_id"])
    return ids


def validate_rules(domain, label, errors):
    status = domain.get("coverage_status")
    source_decision = domain.get("source_ingestion_decision")
    next_action = domain.get("next_action")
    item_ids = domain.get("knowledge_item_ids") if isinstance(domain.get("knowledge_item_ids"), list) else None

    # RULE 1
    if status == "MISSING" and item_ids is not None and len(item_ids) != 0:
        errors.append(f"SEMANTIC: {label}: RULE 1: coverage_status MISSING requires an empty knowledge_item_ids array")
    # RULE 2
    if status in ("COVERED", "PARTIAL") and item_ids is not None and len(item_ids) == 0:
        errors.append(f"SEMANTIC: {label}: RULE 2: coverage_status {status} requires at least one knowledge_item_id")
    # RULE 3
    if status == "DEFERRED" and source_decision != "DEFER":
        errors.append(f"SEMANTIC: {label}: RULE 3: coverage_status DEFERRED requires source_ingestion_decision DEFER; found {source_decision!r}")
    # RULE 4
    if status == "NOT_APPLICABLE":
        if source_decision != "NOT_APPLICABLE":
            errors.append(f"SEMANTIC: {label}: RULE 4: coverage_status NOT_APPLICABLE requires source_ingestion_decision NOT_APPLICABLE; found {source_decision!r}")
        if next_action != "NOT_APPLICABLE":
            errors.append(f"SEMANTIC: {label}: RULE 4: coverage_status NOT_APPLICABLE requires next_action NOT_APPLICABLE; found {next_action!r}")
    # RULE 5
    if next_action == "GRAPH_PILOT_ELIGIBLE" and status not in ("COVERED", "PARTIAL"):
        errors.append(f"SEMANTIC: {label}: RULE 5: next_action GRAPH_PILOT_ELIGIBLE requires coverage_status COVERED or PARTIAL; found {status!r}")
    # RULE 6
    if source_decision == "DEFER" and next_action == "GRAPH_PILOT_ELIGIBLE":
        errors.append(f"SEMANTIC: {label}: RULE 6: source_ingestion_decision DEFER forbids next_action GRAPH_PILOT_ELIGIBLE")
    # RULE 7
    if source_decision in INGESTION_ALLOWED and status == "MISSING" and next_action == "RETURN_TO_SOURCE":
        if not text(domain.get("coverage_rationale")):
            errors.append(
                f"SEMANTIC: {label}: RULE 7: RETURN_TO_SOURCE despite {source_decision} and MISSING requires a non-blank coverage_rationale naming the new source blocker"
            )


def validate_structure(data, errors):
    if not isinstance(data, dict):
        return ["STRUCTURAL: root: must be an object"]
    for field in ROOT_FIELDS:
        if field not in data:
            errors.append(f"STRUCTURAL: root: missing required field {field}")
    for field in sorted(set(data) - set(ROOT_FIELDS)):
        errors.append(f"STRUCTURAL: root: unexpected field {field}")
    if not text(data.get("track")):
        errors.append("STRUCTURAL: root.track: must be a non-blank string")
    if not valid_date(data.get("assessment_date")):
        errors.append("STRUCTURAL: root.assessment_date: invalid YYYY-MM-DD date")
    if data.get("overall_recommendation") not in OVERALL:
        errors.append(f"STRUCTURAL: root.overall_recommendation: invalid value {data.get('overall_recommendation')!r}; allowed: {', '.join(OVERALL)}")
    return errors


def validate_domains(data, errors, registry_ids):
    domains = data.get("domains")
    if not isinstance(domains, list):
        errors.append("STRUCTURAL: root.domains: must be an array")
        return
    if not domains:
        errors.append("STRUCTURAL: root.domains: must not be empty")
    seen_names = set()
    for index, domain in enumerate(domains):
        label = f"domains[{index}]"
        if not isinstance(domain, dict):
            errors.append(f"STRUCTURAL: {label}: must be an object")
            continue
        for field in DOMAIN_FIELDS:
            if field not in domain:
                errors.append(f"STRUCTURAL: {label}: missing required field {field}")
        for field in sorted(set(domain) - set(DOMAIN_FIELDS)):
            errors.append(f"STRUCTURAL: {label}: unexpected field {field}")
        for field in ("domain", "coverage_rationale", "known_gap"):
            if field in domain and not text(domain[field]):
                errors.append(f"STRUCTURAL: {label}.{field}: must be a non-blank string")
        name = domain.get("domain")
        if text(name):
            if name in seen_names:
                errors.append(f"STRUCTURAL: {label}.domain: duplicate domain name {name!r}")
            seen_names.add(name)
        if domain.get("criticality") not in CRITICALITY:
            errors.append(f"STRUCTURAL: {label}.criticality: invalid value {domain.get('criticality')!r}; allowed: {', '.join(CRITICALITY)}")
        if domain.get("source_ingestion_decision") not in SOURCE_DECISIONS:
            errors.append(f"STRUCTURAL: {label}.source_ingestion_decision: invalid value {domain.get('source_ingestion_decision')!r}; allowed: {', '.join(SOURCE_DECISIONS)}")
        if domain.get("coverage_status") not in COVERAGE_STATUSES:
            errors.append(f"STRUCTURAL: {label}.coverage_status: invalid value {domain.get('coverage_status')!r}; allowed: {', '.join(COVERAGE_STATUSES)}")
        if domain.get("next_action") not in NEXT_ACTIONS:
            errors.append(f"STRUCTURAL: {label}.next_action: invalid value {domain.get('next_action')!r}; allowed: {', '.join(NEXT_ACTIONS)}")
        item_ids = domain.get("knowledge_item_ids")
        if not isinstance(item_ids, list):
            errors.append(f"STRUCTURAL: {label}.knowledge_item_ids: must be an array")
        else:
            seen_ids = set()
            for position, item_id in enumerate(item_ids):
                if not text(item_id):
                    errors.append(f"STRUCTURAL: {label}.knowledge_item_ids[{position}]: must be a non-blank string")
                    continue
                if item_id in seen_ids:
                    errors.append(f"STRUCTURAL: {label}.knowledge_item_ids: duplicate knowledge_id {item_id!r}")
                seen_ids.add(item_id)
                if item_id not in registry_ids:
                    errors.append(f"REFERENCE: {label}.knowledge_item_ids: knowledge_id {item_id!r} does not exist in Knowledge Registry")
        validate_rules(domain, label, errors)


def validate_accounting(data, errors, registry_ids):
    accounting = data.get("item_accounting")
    if not isinstance(accounting, dict):
        errors.append("STRUCTURAL: root.item_accounting: must be an object")
        return
    for field in ACCOUNTING_FIELDS:
        if field not in accounting:
            errors.append(f"STRUCTURAL: root.item_accounting: missing required field {field}")
    for field in sorted(set(accounting) - set(ACCOUNTING_FIELDS)):
        errors.append(f"STRUCTURAL: root.item_accounting: unexpected field {field}")
    total = accounting.get("registry_total")
    if not isinstance(total, int) or isinstance(total, bool):
        errors.append("STRUCTURAL: root.item_accounting.registry_total: must be an integer")
    elif total != len(registry_ids):
        errors.append(f"ACCOUNTING: root.item_accounting.registry_total: expected {len(registry_ids)}; found {total}")
    mapped = accounting.get("mapped_item_ids")
    unmapped = accounting.get("unmapped_item_ids")
    for field, value in (("mapped_item_ids", mapped), ("unmapped_item_ids", unmapped)):
        if not isinstance(value, list):
            errors.append(f"STRUCTURAL: root.item_accounting.{field}: must be an array")
    if not isinstance(mapped, list) or not isinstance(unmapped, list):
        return
    for field, value in (("mapped_item_ids", mapped), ("unmapped_item_ids", unmapped)):
        seen = set()
        for position, item_id in enumerate(value):
            if not text(item_id):
                errors.append(f"STRUCTURAL: root.item_accounting.{field}[{position}]: must be a non-blank string")
                continue
            if item_id in seen:
                errors.append(f"ACCOUNTING: root.item_accounting.{field}: duplicate knowledge_id {item_id!r}")
            seen.add(item_id)
            if item_id not in registry_ids:
                errors.append(f"REFERENCE: root.item_accounting.{field}: knowledge_id {item_id!r} does not exist in Knowledge Registry")
    mapped_set = {i for i in mapped if text(i)}
    unmapped_set = {i for i in unmapped if text(i)}
    for item_id in sorted(mapped_set & unmapped_set):
        errors.append(f"ACCOUNTING: knowledge_id {item_id!r} appears in both mapped_item_ids and unmapped_item_ids")
    expected = set(registry_ids)
    for item_id in sorted(expected - (mapped_set | unmapped_set)):
        errors.append(f"ACCOUNTING: knowledge_id {item_id!r} is missing from mapped and unmapped accounting")
    for item_id in sorted((mapped_set | unmapped_set) - expected):
        errors.append(f"ACCOUNTING: knowledge_id {item_id!r} is accounted for but does not exist in Knowledge Registry")


def validate_schema_shape(schema):
    errors = []
    if not isinstance(schema, dict):
        return ["STRUCTURAL: coverage schema is unreadable"]
    if tuple(schema.get("required", ())) != ROOT_FIELDS:
        errors.append("STRUCTURAL: coverage schema root required fields differ from the validator contract")
    definition = schema.get("$defs", {}).get("domain", {})
    if tuple(definition.get("required", ())) != DOMAIN_FIELDS:
        errors.append("STRUCTURAL: coverage schema domain required fields differ from the validator contract")
    for field, allowed in (("criticality", CRITICALITY), ("source_ingestion_decision", SOURCE_DECISIONS), ("coverage_status", COVERAGE_STATUSES), ("next_action", NEXT_ACTIONS)):
        if tuple(definition.get("properties", {}).get(field, {}).get("enum", ())) != allowed:
            errors.append(f"STRUCTURAL: coverage schema {field} enum differs from the validator contract")
    return errors


def validate_assessment(data, knowledge, schema):
    errors = validate_schema_shape(schema)
    if errors:
        return errors
    errors = validate_structure(data, errors)
    registry_ids = known_item_ids(knowledge)
    if not registry_ids:
        errors.append("STRUCTURAL: Knowledge Registry contains no items")
        return errors
    validate_domains(data, errors, registry_ids)
    validate_accounting(data, errors, registry_ids)
    return errors


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("FAIL")
        print("- Usage: python validate_knowledge_coverage.py <coverage-assessment.json> <knowledge-registry.json>")
        return 1
    try:
        data = read_json(args[0])
        knowledge = read_json(args[1])
        schema = read_json(SCHEMA_PATH)
        errors = validate_assessment(data, knowledge, schema)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"STRUCTURAL: unable to read or validate JSON: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
