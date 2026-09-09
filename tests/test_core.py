import copy
import hashlib
import json
import multiprocessing
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from agent_architect.core import Invalid, Project, context, impact, freshness, atomic


def claim(rid='C01', **values):
    return dict(id=rid, type='claim', title='Account owner', description='Interview interpretation',
                status='reported', assertion='Operations creates accounts', applicability='standard',
                evidence=[{'source': 'S01', 'locator': 'line 1'}]) | values


def note(rid, deps=()):
    return dict(id=rid, type='note', title=rid, description='Working note', status='active',
                owner='builder', next_action='Investigate', depends_on=list(deps))


def lock_worker(path, ready):
    with Project(path).locked():
        ready.set()
        # Parent forcibly terminates this process to verify automatic lock release.
        import time
        time.sleep(30)


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Project(Path(self.temp.name) / 'project')
        self.project.init('Onboarding', 'Request to account', 'owner')
        self.project.source('S01', 'Interview', b'Operations creates accounts\n', 'interview',
                            'meeting-1', '2026-09-01', 'operations', 1)

    def put(self, records):
        return self.project.put(records, self.project.read()['revision'], 'test-agent')

    def test_capture_is_content_addressed_and_auditable(self):
        s = self.project.read()['records']['S01']
        self.assertEqual(s['content_hash'], hashlib.sha256(b'Operations creates accounts\n').hexdigest())
        self.assertEqual(self.project.audit()['commits'], 2)
        self.assertEqual(self.project.head()[1]['actor'], 'local-user')

    def test_init_never_overwrites(self):
        before = self.project.head()[0]
        with self.assertRaises(Invalid):
            self.project.init('Again', 'Again', 'Again')
        self.assertEqual(self.project.head()[0], before)

    def test_source_tampering_blocks_read_and_mutation(self):
        source = self.project.read()['records']['S01']
        (self.project.path / source['blob']).write_bytes(b'changed')
        with self.assertRaisesRegex(Invalid, 'tampered'):
            self.project.read()
        with self.assertRaises(Invalid):
            self.project.put(note('N01'), 2)

    def test_deleted_source_fails(self):
        s = self.project.read()['records']['S01']
        (self.project.path / s['blob']).unlink()
        with self.assertRaises(Invalid):
            self.project.audit()

    def test_symlink_source_fails(self):
        s = self.project.read()['records']['S01']
        p = self.project.path / s['blob']
        content = p.read_bytes()
        other = Path(self.temp.name) / 'other'
        other.write_bytes(content)
        p.unlink()
        p.symlink_to(other)
        with self.assertRaises(Invalid):
            self.project.read()

    def test_invalid_batch_rolls_back(self):
        before = self.project.head()[0]
        with self.assertRaises(Invalid):
            self.put([claim(), note('N01', ['missing'])])
        self.assertEqual(before, self.project.head()[0])
        self.assertNotIn('C01', self.project.read()['records'])

    def test_forward_links_are_atomic(self):
        self.put([note('N01', ['C01']), claim()])
        self.assertEqual(impact(self.project.read(), 'S01')['affected'], ['C01', 'N01'])

    def test_duplicate_batch_ids_rejected(self):
        with self.assertRaises(Invalid):
            self.put([claim(), claim()])

    def test_unknown_fields_and_bad_types_rejected(self):
        for bad in (claim(stauts='verified'), claim(evidence='S01'), claim(tags=[3]), claim(review_due='2026-02-31')):
            with self.subTest(record=bad), self.assertRaises(Invalid):
                self.put(bad)

    def test_claim_requires_source_and_locator(self):
        for bad in (claim(evidence=[]), claim(evidence=[{'source': 'S01'}]),
                    claim(evidence=[{'source': 'S01', 'locator': ''}])):
            with self.subTest(record=bad), self.assertRaises(Invalid):
                self.put(bad)

    def test_verified_claim_needs_verification_and_dates(self):
        with self.assertRaises(Invalid):
            self.put(claim(status='verified'))
        self.put(claim(status='verified', verified_on='2026-09-02', review_due='2026-10-01', verification='Observed case S01'))
        data = context(self.project.read(), 'C01', '2026-09-09')
        self.assertEqual(data['warnings'], [])

    def test_date_status_is_explicit(self):
        self.assertEqual(freshness(claim(), '2026-09-09'), 'unknown')
        self.assertEqual(freshness(claim(review_due='2026-09-08'), '2026-09-09'), 'stale')
        self.assertEqual(freshness(claim(review_due='2026-09-09'), '2026-09-09'), 'current')
        self.assertEqual(freshness(claim(verified_on='2026-09-10'), '2026-09-09'), 'future-dated')

    def test_conflicts_must_be_bilateral_and_not_verified(self):
        with self.assertRaises(Invalid):
            self.put([claim(conflicts_with=['C02']), claim('C02')])
        self.put([claim(status='disputed', conflicts_with=['C02']),
                  claim('C02', status='disputed', assertion='Sales creates accounts', conflicts_with=['C01'])])
        result = context(self.project.read(), 'C01', '2026-09-09')
        self.assertTrue({'C01', 'C02', 'S01'} <= {r['id'] for r in result['records']})
        self.assertEqual(len(result['warnings']), 2)

    def test_assertion_rewrite_fails(self):
        self.put(claim())
        with self.assertRaisesRegex(Invalid, 'assertions cannot be rewritten'):
            self.put(claim(assertion='Someone else creates accounts'))

    def test_explicit_supersession_preserves_history_and_context(self):
        self.put([claim(), claim('C02', assertion='Operations handles standard accounts'), note('N01', ['C01'])])
        self.project.supersede('C01', 'C02', 'Updated evidence', 3)
        result = context(self.project.read(), 'N01', '2026-09-09')
        self.assertIn('C02', {r['id'] for r in result['records']})
        self.assertNotIn('C01', {r['id'] for r in result['records']})
        self.assertEqual(result['historical_dependencies'][0]['id'], 'C01')
        self.assertEqual(self.project.audit()['commits'], 4)
        with self.assertRaises(Invalid):
            self.put(claim())

    def test_supersession_chain_reaches_latest(self):
        self.put([claim(), claim('C02'), claim('C03')])
        self.project.supersede('C01', 'C02', 'new', 3)
        self.project.supersede('C02', 'C03', 'newer', 4)
        result = context(self.project.read(), 'C01', '2026-09-09')
        self.assertIn('C03', {r['id'] for r in result['records']})
        with self.assertRaises(Invalid):
            self.project.supersede('C03', 'C01', 'cycle', 5)

    def test_applicability_cannot_be_superseded(self):
        self.put([claim(), claim('C02', applicability='urgent')])
        with self.assertRaisesRegex(Invalid, 'Different applicability'):
            self.project.supersede('C01', 'C02', 'different', 3)

    def test_source_records_are_immutable(self):
        s = self.project.read()['records']['S01']
        with self.assertRaises(Invalid):
            self.put(s)
        with self.assertRaises(Invalid):
            self.project.source('S01', 'Changed', b'changed', 'document', 'new', '2026-09-09', 'test', 2)

    def test_dependency_cycle_rejected(self):
        with self.assertRaisesRegex(Invalid, 'cycle'):
            self.put([note('N01', ['N02']), note('N02', ['N01'])])

    def test_stale_expected_revision_cannot_lose_an_update(self):
        self.put(note('N01'))
        with self.assertRaisesRegex(Invalid, 'Stale revision'):
            self.project.put(note('N02'), 2)
        self.assertIn('N01', self.project.read()['records'])
        self.assertNotIn('N02', self.project.read()['records'])

    def test_process_lock_and_killed_writer_recovery(self):
        ctx = multiprocessing.get_context('fork')
        ready = ctx.Event()
        process = ctx.Process(target=lock_worker, args=(self.project.path, ready))
        process.start()
        try:
            self.assertTrue(ready.wait(5))
            with self.assertRaisesRegex(Invalid, 'busy'):
                self.project.put(note('N01'), 2)
        finally:
            process.terminate()
            process.join(5)
        self.put(note('N02'))
        self.assertEqual(self.project.read()['revision'], 3)

    def test_failure_before_head_does_not_publish_partial_commit(self):
        old = self.project.head()[0]
        def fail_head(path, data):
            if path.name == 'HEAD':
                raise OSError('injected interruption')
            return atomic(path, data)
        with patch('agent_architect.core.atomic', side_effect=fail_head), self.assertRaises(OSError):
            self.put(note('N01'))
        self.assertEqual(self.project.head()[0], old)
        self.assertNotIn('N01', self.project.read()['records'])
        self.assertEqual(self.project.audit()['commits'], 2)
        self.put(note('N02'))
        self.assertEqual(self.project.audit()['commits'], 3)

    def test_history_tampering_blocks_writes(self):
        key, env = self.project.head()
        env['actor'] = 'altered'
        (self.project.path / 'history' / f'{key}.json').write_text(json.dumps(env))
        with self.assertRaisesRegex(Invalid, 'integrity'):
            self.project.audit()

    def test_cold_resume_preserves_pending_work(self):
        self.put(claim())
        self.project.checkpoint(dict(current_task='Map exceptions', completed=['First interview'],
                                     unresolved=['Owner unknown'], next_action='Ask operations for rejected example',
                                     relevant_ids=['C01'], stage='discovery'), 3)
        new_session = Project(self.project.path)
        result = context(new_session.read(), '', '2026-09-09')
        self.assertEqual(result['checkpoint']['unresolved'], ['Owner unknown'])
        self.assertEqual(result['stage'], 'discovery')

    def test_cli_from_unrelated_working_directory(self):
        proc = subprocess.run([sys.executable, str(ROOT/'scripts/aa.py'), '--project', str(self.project.path),
                               'context', '--as-of', '2026-09-09'], cwd=self.temp.name, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['revision'], 2)

    def test_cli_missing_project_is_nonzero_json_error(self):
        proc = subprocess.run([sys.executable, str(ROOT/'scripts/aa.py'), '--project', str(Path(self.temp.name)/'absent'),
                               'show'], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stderr)['status'], 'error')

    def test_invalid_shapes_are_structured_cli_errors(self):
        for value in (None, [None], [5], {'id': 'BAD', 'type': []}):
            file = Path(self.temp.name)/'bad.json'
            file.write_text(json.dumps(value))
            proc = subprocess.run([sys.executable, str(ROOT/'scripts/aa.py'), '--project', str(self.project.path),
                                   'put', str(file), '--expect-revision', '2'], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertEqual(json.loads(proc.stderr)['status'], 'error')
            self.assertEqual(self.project.read()['revision'], 2)

    def test_replacement_conflict_fixed_point(self):
        self.put([claim(), claim('NEW', status='disputed', conflicts_with=['OTHER']),
                  claim('OTHER', assertion='Another route', status='disputed', conflicts_with=['NEW']), note('TASK', ['C01'])])
        self.project.supersede('C01', 'NEW', 'Replacement', 3)
        result = context(self.project.read(), 'TASK', '2026-09-09')
        self.assertTrue({'NEW','OTHER','S01'} <= {r['id'] for r in result['records']})

    def test_changed_scope_requires_new_claim(self):
        value = claim(status='verified', verified_on='2026-09-01', review_due='2026-10-01', verification='Observed standard scope')
        self.put(value)
        with self.assertRaisesRegex(Invalid, 'applicability'):
            self.put(value | {'applicability':'urgent'})

    def test_post_commit_fault_has_explicit_visible_outcome(self):
        def fail_after_head(path, data):
            atomic(path, data)
            if path.name == 'HEAD':
                raise OSError('post-publication flush failure')
        with patch('agent_architect.core.atomic', side_effect=fail_after_head):
            result = self.put(note('N01'))
        self.assertEqual(result['status'], 'committed-durability-uncertain')
        self.assertEqual(result['commit'], self.project.head()[0])
        self.assertEqual(result['revision'], 3)
        self.assertEqual(self.project.audit()['commits'], 3)


if __name__ == '__main__':
    unittest.main()
