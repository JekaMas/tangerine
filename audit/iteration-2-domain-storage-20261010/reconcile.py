"""Reconcile retained clean native observations without rewriting their receipts.

This is an iteration-specific evidence audit, not a workflow runner or a new
application test. The only permitted stale requirement fingerprint is the exact
PER-01 -> SPEC-003 parent-reference correction recorded in TRACE-CORRECTION.json.
Every behavior, source, scenario, oracle and execution input must remain exact.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CHANGE = "implement-teacher-error-trainer"
AUDIT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "openspec/changes" / CHANGE / "evidence/iteration2"
sys.path.insert(0, str(ROOT / ".agents/workflow/scripts"))
from requirement_tests import (EvidenceGraph, canonical_json, command_key,
                               dependency_snapshot, parse_go_events,
                               parse_unittest_events)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode().strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def saved(commit, path):
    return subprocess.check_output(["git", "show", commit + ":" + path], cwd=ROOT)


def main():
    graph = EvidenceGraph(ROOT, CHANGE)
    current = git("rev-parse", "HEAD")
    correction = json.loads((AUDIT / "TRACE-CORRECTION.json").read_text())
    original = correction["old_native_candidate"]
    corrected = "f654b39986f8b6655b57c1481a84f0a9bbfe9a8a"
    properties = {f"I1-{i:02}.P1" for i in range(1, 9)} | {
        f"I2-{i:02}.P1" for i in range(1, 15)}
    selected = {cid: row for cid, row in graph.cases.items()
                if row["property_id"] in properties}
    assert len(selected) == 88
    assert not set(selected) & set(graph.substitution_gaps)
    manifest = "openspec/changes/" + CHANGE + "/verification.json"
    historical = {commit: json.loads(saved(commit, manifest))
                  for commit in (original, corrected)}
    for commit in (original, corrected):
        assert git("merge-base", "--is-ancestor", commit, current) == ""
        old = historical[commit]
        for category in ("cases", "properties", "commands"):
            rows = {row["id"]: row for row in old[category]}
            present = getattr(graph, category)
            ids = (selected if category == "cases" else properties
                   if category == "properties" else
                   {row["command_id"] for row in selected.values()})
            assert all(rows[key] == present[key] for key in ids), category
        # Current acceptance commits may change only records. The exact archive
        # and dependency payloads used by every native owner are checked below.
        changed = git("diff", "--name-only", commit, current).splitlines()
        assert not any(path.startswith(("services/", "tests/", "scripts/", "deploy/"))
                       or path in (".dockerignore", ".env.example") for path in changed)
    spec = "openspec/changes/" + CHANGE + "/specs/iteration-two-storage/spec.md"
    before = saved(original, spec).decode()
    after = saved(corrected, spec).decode()
    assert before.replace("PER-01", "SPEC-003") == after
    assert (ROOT / spec).read_text() == after

    sources = [EVIDENCE / "clean-full.json", EVIDENCE / "clean-storage.json"]
    reports = [json.loads(path.read_text()) for path in sources]
    assert reports[0]["git"] == {"status": "known", "dirty": False, "head": original}
    assert reports[1]["git"] == {"status": "known", "dirty": False, "head": corrected}
    assert reports[0]["status"] == "failed"  # Failed Docker startup stays failed.
    assert reports[1]["status"] == "passed"
    assert all(not report["substitution_gaps"] for report in reports)

    snapshots = {}
    results = {}
    native_checks = []
    for path, report in zip(sources, reports):
        commands = {row["id"]: row for row in report["commands"]}
        old_graph = historical[report["git"]["head"]]
        old_requirements = {row["id"]: row for row in old_graph["requirements"]}
        for command in commands.values():
            # Reparse the preserved, complete native log; do not trust status alone.
            stdout = (EVIDENCE / Path(command["stdout_artifact"]).name).read_text()
            stderr = (EVIDENCE / Path(command["stderr_artifact"]).name).read_text()
            runner = graph.commands[command["id"]]["runner"]
            observed = (parse_go_events(stdout) if runner == "go-test-json" else
                        parse_unittest_events(stdout + "\n" + stderr))
            assert observed == command["observed_tests"]
            if command["exit_code"] == 0:
                assert command["status"] == "exited"
                assert observed and set(observed.values()) == {"pass"}
                native_checks.append({"receipt": path.name, "command": command["id"],
                                      "observed_native_tests": len(observed),
                                      "all_native_tests_passed": True})
        for cid, observation in report["cases"].items():
            if observation["status"] != "passed":
                continue
            assert cid in selected and cid not in results
            case = selected[cid]
            assert case["state"] == "implemented"
            prop = graph.properties[case["property_id"]]
            command = commands[case["command_id"]]
            assert command["exit_code"] == 0 and command["status"] == "exited"
            assert command["argv"] == graph.commands[case["command_id"]]["argv"]
            assert command["observed_tests"][case["test_id"]] == "pass"
            for key in ("test_id", "property_id", "polarity", "scenario",
                        "scenario_fingerprint", "setup", "observable",
                        "red_expectation", "green_expectation",
                        "invalidation_dependencies", "source_path", "source_sha256"):
                assert observation[key] == case[key], (cid, key)
            assert digest(ROOT / case["source_path"]) == case["source_sha256"]
            patterns = tuple(case["invalidation_dependencies"])
            if patterns not in snapshots:
                snapshots[patterns] = dependency_snapshot(ROOT, list(patterns))
                for entries in snapshots[patterns].values():
                    for entry in entries:
                        for commit in (original, corrected):
                            assert hashlib.sha256(saved(commit, entry["path"])).hexdigest() == entry["sha256"]
            old_requirement = old_requirements[prop["requirement_id"]]
            requirement = graph.requirements[prop["requirement_id"]]
            if old_requirement != requirement:
                assert cid.startswith("I2-")
                assert {k: v for k, v in old_requirement.items() if k != "fingerprint"} == {
                    k: v for k, v in requirement.items() if k != "fingerprint"}
            fingerprint_payload = {
                "requirement_fingerprint": old_requirement["fingerprint"],
                "property": prop, "case": case,
                "execution": json.loads(command_key(graph.commands[case["command_id"]])),
                "runner": graph.commands[case["command_id"]]["runner"],
                "test_namespace": graph.commands[case["command_id"]].get("test_namespace"),
                "dependencies": snapshots[patterns]}
            assert hashlib.sha256(canonical_json(fingerprint_payload)).hexdigest() == observation["evidence_fingerprint"], cid
            results[cid] = {"status": "passed", "polarity": case["polarity"],
                            "test_id": case["test_id"], "receipt": path.name,
                            "observed_clean_commit": report["git"]["head"],
                            "original_evidence_fingerprint": observation["evidence_fingerprint"],
                            "unchanged_behavior_inputs_verified": True,
                            "parent_reference_correction_only": old_requirement != requirement}
    assert set(results) == set(selected)
    polarities = dict(Counter(row["polarity"] for row in results.values()))
    assert polarities == {"negative": 44, "positive": 44}
    output = {"status": "passed", "proof_boundary": "Iteration 2 storage and invalidated foundation closure only; no later provider, generation, speech or scoring semantics.",
              "candidate": corrected, "reconciled_at": current,
              "policy": "Retain valid clean native greens; rerun only unavailable or semantically invalidated cases. No receipt fingerprint is rewritten.",
              "required_cases": 88, "polarities": polarities,
              "native_checks": native_checks,
              "receipts": [{"path": path.relative_to(ROOT).as_posix(),
                            "sha256": digest(path), "original_status": report["status"]}
                           for path, report in zip(sources, reports)],
              "trace_correction": {"path": (AUDIT / "TRACE-CORRECTION.json").relative_to(ROOT).as_posix(),
                                   "sha256": digest(AUDIT / "TRACE-CORRECTION.json")},
              "cases": results}
    destination = EVIDENCE / "ACCEPTANCE.json"
    if sys.argv[1:] == ["--check"]:
        retained = json.loads(destination.read_text())
        assert git("merge-base", "--is-ancestor", retained["reconciled_at"], current) == ""
        assert {k: v for k, v in retained.items() if k != "reconciled_at"} == {
            k: v for k, v in output.items() if k != "reconciled_at"}
    else:
        assert not sys.argv[1:], "Use --check for a read-only correspondence audit."
        destination.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "passed", "required_cases": 88, "polarities": polarities,
                      "retained_clean": 36, "fresh_clean": 52}))


if __name__ == "__main__":
    main()
