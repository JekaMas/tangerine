"""Iteration-local evidence bookkeeping, never a product admission/quality gate.

The ledger deliberately separates executable literal bindings, partial retained
assertions, candidate successors, and still-unobserved original obligations.
"""
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CHANGE = "openspec/changes/implement-teacher-error-trainer"
BASELINE = "ab91a998903f537c6c57e6875a85e5943d54a3b9"
HERE = Path(__file__).resolve().parent
CATEGORY_ACTION = "Replay the declared design mutation or request its declared acoustic transformation, then map a localized answer and clean control"
sys.path.insert(0, str(ROOT / ".agents/workflow/scripts"))
from requirement_tests import parse_go_events, parse_unittest_events


@lru_cache(maxsize=1)
def accepted_scope_revision():
    """Keep this dated reconciliation historical after later product work.

    A change to its own code/ledger/observations selects the current scope again.
    Acceptance/report bookkeeping and unrelated product commits do not undo it.
    """
    path = HERE / "ACCEPTANCE.json"
    if not path.is_file():
        return None
    revision = json.loads(path.read_text())["tested_revision"]
    for relative in ["tests/test_completion_i31.py",
                     "audit/iteration-31-reconciliation-20261027/reconcile.py",
                     "audit/iteration-31-reconciliation-20261027/LEDGER.json",
                     "audit/iteration-31-reconciliation-20261027/OBSERVATIONS.json"]:
        observed = subprocess.check_output(["git", "show", revision + ":" + relative], cwd=ROOT)
        if observed != (ROOT / relative).read_bytes():
            return None
    return revision


def scope_source(path):
    revision = accepted_scope_revision()
    return (subprocess.check_output(["git", "show", revision + ":" + path], cwd=ROOT)
            if revision else (ROOT / path).read_bytes())


@lru_cache(maxsize=None)
def frozen(path):
    return json.loads(subprocess.check_output(["git", "show", BASELINE + ":" + path],
                                             cwd=ROOT, text=True))


@lru_cache(maxsize=1)
def original_cases():
    return {c["id"]: c for c in frozen(CHANGE + "/verification.json")["cases"]
            if c["state"] != "implemented"}


@lru_cache(maxsize=1)
def original_bindings():
    return {r["case_id"]: r for r in frozen(
        "specification/v2/domain/verification-fixtures.v1.json")["case_bindings"]}


@lru_cache(maxsize=1)
def auxiliary_literal_ids():
    return {x["case_id"] for x in json.loads((ROOT / "services/api/internal/scoring/testdata/historical-auxiliary.json").read_text())}

def _test_binding(method, source, command, *, proof):
    return dict(test_id=method, source_path=source, command_id=command, proof=proof)


def _py(method):
    return _test_binding("unittest::tests.test_historical_literals.HistoricalLiterals." + method,
                "tests/test_historical_literals.py", "i31-arithmetic-literals",
                proof="Existing exact registry arithmetic over the original literal counters; no semantic, participant, acoustic or provider claim.")


def _observer(method):
    return _test_binding("unittest::tests.test_completion_i31.CompletionI31." + method,
                "tests/test_completion_i31.py", "completion-i31",
                proof="Exact union of unchanged independently observed literal components, or actual existing evidence-runner behavior; no new product execution.")


def _native(method, package="app"):
    return _test_binding("tangerine.local/api/internal/" + package + "::" + method,
                "services/api/internal/" + package + "/historical_literals_test.go", "i31-aux-counterexamples" if package=="scoring" and ".SET2.NEGATIVE" in method else "i31-go-literals",
                proof="Actual native owner on the original labelled constructed text/population; no model, actual participant or speech measurement.")


def literal_binding(cid, b):
    if cid in {f"MET-{n:02d}.P1.SET2.{p}" for n in range(1, 28) for p in ["POSITIVE", "NEGATIVE"]}:
        return _py("test_core_set2_" + b["polarity"])
    if cid in auxiliary_literal_ids():
        return _native("TestHistoricalAuxiliary" + b["polarity"].title() + "/" + cid, "scoring")
    if b["mode"] == "evidence_scope":
        return _observer("test_unobserved_scope_positive" if b["polarity"] == "positive" else "test_static_summary_not_execution_negative")
    fixture = b["fixture_id"]
    if fixture in ["exact-ratio", "set2-DOM-05.P1-positive", "set2-DOM-05.P2-positive"]:
        if b["mode"] == "contract_pair":
            return _observer("test_ratio_pair_" + b["polarity"])
        if b["input"] in [dict(numerator="1", denominator="3"), dict(numerator="3", denominator="4")]:
            return _py("test_ratio_positive")
        if b["input"] == dict(numerator=True, denominator=3.0):
            return _observer("test_ratio_pair_positive") if b["polarity"] == "positive" else _py("test_ratio_invalid_negative")
    if fixture == "unicode":
        if b["mode"] == "contract_pair":
            return _observer("test_unicode_pair_" + b["polarity"])
        if b["input"] == dict(answer="🙂 work; work", target=dict(start_cp=8, end_cp=12, exact_text="work")):
            return _native("TestHistoricalUnicodePositive")
        if b["input"] == dict(answer="🙂 work; work", target=dict(start_cp=9, end_cp=13, exact_text="work")):
            return _observer("test_unicode_pair_positive") if b["polarity"] == "positive" else _native("TestHistoricalUnicodeNegative")
    if fixture == "mutation-replay":
        if b["input"] == dict(canonical="She works here.", edits=[dict(start_cp=8,end_cp=9,exact_text="s",replacement="")]):
            return _native("TestHistoricalMutationPositive")
        if b["input"] == dict(canonical="She works here.", surface="She work there.", edits=[dict(start_cp=8,end_cp=9,exact_text="s",replacement="")]):
            return _observer("test_mutation_rejection_positive") if b["polarity"] == "positive" else _native("TestHistoricalMutationNegative")
    return None


def ledger_errors(packet, graph):
    """Check the exact inspected population and declared proof joins only."""
    errors = []
    original, bindings = original_cases(), original_bindings()
    current = {c["id"]: c for c in graph["cases"]}
    rows = packet.get("cases", [])
    ids = [r.get("case_id") for r in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(original):
        errors.append("original case population changed")
    for row in rows:
        cid = row.get("case_id")
        if cid not in original:
            continue
        old, now = original[cid], current.get(cid, {})
        if row.get("property_id") != old["property_id"] or cid not in current:
            errors.append(cid + " original identity changed")
        if row.get("original_state") != old["state"]:
            errors.append(cid + " history changed")
        if row.get("original_test_id") != old["test_id"]:
            errors.append(cid + " original test identity changed")
        binding = bindings[cid]
        if row.get("fixture_id") != binding["fixture_id"]:
            errors.append(cid + " different fixture")
        if row.get("original_expected") != binding["expected"]:
            errors.append(cid + " different independent expectations")
        for k in ["property_id", "polarity", "scenario", "scenario_fingerprint"]:
            if now.get(k) != old[k]:
                errors.append(cid + " original " + k + " changed")
        disposition = row.get("disposition")
        if disposition == "materialized_literal":
            owner = row.get("literal_test", {})
            expected = literal_binding(cid, binding)
            if not expected or any(owner.get(k) != expected[k]
                                   for k in ["test_id", "command_id", "source_path"]):
                errors.append(cid + " unrelated original-literal binding")
            if not owner or now.get("state") != "implemented":
                errors.append(cid + " missing literal implementation")
            for k in ["test_id", "command_id", "source_path"]:
                if not owner.get(k) or now.get(k) != owner.get(k):
                    errors.append(cid + " incorrect literal " + k)
            if row.get("remaining_assertions"):
                errors.append(cid + " partial evidence promoted")
        elif disposition in ["partial_exact_reuse", "literal_observation_missing",
                             "conditional_population_or_qualification", "fixture_conflict"]:
            if now.get("state") == "implemented" or not row.get("remaining_assertions"):
                errors.append(cid + " unmet original promoted")
            expected_state = "blocked" if disposition in ["conditional_population_or_qualification", "fixture_conflict"] else "planned"
            if now.get("state") != expected_state:
                errors.append(cid + " stale or unsupported execution blocker")
            if "Specification-only authority" in now.get("blocker", ""):
                errors.append(cid + " stale authority blocker")
            if now.get("reconciliation") != "audit/iteration-31-reconciliation-20261027/LEDGER.json#" + cid:
                errors.append(cid + " missing canonical ledger association")
        else:
            errors.append(cid + " unknown disposition")
        for reuse in row.get("partial_evidence", []):
            if binding["action"] != CATEGORY_ACTION:
                errors.append(cid + " a shared category ID does not prove this unrelated operation")
            candidate = current.get(reuse.get("case_id"), {})
            leaf = binding["input"].get("leaf")
            methods = {"LF-01.P1.TestLinguisticContextPositive.": "context",
                       "LF-03.P1.TestLinguisticRecipePositive.": "recipe"}
            kind = next((kind for prefix, kind in methods.items()
                         if leaf and reuse.get("case_id") == prefix + leaf), None)
            if not kind or reuse.get("test_id") != candidate.get("test_id"):
                errors.append(cid + " unrelated category/operation component")
            if kind == "recipe":
                reference = linguistic_references().get(leaf, {})
                if any(binding["input"].get(k) != reference.get(k)
                       for k in ["canonical", "surface"]):
                    errors.append(cid + " different original recipe text")
            if candidate.get("state") != "implemented" or not reuse.get("assertion"):
                errors.append(cid + " unsupported partial assertion")
            if reuse.get("proves_entire_original_case") is not False:
                errors.append(cid + " unproved whole-case reuse")
            if not reuse.get("receipt") or not reuse.get("test_id"):
                errors.append(cid + " missing actual retained observation")
            receipt_path = reuse.get("command_receipt")
            if not receipt_path or not (ROOT / receipt_path).is_file() or command_receipt(receipt_path).get("exit_code") != 0:
                errors.append(cid + " missing successful retained command")
        if not row.get("comparison") or not row.get("owner"):
            errors.append(cid + " comparison/owner absent")
    # Existing accepted physical tests/commands are untouched. Adding new edges
    # does not refresh their source identity or silently rerun their owner.
    for old in frozen(CHANGE + "/verification.json")["cases"]:
        if old["state"] == "implemented" and current.get(old["id"]) != old:
            errors.append(old["id"] + " prior accepted case changed")
    return errors


@lru_cache(maxsize=1)
def linguistic_references():
    return {x["taxonomy_id"]: x for x in json.loads(scope_source(
        "services/api/internal/app/testdata/linguistic-contrasts.json"))["examples"]}


def observation_packet_errors(packet):
    """The original literal obligations own the required observation population."""
    # This diagnostic observes the two open contradictory fixtures. It never
    # satisfies or closes them, but its retained result is part of I31's claim.
    expected = {_py("test_ratio_historical_inconsistent_vector_negative")["test_id"]}
    for cid in original_cases():
        binding = literal_binding(cid, original_bindings()[cid])
        if binding and binding["command_id"] != "completion-i31":
            identity = binding["test_id"]
            expected.add(identity)
            namespace, method = identity.split("::", 1)
            if "/" in method:
                expected.add(namespace + "::" + method.split("/", 1)[0])
    required = packet.get("required_tests", {})
    declared = {test for tests in required.values() for test in tests}
    errors = []
    if declared != expected:
        errors.append("original literal observation population omitted or substituted")
    records = packet.get("commands", [])
    ids = [record.get("id") for record in records]
    if len(ids) != len(set(ids)) or set(ids) != set(required):
        errors.append("observation command association changed")
    for record in records:
        tests = required.get(record.get("id"), [])
        if not tests:
            errors.append("empty physical observation scope")
        errors.extend(observation_errors(record, tests))
    return errors


@lru_cache(maxsize=None)
def command_receipt(path):
    return json.loads((ROOT / path).read_text())


def command_receipt_errors(record):
    """Read the actual executed receipt once; packet labels cannot change it."""
    path = record.get("command_receipt")
    if not path or not (ROOT / path).is_file():
        return ["actual command receipt unavailable"]
    receipt = command_receipt(path)
    if "commands" in receipt:
        matches = [c for c in receipt["commands"]
                   if c["id"] == record.get("receipt_command_id")]
        if len(matches) != 1:
            return ["actual command association changed"]
        actual = matches[0]
        actual_output = Path(actual["stdout_artifact"])
        revision, dirty = receipt["git"]["head"], receipt["git"]["dirty"]
    else:
        # Original five-method Python tool transcript, explicitly dirty.
        actual = receipt
        actual_output = ROOT / actual["retained_output"]
        revision, dirty = actual["tested_revision"], actual["dirty_at_execution"]
    errors = []
    for key in ["argv", "exit_code", "observed_tests"]:
        if record.get(key) != actual.get(key):
            errors.append("actual command " + key + " changed")
    if (ROOT / record.get("retained_output", "")).resolve() != actual_output.resolve():
        errors.append("actual command output replaced")
    if (record.get("tested_revision"), record.get("dirty_at_execution")) != (revision, dirty):
        errors.append("actual command execution provenance changed")
    return errors


def observation_errors(record, expected_tests):
    """Actual typed observations, not report labels/counts, own a retained pass."""
    errors = command_receipt_errors(record)
    subset = record.get("retained_pass_subset", [])
    if record.get("exit_code") != 0 and not (record.get("exit_code") == 1 and subset):
        errors.append("command did not exit zero")
    observed = record.get("observed_tests", {})
    for test in expected_tests:
        if observed.get(test) != "pass":
            errors.append("missing passed exact observation " + test)
    if not record.get("retained_output") or not (ROOT / record["retained_output"]).is_file():
        errors.append("native output unavailable")
    else:
        raw = (ROOT / record["retained_output"]).read_text()
        parsed = (parse_go_events if record.get("runner") == "go-test-json"
                  else parse_unittest_events)(raw)
        for test in expected_tests:
            if parsed.get(test) != "pass":
                errors.append("retained native output does not observe " + test)
        if record.get("exit_code") == 1 and subset:
            failed = {test for test, status in parsed.items() if status != "pass"}
            if set(record.get("failed_sibling_tests", [])) != failed or not failed:
                errors.append("failed sibling accounting changed")
            if not set(expected_tests) <= set(subset):
                errors.append("unobserved failure promoted as an independent pass")
            resolution = record.get("sibling_resolution", {})
            path = ROOT / resolution.get("retained_output", "")
            if resolution.get("exit_code") != 0 or not path.is_file():
                errors.append("failed siblings remain unresolved")
            else:
                resolved = parse_go_events(path.read_text())
                if any(resolved.get(test) != "pass" for test in failed):
                    errors.append("directed repair did not pass every failed sibling")
    if not record.get("source_bindings"):
        errors.append("executed sources unbound")
    for binding in record.get("source_bindings", []):
        if not isinstance(binding, dict) or not binding.get("path") or not binding.get("sha256"):
            errors.append("executed source identity absent")
        elif not (ROOT / binding["path"]).is_file() and not accepted_scope_revision():
            errors.append("executed source missing " + binding["path"])
        elif source_digest(binding["path"]) != binding["sha256"]:
            # A changed file is not automatically a changed tested path. Keep
            # the ORIGINAL hash, the explicitly reviewed new hash, the exact
            # unaffected identities and the source-diff explanation separately.
            reviews = record.get("source_reuse_reviews", [])
            matches = [v for v in reviews if v.get("path") == binding["path"]
                       and v.get("tested_sha256") == binding["sha256"]
                       and v.get("reviewed_current_sha256") == source_digest(binding["path"])
                       and set(expected_tests) <= set(v.get("unchanged_test_ids", []))
                       and v.get("reason") and (ROOT / v.get("reference", "")).is_file()]
            if len(matches) != 1:
                errors.append("executed source changed " + binding["path"])
    if record.get("new_provider_calls") != 0:
        errors.append("unselected provider execution")
    return errors


@lru_cache(maxsize=None)
def source_digest(path):
    # One source observation per development-check process; never application
    # reads, corpus reads or a repeated accepted-data boundary check.
    return hashlib.sha256(scope_source(path)).hexdigest()


def counts(packet):
    return dict(Counter(r["disposition"] for r in packet["cases"]))


def discovery_history_errors(current, prior):
    reviews = {review["id"]: review for review in current["reviews"]}
    return [review["id"] + " prior review rewritten" for review in prior["reviews"]
            if reviews.get(review["id"]) != review]
