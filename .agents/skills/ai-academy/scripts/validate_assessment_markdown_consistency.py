"""Assessment JSON <-> Markdown textual fidelity check; Python standard library only.

Usage:
  python validate_assessment_markdown_consistency.py <assessment.json> [<assessment.json> ...]

The canonical Assessment Markdown must be a LOSSLESS rendering of its JSON: wording, omissions,
abbreviations and paraphrases are all failures. Only these normalisations are allowed (gate 4.7A-CONT3
section 6): CRLF/LF, leading/trailing whitespace, Markdown bullet markers, Markdown table separators,
and Unicode quote glyphs with identical inner text.

Checked fields (section 11): assessment_id, lesson_ids, assessment_type, purpose, target_outcomes,
knowledge_refs, scope, task, expected_evidence, scoring criteria (criterion_id, description,
evidence_source, weight, pass_condition), allowed_support, disallowed_support, feedback_boundary,
limitations.

This validator judges textual fidelity only. It never judges grounding, pedagogy or scoring quality.
"""

import io
import re
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
read_json = runpy.run_path(str(HERE / "validate_source_registry.py"))["read_json"]

QUOTE_MAP = {"\u201c": '"', "\u201d": '"', "\u201c": '"', "\u300c": '"', "\u300d": '"',
             "\u2018": "'", "\u2019": "'", "\uff02": '"'}
SCALAR_FIELDS = ("assessment_id", "assessment_type", "purpose", "scope", "task",
                 "expected_evidence", "feedback_boundary", "limitations", "partial_credit_policy")
LIST_FIELDS = ("lesson_ids", "knowledge_refs", "allowed_support", "disallowed_support")
OUTCOME_FIELD = "target_outcomes"


def normalize(text):
    for src, dst in QUOTE_MAP.items():
        text = text.replace(src, dst)
    return re.sub(r"\s+", "", text)


def check_pair(json_path, json_data, md_text):
    ok = []
    bad = []
    nmd = normalize(md_text)
    for field in SCALAR_FIELDS:
        value = json_data.get(field)
        if value is None:
            continue
        if normalize(str(value)) in nmd:
            ok.append(field)
        else:
            bad.append(field)
    for field in LIST_FIELDS + (OUTCOME_FIELD,):
        for value in json_data.get(field, []):
            if normalize(str(value)) in nmd:
                ok.append(f"{field}:{str(value)[:16]}")
            else:
                bad.append(f"{field}:{value}")
    lines = [normalize(l) for l in md_text.splitlines() if l.strip()]
    for crit in json_data.get("scoring_criteria", []):
        cid = crit["criterion_id"]
        row = [l for l in lines if cid in l]
        if not row:
            bad.append(f"{cid}:missing")
            continue
        row_text = row[0]
        for key in ("description", "evidence_source", "pass_condition"):
            if normalize(str(crit[key])) in row_text:
                ok.append(f"{cid}.{key}")
            else:
                bad.append(f"{cid}.{key}")
        if str(crit["weight"]) in row_text.replace("|", " ").split() or str(crit["weight"]) in row_text:
            ok.append(f"{cid}.weight")
        else:
            bad.append(f"{cid}.weight")
    return ok, bad


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("FAIL")
        print("- Usage: python validate_assessment_markdown_consistency.py <assessment.json> [...]")
        return 1
    errors = []
    for arg in args:
        json_path = Path(arg).resolve()
        md_path = json_path.with_suffix(".md")
        try:
            data = read_json(str(json_path))
            if not md_path.is_file():
                errors.append(f"CONSISTENCY: {json_path.name}: markdown not found at {md_path.name}")
                continue
            md_text = io.open(md_path, encoding="utf-8").read()
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"STRUCTURAL: {json_path.name}: unable to read: {exc}")
            continue
        ok, bad = check_pair(json_path, data, md_text)
        if bad:
            for item in bad:
                errors.append(
                    f"TEXTUAL_VARIANCE: {data.get('assessment_id', json_path.stem)}: "
                    f"{item} does not appear verbatim in the markdown"
                )
    print("FAIL" if errors else "PASS")
    for error in errors:
        print("- " + error)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
