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
            if candidate.get("state") != "implemented" or not reuse.get("assertion"):
                errors.append(cid + " unsupported partial assertion")
            if reuse.get("proves_entire_original_case") is not False:
                errors.append(cid + " unproved whole-case reuse")
            if not reuse.get("receipt") or not reuse.get("test_id"):
                errors.append(cid + " missing actual retained observation")
        if not row.get("comparison") or not row.get("owner"):
            errors.append(cid + " comparison/owner absent")
    # Existing accepted physical tests/commands are untouched. Adding new edges
    # does not refresh their source identity or silently rerun their owner.
    for old in frozen(CHANGE + "/verification.json")["cases"]:
        if old["state"] == "implemented" and current.get(old["id"]) != old:
            errors.append(old["id"] + " prior accepted case changed")
    return errors


def observation_errors(record, expected_tests):
    """Actual typed observations, not report labels/counts, own a retained pass."""
    errors = []
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
