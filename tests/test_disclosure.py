import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class DisclosureTests(unittest.TestCase):
    def test_new_positive_labels_enter_disclosure_cohort(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            with (folder / 'runs.csv').open('w') as stream:
                writer = csv.DictWriter(stream, fieldnames=['run_id', 'condition', 'gamed_by_construction', 'task', 'model', 'prompt_arm', 'self_review'])
                writer.writeheader()
                for run_id in ['new', 'negative', 'missing']:
                    writer.writerow(dict(run_id=run_id, condition='all', gamed_by_construction='False', task='example', model='example'))
            (folder / 'labels.csv').write_text('run_id,gamed,note\nnew,1,shortcut\nnegative,0,computed\n')
            output = folder / 'disclosure.json'
            result = subprocess.run([
                sys.executable, 'harness/disclosure.py', '--csv', str(folder / 'runs.csv'),
                '--labels', str(folder / 'labels.csv'), '--coding', str(folder / 'absent.csv'),
                '--runs', str(folder), '--out', str(output),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual([row['run_id'] for row in json.loads(output.read_text())], ['new'])


if __name__ == '__main__':
    unittest.main()
