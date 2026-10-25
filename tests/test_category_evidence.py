"""Read real recordings and failed/successful calls; this never runs inference."""
import json
from pathlib import Path
import sys
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/category-realization-20261025"
sys.path.insert(0, str(ROOT / "services/speech"))
from category_validation import compare_probe


class CategoryEvidence(unittest.TestCase):
    def test_fresh_acoustic_regeneration_positive(self):
        directory = OUT / "regeneration-check/recordings/pronunciation.segmental.consonant_substitution"
        record = json.loads((directory / "index.json").read_text())
        self.assertEqual(record["origin"], "fresh_native_generation_from_committed_authored_plan")
        self.assertNotEqual((ROOT / record["paths"]["clean"]).read_bytes(), (ROOT / record["paths"]["mutated"]).read_bytes())
        native = json.loads((directory / "source/response.json").read_text())["receipt"]["native"]
        self.assertTrue(native["model_visible_calls"])
        self.assertTrue(native["paired_mutations"])
        self.assertEqual(record["paths"]["clean"], record["paths"]["misleading_metadata"])

    def test_fresh_acoustic_cache_negative(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("category_acoustic_saved", ROOT / "audit/category-realization-20261025/generate_acoustic.py")
        generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
        directory = OUT / "regeneration-check/recordings/pronunciation.segmental.consonant_substitution"
        result = generator.generate_case("pronunciation.segmental.consonant_substitution", directory, lambda *args: self.fail("A saved read must not render"), ROOT)
        self.assertEqual(result["origin"], "fresh_native_generation_from_committed_authored_plan")

    def test_real_recordings_positive(self):
        fixtures = json.loads((ROOT / "audit/category-realization-20261025/FIXTURES.json").read_text())["fixtures"]
        expected = [r for r in fixtures if r["render_kind"] == "text"]
        self.assertGreater(len(expected), 80)
        for fixture in expected:
            directory = OUT / "recordings" / fixture["taxonomy_id"]
            index = json.loads((directory / "index.json").read_text())
            self.assertEqual(index["paths"]["clean"], index["paths"]["misleading_metadata"])
            for role in ("clean", "mutated", "acceptable"):
                with wave.open(str(ROOT / index["paths"][role])) as audio:
                    self.assertEqual((audio.getframerate(), audio.getnchannels(), audio.getsampwidth()), (24000, 1, 2))
                    self.assertGreater(audio.getnframes(), 2400)
                native = json.loads((directory / role / "response.json").read_text())
                self.assertEqual(native["receipt"]["provider"], "local_kokoro")
                self.assertTrue(native["receipt"]["native"]["model_visible_calls"])
        pitch = OUT / "recordings/pronunciation.suprasegmental.pitch_range"
        actual_ranges = []
        for role in ("clean", "mutated"):
            observed = json.loads((pitch / ("measured-" + role) / "response.json").read_text())
            self.assertEqual(observed["receipt"]["inference_calls"], 0)
            actual_ranges.append(float(next(r["numeric_value"] for r in observed["measurements"] if r["feature"] == "f0_range_semitones")))
        self.assertGreater(actual_ranges[1] / actual_ranges[0], 1.6)
        self.assertLess(actual_ranges[1] / actual_ranges[0], 2.5)
        interaction = OUT / "recordings/discourse.turn_taking"
        scene = json.loads((interaction / "index.json").read_text())
        self.assertIn("not rendered or qualified", scene["unimplemented_variant"])
        self.assertEqual(len(scene["binding"]["voice"]), 2)
        for role, expected_speakers in (("clean", ["a", "b"]), ("mutated", ["a", "b", "a"]), ("acceptable", ["a", "b", "a"])):
            timings = json.loads((interaction / (role + "-timing.json")).read_text())
            self.assertEqual([r["speaker"] for r in timings], expected_speakers)
            self.assertTrue(all(a["end"] < b["start"] for a, b in zip(timings, timings[1:])))
            with wave.open(str(ROOT / scene["paths"][role])) as audio:
                self.assertGreater(audio.getnframes(), timings[-1]["end"])

    def test_blind_actual_observation_positive(self):
        directory = OUT / "observations-gemini31/grammar.determiners.article_omission"
        observation = json.loads((directory / "readmitted-response.json").read_text())
        probe = json.loads((directory / "withheld.json").read_text())
        self.assertEqual(observation["wire"]["http_status"], 200)
        self.assertEqual(observation["wire"]["profile"]["billing_mode"], "free_tier")
        self.assertEqual(compare_probe(probe, observation)["audio_confirmation"], "confirmed")
        text = observation["wire"]["request"]["input"][0]["text"]
        self.assertNotIn("expected", text)
        self.assertNotIn("claimed_mutation", text)
        self.assertNotIn("article_omission", text)
        self.assertEqual(len([r for r in observation["wire"]["request"]["input"] if r["type"] == "audio"]), 4)

    def test_actual_unrealized_contrast_negative(self):
        directory = OUT / "observations-gemini31/grammar.determiners.article_choice"
        result = json.loads((directory / "comparison.json").read_text())
        self.assertEqual(result["audio_confirmation"], "not_realized")
        target = next(r for r in result["cases"] if r["role"] == "mutated")
        self.assertEqual((target["expected"], target["actual"], target["outcome"]), ("supported", "contradicted", "failed"))
        self.assertTrue(result["controls_passed"])

    def test_actual_provider_failure_negative(self):
        directory = OUT / "observations-configured/grammar.determiners.article_omission"
        original = json.loads((directory / "response.json").read_text())
        result = json.loads((directory / "comparison.json").read_text())
        self.assertEqual(original["wire"]["http_status"], 503)
        self.assertNotEqual(result["audio_confirmation"], "confirmed")
        self.assertEqual(original["error"], "DIAGNOSTIC_PROVIDER_FAILED")
        admitted_failure = json.loads((OUT / "observations-gemini31/grammar.nouns.number/response.json").read_text())
        self.assertEqual(admitted_failure["wire"]["http_status"], 503)
        self.assertEqual(admitted_failure["receipt"]["inference_calls"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
