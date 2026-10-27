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
sys.path.insert(0, str(ROOT / ".agents/workflow/scripts"))
from requirement_tests import parse_go_events, parse_unittest_events


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
    if record.get("exit_code") != 0:
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
    if not record.get("source_bindings"):
        errors.append("executed sources unbound")
    for binding in record.get("source_bindings", []):
        if not isinstance(binding, dict) or not binding.get("path") or not binding.get("sha256"):
            errors.append("executed source identity absent")
        elif not (ROOT / binding["path"]).is_file() or source_digest(binding["path"]) != binding["sha256"]:
            errors.append("executed source changed " + binding["path"])
    if record.get("new_provider_calls") != 0:
        errors.append("unselected provider execution")
    return errors


@lru_cache(maxsize=None)
def source_digest(path):
    # One source observation per development-check process; never application
    # reads, corpus reads or a repeated accepted-data boundary check.
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def counts(packet):
    return dict(Counter(r["disposition"] for r in packet["cases"]))
