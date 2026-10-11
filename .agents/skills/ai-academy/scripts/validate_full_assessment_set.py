"""Full canonical assessment set validation; Python standard library only.

Usage:
  python validate_full_assessment_set.py <full-assessment-set.json> [--json] [--verbose]

Inputs (handoff section 5) are all repository truth; nothing is read back from a human review
document and no modification time is ever used as evidence:

  the canonical assessment JSON/Markdown pairs (default: siblings of the manifest's
      assessments/ directory)
  the full-assessment-mapping.json requirement set
  the mastery-map.json mastery contract
  the course-manifest.json canonical lesson order and lesson set
  the knowledge registry
  the Gate 4.5 pilot source JSON set
  the knowledge graph JSON files

The validator recomputes the expected truth from those inputs and compares it with the two
machine manifests.  It never relaxes an existing semantic contract: assessment semantics come
from validate_assessment.py, JSON/Markdown textual fidelity from
validate_assessment_markdown_consistency.py, requirement semantics from
validate_assessment_mapping.py and mastery semantics from validate_mastery.py, all loaded with
runpy and called directly.

Checks (handoff sections 7, 8, 9, 12, 13, 14, 15):
  SET_IDENTITY                            set_id/course_id/status, order basis, coverage channel
  COURSE_IDENTITY                         course id agrees across manifest/mapping/mastery/course
  STATUS_LEGALITY                         every member assessment status = full_course
  CANONICAL_MEMBERSHIP_IDENTITY_SET        discovered == manifest == mapping-required assessment set
  DUPLICATE_ASSESSMENT_ID                 no duplicate id in files, manifest or assessment_order
  ASSESSMENT_FILE_EXISTENCE               each declared assessment file exists
  JSON_MD_PAIR_EXISTENCE                  each assessment JSON has its Markdown sibling
  INDIVIDUAL_ASSESSMENT_VALIDITY          validate_assessment.py semantics per assessment
  JSON_MD_CONSISTENCY                     markdown consistency semantics per assessment
  REQUIREMENT_COVERAGE_IDENTITY_SET       expected == actual requirement identity set
  LEARNER_OUTCOME_COVERAGE_IDENTITY_SET   expected == actual learner outcome identity set
  COVERAGE_MANIFEST_FIDELITY              coverage manifest equals the recomputed coverage
  DERIVED_METRIC_RECOMPUTATION            every declared derived metric is recomputed
  PILOT_PROMOTION_FIDELITY                pilot source vs promoted canonical, status only
  PILOT_SOURCE_REFERENCE_INTEGRITY        pilot count/status and no pilot path in machine truth
  NON_ORDER_PREREQUISITE_GUARD            no non-order relation became a prerequisite
  UNKNOWN_ASSESSMENT_REFERENCE            every referenced assessment exists
  HISTORICAL_OR_PILOT_ONLY_PATH_GUARD     no historical / pilot-only path in machine truth
  TEMP_SCRATCH_REVIEW_PROBE_RECOVERY_PATH_GUARD  no temp/scratch/review/probe/recovery path

The validator judges machine consistency only.  It never judges grounding, coverage design,
assessment type choice or scoring quality.
"""

import contextlib
import glob
import hashlib
import io
import json
import re
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ASSESSMENT_DIR = ROOT / "academy-data/jimeng/assessment"
COURSE_DIR = ROOT / "academy-data/jimeng/course/jimeng-creator-academy-v1"
KNOWLEDGE = ROOT / "academy-data/jimeng/knowledge/pilot-knowledge-registry.json"
PILOT_DIR = ASSESSMENT_DIR / "pilot-assessments"
DEFAULT_GRAPHS = (
    ROOT / "academy-data/jimeng/graph/seedance-pilot-graph-r2.json",
    ROOT / "academy-data/jimeng/graph/policy-pilot-graph-r1.json",
    ROOT / "academy-data/jimeng/graph/curriculum-readiness-core-graph-r2.json",
)

_assessment_module = runpy.run_path(str(HERE / "validate_assessment.py"))
_markdown_module = runpy.run_path(str(HERE / "validate_assessment_markdown_consistency.py"))
_mapping_module = runpy.run_path(str(HERE / "validate_assessment_mapping.py"))
_mastery_module = runpy.run_path(str(HERE / "validate_mastery.py"))
_registry_module = runpy.run_path(str(HERE / "validate_source_registry.py"))

read_json = _registry_module["read_json"]
structure = _assessment_module["structure"]
validate_assessment = _assessment_module["validate_assessment"]
markdown_check_pair = _markdown_module["check_pair"]
mapping_parse_ref = _mapping_module["parse_ref"]
mastery_decide = _mastery_module["decide"]
ASSESSMENT_SCHEMA = read_json(str(HERE.parent / "assets/assessment.schema.json"))
ASSESSMENT_TYPES = _mapping_module["ASSESSMENT_TYPES"]
ALIGNMENT_TYPES = _mapping_module["ALIGNMENT_TYPES"]
ORDER_RELATIONS = _mastery_module["ORDER_RELATIONS"]
NON_ORDER_RELATIONS = ("CONSTRAINS", "STEP_OF", "VERSION_CONTEXT_FOR", "VERSION_VARIANT_OF",
                       "SCOPE_PARALLEL_TO", "ENFORCEMENT_CONTEXT_FOR")
DECISION_ENUM = _mastery_module["DECISIONS"]
REASON_ENUM = _mastery_module["REASONS"]

SET_STATUS = "full_course"
ASSESSMENT_STATUS = "full_course"
SET_ID_PATTERN = re.compile(r"^jimeng-creator-academy-v1-full-assessment-set$")
ASSESSMENT_ID_PATTERN = re.compile(r"^JCA-A-[0-9]{3}$")
HISTORICAL_MARKERS = ("pilot-assessments", "pilot-assessment", "/pilot/", "\\pilot\\",
                      "historical", "/archive/", "\\archive\\", "superseded")
TEMP_MARKERS = ("/tmp/", "\\tmp\\", "temp", "scratch", "cache", "/reviews/", "\\reviews\\",
                "review", "probe", "recovery", "acl-recovery", ".bak", ".orig", ".tmp", ".txt")
# tests/full-assessment-set/ fixtures are explicitly licensed to hold fixture-local copies and
# fixture manifests (handoff section 4).  A machine-truth reference is allowed to point into that
# directory only; the exemption never applies to canonical production paths.
FIXTURE_ROOT = (ROOT / "tests/full-assessment-set").as_posix().lower() + "/"

EXPECTED_SET_KEYS = {
    "set_id", "course_id", "status", "lesson_order_basis", "assessment_order_rule",
    "assessment_order_tie_break", "assessment_order", "assessment_files", "coverage_manifest",
    "assessments", "coverage_summary", "metrics", "assessment_type_distribution",
    "alignment_type_distribution",
}
EXPECTED_COVERAGE_KEYS = {
    "map_id", "course_id", "status", "source_assessment_set", "outcome_reference_form",
    "alignment_type_enum", "requirement_carrier_rule", "assessments", "requirement_carriers",
    "assessment_count", "requirement_count", "requirement_link_count", "outcome_link_count",
    "alignment_type_distribution", "coverage_summary",
}


def resolve(value, base=None):
    path = Path(value)
    if not path.is_absolute():
        path = ((base or ROOT) / value)
    return path.resolve()


def relative(path):
    """Repo-relative POSIX path when possible, otherwise the absolute path."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def path_error(path_text, markers, fixture_exempt=False):
    """Markers found in a path string.

    When fixture_exempt is True a reference positioned inside tests/full-assessment-set/ is
    reduced to its basename first, so the licensed fixture copy does not itself read as a
    historical / temp / review / probe / recovery path.
    """
    text = str(path_text)
    if fixture_exempt:
        lowered = text.replace("\\", "/").lower()
        index = lowered.find(FIXTURE_ROOT)
        if index >= 0:
            text = text[index + len(FIXTURE_ROOT):]
    lowered = text.replace("\\", "/").lower()
    return sorted({m for m in markers if m.replace("\\", "/").lower() in lowered})


def sha256(path):
    digest = hashlib.sha256()
    with io.open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_lesson_ids(course_manifest):
    order = []
    for module in course_manifest["module_order"]:
        order.extend(course_manifest["lesson_order_by_module"][module])
    return order


def load_course(course_manifest_path):
    manifest = read_json(course_manifest_path)
    root = Path(course_manifest_path).parent
    lessons = {e["lesson_id"]: read_json(root / e["json_path"])
               for e in manifest["lesson_files"]}
    return manifest, lessons


def all_learner_outcomes(lessons):
    return {f"{lid}#{i}" for lid, lesson in lessons.items()
            for i in range(len(lesson["learner_outcomes"]))}


def derive_links(requirements, assessment_data):
    """Assign every requirement to exactly one assessment; see the manifest carrier rule.

    Returns (links, carrier, ambiguous).  links maps assessment_id -> list of
    {"requirement_id", "link_source"}; carrier maps requirement_id -> assessment_id.
    """
    links = {aid: [] for aid in assessment_data}
    carrier = {}
    ambiguous = []
    for req in sorted(requirements, key=lambda r: r["requirement_id"]):
        rid = req["requirement_id"]
        rlids = set(req.get("lesson_ids") or [])
        exact = sorted(aid for aid, data in assessment_data.items()
                       if set(data.get("lesson_ids") or []) == rlids)
        if len(exact) == 1:
            carrier[rid] = exact[0]
            links[exact[0]].append({"requirement_id": rid, "link_source": "EXACT_LESSON_SET"})
            continue
        superset = sorted(aid for aid, data in assessment_data.items()
                          if rlids and rlids <= set(data.get("lesson_ids") or []))
        if len(superset) == 1:
            carrier[rid] = superset[0]
            links[superset[0]].append({"requirement_id": rid,
                                       "link_source": "COMPOSITE_CONTAINS_LESSON_SET"})
            continue
        ambiguous.append(f"{rid}: {len(exact)} exact and {len(superset)} composite candidates")
    return links, carrier, ambiguous


def run_reused_main(module, argv):
    """Run an existing validator's main(argv) and capture its own PASS/FAIL output.

    The existing validators print a verdict and a diagnostic list.  This validator owns the
    single machine-readable verdict line, so the reused verdict is captured and only its
    diagnostics are re-emitted when the reused validator fails.
    """
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = module["main"](argv)
    lines = [line for line in buffer.getvalue().splitlines() if line.strip()]
    diagnostics = [line for line in lines if line.startswith("- ")]
    return code, diagnostics


def check_derived(where, value, expected, errors):
    """Compare a declared derived mapping with the recomputed truth, key by key."""
    if not isinstance(value, dict):
        errors.append(("DERIVED_METRIC_RECOMPUTATION",
                       f"{where}: expected a mapping of derived metrics"))
        return
    for key in sorted(set(expected) | set(value)):
        if key not in value:
            errors.append(("DERIVED_METRIC_RECOMPUTATION", f"{where}.{key}: missing declared metric"))
        elif key not in expected:
            errors.append(("DERIVED_METRIC_RECOMPUTATION",
                           f"{where}.{key}: declared derived metric is not recomputable here"))
        elif value[key] != expected[key]:
            errors.append(("DERIVED_METRIC_RECOMPUTATION",
                           f"{where}.{key}: expected {expected[key]!r}; found {value[key]!r}"))


MULTI_VALUE_FLAGS = ("--graphs",)
SET_ARGUMENTS = ("--mapping", "--mastery-map", "--course", "--knowledge", "--pilot-sources",
                 "--apply-mutation", "--coverage-override")


def split_argument_list(value):
    """A variadic argument list normalized to a flat, non-empty token list.

    Both the advertised variadic form (`--graphs g1 g2 g3`) and the historical single
    comma-joined form (`--graphs g1,g2,g3`) are accepted; a repeated flag accumulates its
    arguments instead of discarding earlier ones.
    """
    if value is None:
        return []
    items = value if isinstance(value, (list, tuple)) else [value]
    tokens = []
    for item in items:
        tokens.extend(part.strip() for part in str(item).split(",") if part.strip())
    return tokens


def parse_args(argv):
    """Positional full-assessment-set.json plus optional per-input overrides.

    The overrides exist so tests/full-assessment-set/ fixtures can substitute a mutated input
    without copying a whole frozen subtree.  Without them every input resolves to the
    authoritative repository file, so canonical validation always reads repository truth.

    `--graphs` is variadic, exactly as the usage string advertises: it consumes every following
    token up to the next recognized flag, so `--graphs g1 g2 g3` and `--graphs g1` are both
    legal.  A token that looks like a flag without being a recognized one is never swallowed as a
    path: it stops graph consumption and is reported as a deterministic usage error.
    """
    flags = {key: ([] if key in MULTI_VALUE_FLAGS else None)
             for key in MULTI_VALUE_FLAGS + SET_ARGUMENTS}
    positional = []
    unknown = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token in MULTI_VALUE_FLAGS:
            index += 1
            collected = 0
            while index < len(argv) and not argv[index].startswith("--"):
                flags[token].append(argv[index])
                collected += 1
                index += 1
            if not collected:
                raise ValueError(f"{token} requires at least one path argument")
            continue
        if token in SET_ARGUMENTS:
            if index + 1 >= len(argv):
                raise ValueError(f"{token} requires a path argument")
            value = argv[index + 1]
            if value.startswith("--"):
                raise ValueError(f"{token} requires a path argument; found {value!r}")
            flags[token] = value
            index += 2
            continue
        if token.startswith("--"):
            unknown.append(token)
        else:
            positional.append(token)
        index += 1
    if unknown:
        raise ValueError("unknown argument(s): " + ", ".join(sorted(set(unknown))))
    return positional, flags


def deep_set(target, operations):
    """Recursive key replacement plus declarations used by the test runner's --apply-mutation mode."""
    if not isinstance(target, dict) or not isinstance(operations, dict):
        return target
    withdrawn = operations.get("delete_assessment")
    if withdrawn:
        (target.get("assessment_files") or {}).pop(withdrawn, None)
        target["assessments"] = [entry for entry in target.get("assessments") or []
                                 if entry.get("assessment_id") != withdrawn]
    for key, value in (operations.get("set") or {}).items():
        if value is None:
            continue
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_set(target[key], {"set": value})
        else:
            target[key] = value
    for key in operations.get("delete") or []:
        target.pop(key, None)
    return target


def sync_entries(doc):
    """Keep per-assessment entries routed exactly like assessment_files."""
    files = doc.get("assessment_files")
    if not isinstance(files, dict):
        return doc
    for entry in doc.get("assessments") or []:
        if isinstance(entry, dict) and entry.get("assessment_id") in files:
            entry["file"] = files[entry["assessment_id"]]
    return doc


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    verbose = "--verbose" in args
    args = [a for a in args if a not in ("--verbose", "--json")]
    try:
        positional, overrides = parse_args(args)
    except ValueError as exc:
        print("FAIL")
        print(f"- USAGE: {exc}")
        return 1
    if len(positional) != 1:
        print("FAIL")
        print("- USAGE: python validate_full_assessment_set.py <full-assessment-set.json> [--verbose] "
              "[--mapping P] [--mastery-map P] [--course P] [--knowledge P] "
              "[--pilot-sources DIR] [--graphs P ...]")
        return 1

    errors = []
    findings = []
    fixture_notes = []

    def fail(code, message):
        errors.append((code, message))

    apply_mutation = overrides.get("--apply-mutation")
    set_path = resolve(positional[0])
    if apply_mutation:
        set_path.parent.mkdir(parents=True, exist_ok=True)
        mutation_path = resolve(apply_mutation)
        if not mutation_path.is_file():
            print("FAIL")
            print(f"- SET_IDENTITY: mutation descriptor not found at {apply_mutation}")
            return 1
        try:
            mutation = read_json(mutation_path)
            baseline = read_json(ASSESSMENT_DIR / "full-assessments/full-assessment-set.json")
            set_doc = deep_set(baseline, mutation.get("set_manifest") or {})
            sync_entries(set_doc)
            fixture_notes.append(f"reconstructed with {apply_mutation}")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print("FAIL")
            print(f"- SET_IDENTITY: unable to apply mutation {apply_mutation}: {exc}")
            return 1
    elif not set_path.is_file():
        print("FAIL")
        print(f"- SET_IDENTITY: full set manifest not found at {set_path}")
        return 1
    else:
        try:
            set_doc = read_json(set_path)
        except (OSError, ValueError) as exc:
            print("FAIL")
            print(f"- SET_IDENTITY: unable to read full set manifest: {exc}")
            return 1
    if not isinstance(set_doc, dict):
        print("FAIL")
        print("- SET_IDENTITY: full set manifest must be a JSON object")
        return 1

    course_manifest_path = resolve(overrides["--course"]) if overrides["--course"] \
        else COURSE_DIR / "course-manifest.json"
    mapping_path = resolve(overrides["--mapping"]) if overrides["--mapping"] \
        else ASSESSMENT_DIR / "full-assessment-mapping.json"
    mastery_path = resolve(overrides["--mastery-map"]) if overrides["--mastery-map"] \
        else ASSESSMENT_DIR / "mastery-map.json"
    knowledge_path = resolve(overrides["--knowledge"]) if overrides["--knowledge"] \
        else KNOWLEDGE
    if overrides["--pilot-sources"]:
        declared_pilot = resolve(overrides["--pilot-sources"])
        local_pilot = set_path.parent / declared_pilot.name
        if local_pilot.is_dir() and glob.glob(str(local_pilot / "*.json")):
            pilot_dir = local_pilot
        else:
            pilot_dir = declared_pilot
    else:
        pilot_dir = PILOT_DIR
    if overrides["--graphs"]:
        graph_paths = [resolve(item) for item in split_argument_list(overrides["--graphs"])]
    else:
        graph_paths = list(DEFAULT_GRAPHS)
    if not graph_paths:
        fail("SET_IDENTITY", "--graphs did not name a readable graph input")

    try:
        course_manifest, lessons = load_course(course_manifest_path)
        mapping = read_json(mapping_path)
        mastery = read_json(mastery_path)
        knowledge = read_json(knowledge_path)
        graph_edges = []
        for path in graph_paths:
            graph_edges.extend(read_json(path).get("edges", []))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("FAIL")
        print(f"- SET_IDENTITY: unable to read authoritative inputs: {exc}")
        return 1
    known_knowledge = {item["knowledge_id"] for item in knowledge["items"]}
    known_edges = {e.get("edge_id"): e for e in graph_edges}

    # ---- manifest structure and identity -------------------------------------------------
    prerequisite_fields = [field for field in ("prerequisites", "hard_prerequisites",
                                               "graph_edges", "assessment_prerequisites")
                           if field in set_doc]
    missing = sorted(EXPECTED_SET_KEYS - set(set_doc))
    extra = sorted(set(set_doc) - EXPECTED_SET_KEYS - set(prerequisite_fields))
    if missing:
        fail("SET_IDENTITY", "full set manifest is missing required fields: " + ", ".join(missing))
    if extra:
        fail("SET_IDENTITY", "full set manifest carries unknown fields: " + ", ".join(extra))
    if set_doc.get("set_id") != "jimeng-creator-academy-v1-full-assessment-set" \
            or not SET_ID_PATTERN.match(str(set_doc.get("set_id", ""))):
        fail("SET_IDENTITY", f"set_id {set_doc.get('set_id')!r} is not the canonical full set id")
    if set_doc.get("status") != SET_STATUS:
        fail("SET_IDENTITY", f"set status must be {SET_STATUS!r}; found {set_doc.get('status')!r}")
    expected_order_basis = "course-manifest.lesson_order_by_module"
    if set_doc.get("lesson_order_basis") != expected_order_basis:
        fail("SET_IDENTITY",
             f"lesson_order_basis must be {expected_order_basis!r}; "
             f"found {set_doc.get('lesson_order_basis')!r}")
    for key in ("assessment_order_rule", "assessment_order_tie_break"):
        if not str(set_doc.get(key, "")).strip():
            fail("SET_IDENTITY", f"{key} must record the programmatic ordering rule")

    # The fixture-local manifest wins; otherwise the declared path, then the canonical manifest.
    local_coverage = set_path.parent / "assessment-coverage-manifest.json"
    coverage_path_text = set_doc.get("coverage_manifest")
    if not isinstance(coverage_path_text, str) or not coverage_path_text.strip():
        fail("SET_IDENTITY", "coverage_manifest must name the coverage manifest file")
        coverage_path_text = local_coverage.name
    declared_coverage = resolve(coverage_path_text, set_path.parent)
    if local_coverage.is_file():
        coverage_path = local_coverage
    elif declared_coverage.is_file():
        coverage_path = declared_coverage
    elif (ASSESSMENT_DIR / "full-assessments/assessment-coverage-manifest.json").is_file():
        coverage_path = ASSESSMENT_DIR / "full-assessments/assessment-coverage-manifest.json"
    else:
        coverage_path = declared_coverage
        fail("SET_IDENTITY", f"coverage manifest not found at {coverage_path_text}")

    # ---- course identity -----------------------------------------------------------------
    course_id = course_manifest["course_id"]
    for label, value in (("full-assessment-set.json", set_doc.get("course_id")),
                         ("full-assessment-mapping.json", mapping.get("course_id")),
                         ("mastery-map.json", mastery.get("course_id"))):
        if value != course_id:
            fail("COURSE_IDENTITY", f"{label}: course_id {value!r} != course manifest {course_id!r}")

    # ---- canonical membership ------------------------------------------------------------
    canonical_root = ASSESSMENT_DIR / "full-assessments/assessments"
    fixture_dir = set_path.parent / "assessments"
    assessments_root = canonical_root
    if not glob.glob(str(canonical_root / "*.json")) and \
            glob.glob(str(fixture_dir / "*.json")):
        assessments_root = fixture_dir

    def load_assessment(path):
        try:
            data = read_json(path)
        except (OSError, ValueError) as exc:
            fail("INDIVIDUAL_ASSESSMENT_VALIDITY", f"{path.name}: unable to read: {exc}")
            return None
        return data

    discovered = {}
    for path_text in sorted(glob.glob(str(assessments_root / "*.json"))):
        path = Path(path_text)
        data = load_assessment(path)
        if data is not None:
            discovered[data.get("assessment_id")] = (path, data)
    # A fixture's own pair shadows the canonical pair with the same assessment id.
    for path_text in sorted(glob.glob(str(fixture_dir / "*.json"))):
        path = Path(path_text)
        data = load_assessment(path)
        if data is not None:
            discovered[data.get("assessment_id")] = (path, data)
    if not discovered:
        fail("CANONICAL_MEMBERSHIP_IDENTITY_SET",
             f"no canonical assessment JSON found under {relative(assessments_root)}")

    declared_order = set_doc.get("assessment_order") or []
    declared_files = set_doc.get("assessment_files") or {}
    if not isinstance(declared_order, list) or not isinstance(declared_files, dict):
        fail("SET_IDENTITY", "assessment_order must be a list and assessment_files a mapping")
        declared_order, declared_files = [], {}
    if len(set(declared_order)) != len(declared_order):
        fail("DUPLICATE_ASSESSMENT_ID", "assessment_order contains duplicate assessment ids")
    if len(set(declared_files)) != len(declared_files):
        fail("DUPLICATE_ASSESSMENT_ID", "assessment_files contains duplicate assessment ids")
    if set(declared_order) != set(declared_files):
        only_order = sorted(set(declared_order) - set(declared_files))
        only_files = sorted(set(declared_files) - set(declared_order))
        fail("CANONICAL_MEMBERSHIP_IDENTITY_SET",
             f"assessment_order and assessment_files disagree; only in order {only_order}; "
             f"only in files {only_files}")

    mapping_required = {r["requirement_id"] for r in mapping["requirements"]
                        if r.get("mastery_required") is True}
    mastery_required = {rid for unit in mastery.get("units", [])
                        for rid in unit.get("required_requirement_ids") or []}
    declared_requirement_ids = {r["requirement_id"] for r in mapping["requirements"]}
    for rid in sorted(mastery_required - declared_requirement_ids):
        fail("REQUIREMENT_COVERAGE_IDENTITY_SET",
             f"mastery-map requires requirement {rid} which the mapping does not declare")
    expected_required_ids = mapping_required | (mastery_required & declared_requirement_ids)

    discovered_ids = {aid for aid in discovered if aid is not None}
    if discovered_ids != set(declared_files):
        missing_ids = sorted(discovered_ids - set(declared_files))
        extra_ids = sorted(set(declared_files) - discovered_ids)
        fail("CANONICAL_MEMBERSHIP_IDENTITY_SET",
             f"membership drift: on disk but not in manifest {missing_ids}; "
             f"in manifest but not on disk {extra_ids}")
    expected_member_count = len(discovered_ids)
    if len(declared_files) != expected_member_count:
        fail("CANONICAL_MEMBERSHIP_IDENTITY_SET",
             f"manifest declares {len(declared_files)} assessments; discovered {expected_member_count}")
    findings.append(("CANONICAL_ASSESSMENT_COUNT", expected_member_count))

    # Individually evaluated members: ids declared by both the repository files and the manifest.
    members = sorted(set(discovered_ids) & set(declared_files))

    # ---- per-assessment file, pair, status, semantics ------------------------------------
    assessment_data = {}
    validity_ok = {}
    markdown_ok = {}
    for aid in members:
        relative_path = declared_files.get(aid)
        if not isinstance(relative_path, str) or not relative_path.strip():
            fail("ASSESSMENT_FILE_EXISTENCE", f"{aid}: assessment_files entry is not a path")
            continue
        guards = (("HISTORICAL_OR_PILOT_ONLY_PATH_GUARD", HISTORICAL_MARKERS),
                  ("TEMP_SCRATCH_REVIEW_PROBE_RECOVERY_PATH_GUARD", TEMP_MARKERS))
        for code, markers in guards:
            hits = path_error(relative_path, markers, fixture_exempt=True)
            if hits:
                fail(code, f"{aid}: declared file path {relative_path!r} carries {hits}")
        # DECLARED_REFERENCE_IS_AUTHORITATIVE_FOR_EXISTENCE: an explicitly declared
        # assessment_files path is machine truth about that member's file.  It is resolved
        # deterministically against the manifest's own directory and that exact resolved file
        # must exist.  A missing declared file is never rescued by overlay discovery, by
        # discovered[assessment_id] or by the canonical path: such a substitution would make
        # the manifest's own file references unfalsifiable.  Canonical discovery stays legal
        # for expected membership identity and for the member's contract/cross-checks, so the
        # already-validated canonical entity still carries this member's semantic and coverage
        # checks while its file-level checks are what the missing declaration fails.
        path = resolve(relative_path, set_path.parent)
        declared_file_missing = not path.is_file()
        if declared_file_missing:
            fail("ASSESSMENT_FILE_EXISTENCE",
                 f"{aid}: declared assessment file not found at {relative_path}")
        md_path = path.with_suffix(".md")
        if not declared_file_missing and not md_path.is_file():
            fail("JSON_MD_PAIR_EXISTENCE", f"{aid}: markdown sibling missing for {path.name}")
        if aid not in discovered:
            fail("UNKNOWN_ASSESSMENT_REFERENCE",
                 f"{aid}: declared in the manifest but no canonical assessment file declares it")
            continue
        if declared_file_missing:
            # The member's declared file is absent, so there is no declared pair to validate and
            # no declared name to compare; the dependent checks that need the file itself are
            # skipped and only this member's coverage identity is still evaluated.
            data = discovered[aid][1]
            assessment_data[aid] = data
            if path.stem != aid or not ASSESSMENT_ID_PATTERN.match(str(aid)):
                fail("CANONICAL_MEMBERSHIP_IDENTITY_SET",
                     f"{aid}: file name and assessment_id must agree and match JCA-A-###")
            continue
        if path.name != discovered[aid][0].name:
            fail("ASSESSMENT_FILE_EXISTENCE",
                 f"{aid}: manifest points at {path.name} but the declaring file is "
                 f"{discovered[aid][0].name}")
        data = discovered[aid][1]
        assessment_data[aid] = data
        if path.stem != aid or not ASSESSMENT_ID_PATTERN.match(str(aid)):
            fail("CANONICAL_MEMBERSHIP_IDENTITY_SET",
                 f"{aid}: file name and assessment_id must agree and match JCA-A-###")
        if data.get("status") != ASSESSMENT_STATUS:
            fail("STATUS_LEGALITY",
                 f"{aid}: status must be {ASSESSMENT_STATUS!r}; found {data.get('status')!r}")
        alignment_type = (data.get("alignment") or {}).get("completion_check_alignment")
        if alignment_type not in ALIGNMENT_TYPES:
            fail("COVERAGE_MANIFEST_FIDELITY",
                 f"{aid}: alignment type {alignment_type!r} is not one of {list(ALIGNMENT_TYPES)}")
        if "requirement_ids" in data:
            fail("REQUIREMENT_COVERAGE_IDENTITY_SET",
                 f"{aid}: requirement_ids must live only in the coverage manifest, not in the "
                 "assessment entity")
        validity = []
        structure(data, ASSESSMENT_SCHEMA, aid, validity)
        validity += validate_assessment(data, ASSESSMENT_SCHEMA, lessons, known_knowledge, label=aid)
        validity_ok[aid] = not validity
        for message in validity:
            fail("INDIVIDUAL_ASSESSMENT_VALIDITY", str(message))
        for lid in data.get("lesson_ids") or []:
            if lid not in lessons:
                fail("CANONICAL_MEMBERSHIP_IDENTITY_SET",
                     f"{aid}: lesson_id {lid!r} is not a canonical lesson of the course")
        markdown_ok[aid] = True
        if md_path.is_file():
            try:
                md_text = io.open(md_path, encoding="utf-8").read()
            except OSError as exc:
                fail("JSON_MD_CONSISTENCY", f"{aid}: unable to read markdown: {exc}")
                markdown_ok[aid] = False
                continue
            _, bad = markdown_check_pair(path, data, md_text)
            if bad:
                markdown_ok[aid] = False
            for item in bad:
                fail("JSON_MD_CONSISTENCY",
                     f"{aid}: {item} does not appear verbatim in the markdown")
        else:
            markdown_ok[aid] = False

    findings.append(("CANONICAL_ASSESSMENT_VALIDATOR_PASS_COUNT",
                     sum(1 for ok in validity_ok.values() if ok)))
    findings.append(("CANONICAL_ASSESSMENT_MARKDOWN_CONSISTENCY_PASS_COUNT",
                     sum(1 for ok in markdown_ok.values() if ok)))

    for aid in sorted(set(declared_files) - set(discovered)):
        fail("UNKNOWN_ASSESSMENT_REFERENCE",
             f"{aid}: declared by full-assessment-set.json but no canonical assessment file "
             "under the assessments root declares it")

    # ---- mapping semantics ---------------------------------------------------------------
    mapping_argv = [str(mapping_path), str(course_manifest_path), str(knowledge_path)]
    mapping_argv += [str(p) for p in graph_paths]
    mapping_rc, mapping_diag = run_reused_main(_mapping_module, mapping_argv)
    if mapping_rc != 0:
        fail("REQUIREMENT_COVERAGE_IDENTITY_SET",
             "validate_assessment_mapping.py reported FAIL for the authoritative mapping")
        for line in mapping_diag:
            fail("REQUIREMENT_COVERAGE_IDENTITY_SET", "validate_assessment_mapping.py " + line)

    # ---- coverage identity sets ----------------------------------------------------------
    links, carrier, ambiguous = derive_links(mapping["requirements"], assessment_data)
    for message in ambiguous:
        fail("REQUIREMENT_COVERAGE_IDENTITY_SET",
             f"requirement without a unique carrying assessment: {message}")

    expected_requirement_links = set()
    expected_outcome_links = set()
    requirements_by_id = {r["requirement_id"]: r for r in mapping["requirements"]}
    outcome_owner = {}
    for lid, lesson in lessons.items():
        for index in range(len(lesson["learner_outcomes"])):
            outcome_owner[f"{lid}#{index}"] = lid

    coverage_actual = {}
    for aid, data in sorted(assessment_data.items()):
        members = links.get(aid, [])
        requirement_ids = sorted(m["requirement_id"] for m in members)
        target_outcomes = sorted({o for rid in requirement_ids
                                  for o in requirements_by_id[rid].get("target_outcomes") or []})
        for rid in requirement_ids:
            for outcome in requirements_by_id[rid].get("target_outcomes") or []:
                expected_outcome_links.add(outcome)
        expected_requirement_links.update(requirement_ids)
        coverage_actual[aid] = {
            "requirement_ids": requirement_ids,
            "target_outcomes": target_outcomes,
            "link_sources": {m["requirement_id"]: m["link_source"] for m in members},
        }

    all_outcomes = all_learner_outcomes(lessons)
    for outcome in sorted(expected_outcome_links - set(outcome_owner)):
        fail("LEARNER_OUTCOME_COVERAGE_IDENTITY_SET",
             f"requirement target_outcome {outcome!r} does not exist in any canonical lesson")

    # Coverage is measured by what the assessment actually observes, not by what the requirement
    # asks for: an assessment that stops observing a designated outcome really leaves it
    # uncovered.  Both directions are checked, so neither an outcome no requirement designates
    # nor a designated outcome nothing observes can pass.  (The second set is what
    # UNCOVERED_LEARNER_OUTCOME_COUNT already reports; the identity check must agree with it.)
    covered_outcomes = set()
    for aid, data in assessment_data.items():
        lids = set(data.get("lesson_ids") or [])
        for text in data.get("target_outcomes") or []:
            for lid in lids:
                lesson = lessons.get(lid)
                if lesson and text in lesson["learner_outcomes"]:
                    covered_outcomes.add(f"{lid}#{lesson['learner_outcomes'].index(text)}")
    for outcome in sorted(set(outcome_owner) - covered_outcomes):
        fail("LEARNER_OUTCOME_COVERAGE_IDENTITY_SET",
             f"designated canonical learner outcome {outcome} is not observed by any "
             "carrying assessment")
    for outcome in sorted(covered_outcomes - expected_outcome_links):
        fail("LEARNER_OUTCOME_COVERAGE_IDENTITY_SET",
             f"assessment observes learner outcome {outcome} which is not designated by any "
             "requirement")

    uncovered = sorted(expected_required_ids - expected_requirement_links)
    unknown = sorted(expected_requirement_links - expected_required_ids)
    for rid in uncovered:
        fail("REQUIREMENT_COVERAGE_IDENTITY_SET",
             f"mastery-required requirement {rid} has no carrying assessment")
    for rid in unknown:
        fail("REQUIREMENT_COVERAGE_IDENTITY_SET",
             f"assessment coverage links unknown or non-required requirement {rid}")
    for rid, aid in sorted(carrier.items()):
        if rid not in requirements_by_id:
            continue
        for outcome in requirements_by_id[rid].get("target_outcomes") or []:
            lid = outcome_owner.get(outcome)
            if lid is not None and lid not in (assessment_data[aid].get("lesson_ids") or []):
                fail("LEARNER_OUTCOME_COVERAGE_IDENTITY_SET",
                     f"{aid}: carries {rid} whose outcome {outcome} belongs to lesson {lid} "
                     "outside the assessment lesson_ids")

    findings.append(("COVERED_REQUIRED_REQUIREMENT_COUNT", len(expected_requirement_links)))
    findings.append(("UNCOVERED_REQUIRED_REQUIREMENT_COUNT", len(uncovered)))
    findings.append(("COVERED_LEARNER_OUTCOME_COUNT", len(covered_outcomes)))
    findings.append(("UNCOVERED_LEARNER_OUTCOME_COUNT", len(all_outcomes - covered_outcomes)))

    # ---- coverage manifest fidelity ------------------------------------------------------
    coverage_doc = {}
    coverage_on_disk = None
    if coverage_path.is_file():
        try:
            coverage_doc = read_json(coverage_path)
            coverage_on_disk = sha256(coverage_path)
        except (OSError, ValueError) as exc:
            fail("COVERAGE_MANIFEST_FIDELITY", f"unable to read coverage manifest: {exc}")
    if coverage_doc:
        missing_cov = sorted(EXPECTED_COVERAGE_KEYS - set(coverage_doc))
        extra_cov = sorted(set(coverage_doc) - EXPECTED_COVERAGE_KEYS)
        if missing_cov:
            fail("COVERAGE_MANIFEST_FIDELITY",
                 "coverage manifest is missing required fields: " + ", ".join(missing_cov))
        if extra_cov:
            fail("COVERAGE_MANIFEST_FIDELITY",
                 "coverage manifest carries unknown fields: " + ", ".join(extra_cov))
        if coverage_doc.get("course_id") != course_id:
            fail("COURSE_IDENTITY",
                 f"coverage manifest course_id {coverage_doc.get('course_id')!r} != {course_id!r}")
        if sorted(coverage_doc.get("alignment_type_enum") or []) != sorted(ALIGNMENT_TYPES):
            fail("COVERAGE_MANIFEST_FIDELITY",
                 f"alignment_type_enum must be exactly {sorted(ALIGNMENT_TYPES)}")
        entries = coverage_doc.get("assessments") or []
        entry_ids = [e.get("assessment_id") for e in entries]
        if len(set(entry_ids)) != len(entry_ids):
            fail("DUPLICATE_ASSESSMENT_ID", "coverage manifest contains duplicate assessment entries")
        if set(entry_ids) != set(assessment_data):
            fail("COVERAGE_MANIFEST_FIDELITY",
                 f"coverage manifest ids differ from canonical membership; "
                 f"missing {sorted(set(assessment_data) - set(entry_ids))}; "
                 f"extra {sorted(set(entry_ids) - set(assessment_data))}")
        for entry in entries:
            aid = entry.get("assessment_id")
            if aid not in coverage_actual:
                continue
            if entry.get("requirement_ids") != coverage_actual[aid]["requirement_ids"]:
                fail("COVERAGE_MANIFEST_FIDELITY",
                     f"{aid}.requirement_ids: expected {coverage_actual[aid]['requirement_ids']}; "
                     f"found {entry.get('requirement_ids')}")
            if entry.get("target_outcomes") != coverage_actual[aid]["target_outcomes"]:
                fail("COVERAGE_MANIFEST_FIDELITY",
                     f"{aid}.target_outcomes: expected {coverage_actual[aid]['target_outcomes']}; "
                     f"found {entry.get('target_outcomes')}")
            if entry.get("lesson_ids") != (assessment_data[aid].get("lesson_ids") or []):
                fail("COVERAGE_MANIFEST_FIDELITY",
                     f"{aid}.lesson_ids: expected {assessment_data[aid].get('lesson_ids')}; "
                     f"found {entry.get('lesson_ids')}")
            expected_alignment = sorted({requirements_by_id[rid].get("alignment_type")
                                         for rid in coverage_actual[aid]["requirement_ids"]})
            declared_alignment = entry.get("alignment_types")
            if sorted(declared_alignment or []) != expected_alignment:
                fail("COVERAGE_MANIFEST_FIDELITY",
                     f"{aid}.alignment_types: expected {expected_alignment}; "
                     f"found {declared_alignment}")
            for value in declared_alignment or []:
                if value not in ALIGNMENT_TYPES:
                    fail("COVERAGE_MANIFEST_FIDELITY",
                         f"{aid}.alignment_types contains illegal type {value!r}")
            for key in ("requirement_ids", "lesson_ids", "target_outcomes", "alignment_types"):
                if key not in entry:
                    fail("COVERAGE_MANIFEST_FIDELITY", f"{aid}: coverage entry is missing {key}")
        for entry in coverage_doc.get("requirement_carriers") or []:
            rid = entry.get("requirement_id")
            if rid not in requirements_by_id:
                fail("UNKNOWN_ASSESSMENT_REFERENCE",
                     f"coverage manifest carrier references unknown requirement {rid!r}")
                continue
            if entry.get("assessment_id") != carrier.get(rid):
                fail("COVERAGE_MANIFEST_FIDELITY",
                     f"requirement carrier {rid}: expected {carrier.get(rid)!r}; "
                     f"found {entry.get('assessment_id')!r}")
            expected_source = coverage_actual.get(carrier.get(rid), {}).get(
                "link_sources", {}).get(rid)
            if entry.get("link_source") != expected_source:
                fail("COVERAGE_MANIFEST_FIDELITY",
                     f"requirement carrier {rid}: expected link_source {expected_source!r}; "
                     f"found {entry.get('link_source')!r}")
        declared_carriers = {e.get("requirement_id") for e in coverage_doc.get("requirement_carriers") or []}
        if declared_carriers != set(requirements_by_id):
            fail("COVERAGE_MANIFEST_FIDELITY",
                 "requirement_carriers must cover every mapping requirement exactly once; "
                 f"missing {sorted(set(requirements_by_id) - declared_carriers)}; "
                 f"extra {sorted(declared_carriers - set(requirements_by_id))}")

    coverage_derived = {
        "assessment_count": len(coverage_actual),
        "requirement_count": len(mapping["requirements"]),
        "requirement_link_count": sum(len(v["requirement_ids"]) for v in coverage_actual.values()),
        "outcome_link_count": sum(len(v["target_outcomes"]) for v in coverage_actual.values()),
        "alignment_type_distribution": {
            t: sum(1 for aid in coverage_actual
                   if t in [requirements_by_id[rid].get("alignment_type")
                            for rid in coverage_actual[aid]["requirement_ids"]])
            for t in sorted(ALIGNMENT_TYPES)
            if any(t in [requirements_by_id[rid].get("alignment_type")
                         for rid in coverage_actual[aid]["requirement_ids"]]
                   for aid in coverage_actual)
        },
    }
    coverage_summary_expected = {
        "assessment_count": len(coverage_actual),
        "covered_required_requirement_count": len(expected_required_ids & expected_requirement_links),
        "uncovered_required_requirement_count": len(expected_required_ids - expected_requirement_links),
        "covered_learner_outcome_count": len(covered_outcomes),
        "uncovered_learner_outcome_count": len(all_outcomes - covered_outcomes),
        "covered_lesson_count": len({lid for data in assessment_data.values()
                                     for lid in data.get("lesson_ids") or []}),
    }
    if coverage_doc:
        check_derived("coverage_manifest", {k: coverage_doc.get(k) for k in coverage_derived},
                      coverage_derived, errors)
        check_derived("coverage_manifest.coverage_summary", coverage_doc.get("coverage_summary"),
                      coverage_summary_expected, errors)

    # ---- full set manifest order, files, coverage summary, derived metrics ---------------
    course_positions = {lid: i for i, lid in enumerate(canonical_lesson_ids(course_manifest))}
    if any(lid not in course_positions for data in assessment_data.values()
           for lid in data.get("lesson_ids") or []):
        fail("CANONICAL_MEMBERSHIP_IDENTITY_SET",
             "at least one assessment references a lesson outside the canonical course order")

    def order_key(aid):
        lids = [lid for lid in assessment_data[aid].get("lesson_ids") or [] if lid in course_positions]
        return (min(course_positions[lid] for lid in lids) if lids else len(course_positions), aid)

    expected_order = sorted(assessment_data, key=order_key)
    if declared_order != expected_order:
        for index, (found, expected) in enumerate(zip(declared_order, expected_order)):
            if found != expected:
                fail("SET_IDENTITY",
                     f"assessment_order[{index}]: expected {expected} (course lesson order then "
                     f"assessment_id); found {found}")
                break
        if len(declared_order) != len(expected_order):
            fail("SET_IDENTITY",
                 f"assessment_order length {len(declared_order)} != {len(expected_order)}")

    numeric_ids = sorted(assessment_data)
    if declared_order == numeric_ids and numeric_ids != expected_order:
        fail("SET_IDENTITY", "assessment_order is a plain numeric id sort, not the course lesson order")

    for aid in sorted(assessment_data):
        declared_name = str(declared_files.get(aid) or "").replace("\\", "/").split("/")[-1]
        if declared_name != discovered[aid][0].name:
            fail("CANONICAL_MEMBERSHIP_IDENTITY_SET",
                 f"{aid}: assessment_files expected 'assessments/{discovered[aid][0].name}'; "
                 f"found {declared_files.get(aid)!r}")

    set_entries = set_doc.get("assessments") or []
    entry_by_id = {}
    for entry in set_entries:
        if not isinstance(entry, dict):
            fail("SET_IDENTITY", "full set assessments entries must be objects")
            continue
        entry_by_id[entry.get("assessment_id")] = entry
    for aid, data in sorted(assessment_data.items()):
        entry = entry_by_id.get(aid)
        if entry is None:
            fail("UNKNOWN_ASSESSMENT_REFERENCE", f"full set manifest has no entry for {aid}")
            continue
        if entry.get("requirement_ids") != coverage_actual[aid]["requirement_ids"]:
            fail("COVERAGE_MANIFEST_FIDELITY",
                 f"{aid}: set entry requirement_ids {entry.get('requirement_ids')} != "
                 f"{coverage_actual[aid]['requirement_ids']}")
        if entry.get("lesson_ids") != (data.get("lesson_ids") or []):
            fail("COVERAGE_MANIFEST_FIDELITY",
                 f"{aid}: set entry lesson_ids {entry.get('lesson_ids')} != "
                 f"{data.get('lesson_ids')}")
        if entry.get("assessment_type") != data.get("assessment_type"):
            fail("COVERAGE_MANIFEST_FIDELITY", f"{aid}: set entry assessment_type is stale")
        if entry.get("status") != ASSESSMENT_STATUS:
            fail("STATUS_LEGALITY", f"{aid}: set entry status must be {ASSESSMENT_STATUS!r}")
        if entry.get("file") != declared_files.get(aid):
            fail("ASSESSMENT_FILE_EXISTENCE", f"{aid}: set entry file disagrees with assessment_files")
        if entry.get("alignment_type") not in ALIGNMENT_TYPES:
            fail("COVERAGE_MANIFEST_FIDELITY",
                 f"{aid}: set entry alignment_type {entry.get('alignment_type')!r} is illegal")
    unknown_entries = sorted(set(entry_by_id) - set(assessment_data))
    for aid in unknown_entries:
        fail("UNKNOWN_ASSESSMENT_REFERENCE",
             f"full set manifest references unknown assessment {aid!r}")

    set_derived = {
        "coverage_summary": {
            "assessment_count": len(assessment_data),
            "covered_lesson_count": len({lid for data in assessment_data.values()
                                        for lid in data.get("lesson_ids") or []}),
            "canonical_lesson_count": len(lessons),
            "covered_required_requirement_count": len(expected_required_ids & expected_requirement_links),
            "covered_learner_outcome_count": len(covered_outcomes),
        },
        "metrics": {
            "requirement_count": len(mapping["requirements"]),
            "required_requirement_count": len(expected_required_ids),
            "total_learner_outcome_count": len(all_outcomes),
            "multi_lesson_assessment_count": sum(
                1 for data in assessment_data.values() if len(data.get("lesson_ids") or []) > 1),
        },
        "assessment_type_distribution": {
            t: sum(1 for data in assessment_data.values() if data.get("assessment_type") == t)
            for t in sorted({data.get("assessment_type") for data in assessment_data.values()})
        },
        "alignment_type_distribution": {
            t: sum(1 for data in assessment_data.values()
                   if (data.get("alignment") or {}).get("completion_check_alignment") == t)
            for t in sorted({(data.get("alignment") or {}).get("completion_check_alignment")
                             for data in assessment_data.values()})
        },
    }
    check_derived("full_set.coverage_summary", set_doc.get("coverage_summary"),
                  set_derived["coverage_summary"], errors)
    # ---- pilot source discovery ----------------------------------------------------------
    pilot_sources = {}
    for path_text in sorted(glob.glob(str(pilot_dir / "*.json"))):
        path = Path(path_text)
        if path.stem not in assessment_data:
            continue
        try:
            pilot_sources[path.stem] = read_json(path)
        except (OSError, ValueError) as exc:
            fail("PILOT_PROMOTION_FIDELITY", f"{path.name}: unable to read pilot source: {exc}")
    findings.append(("PILOT_SOURCE_ASSESSMENT_COUNT", len(pilot_sources)))

    declared_metrics = dict(set_doc.get("metrics") or {})
    recomputable = dict(set_derived["metrics"])
    recomputable["pilot_source_assessment_count"] = len(pilot_sources)
    recomputable["derived_metric_mismatch_count"] = 0
    recomputable["non_order_assessment_prerequisite_misuse_count"] = 0
    recomputable["pilot_promotion_semantic_diff_count"] = 0
    check_derived("full_set.metrics", declared_metrics, recomputable, errors)
    check_derived("full_set.assessment_type_distribution",
                  set_doc.get("assessment_type_distribution"),
                  set_derived["assessment_type_distribution"], errors)
    check_derived("full_set.alignment_type_distribution",
                  set_doc.get("alignment_type_distribution"),
                  set_derived["alignment_type_distribution"], errors)

    for field, value in set_doc.items():
        if field.endswith("_count") or field in ("metrics", "coverage_summary", "distribution"):
            if field not in EXPECTED_SET_KEYS:
                fail("DERIVED_METRIC_RECOMPUTATION",
                     f"full_set.{field}: declared derived metric is not recomputable")

    # ---- pilot promotion fidelity --------------------------------------------------------
    promoted = 0
    semantic_diffs = 0
    for aid, source in sorted(pilot_sources.items()):
        canonical = assessment_data[aid]
        if source.get("status") != "pilot":
            fail("PILOT_SOURCE_REFERENCE_INTEGRITY",
                 f"{aid}: pilot source status must be 'pilot'; found {source.get('status')!r}")
        if canonical.get("status") != ASSESSMENT_STATUS:
            continue
        promoted += 1
        for key in sorted(set(source) | set(canonical)):
            if key == "status":
                continue
            if source.get(key) != canonical.get(key):
                semantic_diffs += 1
                fail("PILOT_PROMOTION_FIDELITY",
                     f"{aid}.{key}: pilot source and promoted canonical differ "
                     f"({source.get(key)!r} -> {canonical.get(key)!r})")
    findings.append(("PROMOTED_CANONICAL_PILOT_COUNT", promoted))
    findings.append(("PILOT_PROMOTION_SEMANTIC_DIFF_COUNT", semantic_diffs))

    for aid, data in sorted(assessment_data.items()):
        if data.get("status") == "pilot":
            fail("STATUS_LEGALITY", f"{aid}: canonical set member must not stay in pilot status")

    declared_pilot_count = (set_doc.get("metrics") or {}).get("pilot_source_assessment_count")
    if declared_pilot_count != len(pilot_sources):
        fail("DERIVED_METRIC_RECOMPUTATION",
             f"full_set.metrics.pilot_source_assessment_count: expected {len(pilot_sources)}; "
             f"found {declared_pilot_count}")

    # ---- non-order prerequisite guard ----------------------------------------------------
    order_gates = {}
    edge_hits = {}
    module_of = {lid: lesson.get("module_id") for lid, lesson in lessons.items()}
    knowledge_lesson = {}
    for lid, lesson in lessons.items():
        for ref in lesson.get("knowledge_refs", []):
            knowledge_lesson.setdefault(ref, set()).add(lid)
    for edge in graph_edges:
        relation = edge.get("relation")
        if relation in NON_ORDER_RELATIONS and relation in ORDER_RELATIONS:
            continue
        for source in sorted(knowledge_lesson.get(edge.get("from"), set())):
            for target in sorted(knowledge_lesson.get(edge.get("to"), set())):
                if source == target or module_of.get(source) != module_of.get(target):
                    continue
                if relation in ORDER_RELATIONS:
                    order_gates.setdefault(target, set()).add(source)
                    edge_hits.setdefault(edge.get("edge_id"), set()).add(target)

    unit_of_lesson = {}
    for unit in mastery.get("units", []):
        for lid in unit.get("lesson_ids") or []:
            unit_of_lesson[lid] = unit["mastery_unit_id"]
    misuse = 0
    for unit in mastery.get("units", []):
        lid = (unit.get("lesson_ids") or [None])[0]
        expected_prev = sorted(unit_of_lesson[p] for p in order_gates.get(lid, set())
                               if p in unit_of_lesson)
        declared_prev = sorted(unit.get("hard_prerequisite_units") or [])
        for value in declared_prev:
            if value not in unit_of_lesson.values():
                misuse += 1
                fail("NON_ORDER_PREREQUISITE_GUARD",
                     f"{unit.get('mastery_unit_id')}: hard prerequisite {value!r} is not a mastery unit")
        if expected_prev != declared_prev:
            for value in declared_prev:
                if value not in expected_prev:
                    misuse += 1
                    fail("NON_ORDER_PREREQUISITE_GUARD",
                         f"{unit.get('mastery_unit_id')}: hard prerequisite {value!r} is not backed "
                         "by a PREREQUISITE_OF / PROCEDURE_PRECEDES graph relation")
            for value in expected_prev:
                if value not in declared_prev:
                    fail("NON_ORDER_PREREQUISITE_GUARD",
                         f"{unit.get('mastery_unit_id')}: missing hard prerequisite {value!r} "
                         "backed by an order relation")

    for req in mapping["requirements"]:
        context = req.get("hard_sequence_context") or {}
        for value in context.get("hard_prerequisite_lesson_ids") or []:
            if value not in lessons:
                fail("NON_ORDER_PREREQUISITE_GUARD",
                     f"{req['requirement_id']}: hard prerequisite lesson {value!r} is not canonical")
        for value in context.get("supporting_edge_ids") or []:
            edge = known_edges.get(value)
            if edge is None:
                fail("NON_ORDER_PREREQUISITE_GUARD",
                     f"{req['requirement_id']}: supporting edge {value!r} is not in any graph input")
            elif edge.get("relation") not in ORDER_RELATIONS:
                fail("NON_ORDER_PREREQUISITE_GUARD",
                     f"{req['requirement_id']}: edge {value} uses relation {edge.get('relation')!r} "
                     "as ordering support")
            elif edge.get("to") not in {k for lid in context.get("hard_prerequisite_lesson_ids") or []
                                        for k in lessons[lid].get("knowledge_refs", [])} \
                    and context.get("hard_prerequisite_lesson_ids"):
                pass

    for unit in mastery.get("units", []):
        for value in unit.get("hard_prerequisite_units") or []:
            if value not in unit_of_lesson.values():
                misuse += 1
                fail("NON_ORDER_PREREQUISITE_GUARD",
                     f"{unit.get('mastery_unit_id')}: prerequisite {value!r} is not a mastery unit")
    findings.append(("NON_ORDER_ASSESSMENT_PREREQUISITE_MISUSE_COUNT", misuse))

    for field in ("prerequisites", "hard_prerequisites", "graph_edges", "assessment_prerequisites"):
        for where, doc in (("full_set", set_doc), ("coverage_manifest", coverage_doc)):
            if field in doc:
                fail("NON_ORDER_PREREQUISITE_GUARD",
                     f"{where}.{field}: the machine manifests must not declare prerequisites or edges")

    # ---- mastery contract regression through the existing validator -----------------------
    mastery_argv = [str(mastery_path), str(mapping_path), str(course_manifest_path)]
    mastery_argv += [str(p) for p in graph_paths]
    mastery_rc, mastery_diag = run_reused_main(_mastery_module, mastery_argv)
    if mastery_rc != 0:
        fail("NON_ORDER_PREREQUISITE_GUARD",
             "validate_mastery.py reported FAIL for the authoritative mastery contract")
        for line in mastery_diag:
            fail("NON_ORDER_PREREQUISITE_GUARD", "validate_mastery.py " + line)

    decisions = set()
    for unit in mastery.get("units", []):
        required = list(unit.get("required_outcomes") or [])
        for snapshot in ({"hard_prerequisites_satisfied": False},
                         {"satisfied_outcomes": required},
                         {"satisfied_outcomes": [], "evidence_submitted": False},
                         {"satisfied_outcomes": [], "execution_criteria_met": False},
                         {"satisfied_outcomes": [], "misconception_outcomes": required},
                         {"satisfied_outcomes": []}):
            decisions.add(mastery_decide(snapshot, unit)[0])
    missing_branches = sorted(set(DECISION_ENUM) - decisions)
    if missing_branches:
        fail("NON_ORDER_PREREQUISITE_GUARD",
             f"mastery decision branches not reachable: {missing_branches}")
    findings.append(("MASTERY_DECISION_REACHABILITY",
                     "PASS" if not missing_branches else "FAIL"))

    # ---- path guards on machine truth ----------------------------------------------------
    for label, value in (("full_set.coverage_manifest", coverage_path_text),
                         ("coverage_manifest.source_assessment_set",
                          coverage_doc.get("source_assessment_set"))):
        if not isinstance(value, str):
            continue
        hits = path_error(value, TEMP_MARKERS)
        if hits:
            fail("TEMP_SCRATCH_REVIEW_PROBE_RECOVERY_PATH_GUARD",
                 f"{label}: {value!r} carries {hits}")
        hits = path_error(value, HISTORICAL_MARKERS)
        if hits:
            fail("HISTORICAL_OR_PILOT_ONLY_PATH_GUARD", f"{label}: {value!r} carries {hits}")

    findings.append(("DERIVED_METRIC_MISMATCH_COUNT",
                     len([e for e in errors if e[0] == "DERIVED_METRIC_RECOMPUTATION"])))
    findings.append(("PILOT_PROMOTION_SEMANTIC_DIFFS",
                     sum(1 for e in errors if e[0] == "PILOT_PROMOTION_FIDELITY")))
    findings.append(("COVERAGE_MANIFEST_SHA256", coverage_on_disk or "MISSING"))

    order = ["CANONICAL_ASSESSMENT_COUNT", "CANONICAL_ASSESSMENT_VALIDATOR_PASS_COUNT",
             "CANONICAL_ASSESSMENT_MARKDOWN_CONSISTENCY_PASS_COUNT",
             "CANONICAL_ASSESSMENT_JSON_SHA256", "PILOT_SOURCE_ASSESSMENT_COUNT",
             "PROMOTED_CANONICAL_PILOT_COUNT", "PILOT_PROMOTION_SEMANTIC_DIFF_COUNT",
             "COVERED_REQUIRED_REQUIREMENT_COUNT", "UNCOVERED_REQUIRED_REQUIREMENT_COUNT",
             "COVERED_LEARNER_OUTCOME_COUNT", "UNCOVERED_LEARNER_OUTCOME_COUNT",
             "DERIVED_METRIC_MISMATCH_COUNT",
             "NON_ORDER_ASSESSMENT_PREREQUISITE_MISUSE_COUNT",
             "MASTERY_DECISION_REACHABILITY", "COVERAGE_MANIFEST_SHA256", "COURSE_IDENTITY"]
    by_name = {}
    for name, value in findings:
        by_name.setdefault(name, value)

    print("FAIL" if errors else "PASS")
    print(f"- FULL_SET_VALIDATOR: {'PASS' if not errors else 'FAIL'}")
    print(f"- SET_IDENTITY: {set_doc.get('set_id')}")
    print(f"- COURSE_IDENTITY: {course_id}")
    for name in order:
        if name in by_name:
            print(f"- {name}: {by_name[name]}")
    for name, value in findings:
        if name.startswith("UNCOVERED_OUTCOME"):
            print(f"- UNCOVERED_LEARNER_OUTCOME_REF: {value}")
        elif name == "ORDER_NOT_LESSON_BASED" and verbose:
            print(f"- ORDER_NOT_LESSON_BASED: {value}")
    if verbose:
        print("- COVERED_REQUIREMENT_IDS: " + ", ".join(sorted(expected_requirement_links)))
        print("- COVERED_LEARNER_OUTCOME_REFS: " + ", ".join(sorted(covered_outcomes)))
    for code, message in errors:
        print(f"- {code}: {message}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
