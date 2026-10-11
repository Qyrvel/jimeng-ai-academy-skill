"""Offline evidence materialization checks; Python standard library only."""

import re
import runpy
import sys
from datetime import date
from pathlib import Path

SOURCE = runpy.run_path(str(Path(__file__).with_name("validate_source_registry.py")))
read_json = SOURCE["read_json"]


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


def validate_registry(data, sources, registry_path):
    errors = SOURCE["validate_registry"](sources, read_json(SOURCE["SCHEMA_PATH"]))
    if errors:
        return [f"Source Registry: {error}" for error in errors]
    if not isinstance(data, dict) or set(data) != {"materials"} or not isinstance(data["materials"], list):
        return ["root: expected an object containing only a materials array"]
    lookup = {s["source_id"]: s for s in sources["sources"]}
    seen = set()
    required = {"source_id", "captured_at", "evidence_scope", "capture_status", "notes"}
    for index, item in enumerate(data["materials"]):
        label = f"materials[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: must be an object")
            continue
        for key in sorted(required - item.keys()):
            errors.append(f"{label}: missing {key}")
        for key in sorted(item.keys() - required - {"materialized_path"}):
            errors.append(f"{label}: unexpected {key}")
        sid = item.get("source_id")
        source = lookup.get(sid) if isinstance(sid, str) else None
        if source is None:
            errors.append(f"{label}: unknown source_id {sid!r}")
        if isinstance(sid, str):
            if sid in seen:
                errors.append(f"{label}: duplicate source_id {sid!r}")
            seen.add(sid)
        for key in ("source_id", "evidence_scope"):
            if not text(item.get(key)):
                errors.append(f"{label}.{key}: must be non-blank text")
        if not isinstance(item.get("notes"), str):
            errors.append(f"{label}.notes: must be a string")
        if not valid_date(item.get("captured_at")):
            errors.append(f"{label}.captured_at: invalid YYYY-MM-DD date")
        status = item.get("capture_status")
        if status not in ("AVAILABLE", "BLOCKED", "STALE"):
            errors.append(f"{label}: invalid capture_status {status!r}")
        if source and item.get("evidence_scope") != source["evidence_scope"]:
            errors.append(f"{label}: evidence_scope differs from Source Registry")
        path = item.get("materialized_path")
        if path is not None and not text(path):
            errors.append(f"{label}.materialized_path: must be non-blank text or null")
        if status not in ("AVAILABLE", "STALE"):
            continue
        if not text(path):
            errors.append(f"{label}: {status} requires materialized_path")
            continue
        target = Path(registry_path).resolve().parent / path
        if target.suffix.lower() != ".md":
            errors.append(f"{label}: material must be Markdown (.md)")
            continue
        try:
            body = target.read_text(encoding="utf-8-sig")
        except (OSError, ValueError) as exc:
            errors.append(f"{label}: material file unreadable: {exc}")
            continue
        metadata = {}
        for key in ("Source ID", "Original Location", "Captured At", "Evidence Scope", "Materialization Method"):
            values = re.findall(r"^" + re.escape(key) + r":[ \t]*(.*)$", body, re.MULTILINE)
            if len(values) != 1 or not values[0].strip():
                errors.append(f"{label}: Markdown requires one non-blank {key}")
            else:
                metadata[key] = values[0].strip()
        expected = {"Source ID": sid, "Captured At": item.get("captured_at"), "Evidence Scope": item.get("evidence_scope")}
        if source:
            expected["Original Location"] = source["location"]
        for key, value in expected.items():
            if key in metadata and metadata[key] != value:
                errors.append(f"{label}: Markdown {key} does not match registry")
        if not valid_date(metadata.get("Captured At")):
            errors.append(f"{label}: invalid Markdown Captured At date")
        if metadata.get("Materialization Method") not in ("DIRECT_READ", "MANUAL_CAPTURE"):
            errors.append(f"{label}: invalid Materialization Method")
        if not re.search(r"^# Evidence Material[ \t]*$", body, re.MULTILINE):
            errors.append(f"{label}: missing Evidence Material heading")
        for section in ("Evidence Extract", "Capture Notes"):
            match = re.search(r"^## " + section + r"[ \t]*\n(.*?)(?=^## |\Z)", body, re.MULTILINE | re.DOTALL)
            if not match or not match.group(1).strip():
                errors.append(f"{label}: missing or empty {section}")
    return errors


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("FAIL\n- Usage: python validate_materialization_registry.py <materials.json> <sources.json>")
        return 1
    try:
        errors = validate_registry(read_json(args[0]), read_json(args[1]), args[0])
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        errors = [f"Unable to read or validate registry: {exc}"]
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
