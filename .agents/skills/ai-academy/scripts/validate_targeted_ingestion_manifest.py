"""Gate 2.3 offline targeted ingestion manifest validation; Python standard library only."""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = runpy.run_path(str(HERE / "validate_source_registry.py"))
read_json = SOURCE["read_json"]

ROOT_FIELDS = ("gate", "new_item_ids", "source_ids_used", "materialized_source_ids_used", "knowledge_type_counts")
TYPE_KEYS = ("CONCEPT", "CAPABILITY", "PROCEDURE", "CONSTRAINT", "POLICY", "VERSION_CONTEXT")


def text(value):
    return isinstance(value, str) and bool(value.strip())


def index_items(knowledge):
    by_id = {}
    if isinstance(knowledge, dict) and isinstance(knowledge.get("items"), list):
        for item in knowledge["items"]:
            if isinstance(item, dict) and text(item.get("knowledge_id")):
                by_id[item["knowledge_id"]] = item
    return by_id


def index_sources(sources):
    by_id = {}
    if isinstance(sources, dict) and isinstance(sources.get("sources"), list):
        for source in sources["sources"]:
            if isinstance(source, dict) and text(source.get("source_id")):
                by_id[source["source_id"]] = source
    return by_id


def index_materials(materials):
    by_id = {}
    if isinstance(materials, dict) and isinstance(materials.get("materials"), list):
        for entry in materials["materials"]:
            if isinstance(entry, dict) and text(entry.get("source_id")):
                by_id[entry["source_id"]] = entry
    return by_id


def id_list(value, label, errors):
    if not isinstance(value, list):
        errors.append(f"STRUCTURAL: {label}: must be an array")
        return None
    seen = set()
    for position, entry in enumerate(value):
        if not text(entry):
            errors.append(f"STRUCTURAL: {label}[{position}]: must be a non-blank string")
            continue
        if entry in seen:
            errors.append(f"STRUCTURAL: {label}: duplicate id {entry!r}")
        seen.add(entry)
    return [entry for entry in value if text(entry)]


def validate_manifest(data, knowledge, sources, materials):
    errors = []
    if not isinstance(data, dict):
        return ["STRUCTURAL: root: must be an object"]
    for field in ROOT_FIELDS:
        if field not in data:
            errors.append(f"STRUCTURAL: root: missing required field {field}")
    for field in sorted(set(data) - set(ROOT_FIELDS)):
        errors.append(f"STRUCTURAL: root: unexpected field {field}")
    if not text(data.get("gate")):
        errors.append("STRUCTURAL: root.gate: must be a non-blank string")

    items = index_items(knowledge)
    source_by_id = index_sources(sources)
    material_by_id = index_materials(materials)

    new_ids = id_list(data.get("new_item_ids"), "root.new_item_ids", errors)
    used_ids = id_list(data.get("source_ids_used"), "root.source_ids_used", errors)
    materialized_ids = id_list(data.get("materialized_source_ids_used"), "root.materialized_source_ids_used", errors)

    # 2. every new_item_id must exist in the Knowledge Registry
    if new_ids is not None:
        for item_id in new_ids:
            if item_id not in items:
                errors.append(f"REFERENCE: root.new_item_ids: knowledge_id {item_id!r} does not exist in Knowledge Registry")

    # 3./4./9. source_ids_used must exist and be accepted (candidate and other statuses rejected)
    if used_ids is not None:
        for source_id in used_ids:
            source = source_by_id.get(source_id)
            if source is None:
                errors.append(f"REFERENCE: root.source_ids_used: source_id {source_id!r} does not exist in Source Registry")
            elif source.get("status") != "accepted":
                errors.append(f"SOURCE: root.source_ids_used: source_id {source_id!r} has status {source.get('status')!r}; only accepted sources may be used")

    # 5. materialized_source_ids_used must be AVAILABLE
    if materialized_ids is not None:
        for source_id in materialized_ids:
            entry = material_by_id.get(source_id)
            if entry is None:
                errors.append(f"MATERIALIZATION: root.materialized_source_ids_used: source_id {source_id!r} has no Materialization Registry entry")
            elif entry.get("capture_status") != "AVAILABLE":
                errors.append(f"MATERIALIZATION: root.materialized_source_ids_used: source_id {source_id!r} has capture_status {entry.get('capture_status')!r}; required AVAILABLE")

    # 6./7. each new item's evidence must be inside source_ids_used and accepted + AVAILABLE when a material exists
    known_used = set(used_ids or [])
    known_materialized = set(materialized_ids or [])
    if new_ids is not None:
        for item_id in new_ids:
            item = items.get(item_id)
            if item is None:
                continue
            refs = item.get("evidence_refs")
            if not isinstance(refs, list) or not refs:
                errors.append(f"REFERENCE: {item_id}: evidence_refs must be a non-empty array")
                continue
            for ref in refs:
                source_id = ref.get("source_id") if isinstance(ref, dict) else None
                if not text(source_id):
                    errors.append(f"REFERENCE: {item_id}: evidence_ref has no usable source_id")
                    continue
                if source_id not in known_used:
                    errors.append(f"MANIFEST: {item_id}: source_id {source_id!r} is not listed in root.source_ids_used")
                source = source_by_id.get(source_id)
                if source is None:
                    errors.append(f"REFERENCE: {item_id}: source_id {source_id!r} does not exist in Source Registry")
                    continue
                if source.get("status") != "accepted":
                    errors.append(f"SOURCE: {item_id}: source_id {source_id!r} has status {source.get('status')!r}; required accepted")
                entry = material_by_id.get(source_id)
                if entry is not None and entry.get("capture_status") != "AVAILABLE":
                    errors.append(
                        f"MATERIALIZATION: {item_id}: source_id {source_id!r} has a Materialization entry with capture_status "
                        f"{entry.get('capture_status')!r}; required AVAILABLE"
                    )

    # 8. knowledge_type_counts must match the real counts of the new items
    counts = data.get("knowledge_type_counts")
    if not isinstance(counts, dict):
        errors.append("STRUCTURAL: root.knowledge_type_counts: must be an object")
    else:
        for field in sorted(set(counts) - set(TYPE_KEYS)):
            errors.append(f"STRUCTURAL: root.knowledge_type_counts: unexpected key {field}")
        for field in TYPE_KEYS:
            if field not in counts:
                errors.append(f"STRUCTURAL: root.knowledge_type_counts: missing key {field}")
        actual = {key: 0 for key in TYPE_KEYS}
        for item_id in (new_ids or []):
            item = items.get(item_id)
            if item is None:
                continue
            item_type = item.get("knowledge_type")
            if item_type in actual:
                actual[item_type] += 1
            else:
                errors.append(f"STRUCTURAL: {item_id}: knowledge_type {item_type!r} is not a known type")
        for field in TYPE_KEYS:
            declared = counts.get(field)
            if not isinstance(declared, int) or isinstance(declared, bool):
                errors.append(f"STRUCTURAL: root.knowledge_type_counts.{field}: must be an integer")
            elif declared != actual[field]:
                errors.append(f"COUNT: root.knowledge_type_counts.{field}: declared {declared}; actual {actual[field]}")
    return errors


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 4:
        print("FAIL")
        print("- Usage: python validate_targeted_ingestion_manifest.py <manifest.json> <knowledge-registry.json> <source-registry.json> <materialization-registry.json>")
        return 1
    try:
        data = read_json(args[0])
        knowledge = read_json(args[1])
        sources = read_json(args[2])
        materials = read_json(args[3])
        errors = validate_manifest(data, knowledge, sources, materials)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"STRUCTURAL: unable to read or validate JSON: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
