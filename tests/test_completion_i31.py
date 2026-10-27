"""I31: original literal joins, native observations and honest residual scope.

No product/provider/browser operation is run here. This command reuses actual
physical literal-test outputs; it never repeats those accepted executions.
"""
import copy
from functools import lru_cache
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "audit/iteration-31-reconciliation-20261027"
sys.path.insert(0, str(HERE))
import reconcile
from requirement_tests import EvidenceGraph, load_observed_statuses
from discovery_ledger import validate as validate_discovery, DiscoveryError


def read(path):
    return json.loads((ROOT / path).read_text())


def ledger():
    return read("audit/iteration-31-reconciliation-20261027/LEDGER.json")


def graph():
    return read(reconcile.CHANGE + "/verification.json")


class CompletionI31(unittest.TestCase):
    def test_population_positive(self):
        packet = ledger()
        self.assertEqual(1909, len(packet["cases"]))
        self.assertEqual(389, len({x["property_id"] for x in packet["cases"]}))
        self.assertEqual([], reconcile.ledger_errors(packet, graph()))

    def test_population_omission_negative(self):
        for action in ["drop", "duplicate", "replace"]:
            packet = ledger()
            if action == "drop":
                packet["cases"].pop()
            elif action == "duplicate":
                packet["cases"][-1] = packet["cases"][0]
            else:
                packet["cases"][-1]["case_id"] = "COV-999.P1.S1.POSITIVE"
            with self.subTest(action=action):
                self.assertTrue(reconcile.ledger_errors(packet, graph()))

    def test_expected_literal_change_negative(self):
        packet = ledger()
        packet["cases"][0]["original_expected"] = {"all_features": "passed"}
        self.assertTrue(reconcile.ledger_errors(packet, graph()))
        packet = ledger()
        packet["cases"][0]["fixture_id"] = "a-different-easier-fixture"
        self.assertTrue(reconcile.ledger_errors(packet, graph()))

    def test_partial_promotion_negative(self):
        packet, current = ledger(), graph()
        row = next(r for r in packet["cases"] if r["disposition"] == "partial_exact_reuse")
        next(c for c in current["cases"] if c["id"] == row["case_id"])["state"] = "implemented"
        self.assertTrue(reconcile.ledger_errors(packet, current))
        row["partial_evidence"][0]["proves_entire_original_case"] = True
        self.assertTrue(reconcile.ledger_errors(packet, current))

    def test_test_identity_negative(self):
        packet = ledger()
        row = next(r for r in packet["cases"] if r["disposition"] == "materialized_literal")
        row["literal_test"]["test_id"] = "unittest::unrelated.SameCount.test_pass"
        self.assertTrue(reconcile.ledger_errors(packet, graph()))
        packet = ledger()
        packet["cases"][0]["original_test_id"] = "a rewritten historical identity"
        self.assertTrue(reconcile.ledger_errors(packet, graph()))

    def test_discovery_aliases_positive(self):
        self.assertEqual("passed", validate_discovery(ROOT, "implement-teacher-error-trainer")["status"])
        current = read(reconcile.CHANGE + "/discovery.json")
        prior = reconcile.frozen(reconcile.CHANGE + "/discovery.json")
        known = {c["test_id"] for c in graph()["cases"]}
        self.assertFalse(set(current["scope"]["test_ids"]) - known)
        for before in [prior["scope"]] + prior["reviews"]:
            after = current["scope"] if "id" not in before else next(r for r in current["reviews"] if r["id"] == before["id"])
            self.assertFalse(set(before["test_ids"]) - set(after["test_ids"]) - set(after.get("historical_test_ids", [])))

    def test_retired_discovery_identity_negative(self):
        # Test-owned miniature registration, not a rewrite of the real change.
        directory = ROOT / "data/iteration-31-reconciliation-20261027"
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="discovery-", dir=directory) as tmp:
            root = Path(tmp)
            change = root / "openspec/changes/fixture"
            change.mkdir(parents=True)
            (change / "verification.json").write_text(json.dumps({"properties": [{"id": "P1"}], "cases": [{"test_id": "current::literal"}]}))
            review = copy.deepcopy(next(r for r in read(reconcile.CHANGE + "/discovery.json")["reviews"] if r["id"] == "iteration31-literal-reconciliation-20261027"))
            review["property_ids"], review["test_ids"] = ["P1"], ["current::literal"]
            value = {"schema_version": 1, "change": "fixture", "scope": {"property_ids": ["P1"], "test_ids": ["current::literal"]}, "reviews": [review]}
            path = change / "discovery.json"
            path.write_text(json.dumps(value))
            self.assertEqual("passed", validate_discovery(root, "fixture")["status"])
            value["scope"]["test_ids"].append("planned::retired::literal")
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(DiscoveryError, "unknown scoped tests"):
                validate_discovery(root, "fixture")

    def test_prior_accepted_case_rewrite_negative(self):
        current = graph()
        row = next(c for c in current["cases"] if c["id"] not in reconcile.original_cases())
        row["green_expectation"] = "a refreshed hash is equivalent to original evidence"
        self.assertTrue(reconcile.ledger_errors(ledger(), current))

    def test_false_external_blocker_negative(self):
        packet, current = ledger(), graph()
        row = next(r for r in packet["cases"] if r["disposition"] == "literal_observation_missing")
        case = next(c for c in current["cases"] if c["id"] == row["case_id"])
        case["state"] = "blocked"
        case["blocker"] = "Need a corpus, paid API or another product approval before this constructed fixture can run."
        self.assertTrue(reconcile.ledger_errors(packet, current))

    def test_product_sources_preserved_positive(self):
        import subprocess
        changed = subprocess.check_output(["git", "diff", "--name-only", reconcile.BASELINE,
                                           "--", "services", "domain", "specification/v2/domain",
                                           "specification/v2/contracts"], cwd=ROOT, text=True).splitlines()
        allowed = {"services/api/internal/app/historical_literals_test.go",
                   "services/api/internal/scoring/historical_literals_test.go",
                   "services/api/internal/scoring/testdata/historical-auxiliary.json"}
        self.assertFalse(set(changed) - allowed, changed)
        # These old reports remain finite/partial. I31 cannot manufacture the
        # missing Azure/Qwen/source/browser observation by changing a checkbox.
        for path in ["audit/all-iterations-remaining-20261027/ITERATIONS.json",
                     "audit/all-iterations-remaining-20261027/CATEGORIES.json"]:
            self.assertEqual(subprocess_text(path), (ROOT / path).read_text())

    def test_new_literal_observations_positive(self):
        packet = read("audit/iteration-31-reconciliation-20261027/OBSERVATIONS.json")
        required = packet["required_tests"]
        self.assertTrue(required)
        for record in packet["commands"]:
            expected = required[record["id"]]
            with self.subTest(command=record["id"]):
                self.assertEqual([], reconcile.observation_errors(record, expected))
        self.assertEqual(set(required), {r["id"] for r in packet["commands"]})

    def test_counterfeit_observation_negative(self):
        packet = read("audit/iteration-31-reconciliation-20261027/OBSERVATIONS.json")
        for record in packet["commands"]:
            expected = packet["required_tests"][record["id"]]
            for action in ["missing", "skip", "wrong_identity", "exit", "provider", "source_drift", "raw_summary"]:
                altered = copy.deepcopy(record)
                if action == "missing":
                    altered["observed_tests"].pop(expected[0])
                elif action == "skip":
                    altered["observed_tests"][expected[0]] = "skip"
                elif action == "wrong_identity":
                    altered["observed_tests"] = {"unrelated" + str(n): "pass" for n in range(len(expected))}
                elif action == "exit":
                    altered["exit_code"] = 1
                elif action == "provider":
                    altered["new_provider_calls"] = 1
                elif action == "source_drift":
                    altered["source_bindings"][0]["sha256"] = "0" * 64
                else:
                    altered["retained_output"] = "README.md"
                with self.subTest(command=record["id"], action=action):
                    self.assertTrue(reconcile.observation_errors(altered, expected))

    def test_retained_component_reuse_positive(self):
        packet = ledger()
        original = {c["id"]: c for c in reconcile.frozen(reconcile.CHANGE + "/verification.json")["cases"]}
        parsed = {}
        seen = set()
        for row in packet["cases"]:
            for retained in row["partial_evidence"]:
                identity = retained["case_id"]
                candidate = original[identity]
                path = ROOT / retained["receipt"]
                if path not in parsed:
                    parsed[path] = reconcile.parse_go_events(path.read_text())
                self.assertEqual(candidate["test_id"], retained["test_id"])
                self.assertEqual("pass", parsed[path].get(candidate["test_id"]))
                self.assertEqual(current_source(candidate["source_path"]),
                                 subprocess_text(candidate["source_path"]))
                self.assertFalse(retained["proves_entire_original_case"])
                seen.add(identity)
        self.assertTrue(seen)

    def test_missing_partial_receipt_negative(self):
        packet = ledger()
        row = next(r for r in packet["cases"] if r["partial_evidence"])
        row["partial_evidence"][0]["receipt"] = None
        self.assertTrue(reconcile.ledger_errors(packet, graph()))

    def test_unobserved_scope_positive(self):
        evidence_graph = EvidenceGraph(ROOT, "implement-teacher-error-trainer")
        rows = [r for r in reconcile.original_bindings().values()
                if r["case_id"] in reconcile.original_cases() and r["mode"] == "evidence_scope"
                and r["polarity"] == "positive"]
        self.assertEqual(50, len(rows))
        with temporary_receipt() as path:
            for row in rows:
                self.assertEqual(0, row["input"]["actual_behavior_runs"])
                self.assertEqual(400, row["input"]["static_checks"])
                self.assertFalse(row["expected"]["behavior_complete"])
                path.write_text(json.dumps({"change": evidence_graph.change, "status": "passed",
                                           "static_checks": 400, "actual_behavior_runs": 0, "cases": {}}))
                self.assertEqual({}, load_observed_statuses(evidence_graph, [path]))

    def test_static_summary_not_execution_negative(self):
        evidence_graph = EvidenceGraph(ROOT, "implement-teacher-error-trainer")
        rows = [r for r in reconcile.original_bindings().values()
                if r["case_id"] in reconcile.original_cases() and r["mode"] == "evidence_scope"
                and r["polarity"] == "negative"]
        self.assertEqual(50, len(rows))
        with temporary_receipt() as path:
            for row in rows:
                self.assertTrue(row["input"]["claim_behavior_complete"])
                self.assertFalse(row["expected"]["static_as_runtime"])
                cid = row["case_id"]
                path.write_text(json.dumps({"change": evidence_graph.change, "status": "passed",
                                           "static_checks": 400, "actual_behavior_runs": 0,
                                           "cases": {cid: {"status": "passed"}}}))
                self.assertEqual("stale", load_observed_statuses(evidence_graph, [path])[cid])

    def test_ratio_pair_positive(self):
        self.require_literal_receipts("unittest::tests.test_historical_literals.HistoricalLiterals.test_ratio_positive",
                                      "unittest::tests.test_historical_literals.HistoricalLiterals.test_ratio_invalid_negative")

    def test_ratio_pair_negative(self):
        self.require_literal_receipts("unittest::tests.test_historical_literals.HistoricalLiterals.test_ratio_invalid_negative",
                                      "unittest::tests.test_historical_literals.HistoricalLiterals.test_ratio_positive")

    def test_unicode_pair_positive(self):
        self.require_native_receipts("tangerine.local/api/internal/app::TestHistoricalUnicodePositive",
                                     "tangerine.local/api/internal/app::TestHistoricalUnicodeNegative")

    def test_unicode_pair_negative(self):
        self.require_native_receipts("tangerine.local/api/internal/app::TestHistoricalUnicodeNegative",
                                     "tangerine.local/api/internal/app::TestHistoricalUnicodePositive")

    def test_mutation_rejection_positive(self):
        self.require_native_receipts("tangerine.local/api/internal/app::TestHistoricalMutationNegative")

    def require_literal_receipts(self, *tests):
        packet = read("audit/iteration-31-reconciliation-20261027/OBSERVATIONS.json")
        record = next(r for r in packet["commands"] if r["id"] == "python-literals")
        self.assertEqual([], reconcile.observation_errors(record, tests))

    def require_native_receipts(self, *tests):
        packet = read("audit/iteration-31-reconciliation-20261027/OBSERVATIONS.json")
        record = next(r for r in packet["commands"] if r["id"] == "native-literals")
        self.assertEqual([], reconcile.observation_errors(record, tests))


@lru_cache(maxsize=None)
def subprocess_text(path):
    import subprocess
    return subprocess.check_output(["git", "show", reconcile.BASELINE + ":" + path], cwd=ROOT, text=True)


@lru_cache(maxsize=None)
def current_source(path):
    return (ROOT / path).read_text()


class temporary_receipt:
    def __enter__(self):
        directory = ROOT / "data/iteration-31-reconciliation-20261027"
        directory.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="scope-", dir=directory)
        return Path(self.tmp.name) / "constructed-static-result.json"

    def __exit__(self, *args):
        self.tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
