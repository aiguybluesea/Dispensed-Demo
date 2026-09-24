import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from triage import evaluate, triage

class TriageTests(unittest.TestCase):
    def test_fixture_results(self):
        report = evaluate(json.loads((ROOT / "examples" / "cases.json").read_text()))
        self.assertEqual(report["passed"], report["total"])

    def test_urgent_overrides_order(self):
        self.assertEqual(triage("Chest pain; my parcel is late")["category"], "urgent_clinical")

    def test_never_auto_sends(self):
        self.assertFalse(triage("Where is my order?")["automatic_send"])

    def test_reject_empty(self):
        with self.assertRaises(ValueError):
            triage("  ")

if __name__ == "__main__":
    unittest.main()
