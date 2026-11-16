import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("benchmark", Path(__file__).resolve().parents[1] / "scripts/benchmark.py")
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.answers = {"one": {"options": ["A", "B"], "choice": "A"}}

    def test_known_probability_score(self):
        result = benchmark.score(self.answers, {"one": {"probabilities": {"A": .8, "B": .2}}})
        self.assertEqual(result["choice_accuracy"], 1)
        self.assertAlmostEqual(result["multiclass_brier_sum"], .08)
        low, high = result["accuracy_wilson_95"]
        self.assertLess(low, .3)
        self.assertAlmostEqual(high, 1)

    def test_uniform_probabilities_with_explicit_tie_choice(self):
        result = benchmark.score(self.answers, {"one": {"choice": "B", "probabilities": {"A": .5, "B": .5}}})
        self.assertEqual(result["choice_accuracy"], 0)
        self.assertAlmostEqual(result["multiclass_brier_sum"], .5)

    def test_confident_error(self):
        result = benchmark.score(self.answers, {"one": {"probabilities": {"A": 0, "B": 1}}})
        self.assertEqual(result["choice_accuracy"], 0)
        self.assertEqual(result["multiclass_brier_sum"], 2)

    def test_rejects_missing_and_extra_cases(self):
        for predictions in ({}, {"other": {}}, {"one": {}, "extra": {}}):
            with self.assertRaises(ValueError):
                benchmark.score(self.answers, predictions)

    def test_rejects_invalid_probability_distributions(self):
        for probs in ({"A": .5, "B": .5}, {"A": .9, "B": .9}, {"A": float('nan'), "B": 1},
                      {"A": True, "B": 0}, {"A": -1, "B": 2}, {"A": 1}, {"A": None, "B": None}):
            with self.subTest(probs=probs), self.assertRaises(ValueError):
                benchmark.score(self.answers, {"one": {"probabilities": probs}})

    def test_rejects_unanswered_case(self):
        self.answers["one"]["choice"] = None
        with self.assertRaises(ValueError):
            benchmark.score(self.answers, {"one": {"probabilities": {"A": .8, "B": .2}}})

    def test_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.jsonl"
            path.write_text('{"id":"one"}\n{"id":"one"}\n')
            with self.assertRaises(ValueError):
                benchmark.load_records(path)

    def test_init_preserves_evidence_and_has_no_answers(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            benchmark.initialize(destination)
            answers = benchmark.load_records(destination / "answers.jsonl")
            self.assertTrue(all(a["choice"] is None for a in answers.values()))
            path = destination / "scenarios.json"
            path.write_text("keep my evidence")
            with self.assertRaises(ValueError):
                benchmark.initialize(destination)
            self.assertEqual(path.read_text(), "keep my evidence")


if __name__ == "__main__":
    unittest.main()
