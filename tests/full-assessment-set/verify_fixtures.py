"""Verify every tests/full-assessment-set/ fixture artifact against repository truth.

Usage:
  python tests/full-assessment-set/verify_fixtures.py

This is a harness check, not a machine-semantics validator.  It proves six things:

 1. GENERATED FIXTURE BYTES.  Every persisted fixture-local file (mutation descriptor, mutated
    assessment pair, fixture-local coverage manifest, isolated pilot source set, shared baseline
    mirror, source-fingerprint manifest, index) is exactly the document generate_fixtures.py
    derives from repository truth, so no expectation and no mutated evidence file is
    hand-maintained.

 2. HYBRID SOURCE FIDELITY.  The shared `_baseline/` package is a HYBRID_DECLARATIVE_BASELINE and
    every canonical assessment member declares exactly one of the two legal source modes:

      * LOCAL_BYTE_EXACT_COPY       the fixture-local mirror exists and its bytes are identical to
                                    the canonical member (equal SHA-256, equal byte size);
      * CANONICAL_DIRECT_DECLARATION no copy is produced, and the declared source is the exact
                                    frozen canonical path, whose SHA-256 and byte size equal the
                                    fingerprint's recorded canonical values.

    A member never mixes the two, and a declared canonical path is never a rescue for a missing
    local mirror.  The per-file `declared_sha256` / `declared_byte_size` are recomputed from the
    bytes the declared path actually holds, so undeclared drift in either mode is an error.

 3. DECLARED REFERENCE RESOLUTION.  Every member path a fixture declares in `assessment_files`
    resolves against that fixture's own directory and really is a file -- except for the single
    member the declared-reference fixture withdraws, whose declared path must be physically
    absent.  That fixture must declare exactly one absent path and every other declared path in it
    must resolve (NON_TARGET_DECLARED_PATH_MISSING_COUNT = 0).  No declared path is ever rescued
    by canonical discovery or by an overlay, and each declared path must be the file its member's
    declared source mode names.

 4. FOUR-WAY AGREEMENT.  The persisted mutation descriptor equals the descriptor SPECS declares,
    the persisted _index.json equals the recomputed index record, the persisted source-fingerprint
    manifest equals the recomputed manifest, and the declared path map every descriptor carries is
    the same hybrid declaration model -- descriptors, SPECS, the fingerprint manifest and the
    index never diverge.  There is no second, independent truth table.

 5. INVENTORY CLASSIFICATION.  Every file under tests/full-assessment-set/ falls into exactly one
    inventory class, and the classes are mutually exclusive and ordered:

      ACTIVE_BASELINE_CONTENT       a declared member/pilot source path of baseline-fingerprint.json
      DECLARED_FIXTURE_CONTENT      a file the generator emits or a fixture's declared artifact
      DECLARED_FIXTURE_LOCAL_OVERLAY a declared fixture-local input overlay (pilot sources)
      DECLARED_INERT_HYGIENE_DEBT   an entry of hygiene-debt.json, re-proved inert here
      UNDECLARED_ORPHAN             anything else -- always a failure

    A path belongs to one class only.  Orphan means "neither an active artifact nor a strictly
    registered, individually re-proved inert entry", so HYGIENE_DEBT_FILE_COUNT > 0 and
    ORPHAN_FILE_COUNT == 0 are both reachable and mean different things.

 6. HYGIENE DEBT IS NOT AN IGNORE LIST.  hygiene-debt.json is never an input to
    generate_fixtures.py, run_fixtures.py or validate_full_assessment_set.py, and this verifier
    only reads it to disprove inertness.  For every registered entry it re-proves: the file
    exists; its bytes still hash and measure to the registered sha256/byte_size; and it is absent
    from SPECS, from the active fixture _index, from the baseline-fingerprint members and declared
    paths, from the source descriptors, from every mutation descriptor's active inputs, and from
    the source text of the generator, runner and validator.  Any entry that fails is
    HYGIENE_DEBT_NOT_INERT and fails the run; a registered filename is matched by exact path, not
    by pattern, so no entry can widen into a glob.  Entries under `external_hygiene_debt` live
    outside this tree and are reported, never admitted into this tree's orphan audit.
"""

import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE_ROOT))

import generate_fixtures  # noqa: E402

HYGIENE_DEBT_REL = "tests/full-assessment-set/hygiene-debt.json"
# Absolute-path override, used only to point a negative control at a deliberately broken copy of
# the register.  The normal run always reads the in-tree register.
HYGIENE_DEBT_PATH = Path(os.environ.get(
    "AI_ACADEMY_HYGIENE_DEBT", str(ROOT / HYGIENE_DEBT_REL)))
HYGIENE_DEBT_CLASSIFICATION = "DECLARED_INERT_HYGIENE_DEBT"

# The three scripts hygiene-debt.json may never influence.  Their source text is part of the
# inertness proof: a registered artifact whose name still appears in the code that generates,
# runs or validates the fixtures is not inert.
PROOF_SOURCES = (
    "tests/full-assessment-set/generate_fixtures.py",
    "tests/full-assessment-set/run_fixtures.py",
    ".agents/skills/ai-academy/scripts/validate_full_assessment_set.py",
)

# Non-generated members of this harness that are neither fixture content nor debt.  Every one is
# named explicitly; none of them is a pattern that could swallow a future unknown file.
HARNESS_SOURCES = (
    "tests/full-assessment-set/generate_fixtures.py",
    "tests/full-assessment-set/verify_fixtures.py",
    "tests/full-assessment-set/run_fixtures.py",
    "tests/full-assessment-set/build_manifests.py",
    HYGIENE_DEBT_REL,
)

MISSING_FILE_FIXTURE = "invalid-missing-assessment-file"

BASELINE_ASSESSMENT_PREFIX = "tests/full-assessment-set/_baseline/assessments/"
BASELINE_PILOT_PREFIX = "tests/full-assessment-set/_baseline/pilot-sources/"

# A registered filename is only "referenced" by tooling source when it appears as a whole token,
# so `_probe_cr.txt` is not matched by an unrelated `_probe_crlf` mention.
TOKEN_BOUNDARY = r"(?<![A-Za-z0-9_.\-]){}(?![A-Za-z0-9_.\-])"


def read_text(path):
    return io.open(path, encoding="utf-8", newline="").read()


def equal(persisted_text, expected_text, path):
    if str(path).endswith(".json"):
        try:
            return (json.loads(persisted_text) == json.loads(expected_text),
                    "JSON document differs")
        except ValueError as exc:
            return False, f"unreadable JSON: {exc}"
    return persisted_text == expected_text, "text differs"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def declared_members(spec):
    return dict(spec.get("declared_paths") or {})


def load_hygiene_debt(errors):
    """The strict register of proven-inert files, or an empty register when it is unusable."""
    if not HYGIENE_DEBT_PATH.is_file():
        errors.append(f"{HYGIENE_DEBT_REL}: missing; the inert-debris register is required")
        return {"entries": [], "external_hygiene_debt": []}
    try:
        document = json.loads(read_text(HYGIENE_DEBT_PATH))
    except ValueError as exc:
        errors.append(f"{HYGIENE_DEBT_REL}: unreadable JSON: {exc}")
        return {"entries": [], "external_hygiene_debt": []}
    if not isinstance(document.get("entries"), list):
        errors.append(f"{HYGIENE_DEBT_REL}: no `entries` list")
        document["entries"] = []
    if not isinstance(document.get("external_hygiene_debt"), list):
        errors.append(f"{HYGIENE_DEBT_REL}: no `external_hygiene_debt` list")
        document["external_hygiene_debt"] = []
    return document


def main(argv=None):
    errors = []
    notes = []
    generated = dict(generate_fixtures.fixture_files())

    # ---- 1. generated fixture bytes ------------------------------------------------------
    for path, expected in sorted(generated.items()):
        target = ROOT / path
        if not target.is_file():
            errors.append(f"{path}: missing")
            continue
        persisted = read_text(target)
        same, reason = equal(persisted, expected, path)
        if not same:
            errors.append(f"{path}: {reason} (expected {len(expected)} bytes, "
                          f"found {len(persisted)} bytes)")

    # ---- 2. hybrid source fidelity -------------------------------------------------------
    fingerprint_rel = generate_fixtures.BASELINE_FINGERPRINT.relative_to(ROOT).as_posix()
    fingerprint_path = ROOT / fingerprint_rel
    fingerprint = None
    if not fingerprint_path.is_file():
        errors.append(f"{fingerprint_rel}: missing")
    else:
        try:
            fingerprint = json.loads(read_text(fingerprint_path))
        except ValueError as exc:
            errors.append(f"{fingerprint_rel}: unreadable JSON: {exc}")

    local_copy_count = 0
    canonical_direct_count = 0
    local_files_checked = 0
    canonical_direct_files_checked = 0
    baseline_file_count = 0
    fingerprint_modes = {}
    baseline_internal_paths = set()
    fingerprint_member_paths = set()
    pilot_overlay_specs = {}
    if fingerprint is not None:
        recomputed = generate_fixtures.baseline_fingerprint()
        if fingerprint != recomputed:
            errors.append(f"{fingerprint_rel}: differs from the recomputed source-fingerprint "
                          "manifest")
        modes = fingerprint.get("legal_source_modes")
        if modes != list(generate_fixtures.LEGAL_SOURCE_MODES):
            errors.append(f"{fingerprint_rel}: legal_source_modes must be "
                          f"{list(generate_fixtures.LEGAL_SOURCE_MODES)}; found {modes!r}")
        declared_in_manifest = set()
        for entry in fingerprint.get("entries") or []:
            aid = entry.get("assessment_id")
            mode = entry.get("source_mode")
            fingerprint_modes[aid] = mode
            expected_mode = generate_fixtures.member_source_mode(aid)
            if mode != expected_mode:
                errors.append(f"{aid}: source_mode {mode!r} is not the programmatically derived "
                              f"{expected_mode!r}")
            if mode == generate_fixtures.LOCAL_BYTE_EXACT_COPY:
                local_copy_count += 1
            elif mode == generate_fixtures.CANONICAL_DIRECT_DECLARATION:
                canonical_direct_count += 1
            for record in entry.get("files") or []:
                suffix = record.get("suffix")
                path_text = record.get("declared_path")
                declared_in_manifest.add(path_text)
                # The fingerprint's own declaration is the ONLY source of active baseline
                # membership.  The baseline directory is never counted by glob.
                if path_text.startswith(BASELINE_ASSESSMENT_PREFIX):
                    baseline_internal_paths.add(path_text)
                fingerprint_member_paths.add(path_text)
                canonical_path_text = record.get("canonical_path")
                canonical = ROOT / canonical_path_text
                declared = ROOT / path_text
                if not declared.is_file():
                    errors.append(f"{aid}{suffix}: declared path {path_text} does not exist")
                    continue
                raw = declared.read_bytes()
                if digest(raw) != record.get("declared_sha256") \
                        or len(raw) != record.get("declared_byte_size"):
                    errors.append(f"{aid}{suffix}: {path_text} no longer holds the bytes the "
                                  "manifest declares")
                if not canonical.is_file():
                    errors.append(f"{aid}{suffix}: canonical source {canonical_path_text} missing")
                    continue
                if mode == generate_fixtures.LOCAL_BYTE_EXACT_COPY:
                    local_files_checked += 1
                    if not path_text.startswith(BASELINE_ASSESSMENT_PREFIX):
                        errors.append(f"{aid}{suffix}: a LOCAL_BYTE_EXACT_COPY member must be "
                                      f"declared inside the shared baseline; found {path_text}")
                    elif raw != canonical.read_bytes():
                        errors.append(f"{aid}{suffix}: baseline mirror {path_text} is not "
                                      f"byte-identical to {canonical_path_text}")
                    if record.get("declared_byte_identical") is not True:
                        errors.append(f"{aid}{suffix}: mirror is not recorded byte-identical")
                elif mode == generate_fixtures.CANONICAL_DIRECT_DECLARATION:
                    canonical_direct_files_checked += 1
                    approved = (generate_fixtures.CANONICAL_DIR / f"{aid}{suffix}") \
                        .relative_to(ROOT).as_posix()
                    if path_text != canonical_path_text or path_text != approved:
                        errors.append(f"{aid}{suffix}: CANONICAL_DIRECT_DECLARATION must name the "
                                      f"exact frozen canonical path {approved}; found {path_text}")
                    if digest(raw) != record.get("canonical_sha256") \
                            or len(raw) != record.get("canonical_byte_size"):
                        errors.append(f"{aid}{suffix}: declared canonical source {path_text} no "
                                      "longer matches the frozen canonical fingerprint")
                else:
                    errors.append(f"{aid}{suffix}: illegal source mode {mode!r}")
        for aid in generate_fixtures.canonical_assessment_ids():
            for suffix in (".json", ".md"):
                expected_path = (
                    generate_fixtures.BASELINE_ASSESSMENT_DIR / f"{aid}{suffix}"
                    if generate_fixtures.member_mirror_exact(aid)
                    else generate_fixtures.CANONICAL_DIR / f"{aid}{suffix}"
                ).relative_to(ROOT).as_posix()
                if expected_path not in declared_in_manifest:
                    errors.append(f"{aid}{suffix}: the manifest declares no source path")
        baseline_pilot_source_count = 0
        for entry in fingerprint.get("pilot_sources") or []:
            aid = entry.get("assessment_id")
            path_text = entry.get("declared_path")
            declared = ROOT / path_text
            if not declared.is_file():
                errors.append(f"pilot source {aid}: declared path {path_text} does not exist")
                continue
            raw = declared.read_bytes()
            canonical = ROOT / entry.get("canonical_path")
            # The pilot baseline package is DECLARED_BASELINE_CONTENT: every member here is a
            # fingerprint-declared path, so it is active baseline content, never debris.
            baseline_internal_paths.add(path_text)
            fingerprint_member_paths.add(path_text)
            baseline_pilot_source_count += 1
            if not path_text.startswith(BASELINE_PILOT_PREFIX):
                errors.append(f"pilot source {aid}: a baseline pilot source must be declared "
                              f"inside the shared baseline; found {path_text}")
            if entry.get("source_mode") == generate_fixtures.LOCAL_BYTE_EXACT_COPY:
                if not canonical.is_file() or raw != canonical.read_bytes():
                    errors.append(f"pilot source {aid}: {path_text} is not byte-identical to "
                                  f"{entry.get('canonical_path')}")
            if digest(raw) != entry.get("declared_sha256") \
                    or len(raw) != entry.get("declared_byte_size"):
                errors.append(f"pilot source {aid}: {path_text} no longer holds the bytes the "
                              "manifest declares")
            if path_text not in generated:
                errors.append(f"pilot source {aid}: {path_text} is declared baseline content but "
                              "the generator does not emit it")
        expected_local = len(generate_fixtures.mirrored_assessment_ids())
        if local_copy_count != expected_local:
            errors.append(f"manifest reports {local_copy_count} LOCAL_BYTE_EXACT_COPY members; "
                          f"the generator derives {expected_local}")
        expected_pilot = len(generate_fixtures.PILOT_SOURCE_IDS)
        if baseline_pilot_source_count != expected_pilot:
            errors.append(f"the manifest declares {baseline_pilot_source_count} baseline pilot "
                          f"sources; the generator derives {expected_pilot}")
        for aid in generate_fixtures.mirrored_assessment_ids():
            for suffix in (".json", ".md"):
                mirror = generate_fixtures.BASELINE_ASSESSMENT_DIR / f"{aid}{suffix}"
                if not mirror.is_file():
                    errors.append(f"{aid}{suffix}: mirrored member is missing its baseline file")
                else:
                    baseline_file_count += 1
    else:
        baseline_pilot_source_count = 0

    # ---- 3. declared reference resolution ------------------------------------------------
    index = generate_fixtures.build_index()
    specs = {spec["fixture"]: spec for spec in generate_fixtures.SPECS}
    absent_report = []
    non_target_missing_total = 0
    for fixture in index["fixtures"]:
        name = fixture["fixture"]
        spec = specs[name]
        declared = declared_members(spec)
        if not declared:
            errors.append(f"{name}: declares no assessment_files path map")
            continue
        fixture_directory = generate_fixtures.fixture_dir(name)
        shadowed = generate_fixtures.shadowed_member_ids(spec)
        expected_members = len(generate_fixtures.canonical_assessment_ids()) \
            - len(generate_fixtures.withdrawn_assessment_ids(spec))
        if len(declared) != expected_members:
            errors.append(f"{name}: declares {len(declared)} member paths; canonical membership "
                          f"less withdrawals is {expected_members}")
        absent_here = []
        for aid, declared_path in sorted(declared.items()):
            resolved = (fixture_directory / declared_path).resolve()
            if not resolved.is_file():
                absent_here.append((aid, declared_path))
                continue
            if aid in shadowed:
                if declared_path != f"assessments/{aid}.json":
                    errors.append(f"{name}: {aid} is a fixture-local shadow but is declared at "
                                  f"{declared_path}")
            else:
                mode = fingerprint_modes.get(aid)
                if mode == generate_fixtures.LOCAL_BYTE_EXACT_COPY \
                        and not declared_path.startswith("../_baseline/assessments/"):
                    errors.append(f"{name}: {aid} is {mode} in the manifest but is declared at "
                                  f"{declared_path}")
                if mode == generate_fixtures.CANONICAL_DIRECT_DECLARATION \
                        and not declared_path.startswith(
                            "../../../academy-data/jimeng/assessment/full-assessments/"
                            "assessments/"):
                    errors.append(f"{name}: {aid} is {mode} in the manifest but is declared at "
                                  f"{declared_path}")
            canonical = generate_fixtures.CANONICAL_DIR / f"{aid}.json"
            # A shadowed member is the fixture's own mutated pair, so it is deliberately NOT the
            # canonical bytes; every other declared path must be.
            if aid not in shadowed and resolved.read_bytes() != canonical.read_bytes():
                errors.append(f"{name}: declared path {declared_path} for {aid} is not "
                              "byte-identical to the canonical member")
            try:
                payload = json.loads(read_text(resolved))
            except ValueError as exc:
                errors.append(f"{name}: declared path {declared_path} is unreadable JSON: {exc}")
                continue
            if payload.get("assessment_id") != aid:
                errors.append(f"{name}: declared path {declared_path} does not declare "
                              f"assessment_id {aid}")
        if absent_here:
            absent_report.append((name, absent_here))
            if name != MISSING_FILE_FIXTURE:
                errors.append(f"{name}: declares absent member path(s) {absent_here}")
            if len(absent_here) != 1:
                errors.append(f"{name}: declares {len(absent_here)} absent member paths; expected "
                              "exactly 1")
            elif absent_here[0][0] != generate_fixtures.MISSING_ASSESSMENT_FILE_ID:
                errors.append(f"{name}: absent member {absent_here[0][0]} is not the selected "
                              f"target {generate_fixtures.MISSING_ASSESSMENT_FILE_ID}")
            present = [aid for aid in declared if aid not in {a for a, _ in absent_here}]
            for aid in present:
                if not (fixture_directory / declared[aid]).resolve().is_file():
                    non_target_missing_total += 1
        else:
            if name == MISSING_FILE_FIXTURE:
                errors.append(f"{name}: no declared member path is physically absent; the literal "
                              "physical-absence sub-case is not exercised")
            for aid, declared_path in sorted(declared.items()):
                if not (fixture_directory / declared_path).resolve().is_file():
                    non_target_missing_total += 1
                    errors.append(f"{name}: NON_TARGET_DECLARED_PATH_MISSING: {aid} "
                                  f"{declared_path}")
    if len(absent_report) != 1 or absent_report[0][0] != MISSING_FILE_FIXTURE:
        errors.append("exactly one fixture (the declared-reference fixture) must declare exactly "
                      f"one absent member path; found {absent_report}")

    # ---- 4. four-way agreement -----------------------------------------------------------
    declared_map_signature = {}
    mutation_descriptor_text = {}
    for fixture in index["fixtures"]:
        name = fixture["fixture"]
        spec = specs[name]
        descriptor_path = ROOT / fixture["mutation_descriptor"]
        if not descriptor_path.is_file():
            errors.append(f"{name}: mutation descriptor missing")
            continue
        payload = json.loads(read_text(descriptor_path))
        mutation_descriptor_text[name] = read_text(descriptor_path)
        expected_descriptor = json.loads(
            generate_fixtures.dumps(generate_fixtures.mutation_descriptor(spec)))
        if payload != expected_descriptor:
            errors.append(f"{name}: descriptor differs from SPECS")
        if payload.get("base_coverage_manifest") != generate_fixtures.CANONICAL_COVERAGE_REL:
            errors.append(f"{name}: descriptor base_coverage_manifest differs from canonical "
                          "coverage truth")
        if payload.get("note") != fixture["intended_defect"]:
            errors.append(f"{name}: descriptor note differs from SPECS")
        for path in fixture["files"]:
            if not (ROOT / path).is_file():
                errors.append(f"{name}: declared file missing: {path}")
        declared_map = (payload.get("set_manifest") or {}).get("set", {}).get("assessment_files")
        if not isinstance(declared_map, dict):
            errors.append(f"{name}: descriptor carries no declared assessment_files map")
            continue
        if declared_map != spec["declared_paths"]:
            errors.append(f"{name}: descriptor declared path map differs from SPECS")
        declared_map_signature[name] = dict(declared_map)

    for name, declared_map in declared_map_signature.items():
        for aid, path in declared_map.items():
            if aid in generate_fixtures.shadowed_member_ids(specs[name]):
                continue
            mode = fingerprint_modes.get(aid)
            if mode == generate_fixtures.LOCAL_BYTE_EXACT_COPY \
                    and not path.startswith("../_baseline/assessments/"):
                errors.append(f"{name}: {aid} is {mode} in the manifest but declared at {path}")
            if mode == generate_fixtures.CANONICAL_DIRECT_DECLARATION \
                    and path.startswith("../_baseline/assessments/"):
                errors.append(f"{name}: {aid} is {mode} in the manifest but declared at the "
                              f"baseline mirror {path}")

    persisted_index = ROOT / "tests/full-assessment-set/_index.json"
    if not persisted_index.is_file():
        errors.append("_index.json: missing")
    else:
        same, reason = equal(read_text(persisted_index),
                             generate_fixtures.dumps(generate_fixtures.index_record()),
                             "_index.json")
        if not same:
            errors.append(f"_index.json: {reason}")
        try:
            persisted = json.loads(read_text(persisted_index))
        except ValueError as exc:
            errors.append(f"_index.json: unreadable JSON: {exc}")
            persisted = {}
        baseline_block = persisted.get("baseline") or {}
        if baseline_block.get("fingerprint") != fingerprint_rel:
            errors.append("_index.json: baseline fingerprint path differs from the generator")
        if baseline_block.get("legal_source_modes") != list(generate_fixtures.LEGAL_SOURCE_MODES):
            errors.append("_index.json: baseline legal_source_modes differ from the generator")

    # ---- 5. declared fixture-local pilot overlays -----------------------------------------
    # A fixture-local pilot source set is a DECLARED_FIXTURE_LOCAL_PILOT_OVERLAY only when the
    # generator derives it, the fixture's SPECS file inventory declares it and the fixture's
    # mutation descriptor still carries it as an active input.  The classification bug this closes
    # is the blanket "any fixture-local pilot source is superseded debris" rule: a pilot-source copy
    # that baseline-fingerprint.json / SPECS / the mutation descriptor still declare is legitimate
    # fixture content, so only an UNDECLARED copy could ever be debris.
    overlay_file_count = 0
    for spec in generate_fixtures.SPECS:
        name = spec["fixture"]
        declared_overlays = sorted(entry for entry in spec["files"]
                                   if entry.startswith("pilot-sources/"))
        if not declared_overlays:
            continue
        descriptor_text = mutation_descriptor_text.get(name, "")
        try:
            descriptor_keys = set(json.loads(descriptor_text)) if descriptor_text else set()
        except ValueError:
            descriptor_keys = set()
        declared_input_dirs = set()
        for key, value in sorted((spec.get("inputs") or {}).items()):
            if key != "--pilot-sources" or value in (None, ""):
                continue
            declared_input_dirs.add(str(value).rstrip("/"))
        if not declared_input_dirs:
            errors.append(f"{name}: emits pilot-source overlays but SPECS declares no "
                          "--pilot-sources input for it")
        for required_key in ("set_manifest",):
            if required_key not in descriptor_keys:
                errors.append(f"{name}: its mutation descriptor carries no {required_key}, so the "
                              "pilot-source input has no declared manifest to mutate")
        for entry in declared_overlays:
            rel_path = f"tests/full-assessment-set/{name}/{entry}"
            if rel_path not in generated:
                errors.append(f"{name}: declares {entry} but the generator emits no such overlay")
                continue
            if not (ROOT / rel_path).is_file():
                errors.append(f"{name}: declared overlay {entry} is missing from the tree")
                continue
            if (ROOT / rel_path).read_bytes() != generated[rel_path].encode("utf-8"):
                errors.append(f"{name}: overlay {entry} is not the bytes the generator derives")
                continue
            overlay_file_count += 1
        mutated_ids = {change["assessment_id"] for change in spec.get("pilot_sources") or []}
        pilot_overlay_specs[name] = {
            "declared_files": declared_overlays,
            "declared_input_dirs": sorted(declared_input_dirs),
            "mutated_pilot_ids": sorted(mutated_ids),
        }
        for change in spec.get("pilot_sources") or []:
            aid = change["assessment_id"]
            rel_path = f"tests/full-assessment-set/{name}/pilot-sources/{aid}.json"
            canonical = generate_fixtures.PILOT_DIR / f"{aid}.json"
            if not canonical.is_file():
                errors.append(f"{name}: mutated pilot source {aid} has no canonical original")
                continue
            try:
                overlay = json.loads(read_text(ROOT / rel_path))
            except ValueError as exc:
                errors.append(f"{name}: pilot overlay {aid} is unreadable JSON: {exc}")
                continue
            if not isinstance(overlay, dict):
                errors.append(f"{name}: pilot overlay {aid} is not a JSON object")
                continue
            base = json.loads(read_text(canonical))
            # `pilot_source_bytes` already returns the serialized artifact text, which is exactly
            # what `fixture_files` persists, so the derived document is parsed straight from it.
            derived = json.loads(generate_fixtures.pilot_source_bytes(spec, aid))
            if overlay != derived:
                errors.append(f"{name}: pilot overlay {aid} is not the declared derived artifact")
                continue
            keys = sorted(set(base) | set(overlay))
            drift = [key for key in keys if base.get(key) != overlay.get(key)]
            notes.append(f"PILOT_OVERLAY_DRIFT: {name} {aid} drifting_keys={drift}")
            if drift != ["scope"]:
                errors.append(f"{name}: pilot overlay {aid} drifts in {drift}; the declared "
                              "PILOT_PROMOTION_FIDELITY defect is a scope-only drift")
            if overlay.get("status") != "pilot":
                errors.append(f"{name}: pilot overlay {aid} no longer declares pilot status")
            if base.get("status") != "pilot":
                errors.append(f"{name}: canonical pilot original {aid} is not in pilot status")

    # ---- 6. inventory / orphan audit ------------------------------------------------------
    # Build the known-active reference universe from repository truth and the generator, not from
    # a hand-written allow list.
    claimed = set(generated) | set(HARNESS_SOURCES)
    index_artifacts = set()
    for fixture in index["fixtures"]:
        index_artifacts.update(fixture["files"])
        index_artifacts.add(fixture["mutation_descriptor"])
    # SPECS' own file inventory is active fixture content even when the fixture's inputs section
    # does not consume it at run time (a fixture-local pilot overlay prepared for a run that reads
    # canonical pilot truth instead is declared fixture content, not inert debt).
    specs_artifacts = set()
    for spec in generate_fixtures.SPECS:
        for entry in spec["files"]:
            specs_artifacts.add(f"tests/full-assessment-set/{spec['fixture']}/{entry}")
    declared_artifacts = index_artifacts | specs_artifacts
    specs_declared_paths = {aid: path for spec in generate_fixtures.SPECS
                            for aid, path in declared_members(spec).items()}

    active_baseline_files = set()
    for rel_path in sorted(baseline_internal_paths):
        if (ROOT / rel_path).is_file():
            active_baseline_files.add(rel_path)

    debt_document = load_hygiene_debt(errors)
    debt_by_path = {}
    for entry in debt_document["entries"]:
        rel_path = entry.get("relative_path")
        if not isinstance(rel_path, str) or not rel_path:
            errors.append(f"{HYGIENE_DEBT_REL}: entry without a relative_path: {entry!r}")
            continue
        if rel_path in debt_by_path:
            errors.append(f"{HYGIENE_DEBT_REL}: {rel_path} is registered more than once")
            continue
        debt_by_path[rel_path] = entry
    external_paths = set()
    for entry in debt_document["external_hygiene_debt"]:
        rel_path = entry.get("relative_path")
        if not isinstance(rel_path, str) or not rel_path:
            errors.append(f"{HYGIENE_DEBT_REL}: external entry without a relative_path: "
                          f"{entry!r}")
            continue
        external_paths.add(rel_path)
        if rel_path.startswith("tests/full-assessment-set/"):
            errors.append(f"{rel_path}: registered as external hygiene debt but it lives inside "
                          "the fixture tree and must be audited there")

    # The proof of inertness, re-derived per entry rather than trusted from the register.
    proof_source_text = "\n".join(read_text(ROOT / path) for path in PROOF_SOURCES)
    canonical_ids = set(generate_fixtures.canonical_assessment_ids())
    for rel_path, entry in sorted(debt_by_path.items()):
        target = ROOT / rel_path
        if not target.is_file():
            errors.append(f"{rel_path}: registered as hygiene debt but the file does not exist "
                          "(HYGIENE_DEBT_NOT_INERT)")
            continue
        raw = target.read_bytes()
        if entry.get("classification") != HYGIENE_DEBT_CLASSIFICATION:
            errors.append(f"{rel_path}: hygiene-debt classification must be "
                          f"{HYGIENE_DEBT_CLASSIFICATION}; found {entry.get('classification')!r}")
        if digest(raw) != entry.get("sha256") or len(raw) != entry.get("byte_size"):
            errors.append(f"{rel_path}: registered sha256/byte_size no longer describe the file "
                          "(HYGIENE_DEBT_NOT_INERT)")
        if rel_path in declared_artifacts or rel_path in index_artifacts:
            errors.append(f"{rel_path}: a fixture's own file inventory declares this path "
                          "(HYGIENE_DEBT_NOT_INERT)")
        if rel_path in specs_declared_paths.values():
            errors.append(f"{rel_path}: SPECS declares this path as an active member reference "
                          "(HYGIENE_DEBT_NOT_INERT)")
        if rel_path in fingerprint_member_paths:
            errors.append(f"{rel_path}: baseline-fingerprint.json declares this path "
                          "(HYGIENE_DEBT_NOT_INERT)")
        if rel_path in active_baseline_files:
            errors.append(f"{rel_path}: counted as active baseline content "
                          "(HYGIENE_DEBT_NOT_INERT)")
        if rel_path in generated:
            errors.append(f"{rel_path}: the generator emits this path "
                          "(HYGIENE_DEBT_NOT_INERT)")
        if rel_path in external_paths:
            errors.append(f"{rel_path}: registered both in-tree and as external hygiene debt")
        # The tooling-source proof works on the file's own name.  An A-class leftover is named
        # after a live canonical assessment id, so a name match there would only re-find the
        # canonical member; those entries are proved inert above, by the fingerprint's own
        # declaration and by their absence from SPECS, the index and the generator.
        basename = rel_path.rsplit("/", 1)[-1]
        stem = basename.rsplit(".", 1)[0]
        if stem in canonical_ids:
            continue
        if re.search(TOKEN_BOUNDARY.format(re.escape(basename)), proof_source_text):
            errors.append(f"{rel_path}: the generator, runner or validator source still names this "
                          "file (HYGIENE_DEBT_NOT_INERT)")

    # The register must not be able to widen into a glob, and must never name an artifact the
    # generator produces.
    for rel_path in sorted(generated):
        if rel_path in debt_by_path:
            errors.append(f"{rel_path}: a generated artifact is registered as hygiene debt")

    hygiene_entries = []
    fixture_content_entries = []
    overlay_entries = []
    baseline_content_entries = []
    undeclared = []
    classification_of = {}
    for item in sorted(FIXTURE_ROOT.rglob("*")):
        if not item.is_file():
            continue
        rel = item.relative_to(ROOT).as_posix()
        if rel in debt_by_path:
            classification_of[rel] = HYGIENE_DEBT_CLASSIFICATION
            hygiene_entries.append(rel)
        elif rel in active_baseline_files:
            classification_of[rel] = "ACTIVE_BASELINE_CONTENT"
            baseline_content_entries.append(rel)
        elif "/pilot-sources/" in rel and rel in specs_artifacts:
            classification_of[rel] = "DECLARED_FIXTURE_LOCAL_PILOT_OVERLAY"
            overlay_entries.append(rel)
        elif rel in generated or rel in declared_artifacts or rel in claimed:
            classification_of[rel] = "DECLARED_FIXTURE_CONTENT"
            fixture_content_entries.append(rel)
        else:
            # A path that is neither an active artifact nor a strictly registered, individually
            # re-proved inert entry is exactly UNDECLARED_ORPHAN.  A pilot-source copy inside a
            # fixture directory whose fixture never declares it lands here, and is never silently
            # exempted by a pattern.
            classification_of[rel] = "UNDECLARED_ORPHAN"
            undeclared.append(rel)

    # The five classes partition the tree: every file has exactly one class, and no file is both
    # active content and registered debt.
    if len(classification_of) != (len(hygiene_entries) + len(baseline_content_entries)
                                  + len(overlay_entries) + len(fixture_content_entries)
                                  + len(undeclared)):
        errors.append("the inventory classes do not partition the tree")
    for rel in hygiene_entries:
        if rel in fixture_content_entries or rel in baseline_content_entries \
                or rel in overlay_entries:
            errors.append(f"{rel}: classified as both hygiene debt and active content")
    for rel in overlay_entries:
        if rel not in generated:
            errors.append(f"{rel}: SPECS declares a fixture-local pilot overlay the generator "
                          "does not emit")
    if len(overlay_entries) != overlay_file_count:
        errors.append(f"the SPECS inventory declares {len(overlay_entries)} fixture-local "
                      f"pilot-source overlays; {overlay_file_count} were re-proved against the "
                      "generator")

    for rel in sorted(debt_by_path):
        notes.append(f"HYGIENE_DEBT: {debt_by_path[rel].get('reason', '')[:60]} {rel}")
    for rel in undeclared:
        errors.append(f"{rel}: unexpected orphan file (UNDECLARED_ORPHAN)")

    # ---- report --------------------------------------------------------------------------
    print("FAIL" if errors else "PASS")
    for error in errors:
        print("- FIXTURE_FIDELITY: " + error)
    print(f"BASELINE_FILE_COUNT: {baseline_file_count}")
    print(f"ACTIVE_BASELINE_FILE_COUNT: {len(active_baseline_files)}")
    print(f"DECLARED_INERT_BASELINE_DEBT_FILE_COUNT: "
          f"{sum(1 for rel in debt_by_path if rel.startswith(BASELINE_ASSESSMENT_PREFIX))}")
    raw_baseline_directory_count = 0
    if generate_fixtures.BASELINE_DIR.is_dir():
        raw_baseline_directory_count = sum(
            1 for item in generate_fixtures.BASELINE_DIR.rglob("*") if item.is_file())
    print(f"RAW_BASELINE_DIRECTORY_FILE_COUNT: {raw_baseline_directory_count}")
    print(f"FINGERPRINT_DECLARED_PATH_COUNT: {len(fingerprint_member_paths)}")
    print(f"CANONICAL_DIRECT_DECLARED_PATH_COUNT: "
          f"{len(fingerprint_member_paths) - len(active_baseline_files)}")
    print(f"BASELINE_PILOT_SOURCE_COUNT: {baseline_pilot_source_count}")
    print(f"LOCAL_BYTE_EXACT_COPY_MEMBER_COUNT: {local_copy_count}")
    print(f"LOCAL_BYTE_EXACT_COPY_FILE_COUNT_CHECKED: {local_files_checked}")
    print(f"CANONICAL_DIRECT_DECLARATION_MEMBER_COUNT: {canonical_direct_count}")
    print(f"CANONICAL_DIRECT_DECLARATION_FILE_COUNT_CHECKED: {canonical_direct_files_checked}")
    print(f"DECLARED_REFERENCE_ABSENT_FIXTURE_COUNT: {len(absent_report)}")
    for name, absent in absent_report:
        for aid, declared_path in absent:
            print(f"ABSENT_DECLARED_PATH: {name} {aid} {declared_path}")
    print(f"NON_TARGET_DECLARED_PATH_MISSING_COUNT: {non_target_missing_total}")
    active_fixture_content = sum(1 for rel in classification_of
                                 if classification_of[rel] == "DECLARED_FIXTURE_CONTENT")
    print(f"DECLARED_FIXTURE_CONTENT_FILE_COUNT: {active_fixture_content}")
    print(f"DECLARED_FIXTURE_LOCAL_PILOT_OVERLAY_FILE_COUNT: {len(overlay_entries)}")
    print(f"ACTIVE_BASELINE_CONTENT_FILE_COUNT: {len(baseline_content_entries)}")
    print(f"INVENTORY_CLASSIFIED_FILE_COUNT: {len(classification_of)}")
    print(f"HYGIENE_DEBT_FILE_COUNT: {len(hygiene_entries)}")
    print(f"IN_TREE_HYGIENE_DEBT_FILE_COUNT: {len(debt_by_path)}")
    print(f"EXTERNAL_HYGIENE_DEBT_FILE_COUNT: {len(external_paths)}")
    print(f"LEGACY_ARTIFACT_FILE_COUNT: "
          f"{sum(1 for rel in debt_by_path if 'PRE_HYBRID_BASELINE_MIRROR' in str(debt_by_path[rel].get('reason', '')))}")
    for rel, extra in sorted(pilot_overlay_specs.items()):
        print(f"PILOT_OVERLAY_DECLARATION: {rel} files={len(extra['declared_files'])} "
              f"declared_inputs={extra['declared_input_dirs']} "
              f"mutated_pilot_ids={extra['mutated_pilot_ids']}")
    for note in notes:
        print("- " + note)
    print(f"ORPHAN_FILE_COUNT: {len(undeclared)}")
    print(f"FIXTURE_FIDELITY_ERROR_COUNT: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
