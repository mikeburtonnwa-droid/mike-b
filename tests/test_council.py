import copy
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('council_check', ROOT/'scripts/check_council.py')
council = importlib.util.module_from_spec(spec)
spec.loader.exec_module(council)


class CouncilTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.gate = self.root/'development/gates/G1'
        shutil.copytree(ROOT/'development/gates/G1', self.gate)

    def test_real_recorded_gate(self):
        result = council.check_gate(self.root, 'G1')
        self.assertEqual(result['reviewers'], 3)

    def test_tampered_transcript_fails(self):
        p = self.gate/'transcript.jsonl'
        p.write_text(p.read_text().replace('Review gate G1 independently', 'changed', 1))
        with self.assertRaises(ValueError):
            council.check_gate(self.root, 'G1')

    def test_tampered_approval_fails(self):
        p = self.gate/'product-r2.md'
        p.write_text(p.read_text().replace('APPROVE', 'DENY'))
        with self.assertRaises(ValueError):
            council.check_gate(self.root, 'G1')

    def test_missing_reviewer_fails(self):
        p = self.gate/'decision.json'
        value = json.loads(p.read_text())
        value['reviews'].pop()
        p.write_text(json.dumps(value))
        with self.assertRaises(ValueError):
            council.check_gate(self.root, 'G1')

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            council.check_gate(self.root, '../G1')

    def rewrite_log(self, events):
        lines=[]
        for i,e in enumerate(events):
            e['sequence']=i+1
            e['previous_hash']=hashlib.sha256(lines[-1].encode()).hexdigest() if lines else None
            lines.append(json.dumps(e))
        (self.gate/'transcript.jsonl').write_text('\n'.join(lines)+'\n')

    def events(self):
        return [json.loads(x) for x in (self.gate/'transcript.jsonl').read_text().splitlines()]

    def test_denial_cannot_be_overridden_by_example(self):
        body='Verdict: DENY\nCandidate SHA-256: '+'a'*64+'\nThe prior review said: Verdict: APPROVE\n'
        self.assertEqual(council.report_header(body)[0], 'DENY')
        with self.assertRaises(ValueError):
            council.report_header(body+'Verdict: APPROVE\n')

    def test_wrong_candidate_approval_rejected(self):
        p=self.gate/'decision.json'; d=json.loads(p.read_text())
        old=d['candidate_hash']; target=self.gate/d['candidate']
        candidate=json.loads(target.read_text()); candidate['docs/CONTRACT.md']='b'*64
        target.write_text(json.dumps(candidate)); d['candidate_hash']=council.sha(target)
        p.write_text(json.dumps(d))
        events=self.events(); events[-1]['message']=p.read_text(); self.rewrite_log(events)
        with self.assertRaisesRegex(ValueError, 'candidate'):
            council.check_gate(self.root,'G1')

    def test_early_decision_rejected(self):
        events=self.events(); last=events.pop(); events.insert(0,last); self.rewrite_log(events)
        with self.assertRaises(ValueError): council.check_gate(self.root,'G1')

    def test_missing_timestamp_rejected(self):
        events=self.events(); events[0].pop('time'); self.rewrite_log(events)
        with self.assertRaises(ValueError): council.check_gate(self.root,'G1')

    def test_missing_predecessor_rejected(self):
        other=self.root/'development/gates/G2'; shutil.copytree(self.gate,other)
        p=other/'decision.json'; d=json.loads(p.read_text()); d['gate']='G2'; p.write_text(json.dumps(d))
        self.gate=other
        events=self.events(); events[-1]['message']=p.read_text(); self.rewrite_log(events)
        with self.assertRaisesRegex(ValueError,'preceding'):
            council.check_gate(self.root,'G2')


if __name__ == '__main__':
    unittest.main()
