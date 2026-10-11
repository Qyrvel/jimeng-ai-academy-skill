"""Run every tests/course-evaluation/ fixture and compare it with its declared expectation.

Usage:
  python .agents/skills/ai-academy/scripts/run_course_evaluation_fixtures.py [fixture-name ...]
  python .agents/skills/ai-academy/scripts/run_course_evaluation_fixtures.py --verbose

For each fixture the runner:

  1. materialises the fixture snapshot from `tests/course-evaluation/fixture_declarations.py`
     plus the frozen course manifest (the fixture is SPEC-derived, never a stored observation),
  2. runs `evaluate_course_completion.py` as a subprocess and records exit code, verdict, every
     attributed diagnostic code and (when the snapshot is legal) the parsed evaluation result,
  3. runs `validate_course_evaluation.py` as a subprocess on the same snapshot -- for a legal
     snapshot the engine's own result is streamed in as `--evaluation`, so the validator must
     independently confirm the engine's aggregation, routing and derived metrics,
  4. compares everything with the fixture's declaration.

Both inputs travel on stdin (`--stdin`), because the sandbox forbids writes outside the session
workspace and this runner must not create temporary files.

Strict declared-code policy (mirrors tests/full-assessment-set/run_fixtures.py)
-----------------------------------------------------------------------------
A fixture is a MATCH only when all of these hold:

    required_codes  <=  observed_codes
    observed_codes  <=  (required_codes | companion_codes)
    engine exit     ==  declared engine exit
    validator exit  ==  declared validator exit
    every observed diagnostic head is attributed to a known diagnostic code

An observed code that no declaration allows is an UNEXPECTED code and makes the fixture a
MISMATCH; `MATCH` next to `UNEXPECTED codes` is not a reachable state.  The runner never trusts
the declared expectation alone and never edits an expectation to match an observation.
"""

import ast
import io
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FIXTURE_ROOT = ROOT / "tests/course-evaluation"
SCRIPTS = ROOT / ".agents/skills/ai-academy/scripts"
ENGINE = SCRIPTS / "evaluate_course_completion.py"
VALIDATOR = SCRIPTS / "validate_course_evaluation.py"
CONTRACT = ROOT / "academy-data/jimeng/assessment/course-evaluation/course-evaluation-contract.json"
MASTERY = ROOT / "academy-data/jimeng/assessment/mastery-map.json"
MANIFEST = ROOT / "academy-data/jimeng/course/jimeng-creator-academy-v1/course-manifest.json"
GRAPHS = [
    ROOT / "academy-data/jimeng/graph/seedance-pilot-graph-r2.json",
    ROOT / "academy-data/jimeng/graph/policy-pilot-graph-r1.json",
    ROOT / "academy-data/jimeng/graph/curriculum-readiness-core-graph-r2.json",
]

sys.path.insert(0, str(FIXTURE_ROOT))
import fixture_declarations  # noqa: E402

COURSE_BRANCHES = ("COMPLETE", "RETRY_REQUIRED", "REMEDIATION_REQUIRED", "BLOCKED")
SEVERITY = {"RETRY_REQUIRED": 1, "REMEDIATION_REQUIRED": 2, "BLOCKED": 3}

# Tokens that are enum values, verdict words or relation names, never diagnostics.
NON_CODE_TOKENS = {
    "PASS", "FAIL", "COMPLETE", "RETRY_REQUIRED", "REMEDIATION_REQUIRED", "BLOCKED",
    "RETRY", "REMEDIATION", "PREREQUISITE_OF", "PROCEDURE_PRECEDES", "APPLICABLE",
    "NOT_APPLICABLE", "COURSE", "FAILED", "GRADUATED", "FINAL_GRADE",
}

# Report heads that carry their value inline: an all-caps or all-lowercase single token.
# Diagnostic codes always carry a message, so they never match this shape.
STATIC_HEAD = re.compile(r"^(?:[A-Z][A-Z0-9_]*|[a-z][a-z0-9_]*)$")

# The validator marks every verdict report field with this prefix, so a field label can never be
# mistaken for a diagnostic code even when the two share a name.
FIELD_PREFIX = "REPORT_"


def uppercase_constants(path):
    """Every all-caps underscore string constant in a tool's source, from the AST."""
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    tokens = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value.strip()
            if text and text.isupper() and " " not in text and len(text) > 3 \
                    and text.replace("_", "").isalnum():
                tokens.add(text)
    return tokens


def string_texts(node):
    """Every literal text a Constant/JoinedStr node can produce (an f-string yields its parts).

    Whitespace is collapsed to single ordinary spaces: one report label in the engine contains an
    em-space, and a detector that only recognises U+0020 silently loses it.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        yield " ".join(node.value.split())
    elif isinstance(node, ast.JoinedStr):
        for value in node.values:
            for text in string_texts(value):
                yield text


def is_report_label(stripped_text):
    """`- LABEL:` or `- LABEL: value` where LABEL is one unspaced token that is not all-caps.

    Diagnostic codes are always all-caps, so requiring a non-all-caps token keeps an f-string
    report label (`- RETRY_TARGETS: {...}`) out of the diagnostic code set while still
    recognising it as a known head.
    """
    if not stripped_text.startswith("- "):
        return None
    rest = stripped_text[2:]
    if ":" not in rest:
        return None
    head = rest.split(":", 1)[0].strip()
    if not head or " " in head or head.isupper():
        return None
    return head


def report_labels(path):
    """Report-field labels a tool prints as `- LABEL: ...` on its verdict report lines."""
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    labels = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "print" and node.args):
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            texts = [first.value]
        elif isinstance(first, ast.JoinedStr):
            texts = list(string_texts(first))
        else:
            texts = []
        for text in texts:
            head = is_report_label(text.strip())
            if head:
                labels.add(head)
    return labels


def call_name(node):
    """`name(...)` -> 'name'; `obj.name(...)` -> 'name'."""
    if not isinstance(node, ast.Call):
        return None
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def module_string_constants(tree):
    """Module-level `NAME = "VALUE"` bindings, so `findings.fail(CONST, ...)` is resolvable."""
    table = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    table[target.id] = node.value.value
    return table


def tool_tokens(path):
    """(diagnostic codes, known non-code tokens) read from a tool's own call sites.

    Diagnostic codes are the string literals raised or failed with -- `SnapshotError("CODE", ...)`,
    `findings.fail("CODE", ...)` and `findings.fail(MODULE_CONSTANT, ...)`.  Everything else the
    tool can print as a `- HEAD:` line is a report-field label or an enum value, not a code; a
    head that is neither is unattributed.
    """
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    constants = module_string_constants(tree)
    codes, others = set(), set()
    for node in ast.walk(tree):
        name = call_name(node)
        if name not in ("SnapshotError", "fail", "field", "emit") or not node.args:
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            token = first.value
        elif isinstance(first, ast.Name) and first.id in constants:
            token = constants[first.id]
        else:
            continue
        if name in ("SnapshotError", "fail"):
            codes.add(token)
        else:
            others.add(token)
    others |= report_labels(path)
    others |= uppercase_constants(path)
    others |= NON_CODE_TOKENS
    return codes, others


ENGINE_CODES, ENGINE_KNOWN = tool_tokens(ENGINE)
VALIDATOR_CODES, VALIDATOR_KNOWN = tool_tokens(VALIDATOR)
ALL_CODES = ENGINE_CODES | VALIDATOR_CODES


def read_json(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def lesson_order():
    manifest = read_json(MANIFEST)
    return [lid for module in manifest["module_order"]
            for lid in manifest["lesson_order_by_module"][module]]


def diagnostic_heads(stdout):
    """Heads of the diagnostic lines (`- HEAD: message`) printed after the verdict line.

    A diagnostic always carries a non-empty message after the colon.  A verdict report line
    carries a JSON value instead -- always a quoted string, an array, an object, a number or a
    boolean -- so it is never mistaken for a code even when its label is all-caps.
    """
    heads = []
    for line in stdout.splitlines()[1:]:
        if line.startswith("- ") and ": " in line:
            head, value = line[2:].split(": ", 1)
            if value[:1] in ('"', "[", "{") or " " in value:
                heads.append(head.strip())
    return heads


def classify(heads, codes, known):
    """Split diagnostic heads into attributed codes and unattributed heads.

    A head is attributed when it is a known diagnostic code of that tool, when it is a known
    static report field of that tool, or when it is the first token of an engine report line that
    carries its value inline (`- module_statuses: {...}`).  Anything else is unattributed and is
    reported as such rather than silently dropped.
    """
    observed, unattributed = [], []
    for head in heads:
        if head in codes:
            observed.append(head)
        elif head in known or head.startswith(FIELD_PREFIX) or STATIC_HEAD.match(head):
            continue
        else:
            unattributed.append(head)
    return sorted(set(observed)), sorted(set(unattributed))


def run(argv, stdin_text=None):
    proc = subprocess.run([sys.executable, "-X", "utf8", *[str(a) for a in argv]],
                          cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=600, input=stdin_text)
    return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()


def parse_evaluation(stdout):
    """The engine prints its result as a JSON document after the PASS report lines."""
    lines = stdout.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("{"):
            try:
                blob = json.loads("\n".join(lines[index:]))
            except ValueError:
                return None
            return blob.get("evaluation")
    return None


def evaluate_fixture(name, snapshot):
    spec = fixture_declarations.FIXTURES[name]
    declared_valid = bool(spec.get("valid"))
    required = sorted(spec.get("declared_codes") or [])
    companion = sorted(spec.get("companion_codes") or [])
    snapshot_text = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"

    engine_code, engine_out, engine_err = run(
        [ENGINE, CONTRACT, "-", MASTERY, MANIFEST, *GRAPHS, "--stdin", "--json"],
        stdin_text=snapshot_text)
    engine_codes, engine_unattributed = classify(diagnostic_heads(engine_out),
                                                 ENGINE_CODES, ENGINE_KNOWN)
    evaluation = parse_evaluation(engine_out)

    if evaluation is not None:
        validator_stdin = json.dumps({"snapshot": snapshot, "evaluation": evaluation},
                                     ensure_ascii=False)
        validator_argv = [VALIDATOR, CONTRACT, "-", MASTERY, MANIFEST, *GRAPHS, "--stdin",
                          "--evaluation", "-"]
    else:
        validator_stdin = snapshot_text
        validator_argv = [VALIDATOR, CONTRACT, "-", MASTERY, MANIFEST, *GRAPHS, "--stdin"]
    validator_code, validator_out, validator_err = run(validator_argv, stdin_text=validator_stdin)
    validator_codes, validator_unattributed = classify(diagnostic_heads(validator_out),
                                                       VALIDATOR_CODES, VALIDATOR_KNOWN)
    unattributed = sorted(set(engine_unattributed) | set(validator_unattributed))

    expected_engine_exit = 0 if declared_valid else 1
    expected_validator_exit = 0 if declared_valid else 1
    allowed = set(required) | set(companion)
    observed = set(engine_codes) | set(validator_codes)
    missing = sorted(set(required) - observed)
    unexpected = sorted(observed - allowed)

    problems = []
    if engine_code != expected_engine_exit:
        problems.append(f"engine exit {engine_code} != declared {expected_engine_exit}")
    if validator_code != expected_validator_exit:
        problems.append(f"validator exit {validator_code} != declared {expected_validator_exit}")
    if missing:
        problems.append(f"missing required codes {missing}")
    if unexpected:
        problems.append(f"UNEXPECTED codes {unexpected}")
    if unattributed:
        problems.append(f"UNATTRIBUTED diagnostic heads {sorted(set(unattributed))}")

    course_status = None
    modules_reached = []
    routing_present = {}
    lossless = None
    if declared_valid:
        if evaluation is None:
            problems.append("a legal snapshot produced no parseable evaluation result")
        else:
            course_status = evaluation.get("course_status")
            modules_reached = sorted(set((evaluation.get("module_statuses") or {}).values()))
            routing_present = {key: bool(evaluation.get(key)) for key in
                               ("retry_targets", "remediation_targets", "blocked_targets",
                                "blocked_by_mastery_units")}
            if course_status not in COURSE_BRANCHES:
                problems.append(f"course_status {course_status!r} outside the course enum")
            present_severity = sorted({SEVERITY[s] for s in
                                       ("RETRY_REQUIRED" if routing_present["retry_targets"] else None,
                                        "REMEDIATION_REQUIRED"
                                        if routing_present["remediation_targets"] else None,
                                        "BLOCKED" if routing_present["blocked_targets"] else None)
                                       if s})
            if course_status == "COMPLETE":
                lossless = not present_severity
                for key, present in routing_present.items():
                    if present:
                        problems.append(f"COMPLETE course carries non-empty {key}")
            else:
                # the headline status is the highest severity present, and the other real routing
                # sets are still carried: the routing is lossless
                lossless = bool(present_severity) \
                    and present_severity[-1] == SEVERITY.get(course_status)
                if not lossless:
                    problems.append(
                        f"course_status {course_status} does not match the severities present in "
                        "the routing sets")
            if evaluation.get("track_results"):
                problems.append("evaluation carries synthetic track results")
    else:
        # An illegal snapshot must never be reported as a legal course result.  A structural
        # failure is allowed to carry an evaluation object only when the engine itself flags the
        # result as INCONSISTENT_EVALUATION_SNAPSHOT.
        if evaluation is not None \
                and evaluation.get("course_status") != "INCONSISTENT_EVALUATION_SNAPSHOT":
            problems.append("an illegal snapshot produced a legal course result")

    return {
        "fixture": name,
        "declared_valid": declared_valid,
        "declared_codes": required,
        "companion_codes": companion,
        "engine_exit": engine_code,
        "engine_verdict": engine_out.splitlines()[0] if engine_out else "",
        "engine_codes": engine_codes,
        "validator_exit": validator_code,
        "validator_verdict": validator_out.splitlines()[0] if validator_out else "",
        "validator_codes": validator_codes,
        "observed_codes": sorted(observed),
        "missing_codes": missing,
        "unexpected_codes": unexpected,
        "unattributed_heads": sorted(set(unattributed)),
        "course_status": course_status,
        "module_statuses_reached": modules_reached,
        "routing_present": routing_present,
        "lossless": lossless,
        "problems": problems,
        "engine_stderr": engine_err[:200],
        "validator_stderr": validator_err[:200],
        "verdict": "MATCH" if not problems else "MISMATCH",
    }


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    verbose = "--verbose" in args
    wanted = [a for a in args if not a.startswith("--")]
    order = lesson_order()
    names = [n for n in fixture_declarations.ORDER if not wanted or n in wanted]

    results = [evaluate_fixture(name, fixture_declarations.materialise(name, order))
               for name in names]

    matched = sum(1 for r in results if r["verdict"] == "MATCH")
    unexpected_fixtures = sum(1 for r in results if r["unexpected_codes"])
    mismatches = [r for r in results if r["verdict"] != "MATCH"]
    course_branches = sorted({r["course_status"] for r in results if r["course_status"]})
    module_branches = sorted({m for r in results for m in r["module_statuses_reached"]})
    covered_invalid = {
        axis: any(r["fixture"] == fixture and r["declared_valid"] is False
                  and r["verdict"] == "MATCH"
                  for r in results)
        for axis, fixture in fixture_declarations.REQUIRED_INVALID_CASES.items()}
    mixed_names = ("valid-retry-plus-remediation", "valid-remediation-plus-blocked",
                   "valid-retry-remediation-blocked")
    mixed_ok = []
    for item in results:
        if item["fixture"] not in mixed_names or item["verdict"] != "MATCH":
            continue
        present = item["routing_present"]
        # each mixed fixture must really carry the state combination it claims
        if "retry-plus-remediation" in item["fixture"]:
            ok = present.get("retry_targets") and present.get("remediation_targets") \
                and not present.get("blocked_targets")
        elif "remediation-plus-blocked" in item["fixture"]:
            ok = present.get("remediation_targets") and present.get("blocked_targets") \
                and item["course_status"] == "BLOCKED"
        else:
            ok = present.get("retry_targets") and present.get("remediation_targets") \
                and present.get("blocked_targets") and item["course_status"] == "BLOCKED"
        if ok and item["lossless"]:
            mixed_ok.append(item)

    for item in results:
        print(f"FIXTURE: {item['fixture']}")
        print(f"  engine exit: {item['engine_exit']}  verdict: {item['engine_verdict']}")
        print(f"  validator exit: {item['validator_exit']}  verdict: {item['validator_verdict']}")
        print(f"  required codes: {item['declared_codes']}")
        if item["companion_codes"]:
            print(f"  allowed companion codes: {item['companion_codes']}")
        print(f"  observed codes: {item['observed_codes']}")
        if item["missing_codes"]:
            print(f"  MISSING required codes: {item['missing_codes']}")
        if item["unexpected_codes"]:
            print(f"  UNEXPECTED codes: {item['unexpected_codes']}")
        if item["unattributed_heads"]:
            print(f"  UNATTRIBUTED diagnostic heads: {item['unattributed_heads']}")
        if item["course_status"]:
            print(f"  course_status: {item['course_status']}")
            print(f"  module statuses reached: {item['module_statuses_reached']}")
        for problem in item["problems"]:
            print(f"  PROBLEM: {problem}")
        print(f"  verdict: {item['verdict']}")
        if verbose and item["engine_stderr"]:
            print(f"  engine stderr: {item['engine_stderr']}")
        if verbose and item["validator_stderr"]:
            print(f"  validator stderr: {item['validator_stderr']}")

    print(f"COURSE_EVALUATION_FIXTURE_COUNT: {len(results)}")
    print(f"COURSE_EVALUATION_FIXTURE_EXPECTATION_MATCH_COUNT: {matched}")
    print(f"FIXTURE_EXPECTATION_MISMATCH_COUNT: {len(mismatches)}")
    print(f"UNEXPECTED_CODE_FIXTURE_COUNT: {unexpected_fixtures}")
    print(f"COURSE_DECISION_BRANCH_REACHABILITY: {len(course_branches)} / 4")
    print(f"COURSE_DECISION_BRANCHES: {course_branches}")
    print(f"MODULE_DECISION_BRANCH_REACHABILITY: {len(module_branches)} / 4")
    print(f"MODULE_DECISION_BRANCHES: {module_branches}")
    print(f"MIXED_STATE_PRECEDENCE_CASE_COUNT: {len(mixed_ok)}")
    print(f"INVALID_SNAPSHOT_REQUIRED_CASE_COVERAGE: "
          f"{sum(1 for v in covered_invalid.values() if v)} / "
          f"{len(fixture_declarations.REQUIRED_INVALID_CASES)}")
    for axis, ok in sorted(covered_invalid.items()):
        print(f"  INVALID_AXIS {axis}: {'COVERED' if ok else 'NOT_COVERED'}")
    print(f"CRITICAL_COURSE_EVALUATION_FIXTURES: "
          f"{'PASS' if matched == len(results) else 'FAIL'}")
    return 0 if matched == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
