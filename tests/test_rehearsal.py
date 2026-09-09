"""End-to-end integration: execute SQLite and inspect durable handoff, not canned pass data."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from agent_architect.core import Project
from agent_architect import workflow as w


class RehearsalTests(unittest.TestCase):
    def test_actual_query_to_verified_recovery_and_changed_rollback(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / 'rehearsal with spaces'
            run = subprocess.run([sys.executable, str(ROOT / 'examples/order-triage/rehearse.py'),
                                  '--output', str(out)], cwd=directory, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            report = json.loads(run.stdout)
            self.assertEqual(report['failed'], [])
            self.assertEqual((report['naive_rows'], report['corrected_rows']), (13, 4))
            checks = json.loads((out / 'checks.json').read_text())
            self.assertTrue(all(item['passed'] for item in checks))
            ready = Project(out / 'ready-project')
            state = ready.read()
            self.assertEqual(ready.audit()['status'], 'pass')
            self.assertEqual(state['active_release'], 'REL2')
            self.assertEqual(state['records']['EV_NAIVE']['status'], 'fail')
            self.assertEqual(state['records']['EV_FAILED_RECOVERY']['status'], 'fail')
            self.assertEqual(state['records']['INC_FEED']['verification'], 'EV_RECOVERED')
            self.assertEqual(w.readiness(state, report['as_of'], 'fixture', 'HANDOFF')['status'], 'pass')
            changed = Project(out / 'project')
            self.assertEqual(changed.audit()['status'], 'pass')
            self.assertEqual(w.readiness(changed.read(), report['as_of'], 'fixture', 'HANDOFF')['status'], 'fail')
            events = json.loads((out / 'events.json').read_text())
            executed = [e for e in events if 'argv' in e]
            self.assertTrue(any(e['returncode'] == 1 for e in executed))
            self.assertTrue(any(e['returncode'] == 0 for e in executed))

    def test_rehearsal_never_overwrites_an_existing_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / 'important.txt'
            marker.write_text('keep this')
            run = subprocess.run([sys.executable, str(ROOT / 'examples/order-triage/rehearse.py'),
                                  '--output', directory], capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('never overwritten', run.stderr)
            self.assertEqual(marker.read_text(), 'keep this')
            self.assertEqual(list(Path(directory).iterdir()), [marker])


if __name__ == '__main__':
    unittest.main()
