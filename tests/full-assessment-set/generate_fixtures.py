"""Build the tests/full-assessment-set/ critical fixtures (handoff sections 16-18).

Every fixture starts from repository truth (23 canonical assessment pairs, the frozen mapping,
the frozen mastery map, the frozen course manifest) and applies exactly one mutation.  The
declarative SPECS table below is the single source of truth for both the fixture file inventory
and the expected outcome; run_fixtures.py imports build_index() so no expectation is ever
hand-maintained twice.

Usage:
  python tests/full-assessment-set/generate_fixtures.py [--emit]
  python tests/full-assessment-set/generate_fixtures.py --audit

--emit prints every fixture-local file (mutation descriptor, mutated pilot source, mutated
assessment pair, fixture-local coverage manifest, shared _baseline mirror, source-fingerprint
manifest, index) as labelled blocks so the bytes can be persisted verbatim.  verify_fixtures.py
then proves the persisted bytes are exactly these bytes.

--audit prints, per canonical assessment file, whether this file toolchain can reproduce the
canonical bytes exactly.  Nothing in the fixture set is derived from that audit at run time: it
is the evidence record for the declared source-mode split below.

Hybrid declarative baseline (Gate 4.7A-CONT7-R3A-CONT2-R3)
---------------------------------------------------------
The shared fixture-local package is `_baseline/`, and it is a HYBRID_DECLARATIVE_BASELINE: every
canonical assessment member is declared with exactly one of two legal source modes, and there is
no implicit third.

  * `LOCAL_BYTE_EXACT_COPY` -- the member's canonical pair is mirrored verbatim into
    `_baseline/assessments/`, and the fixture manifests declare that mirror.  The mirror is
    required to be byte-identical to the canonical file (same SHA-256, same byte size), so the
    baseline can never become a second, drifting machine truth.

  * `CANONICAL_DIRECT_DECLARATION` -- no copy is produced.  The fixture manifests explicitly
    declare the exact frozen canonical source path for that member.  Every declared canonical
    path must exist, must be the approved canonical member path, and its SHA-256 must equal the
    frozen canonical fingerprint.

The split is decided programmatically, never hand-listed.  A canonical member pair is mirrored
only when both siblings' bytes are reproducible exactly by this file toolchain; the DSH write
tool normalises line endings to LF, so a canonical sibling that carries CR bytes cannot be
mirrored byte-exactly.  Manufacturing an LF-normalised *approximate* copy for such a member is
forbidden, so it is declared straight from canonical instead.

A member is never half-mirrored: the validator derives the Markdown sibling from the declared
JSON path, so a member whose Markdown sibling is not reproducible is declared from canonical as
a whole.

Declared assessment references (Gate 4.7A-CONT7-R3A-CONT2-R2/R3)
----------------------------------------------------------------
Every fixture manifest declares each member's `assessment_files` path explicitly, and that
declared path map is the same 23-entry model for all eleven fixtures.  The validator treats a
declared path as the authoritative reference for existence
(DECLARED_REFERENCE_IS_AUTHORITATIVE_FOR_EXISTENCE), so a declared path that does not resolve is
a real ASSESSMENT_FILE_EXISTENCE defect -- never a fallback to discovered[assessment_id], to a
discovered overlay, or to the canonical path.  An explicitly declared path that does not exist
must still fail: explicit declaration is not a licence for hidden fallback.

Nothing in this module reads a modification time, and no expectation is ever weakened.
"""

import copy
import hashlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSESSMENT_DIR = ROOT / "academy-data/jimeng/assessment"
CANONICAL_DIR = ASSESSMENT_DIR / "full-assessments/assessments"
COURSE_DIR = ROOT / "academy-data/jimeng/course/jimeng-creator-academy-v1"
PILOT_DIR = ASSESSMENT_DIR / "pilot-assessments"
FIXTURE_ROOT = ROOT / "tests/full-assessment-set"
BASELINE_DIR = FIXTURE_ROOT / "_baseline"
BASELINE_ASSESSMENT_DIR = BASELINE_DIR / "assessments"
BASELINE_PILOT_DIR = BASELINE_DIR / "pilot-sources"
BASELINE_FINGERPRINT = BASELINE_DIR / "baseline-fingerprint.json"
CANONICAL_COVERAGE_REL = ("academy-data/jimeng/assessment/full-assessments/"
                          "assessment-coverage-manifest.json")
CANONICAL_SET_REL = "academy-data/jimeng/assessment/full-assessments/full-assessment-set.json"
# The authoritative graph set: the same three files validate_mastery.py is pointed at directly.
# run_fixtures.py passes each of them as its own --graphs token (never a comma-joined token).
GRAPHS = [
    "academy-data/jimeng/graph/seedance-pilot-graph-r2.json",
    "academy-data/jimeng/graph/policy-pilot-graph-r1.json",
    "academy-data/jimeng/graph/curriculum-readiness-core-graph-r2.json",
]
VALIDATOR = ".agents/skills/ai-academy/scripts/validate_full_assessment_set.py"

# The two legal member source modes of the hybrid declarative baseline.  There is no third: a
# member is either mirrored byte-exactly or declared straight from its frozen canonical source.
LOCAL_BYTE_EXACT_COPY = "LOCAL_BYTE_EXACT_COPY"
CANONICAL_DIRECT_DECLARATION = "CANONICAL_DIRECT_DECLARATION"
LEGAL_SOURCE_MODES = (LOCAL_BYTE_EXACT_COPY, CANONICAL_DIRECT_DECLARATION)
SOURCE_MODE_SPLIT_RULE = ("a canonical member pair is LOCAL_BYTE_EXACT_COPY only when both of its "
                          "siblings' bytes are reproducible exactly by the current write channel; "
                          "every other member is CANONICAL_DIRECT_DECLARATION")

PILOT_DRIFT_SCOPE = ("夹具缺陷：pilot 源文件的 frozen scope 与已晋升 canonical 不同，"
                     "用于触发 pilot promotion 语义漂移。")
JSON_MD_MISMATCH_PURPOSE = ("夹具缺陷：该 purpose 文本只在 JSON 中存在，Markdown 仍保留原文，"
                            "用于触发 JSON/Markdown 文本保真度不一致。")
PILOT_SOURCE_IDS = ["JCA-A-001", "JCA-A-002", "JCA-A-003", "JCA-A-004"]
OUTCOME_DRIFT_ASSESSMENT = "JCA-A-004"
OUTCOME_DRIFT_OUTCOME = "JCA-M08-L02#1"

# The four remaining required full-set fixtures (handoff sections 7-10).  Each is derived from
# canonical truth and carries exactly one intended defect; the first three defects are provably
# emitted as the fixture's only diagnostic code (measured against the validator, never assumed).
UNKNOWN_ASSESSMENT_ID = "JCA-A-999"
UNKNOWN_ASSESSMENT_MUTATION = (
    "the full set's own assessment entry list references an assessment id that exists in no "
    "canonical membership: a phantom manifest entry for an id with no canonical assessment file")
# The declared-reference mutation target is read out of the live canonical manifest and the live
# source-mode split, never hardcoded here; see missing_file_target_id().
MISSING_ASSESSMENT_FILE_ABSENT_NAME = "{id}.absent.json"
MISSING_ASSESSMENT_FILE_MUTATION = (
    "one member's declared assessment file path is redirected to a fixture-local path that holds "
    "no file at all, so the declared reference for that member cannot supply its assessment while "
    "every other declared member path still resolves")
DUPLICATE_ASSESSMENT_MUTATION = (
    "the coverage manifest repeats one assessment entry, so the same assessment id is declared "
    "twice")
BAD_COVERAGE_LINK_MUTATION = (
    "the coverage manifest mislabels the link_source of one requirement carrier, so an existing "
    "requirement link is declared with the wrong provenance")
COVERAGE_LINK_CARRIER = "JCA-AR-003"
COVERAGE_LINK_EXPECTED_SOURCE = "COMPOSITE_CONTAINS_LESSON_SET"
COVERAGE_LINK_WRONG_SOURCE = "EXACT_LESSON_SET"

ASSESSMENT_IDS_PLACEHOLDER = "__ASSESSMENT_IDS__"
ABSENT_ID_PLACEHOLDER = "__ABSENT_ID__"
ABSENT_PATH_PLACEHOLDER = "__ABSENT_PATH__"


def fixture_coverage_rel(name):
    """The fixture-local coverage manifest path for a fixture that mutates coverage truth."""
    return f"tests/full-assessment-set/{name}/assessment-coverage-manifest.json"


def raw_json(path):
    """Read a repository JSON document (usable while the SPECS table is still being built)."""
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def raw_bytes(path):
    with io.open(path, "rb") as handle:
        return handle.read()


def line_endings_exact(path):
    """Whether this file toolchain can reproduce this file's bytes exactly.

    The DSH write tool normalises every line ending to LF, so a canonical file whose bytes contain
    a CR cannot be mirrored byte-exactly.  This is decided from the canonical bytes themselves, so
    it stays correct if canonical truth ever changes; it is never a hand-written list.
    """
    return b"\r" not in raw_bytes(path)


def member_mirror_exact(assessment_id):
    """Whether a member's whole pair can be mirrored into `_baseline/assessments/` byte-exactly.

    Both siblings are required: the validator derives the Markdown sibling from the JSON's own
    path, so a member is mirrored only when the pair is reproducible together.  A member with any
    non-reproducible sibling declares the canonical source pair instead, and is never half-copied.
    """
    return all(line_endings_exact(CANONICAL_DIR / f"{assessment_id}{suffix}")
               for suffix in (".json", ".md"))


def member_source_mode(assessment_id):
    """The declared source mode of one canonical assessment member (exactly one of two)."""
    return LOCAL_BYTE_EXACT_COPY if member_mirror_exact(assessment_id) \
        else CANONICAL_DIRECT_DECLARATION


def mirrored_assessment_ids():
    """The members whose canonical pair is mirrored byte-exactly into the shared baseline."""
    return [aid for aid in canonical_assessment_ids() if member_mirror_exact(aid)]


def canonical_direct_assessment_ids():
    """The members declared straight from their frozen canonical source, with no local copy."""
    return [aid for aid in canonical_assessment_ids() if not member_mirror_exact(aid)]


def canonical_set_entries():
    """Byte-faithful copies of the canonical full set's per-assessment entries."""
    return copy.deepcopy(raw_json(ROOT / CANONICAL_SET_REL)["assessments"])


def canonical_assessment_ids():
    """Every canonical assessment id, read from the canonical manifest's own file map."""
    return sorted(raw_json(ROOT / CANONICAL_SET_REL)["assessment_files"])


def missing_file_target_id():
    """The member the declared-reference mutation withdraws, chosen by a deterministic rule.

    Handoff section 9: prefer a `LOCAL_BYTE_EXACT_COPY` member so the literal physical-absence
    sub-case is cleanest, and never hard-bind one id.  The rule is "the first eligible
    LOCAL_BYTE_EXACT_COPY member in canonical assessment order", and the actual target is written
    into the mutation metadata by _materialize_spec().
    """
    return local_member_ids()[0]


def local_member_ids():
    """`LOCAL_BYTE_EXACT_COPY` members in canonical assessment order (deterministic)."""
    return [aid for aid in canonical_assessment_ids() if member_mirror_exact(aid)]


def fixture_dir(name):
    return FIXTURE_ROOT / name.replace("_", "-")


def rel_to(from_dir, to_path):
    """A POSIX relative path from one real directory to another real path.

    Depth is derived from the actual directories (`os.path.relpath`), never hand-guessed, so a
    fixture moved to another depth keeps a correct declared reference.
    """
    return Path(os.path.relpath(str(Path(to_path)), str(Path(from_dir)))).as_posix()


def shadowed_member_ids(spec):
    """Members this fixture intentionally shadows with its own persisted pair.

    Read from the SPECS entry's own file inventory rather than from the filesystem, so the
    declared path map is a function of declared truth and cannot drift with what happens to be
    persisted at generation time.  A shadowed member must be declared at the file the fixture
    actually persists: otherwise the declared reference and the discovered pair would be two
    different files, which is precisely the inconsistency the strict declared-reference rule
    exists to catch.
    """
    return {entry["assessment_id"] for entry in spec.get("assessments") or []}


def declared_assessment_path(spec, assessment_id):
    """The explicit declared path for one member of one fixture, derived from that member's mode.

    `LOCAL_BYTE_EXACT_COPY` members are declared at the shared byte-exact baseline mirror;
    `CANONICAL_DIRECT_DECLARATION` members are declared at the exact frozen canonical source path.
    A member the fixture itself shadows is declared at the fixture-local pair it persists.
    """
    name = spec["fixture"]
    from_dir = fixture_dir(name)
    if assessment_id in shadowed_member_ids(spec):
        return rel_to(from_dir, from_dir / "assessments" / f"{assessment_id}.json")
    if member_mirror_exact(assessment_id):
        target = BASELINE_ASSESSMENT_DIR / f"{assessment_id}.json"
    else:
        target = CANONICAL_DIR / f"{assessment_id}.json"
    return rel_to(from_dir, target)


def declared_assessment_paths(spec):
    """The complete `assessment_files` mapping one fixture declares, by id.

    A fixture that withdraws a canonical assessment declares the remaining members only: the
    withdrawn member is absent from the manifest's own membership, so declaring its file path
    would contradict the withdrawal the fixture is making.
    """
    withdrawn = withdrawn_assessment_ids(spec)
    return {aid: declared_assessment_path(spec, aid)
            for aid in canonical_assessment_ids() if aid not in withdrawn}


def withdrawn_assessment_ids(spec):
    """The canonical assessment ids this fixture withdraws from the manifest's membership."""
    withdrawn = (spec.get("mutation", {}).get("set_manifest") or {}).get("delete_assessment")
    return {withdrawn} if withdrawn else set()


def absent_assessment_path(name, assessment_id):
    """A declared path into `_baseline/assessments/` that holds no file at all.

    It is the sibling of a genuine baseline mirror, so the physical absence is a real absence
    inside the declared baseline package rather than a syntactically unusable path.
    """
    return rel_to(fixture_dir(name),
                  BASELINE_ASSESSMENT_DIR / MISSING_ASSESSMENT_FILE_ABSENT_NAME.format(
                      id=assessment_id))


def baseline_mirror_ids():
    """Canonical assessment members this toolchain mirrors into `_baseline/` byte-exactly."""
    return mirrored_assessment_ids()


def _member_fingerprint(assessment_id):
    """The source-fingerprint record of one canonical assessment member (hybrid declaration).

    The record is identical for every fixture, so the declared paths are recorded as the
    declaration symbol plus the per-file mirror/source path and the digest of whichever bytes are
    authoritative for that mode.  Each fixture's own relative declared path is derived from the
    same rule by `declared_assessment_path()`, and verify_fixtures.py proves every fixture agrees.
    """
    mode = member_source_mode(assessment_id)
    mirrored = mode == LOCAL_BYTE_EXACT_COPY
    files = []
    for suffix in (".json", ".md"):
        canonical = CANONICAL_DIR / f"{assessment_id}{suffix}"
        data = raw_bytes(canonical)
        record = {
            "suffix": suffix,
            "canonical_path": canonical.relative_to(ROOT).as_posix(),
            "canonical_sha256": hashlib.sha256(data).hexdigest(),
            "canonical_byte_size": len(data),
            "canonical_contains_cr": b"\r" in data,
            "declared_authority": "_baseline_mirror" if mirrored else "canonical_source",
            "declared_sha256": hashlib.sha256(data).hexdigest(),
            "declared_byte_size": len(data),
        }
        if mirrored:
            local = BASELINE_ASSESSMENT_DIR / f"{assessment_id}{suffix}"
            record["declared_path"] = local.relative_to(ROOT).as_posix()
            if local.is_file():
                local_bytes = raw_bytes(local)
                record["declared_sha256"] = hashlib.sha256(local_bytes).hexdigest()
                record["declared_byte_size"] = len(local_bytes)
                record["declared_byte_identical"] = local_bytes == data
            else:
                record["declared_sha256"] = None
                record["declared_byte_size"] = None
                record["declared_byte_identical"] = False
        else:
            record["declared_path"] = record["canonical_path"]
            record["declared_byte_identical"] = True
        files.append(record)
    return {
        "assessment_id": assessment_id,
        "source_mode": mode,
        "declared_json_path": files[0]["declared_path"],
        "declared_markdown_path": files[1]["declared_path"],
        "files": files,
    }


def baseline_fingerprint():
    """The source-fingerprint manifest of the hybrid declarative baseline.

    It is the provenance record every fixture's declared source model is checked against: per
    member the declared source mode and, per sibling, the canonical path/digest/size, the declared
    authority, the declared path and the digest and size of the bytes that path actually holds --
    so a `LOCAL_BYTE_EXACT_COPY` member carries its local copy's own digest and a
    `CANONICAL_DIRECT_DECLARATION` member is accounted for straight from its frozen source.
    """
    entries = [_member_fingerprint(aid) for aid in canonical_assessment_ids()]
    pilot_entries = []
    for aid in PILOT_SOURCE_IDS:
        canonical = PILOT_DIR / f"{aid}.json"
        data = raw_bytes(canonical)
        mirrored = line_endings_exact(canonical)
        record = {
            "assessment_id": aid,
            "source_mode": LOCAL_BYTE_EXACT_COPY if mirrored else CANONICAL_DIRECT_DECLARATION,
            "canonical_path": canonical.relative_to(ROOT).as_posix(),
            "canonical_sha256": hashlib.sha256(data).hexdigest(),
            "canonical_byte_size": len(data),
            "canonical_contains_cr": b"\r" in data,
            "declared_authority": "_baseline_mirror" if mirrored else "canonical_source",
            "declared_sha256": hashlib.sha256(data).hexdigest(),
            "declared_byte_size": len(data),
        }
        if mirrored:
            local = BASELINE_PILOT_DIR / f"{aid}.json"
            record["declared_path"] = local.relative_to(ROOT).as_posix()
            if local.is_file():
                local_bytes = raw_bytes(local)
                record["declared_sha256"] = hashlib.sha256(local_bytes).hexdigest()
                record["declared_byte_size"] = len(local_bytes)
                record["declared_byte_identical"] = local_bytes == data
            else:
                record["declared_sha256"] = None
                record["declared_byte_size"] = None
                record["declared_byte_identical"] = False
        else:
            record["declared_path"] = record["canonical_path"]
            record["declared_byte_identical"] = True
        pilot_entries.append(record)
    local_count = sum(1 for e in entries if e["source_mode"] == LOCAL_BYTE_EXACT_COPY)
    return {
        "artifact": BASELINE_FINGERPRINT.relative_to(ROOT).as_posix(),
        "baseline_root": BASELINE_DIR.relative_to(ROOT).as_posix(),
        "shared": True,
        "design": "HYBRID_DECLARATIVE_BASELINE",
        "purpose": ("one shared immutable fixture-local baseline every full-set fixture declares "
                    "its assessment references into"),
        "legal_source_modes": list(LEGAL_SOURCE_MODES),
        "source_mode_split_rule": SOURCE_MODE_SPLIT_RULE,
        "assessment_member_count": len(entries),
        "assessment_file_count": sum(len(e["files"]) for e in entries),
        "local_byte_exact_copy_count": local_count,
        "canonical_direct_declaration_count": len(entries) - local_count,
        "local_byte_exact_file_count": sum(len(e["files"]) for e in entries
                                           if e["source_mode"] == LOCAL_BYTE_EXACT_COPY),
        "canonical_direct_file_count": sum(len(e["files"]) for e in entries
                                           if e["source_mode"] == CANONICAL_DIRECT_DECLARATION),
        "canonical_source_dir": CANONICAL_DIR.relative_to(ROOT).as_posix(),
        "pilot_source_dir": PILOT_DIR.relative_to(ROOT).as_posix(),
        "declared_path_rule": ("each fixture declares every member's assessment_files path; a "
                               "LOCAL_BYTE_EXACT_COPY member is declared at the shared "
                               "_baseline/assessments/ mirror, a CANONICAL_DIRECT_DECLARATION "
                               "member at the exact frozen canonical source path, and a member "
                               "the fixture shadows at the fixture-local pair it persists"),
        "missing_file_target_rule": ("the first eligible LOCAL_BYTE_EXACT_COPY member in "
                                     "canonical assessment order"),
        "missing_file_target_id": missing_file_target_id(),
        "mirror_rule": ("a canonical member pair is mirrored verbatim into _baseline/assessments/ "
                        "only when both siblings' bytes are reproducible exactly by this file "
                        "toolchain; a pair that cannot be reproduced exactly is never mirrored, "
                        "and its fixtures declare the canonical source path itself"),
        "entries": entries,
        "pilot_sources": pilot_entries,
    }


def phantom_assessment_entry():
    """An extra set-manifest assessment entry whose id no canonical assessment declares.

    The entry is a byte-faithful copy of a real canonical entry with only the identity fields
    changed, so the fixture introduces an unknown reference and nothing else: it is deliberately
    absent from assessment_files and assessment_order, so it never perturbs canonical membership.
    """
    entry = copy.deepcopy(raw_json(ROOT / CANONICAL_SET_REL)["assessments"][0])
    entry["assessment_id"] = UNKNOWN_ASSESSMENT_ID
    entry["file"] = f"assessments/{UNKNOWN_ASSESSMENT_ID}.json"
    return entry


def coverage_operations(doc, operations):
    """Apply one fixture's declared coverage-manifest operations to canonical coverage truth.

    Operations are declarative, so the fixture-local coverage manifest is always a faithful copy
    of repository truth plus exactly the declared link-level change -- never a hand-maintained
    document.  Supported forms:

      {"set": {...}}                       nested key merge
      {"delete": [...]}                    key removal
      {"append": {"assessments": [...]}}   append entries to a list field
      {"duplicate": {"assessments": [{"index": 0}]}}
                                           repeat one existing list entry in place
      {"mutate": {"assessments": [{match, set}], "requirement_carriers": [...]}}
                                           patch entries matched by one identifying field
    """
    for key, value in (operations.get("set") or {}).items():
        if value is None:
            continue
        if isinstance(value, dict) and isinstance(doc.get(key), dict):
            coverage_operations(doc[key], {"set": value})
        else:
            doc[key] = value
    for key in operations.get("delete") or []:
        doc.pop(key, None)
    for key, entries in (operations.get("append") or {}).items():
        doc[key] = list(doc.get(key) or []) + copy.deepcopy(list(entries))
    for key, specs in (operations.get("duplicate") or {}).items():
        for spec in specs:
            entries = list(doc.get(key) or [])
            index = spec.get("index")
            if not isinstance(index, int) or not 0 <= index < len(entries):
                raise ValueError(f"coverage duplicate index {index!r} is out of range for {key}")
            entries.append(copy.deepcopy(entries[index]))
            doc[key] = entries
    for key, patches in (operations.get("mutate") or {}).items():
        for patch in patches:
            match = patch.get("match") or {}
            found = 0
            for entry in doc.get(key) or []:
                if all(entry.get(field) == value for field, value in match.items()):
                    entry.update(patch.get("set") or {})
                    found += 1
            if found != 1:
                raise ValueError(f"coverage mutate matched {found} entries for {key} {match!r}")
    return doc


def fixture_coverage_bytes(spec):
    """The fixture-local coverage manifest: canonical coverage truth plus the declared change."""
    doc = raw_json(ROOT / CANONICAL_COVERAGE_REL)
    return dumps(coverage_operations(doc, spec["coverage_ops"]))


SPECS = [
    {
        "fixture": "valid-full-set",
        "expected": "PASS",
        "expected_codes": [],
        "intended_defect": "no defect: canonical assessment truth replayed through the fixture "
                           "harness with every member's declared source path explicit",
        "set_manifest_mode": "fixture-local",
        "mutation": {"set_manifest": {"set": {}}, "coverage_manifest": CANONICAL_COVERAGE_REL},
        "inputs": {},
        "files": ["mutation.json"],
    },
    {
        "fixture": "invalid-derived-count",
        "expected": "FAIL",
        "expected_codes": ["DERIVED_METRIC_RECOMPUTATION"],
        "intended_defect": "full_set.metrics.requirement_count is one above the recomputed count",
        "mutation": {"set_manifest": {"set": {"metrics": {"requirement_count": 25}}},
                     "coverage_manifest": CANONICAL_COVERAGE_REL},
        "inputs": {},
        "files": ["mutation.json"],
    },
    {
        "fixture": "invalid-json-md-semantic-mismatch",
        "expected": "FAIL",
        "expected_codes": ["JSON_MD_CONSISTENCY"],
        "intended_defect": "the canonical markdown is frozen while one JSON scalar (purpose) "
                           "changed",
        "mutation": {"set_manifest": {"set": {"coverage_manifest": CANONICAL_COVERAGE_REL}},
                     "coverage_manifest": CANONICAL_COVERAGE_REL},
        "inputs": {},
        # The markdown keeps canonical text while this one JSON scalar changes, so the fixture
        # pair is byte-faithful to canonical apart from the declared defect field.
        "assessments": [{"assessment_id": "JCA-A-012",
                         "set": {"purpose": JSON_MD_MISMATCH_PURPOSE}}],
        "files": ["mutation.json", "assessments/JCA-A-012.json", "assessments/JCA-A-012.md"],
    },
    {
        "fixture": "invalid-nonorder-prerequisite",
        "expected": "FAIL",
        "expected_codes": ["NON_ORDER_PREREQUISITE_GUARD"],
        "intended_defect": "the set manifest declares an assessment prerequisite backed by no "
                           "order relation",
        "mutation": {"set_manifest": {"set": {
                         "assessment_prerequisites": {"JCA-A-012": ["JCA-A-011"]}}},
                     "coverage_manifest": CANONICAL_COVERAGE_REL},
        "inputs": {},
        "files": ["mutation.json"],
    },
    {
        "fixture": "invalid-pilot-semantic-drift",
        "expected": "FAIL",
        "expected_codes": ["PILOT_PROMOTION_FIDELITY"],
        "intended_defect": "one frozen pilot source field (scope) differs from the promoted "
                           "canonical beyond status",
        "mutation": {"set_manifest": {"set": {}}, "coverage_manifest": CANONICAL_COVERAGE_REL},
        # The isolated pilot directory must hold the whole Gate 4.5 pilot set so the validator
        # sees the four pilot sources the canonical full set declares.  Exactly one of them
        # carries the intended frozen-field drift.
        "inputs": {"--pilot-sources": "pilot-sources"},
        "pilot_sources": [{"assessment_id": "JCA-A-002", "set": {"scope": PILOT_DRIFT_SCOPE}}],
        "files": ["mutation.json"] + [f"pilot-sources/{aid}.json" for aid in PILOT_SOURCE_IDS],
    },
    {
        "fixture": "invalid-uncovered-requirement",
        "expected": "FAIL",
        "expected_codes": ["REQUIREMENT_COVERAGE_IDENTITY_SET"],
        "intended_defect": "JCA-A-023 is withdrawn, so mastery-required requirement JCA-AR-024 "
                           "has no carrier",
        "mutation": {"set_manifest": {"delete_assessment": "JCA-A-023",
                                      "set": {
                                          "coverage_manifest": CANONICAL_COVERAGE_REL,
                                          "coverage_summary": {
                                              "assessment_count": 22,
                                              "covered_lesson_count": 23,
                                              "canonical_lesson_count": 24,
                                              "covered_required_requirement_count": 23,
                                              "covered_learner_outcome_count": 57},
                                          "assessment_type_distribution": {
                                              "APPLY_RULE": 4,
                                              "CLASSIFY": 3,
                                              "EXPLAIN_BOUNDARY": 6,
                                              "IDENTIFY": 2,
                                              "INTEGRATED_TASK": 2,
                                              "PERFORM_PROCEDURE": 5},
                                          "alignment_type_distribution": {
                                              "COMPOSITE_FROM_MULTIPLE_COMPLETION_CHECKS": 1,
                                              "DIRECT": 21}}},
                     "coverage_manifest": CANONICAL_COVERAGE_REL},
        "inputs": {},
        # Withdrawing one assessment necessarily also removes its persisted pair and leaves the
        # frozen coverage manifest one revision behind.  Those cousins come from the same single
        # mutation and are declared, not suppressed.
        "companion_codes": ["CANONICAL_MEMBERSHIP_IDENTITY_SET", "COVERAGE_MANIFEST_FIDELITY",
                            "DERIVED_METRIC_RECOMPUTATION",
                            "LEARNER_OUTCOME_COVERAGE_IDENTITY_SET"],
        "files": ["mutation.json", "assessments/JCA-A-023.json", "assessments/JCA-A-023.md"],
    },
    {
        "fixture": "invalid-uncovered-outcome",
        "expected": "FAIL",
        "expected_codes": ["LEARNER_OUTCOME_COVERAGE_IDENTITY_SET"],
        "intended_defect": "the assessment no longer observes JCA-M08-L02#1, so that canonical "
                           "outcome has no coverage link",
        "mutation": {"coverage_manifest": CANONICAL_COVERAGE_REL,
                     "set_manifest": {"set": {
                         "coverage_manifest": CANONICAL_COVERAGE_REL}}},
        "inputs": {},
        # The fixture-local pair is the assessed evidence for this run: it observes one fewer
        # designated outcome than canonical truth.  The pair and its markdown are both derived
        # from canonical bytes by exactly this declared change, so the intended coverage defect
        # is the fixture's only intrinsic one.
        "assessments": [{"assessment_id": OUTCOME_DRIFT_ASSESSMENT,
                         "remove_target_outcomes": [OUTCOME_DRIFT_OUTCOME],
                         "remove_outcome_texts": ["输入与创作意图相符的图片提示词"]}],
        # Cousins of the same single mutation: the set coverage_summary still declares the
        # pre-mutation observation count, and the frozen pilot source for this assessment still
        # records the outcome this run stops observing.  Declared, not hidden.
        "companion_codes": ["DERIVED_METRIC_RECOMPUTATION", "PILOT_PROMOTION_FIDELITY"],
        "files": ["mutation.json", "assessments/JCA-A-004.json", "assessments/JCA-A-004.md"],
    },
    {
        "fixture": "invalid-unknown-assessment",
        "expected": "FAIL",
        "expected_codes": ["UNKNOWN_ASSESSMENT_REFERENCE"],
        "intended_defect": UNKNOWN_ASSESSMENT_MUTATION,
        "mutation": {"set_manifest": {"set": {
                         "assessments": canonical_set_entries() + [phantom_assessment_entry()],
                         "coverage_manifest": CANONICAL_COVERAGE_REL}},
                     "coverage_manifest": CANONICAL_COVERAGE_REL},
        "inputs": {},
        "files": ["mutation.json"],
    },
    {
        "fixture": "invalid-duplicate-assessment",
        "expected": "FAIL",
        "expected_codes": ["DUPLICATE_ASSESSMENT_ID"],
        "intended_defect": DUPLICATE_ASSESSMENT_MUTATION,
        "mutation": {"set_manifest": {"set": {}},
                     "coverage_manifest": fixture_coverage_rel("invalid-duplicate-assessment")},
        "coverage_ops": {"duplicate": {"assessments": [{"index": 0}]}},
        "inputs": {},
        "files": ["mutation.json", "assessment-coverage-manifest.json"],
    },
    {
        "fixture": "invalid-missing-assessment-file",
        "expected": "FAIL",
        # Primary intended code (handoff section 9): the declared reference for exactly one member
        # points at a physically absent fixture-local baseline path.
        "expected_codes": ["ASSESSMENT_FILE_EXISTENCE"],
        "intended_defect": MISSING_ASSESSMENT_FILE_MUTATION,
        # The target id and its declared path map are filled in programmatically below, from the
        # live source-mode split; nothing here hardcodes a member.
        "mutation": {"set_manifest": {"set": {
                         "assessment_files": ASSESSMENT_IDS_PLACEHOLDER,
                         "coverage_manifest": CANONICAL_COVERAGE_REL}},
                     "coverage_manifest": CANONICAL_COVERAGE_REL},
        "inputs": {},
        # Companion codes are measured against the validator and recorded here; see
        # REALIZED_COMPANION_CODES below.
        "files": ["mutation.json"],
    },
    {
        "fixture": "invalid-bad-coverage-link",
        "expected": "FAIL",
        "expected_codes": ["COVERAGE_MANIFEST_FIDELITY"],
        "intended_defect": BAD_COVERAGE_LINK_MUTATION,
        "mutation": {"set_manifest": {"set": {}},
                     "coverage_manifest": fixture_coverage_rel("invalid-bad-coverage-link")},
        "coverage_ops": {"mutate": {"requirement_carriers": [{
            "match": {"requirement_id": COVERAGE_LINK_CARRIER},
            "set": {"link_source": COVERAGE_LINK_WRONG_SOURCE}}]}},
        "inputs": {},
        "files": ["mutation.json", "assessment-coverage-manifest.json"],
    },
]

# Declared-references mutation: which member is withdrawn and what its declared path becomes are
# both derived from canonical truth, the live source-mode split and the real directory depth,
# never hardcoded.
MISSING_ASSESSMENT_FILE_ID = missing_file_target_id()
ABSENT_ASSESSMENT_FILE_PATH = absent_assessment_path("invalid-missing-assessment-file",
                                                     MISSING_ASSESSMENT_FILE_ID)

# Companion codes of the declared-references mutation, measured against the validator with the
# fixture's actual inputs (see run_fixtures.py output).  A companion code is listed only when the
# single declared-path mutation mechanically causes it; anything else makes the fixture a
# MISMATCH, which is exactly what the strict runner must be able to say.
REALIZED_COMPANION_CODES = ["CANONICAL_MEMBERSHIP_IDENTITY_SET"]


def _materialize_spec(spec):
    """Resolve every placeholder in one SPECS entry from canonical truth and the source-mode split.

    Every fixture-local manifest declares the complete `assessment_files` path map, so no member's
    existence check can fall back to canonical discovery: each declared path is authoritative for
    that member whether it lands in `_baseline/`, in the fixture's own shadowing pair, or -- for
    the one declared-reference fixture -- on a fixture-local path that holds no file.
    """
    spec = copy.deepcopy(spec)
    if spec.get("set_manifest_mode") == "canonical":
        return spec
    name = spec["fixture"]
    # A shadowed member keeps its persisted pair in the fixture inventory even when the SPECS
    # entry only names the mutated field, so the inventory is complete before the declared path
    # map is derived from it.
    for entry in spec.get("assessments") or []:
        for item in (f"assessments/{entry['assessment_id']}.json",
                     f"assessments/{entry['assessment_id']}.md"):
            if item not in spec["files"]:
                spec["files"].append(item)
    paths = declared_assessment_paths(spec)
    if name == "invalid-missing-assessment-file":
        paths[MISSING_ASSESSMENT_FILE_ID] = ABSENT_ASSESSMENT_FILE_PATH
        spec["absent_assessment_id"] = MISSING_ASSESSMENT_FILE_ID
        spec["absent_declared_path"] = ABSENT_ASSESSMENT_FILE_PATH
        spec["absent_source_mode"] = member_source_mode(MISSING_ASSESSMENT_FILE_ID)
        spec["target_declared_path_exists"] = False
        spec["non_target_declared_path_missing_count"] = 0
        spec["companion_codes"] = list(REALIZED_COMPANION_CODES)
    spec["declared_paths"] = paths
    spec["source_modes"] = {aid: member_source_mode(aid) for aid in canonical_assessment_ids()}
    withdrawn = sorted(withdrawn_assessment_ids(spec))
    if withdrawn:
        spec["withdrawn_assessment_ids"] = withdrawn
    operations = spec["mutation"].setdefault("set_manifest", {}).setdefault("set", {})
    operations["assessment_files"] = paths
    # The per-member entry records need no override here: the validator routes every entry from
    # assessment_files after the mutation is applied, so the manifest's entry list and its
    # assessment_files map cannot disagree about a member's declared reference.
    return spec


SPECS = [_materialize_spec(spec) for spec in SPECS]


def read_json(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def _compact_leaf_lines(value):
    """Render one record object as a single line, so the manifest stays compact and readable.

    The source-fingerprint manifest carries one record per canonical assessment file; rendering
    each record on one line keeps the artifact auditable line by line without inflating it with
    pure punctuation.  Every value is still produced by `json.dumps`, so no field is ever a
    hand-formatted string.
    """
    return json.dumps(value, ensure_ascii=False, separators=(", ", ": "))


def dumps_manifest(data):
    """`dumps`, but every list-of-objects becomes a list of one-line records.

    Used for the source-fingerprint manifest, whose per-file records are the smallest unit of
    review.  Scalars and nested lists of scalars keep the standard two-space layout.
    """
    lines = _manifest_lines(data, 0)
    return "\n".join(lines) + "\n"


def _manifest_lines(value, depth):
    pad = "  " * depth
    inner = "  " * (depth + 1)
    if isinstance(value, dict):
        if all(not isinstance(item, (dict, list)) for item in value.values()) and depth >= 2:
            return [pad + _compact_leaf_lines(value)]
        lines = [pad + "{"]
        keys = list(value)
        for position, key in enumerate(keys):
            comma = "," if position < len(keys) - 1 else ""
            rendered = _manifest_lines(value[key], depth + 1)
            first = inner + json.dumps(key, ensure_ascii=False) + ": "
            if isinstance(value[key], (dict, list)):
                lines.append(first + rendered[0].lstrip())
                lines.extend(rendered[1:])
            else:
                lines.append(first + rendered[0].strip())
            if comma:
                lines[-1] += ","
        lines.append(pad + "}")
        return lines
    if isinstance(value, list):
        if not value:
            return [pad + "[]"]
        if all(not isinstance(item, (dict, list)) for item in value):
            return [pad + json.dumps(value, ensure_ascii=False)]
        lines = [pad + "["]
        for position, item in enumerate(value):
            comma = "," if position < len(value) - 1 else ""
            rendered = _manifest_lines(item, depth + 1)
            lines.extend(rendered)
            lines[-1] += comma
        lines.append(pad + "]")
        return lines
    return [pad + json.dumps(value, ensure_ascii=False)]


def fixture_inputs(name, extra=None):
    inputs = {
        "--course": "academy-data/jimeng/course/jimeng-creator-academy-v1/course-manifest.json",
        "--graphs": GRAPHS,
        "--knowledge": "academy-data/jimeng/knowledge/pilot-knowledge-registry.json",
        "--mapping": "academy-data/jimeng/assessment/full-assessment-mapping.json",
        "--mastery-map": "academy-data/jimeng/assessment/mastery-map.json",
    }
    for key, value in (extra or {}).items():
        inputs[key] = (f"tests/full-assessment-set/{name}/{value}"
                       if not value.startswith("academy-data/") else value)
    return inputs


def build_index():
    """Recompute the fixture inventory and expectations from SPECS plus repository truth."""
    fixtures = []
    for spec in SPECS:
        name = spec["fixture"]
        mode = spec.get("set_manifest_mode", "fixture-local")
        fixtures.append({
            "fixture": name,
            "validator": VALIDATOR,
            "set_manifest": (CANONICAL_SET_REL if mode == "canonical"
                             else f"tests/full-assessment-set/{name}/full-assessment-set.json"),
            "set_manifest_mode": mode,
            "mutation_descriptor": f"tests/full-assessment-set/{name}/mutation.json",
            "mutation": spec["mutation"],
            "inputs": fixture_inputs(name, spec.get("inputs")),
            "expected": spec["expected"],
            "expected_exit": 0 if spec["expected"] == "PASS" else 1,
            "expected_codes": spec["expected_codes"],
            "companion_codes": spec.get("companion_codes") or [],
            "intended_defect": spec["intended_defect"],
            "files": [f"tests/full-assessment-set/{name}/{item}" for item in spec["files"]],
        })
    return {
        "set": "Gate 4.7A-CONT7-R3A critical full-set fixtures",
        "runner": "tests/full-assessment-set/run_fixtures.py",
        "validator": VALIDATOR,
        "baseline": {
            "root": BASELINE_DIR.relative_to(ROOT).as_posix(),
            "fingerprint": BASELINE_FINGERPRINT.relative_to(ROOT).as_posix(),
            "shared": True,
            "design": "HYBRID_DECLARATIVE_BASELINE",
            "legal_source_modes": list(LEGAL_SOURCE_MODES),
            "declared_reference_rule": ("each fixture declares every member's assessment_files "
                                        "path explicitly; a LOCAL_BYTE_EXACT_COPY member is "
                                        "declared into the byte-identical "
                                        "_baseline/assessments/ mirror, and a "
                                        "CANONICAL_DIRECT_DECLARATION member into the exact "
                                        "frozen canonical source path"),
        },
        "mutation_descriptor_contract": {
            "applied_by": f"{VALIDATOR} --apply-mutation <mutation.json>",
            "set_manifest": "nested set / delete operations merged into the canonical full set "
                            "manifest; delete_assessment withdraws one canonical assessment and "
                            "its assessment_files entry; assessment_files is replaced with the "
                            "fixture's full declared path map",
            "coverage_manifest": "repository path used when the fixture folder has no local "
                                 "assessment-coverage-manifest.json",
        },
        "fixtures": fixtures,
    }


def mutation_descriptor(spec):
    descriptor = {
        "fixture": spec["fixture"],
        "base_set_manifest": CANONICAL_SET_REL,
        "base_coverage_manifest": CANONICAL_COVERAGE_REL,
        "coverage_manifest": spec["mutation"]["coverage_manifest"],
        "set_manifest": spec["mutation"]["set_manifest"],
        "note": spec["intended_defect"],
    }
    if spec.get("declared_paths"):
        descriptor["declared_member_count"] = len(spec["declared_paths"])
        descriptor["declared_source_mode_counts"] = source_mode_counts(spec)
    if spec.get("withdrawn_assessment_ids"):
        descriptor["withdrawn_assessment_ids"] = list(spec["withdrawn_assessment_ids"])
    if spec.get("absent_declared_path"):
        descriptor["absent_assessment_id"] = spec["absent_assessment_id"]
        descriptor["absent_declared_path"] = spec["absent_declared_path"]
        descriptor["absent_member_source_mode"] = spec["absent_source_mode"]
        descriptor["target_declared_path_exists"] = spec["target_declared_path_exists"]
        descriptor["non_target_declared_path_missing_count"] = \
            spec["non_target_declared_path_missing_count"]
    # The coverage linkage mutations are materialized into the fixture-local coverage manifest by
    # the generator, so the descriptor records the exact declared link-level operations next to
    # the manifest they produced.
    if spec.get("coverage_ops"):
        descriptor["coverage_ops"] = spec["coverage_ops"]
    if spec.get("companion_codes"):
        descriptor["companion_codes"] = list(spec["companion_codes"])
    return descriptor


def source_mode_counts(spec):
    """How many declared members of one fixture use each legal source mode.

    A member the fixture shadows with its own persisted pair keeps its own legal mode for the
    baseline account but is declared at the fixture-local pair, so it is counted separately as
    FIXTURE_LOCAL_SHADOW and never counted as a baseline declaration.
    """
    counts = {mode: 0 for mode in LEGAL_SOURCE_MODES}
    counts["FIXTURE_LOCAL_SHADOW"] = 0
    counts["WITHDRAWN_FROM_MEMBERSHIP"] = 0
    for aid in canonical_assessment_ids():
        if aid in withdrawn_assessment_ids(spec):
            counts["WITHDRAWN_FROM_MEMBERSHIP"] += 1
            continue
        if aid in shadowed_member_ids(spec):
            counts["FIXTURE_LOCAL_SHADOW"] += 1
            continue
        counts[member_source_mode(aid)] += 1
    if not counts["WITHDRAWN_FROM_MEMBERSHIP"]:
        del counts["WITHDRAWN_FROM_MEMBERSHIP"]
    return counts


def index_record():
    """The persisted _index.json: a compact, auditable inventory of this round's fixtures.

    The mutation operations and inputs live in each fixture's own persisted mutation.json (which
    the verifier compares against the generator byte for byte), so the index stays a readable
    inventory and never becomes a second, partial copy of the descriptors.
    """
    full = build_index()
    return {
        "set": full["set"],
        "runner": full["runner"],
        "validator": full["validator"],
        "graphs": list(GRAPHS),
        "baseline": full["baseline"],
        "mutation_descriptor_contract": full["mutation_descriptor_contract"],
        "fixtures": [
            {
                "fixture": item["fixture"],
                "expected": item["expected"],
                "expected_exit": item["expected_exit"],
                "expected_codes": item["expected_codes"],
                "companion_codes": item["companion_codes"],
                "set_manifest_mode": item["set_manifest_mode"],
                "mutation_descriptor": item["mutation_descriptor"],
                "intended_defect": item["intended_defect"],
                "files": item["files"],
            }
            for item in full["fixtures"]
        ],
    }


def learner_outcomes(lesson_id):
    """The canonical learner outcomes of one course lesson, via the course manifest paths."""
    manifest = read_json(COURSE_DIR / "course-manifest.json")
    for entry in manifest["lesson_files"]:
        if entry["lesson_id"] == lesson_id:
            return read_json(COURSE_DIR / entry["json_path"]).get("learner_outcomes") or []
    return []


def assessment_bytes(entry):
    """A mutated canonical assessment pair: the canonical JSON plus only the declared change.

    `set` replaces declared scalar fields (the JSON/Markdown mismatch fixture).  Observed
    outcomes are dropped either by their canonical outcome reference (`<lesson_id>#<index>`,
    resolved against the course lesson's outcome list) or by their literal text (the
    uncovered-outcome fixture).

    The fixture-local pair is canonical truth with exactly this declared change; the mutation
    descriptor only redirects which coverage manifest the validator reads for the run.
    """
    data = read_json(CANONICAL_DIR / f"{entry['assessment_id']}.json")
    data.update(entry.get("set") or {})
    texts = set(entry.get("remove_outcome_texts") or [])
    for reference in entry.get("remove_target_outcomes") or []:
        lesson_id, _, index = reference.partition("#")
        if not index.isdigit():
            continue
        outcomes = learner_outcomes(lesson_id)
        if int(index) < len(outcomes):
            texts.add(outcomes[int(index)])
    keep = [text for text in data.get("target_outcomes") or [] if text not in texts]
    if len(keep) != len(data.get("target_outcomes") or []):
        data["target_outcomes"] = keep
    return dumps(data)


def markdown_bytes(entry, spec):
    """The markdown sibling derived from canonical text by the same declared change.

    The markdown must stay a lossless rendering of the fixture JSON, so the same declared
    removal is applied to it: an observed-outcome bullet is dropped for the uncovered-outcome
    fixture, and nothing else in the canonical evidence text changes.
    """
    text = io.open(CANONICAL_DIR / f"{Path(entry).stem}.md", encoding="utf-8").read()
    for change in spec.get("assessments") or []:
        if Path(entry).stem != change["assessment_id"]:
            continue
        for outcome in change.get("remove_outcome_texts") or []:
            lines = text.splitlines(keepends=True)
            text = "".join(line for line in lines if line.strip() != f"- {outcome}")
    return text


def pilot_source_bytes(spec, assessment_id):
    """An isolated pilot source: byte-faithful canonical pilot truth plus the declared drift."""
    data = read_json(PILOT_DIR / f"{assessment_id}.json")
    for mutation in spec.get("pilot_sources") or []:
        if mutation["assessment_id"] != assessment_id:
            continue
        if mutation.get("remove_field"):
            data.pop(mutation["remove_field"], None)
        else:
            data.update(mutation.get("set") or {})
    return dumps(data)


def baseline_files():
    """The byte-exact part of the shared baseline plus its source-fingerprint manifest.

    Only member pairs this toolchain reproduces exactly are mirrored (LOCAL_BYTE_EXACT_COPY);
    every other member stays at its canonical path and is declared from there
    (CANONICAL_DIRECT_DECLARATION), so the baseline never becomes a second, drifting machine
    truth.
    """
    files = [(BASELINE_FINGERPRINT.relative_to(ROOT).as_posix(),
              dumps_manifest(baseline_fingerprint()))]
    for aid in mirrored_assessment_ids():
        for suffix in (".json", ".md"):
            canonical = CANONICAL_DIR / f"{aid}{suffix}"
            path = (BASELINE_ASSESSMENT_DIR / f"{aid}{suffix}").relative_to(ROOT).as_posix()
            files.append((path, io.open(canonical, encoding="utf-8").read()))
    for aid in PILOT_SOURCE_IDS:
        canonical = PILOT_DIR / f"{aid}.json"
        if not line_endings_exact(canonical):
            continue
        path = (BASELINE_PILOT_DIR / f"{aid}.json").relative_to(ROOT).as_posix()
        files.append((path, io.open(canonical, encoding="utf-8").read()))
    return files


def fixture_files():
    """Every persisted fixture-local file, as (repo-relative path, verbatim text).

    The mutated full set manifest is materialized at run time by applying the fixture's mutation
    descriptor to the canonical manifest, so no copy of a frozen manifest is persisted.  Every
    other declared file -- mutation descriptor, mutated coverage manifest, mutated assessment
    pair, isolated pilot source set, shared baseline mirror, source-fingerprint manifest, index --
    is emitted here so the persisted bytes are exactly the generated bytes.
    """
    files = list(baseline_files())
    for spec in SPECS:
        name = spec["fixture"]
        assessed = {entry["assessment_id"]: entry for entry in spec.get("assessments") or []}
        files.append((f"tests/full-assessment-set/{name}/mutation.json",
                      dumps(mutation_descriptor(spec))))
        for entry in spec["files"]:
            if entry == "mutation.json":
                continue
            path = f"tests/full-assessment-set/{name}/{entry}"
            if entry == "assessment-coverage-manifest.json":
                files.append((path, fixture_coverage_bytes(spec)))
            elif entry.endswith(".md"):
                files.append((path, markdown_bytes(entry, spec)))
            elif entry.startswith("pilot-sources/"):
                files.append((path, pilot_source_bytes(spec, Path(entry).stem)))
            elif entry.endswith(".json"):
                stem = Path(entry).stem
                files.append((path, assessment_bytes(
                    assessed.get(stem) or {"assessment_id": stem})))
            else:
                raise ValueError(f"{name}: unsupported fixture file {entry}")
    files.append(("tests/full-assessment-set/_index.json", dumps(index_record())))
    return files


def audit():
    """Print the per-canonical-file mirror decision this toolchain actually supports."""
    ids = canonical_assessment_ids()
    print("CANONICAL_ASSESSMENT_FILE_COUNT: " + str(len(ids) * 2))
    exact = sum(1 for aid in ids for suffix in (".json", ".md")
                if line_endings_exact(CANONICAL_DIR / f"{aid}{suffix}"))
    print(f"BYTE_EXACT_MIRRORABLE_COUNT: {exact}")
    print(f"NOT_BYTE_EXACT_MIRRORABLE_COUNT: {len(ids) * 2 - exact}")
    print(f"LOCAL_BYTE_EXACT_COPY_COUNT: {len(mirrored_assessment_ids())}")
    print(f"CANONICAL_DIRECT_DECLARATION_COUNT: {len(canonical_direct_assessment_ids())}")
    print("LOCAL_BYTE_EXACT_COPY_MEMBERS: " + ",".join(mirrored_assessment_ids()))
    print("CANONICAL_DIRECT_DECLARATION_MEMBERS: " + ",".join(canonical_direct_assessment_ids()))
    print("MISSING_FILE_TARGET_ID: " + missing_file_target_id())
    for entry in baseline_fingerprint()["entries"]:
        for record in entry["files"]:
            if record["canonical_contains_cr"]:
                print("- CANONICAL_CONTAINS_CR: " + record["canonical_path"])
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--audit" in args:
        return audit()
    files = fixture_files()
    if "--emit" in args:
        for path, text in files:
            print(f"=== FILE {path} ===")
            sys.stdout.write(text if text.endswith("\n") else text + "\n")
    print(f"=== SUMMARY {len(SPECS)} fixtures, {len(files)} files ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
