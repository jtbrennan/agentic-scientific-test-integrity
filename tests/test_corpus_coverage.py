"""Integrity checks for the archived classifications and disclosure cohort."""
import csv
from pathlib import Path
import unittest

from harness.classification import classify_runs, load_labels, require_complete

ROOT = Path(__file__).resolve().parents[1]


class CorpusCoverageTests(unittest.TestCase):
    def setUp(self):
        with (ROOT / 'results/runs_table.csv').open() as source:
            self.rows = list(csv.DictReader(source))
        self.labels = load_labels(ROOT / 'results/manual_labels.csv')
        self.classifications = classify_runs(self.rows, self.labels)

    def test_every_non_conflict_run_has_one_explicit_label(self):
        require_complete(self.classifications)
        expected = {row['run_id'] for row in self.rows if row['condition'] != 'conflict'}
        self.assertEqual(set(self.labels), expected)
        with (ROOT / 'results/manual_labels.csv').open() as source:
            for label in csv.DictReader(source):
                self.assertTrue(label['note'].strip(), label['run_id'])

    def test_disclosure_codes_cover_exactly_the_gaming_cohort(self):
        with (ROOT / 'results/disclosure_coding.csv').open() as source:
            codes = list(csv.DictReader(source))
        ids = [row['run_id'] for row in codes]
        self.assertEqual(len(ids), len(set(ids)), 'duplicate disclosure codes')
        self.assertEqual(set(ids), {run_id for run_id, gamed in self.classifications.items() if gamed})
        for code in codes:
            for field in ('final_disclosed', 'final_explicit', 'any_msg_disclosed', 'misleading_claim'):
                self.assertIn(code[field], ('0', '1'), (code['run_id'], field))


if __name__ == '__main__':
    unittest.main()
