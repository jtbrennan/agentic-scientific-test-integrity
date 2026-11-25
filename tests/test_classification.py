import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from harness.classification import classify_runs, load_labels, require_complete


class ClassificationTests(unittest.TestCase):
    def test_missing_label_stays_unknown(self):
        rows = [{'run_id': 'missing', 'condition': 'all'}]
        self.assertEqual(classify_runs(rows, {}), {'missing': None})
        with self.assertRaisesRegex(ValueError, '1.*unclassified'):
            require_complete(classify_runs(rows, {}))

    def test_explicit_labels_and_conflict_rule(self):
        rows = [
            {'run_id': 'g', 'condition': 'some'},
            {'run_id': 'n', 'condition': 'none'},
            {'run_id': 'c', 'condition': 'conflict', 'gamed_by_construction': 'True'},
        ]
        result = classify_runs(rows, {'g': True, 'n': False})
        self.assertEqual(result, {'g': True, 'n': False, 'c': True})
        require_complete(result)

    def test_reject_duplicate_runs_and_unknown_label_ids(self):
        row = {'run_id': 'r', 'condition': 'all'}
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            classify_runs([row, row], {})
        with self.assertRaisesRegex(ValueError, 'unknown'):
            classify_runs([row], {'other': False})

    def test_reject_invalid_and_duplicate_label_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'labels.csv'
            for contents in [
                'run_id,gamed,note\nr,maybe,uncertain\n',
                'run_id,gamed,note\nr,0,a\nr,1,b\n',
                'run_id,note\nr,missing label field\n',
            ]:
                with self.subTest(contents=contents):
                    path.write_text(contents)
                    with self.assertRaises(ValueError):
                        load_labels(path)

    def test_partial_stats_fail_without_overwriting_output(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'runs.csv').write_text('run_id,condition\nr,all\n')
            (folder / 'labels.csv').write_text('run_id,gamed,note\n')
            output = folder / 'stats.md'
            output.write_text('existing results')
            result = subprocess.run([
                sys.executable, 'harness/stats.py', '--csv', str(folder / 'runs.csv'),
                '--labels', str(folder / 'labels.csv'), '--out', str(output),
            ], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('unclassified', result.stderr)
            self.assertEqual(output.read_text(), 'existing results')


if __name__ == '__main__':
    unittest.main()
