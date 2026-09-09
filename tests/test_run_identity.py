import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from agent_architect import workflow as w
from agent_architect.core import Invalid
from support import *


class RunIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.p=ready_project(Path(self.temp.name)/'project')

    def import_source(self,source,rid,criterion=CRITERION):
        return w.evaluate(self.p,dict(id=rid,title=rid,description='Synthetic replay regression',targets=['REQ','COMP'],
                                      result_source=source,valid_until='2026-10-09',criterion=criterion),revision(self.p))

    def payload(self,source='RESULT_EV1'):
        r=self.p.read()['records'][source]
        return json.loads((self.p.path/r['blob']).read_text())

    def capture_run(self,rid,at,passed=True):
        value=self.payload()|dict(run_id=str(uuid.uuid4()),run_at=at,observed={'decisions':1 if passed else 2})
        capture(self.p,'SRC_'+rid,json.dumps(value).encode(),'query-result')
        return self.import_source('SRC_'+rid,rid)

    def test_old_source_and_content_alias_cannot_resolve_later_failure(self):
        release(self.p)
        run_result(self.p,'FAIL',observed=False)
        raw=self.p.path/self.p.read()['records']['RESULT_EV1']['blob']
        capture(self.p,'ALIAS',raw.read_bytes(),'query-result')
        for source,rid in [('RESULT_EV1','REPLAY'),('ALIAS','ALIAS_REPLAY')]:
            before=self.p.head()[0]
            with self.assertRaisesRegex(Invalid,'already evaluated'):self.import_source(source,rid)
            self.assertEqual(before,self.p.head()[0])
        self.assertEqual(w.readiness(self.p.read(),DATE,'test','HANDOFF')['status'],'fail')
        with self.assertRaises(Invalid):w.activate(self.p,'REL1',DATE,'test','local',revision(self.p))
        run_result(self.p,'NEW_SUCCESS')
        self.assertEqual(w.readiness(self.p.read(),DATE,'test','HANDOFF')['evaluations'],['NEW_SUCCESS'])

    def test_duplicate_run_id_survives_reformatted_json(self):
        raw=json.dumps(self.payload(),indent=4).encode()
        capture(self.p,'REFORMATTED',raw,'query-result')
        with self.assertRaisesRegex(Invalid,'already evaluated'):self.import_source('REFORMATTED','REPLAY')

    def test_import_order_cannot_promote_older_previously_unimported_run(self):
        run_result(self.p,'FAILED',observed=False)
        self.capture_run('BACKFILLED',DATE+'T00:00:00+00:00')
        self.assertEqual(w.readiness(self.p.read(),DATE,'test','HANDOFF')['status'],'fail')

    def test_same_time_conflict_requires_a_strictly_later_success(self):
        self.capture_run('FAIL',DATE+'T23:59:00+00:00',False)
        self.capture_run('PASS',DATE+'T23:59:00+00:00',True)
        self.assertEqual(w.readiness(self.p.read(),DATE,'test','HANDOFF')['status'],'fail')
        self.capture_run('LATER_PASS',DATE+'T23:59:01+00:00',True)
        self.assertEqual(w.readiness(self.p.read(),DATE,'test','HANDOFF')['evaluations'],['LATER_PASS'])

    def test_recovery_replay_cannot_close_incident(self):
        release(self.p)
        self.p.put(incident(self.p)|dict(diagnosis='fixture fault',action='restore fixture',follow_up='retest'),revision(self.p))
        run_result(self.p,'OLD_RECOVERY',criterion='Service recovered')
        run_result(self.p,'FAILED_RECOVERY',criterion='Service recovered',observed=False)
        source=self.p.read()['records']['RESULT_OLD_RECOVERY']
        capture(self.p,'ALIAS_RECOVERY',(self.p.path/source['blob']).read_bytes(),'query-result')
        for source_id,ev in [('RESULT_OLD_RECOVERY','REPLAY'),('ALIAS_RECOVERY','ALIAS_REPLAY')]:
            before=self.p.head()[0]
            with self.assertRaises(Invalid):self.import_source(source_id,ev,'Service recovered')
            self.assertEqual(before,self.p.head()[0])
        with self.assertRaises(Invalid):w.close_incident(self.p,'INC1','OLD_RECOVERY',DATE,revision(self.p))
        self.assertEqual(self.p.read()['records']['INC1']['status'],'open')
        run_result(self.p,'NEW_RECOVERY',criterion='Service recovered')
        w.close_incident(self.p,'INC1','NEW_RECOVERY',DATE,revision(self.p))
        self.assertEqual(self.p.read()['records']['INC1']['status'],'closed')

    def test_run_timestamp_and_identity_are_validated(self):
        for i,delta in enumerate([dict(run_id='not-a-uuid'),dict(run_at=DATE+'T12:00:00'),dict(run_at='2026-09-10T12:00:00Z')]):
            value=self.payload()|dict(run_id=str(uuid.uuid4()))|delta
            capture(self.p,'BAD_SRC'+str(i),json.dumps(value).encode(),'query-result')
            with self.assertRaises(Invalid):self.import_source('BAD_SRC'+str(i),'BAD'+str(i))


if __name__=='__main__':unittest.main()
