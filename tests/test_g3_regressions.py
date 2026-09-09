import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from agent_architect.core import Invalid,Project,context,digest,validate_state
from agent_architect import workflow as w
from support import *


class G3RegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.p=ready_project(Path(self.temp.name)/'project')

    def put(self,value):
        return self.p.put(value,revision(self.p))

    def test_release_namespace_is_unique_in_every_creation_direction(self):
        release(self.p)
        for op in (lambda:self.put(record('REL1','note',owner='test',next_action='test')),
                   lambda:capture(self.p,'REL1',b'collision'),
                   lambda:w.evaluate(self.p,dict(id='REL1',title='collision',description='collision',targets=['REQ','COMP'],
                        result_source='RESULT_EV1',valid_until='2026-10-09',criterion=CRITERION),revision(self.p)),
                   lambda:release(self.p,'REQ')):
            before=self.p.head()[0]
            with self.assertRaises(Invalid):op()
            self.assertEqual(before,self.p.head()[0])
        state=self.p.read();state['records']['REL1']=record('REL1','note',owner='test',next_action='test')
        with self.assertRaisesRegex(Invalid,'unique'):validate_state(state)

    def test_later_failure_blocks_release_activation_and_recovers_on_later_pass(self):
        release(self.p)
        run_result(self.p,'FAILED',observed={'decisions':2},run_on='2026-09-10')
        self.assertEqual(w.readiness(self.p.read(),'2026-09-10','test','HANDOFF')['status'],'fail')
        for op in (lambda:w.create_release(self.p,'REL2','HANDOFF','2026-09-10','test','local',revision(self.p)),
                   lambda:w.activate(self.p,'REL1','2026-09-10','test','local',revision(self.p))):
            before=self.p.head()[0]
            with self.assertRaises(Invalid):op()
            self.assertEqual(before,self.p.head()[0])
        run_result(self.p,'REPAIRED',run_on='2026-09-10')
        self.assertEqual(w.readiness(self.p.read(),'2026-09-10','test','HANDOFF')['evaluations'],['REPAIRED'])

    def test_same_day_run_order_uses_execution_time_not_id(self):
        run_result(self.p,'ZZZ')
        run_result(self.p,'AAA',observed=False)
        self.assertEqual(w.readiness(self.p.read(),DATE,'test','HANDOFF')['status'],'fail')
        receipt=run_result(self.p,'AAB')
        self.assertEqual(receipt['outcome'],'pass')
        self.assertEqual(w.readiness(self.p.read(),DATE,'test','HANDOFF')['evaluations'],['AAB'])

    def test_future_captured_incident_evidence_and_later_failure_cannot_close(self):
        release(self.p)
        self.put(incident(self.p)|dict(diagnosis='fault',action='restore',follow_up='retest'))
        result=dict(environment='test',run_on=DATE,command='recovery check',exit_code=0,expected=True,observed=True,
                    run_id=str(__import__('uuid').uuid4()),run_at=DATE+'T00:01:00+00:00',
                    criterion='Service recovered',target_hashes=w.fingerprints(self.p.read()['records'],['COMP']),brief_hash=w.brief_hash(self.p.read()))
        capture(self.p,'FUTURE_RESULT',json.dumps(result).encode(),'query-result',date='2026-09-10')
        w.evaluate(self.p,dict(id='FUTURE',title='recovery',description='future capture',targets=['COMP'],result_source='FUTURE_RESULT',
                             valid_until='2026-10-09',criterion='Service recovered'),revision(self.p))
        before=self.p.head()[0]
        with self.assertRaises(Invalid):w.close_incident(self.p,'INC1','FUTURE',DATE,revision(self.p))
        self.assertEqual(before,self.p.head()[0]);self.assertEqual(self.p.read()['records']['INC1']['status'],'open')
        run_result(self.p,'RECOVERED',criterion='Service recovered')
        run_result(self.p,'FAILED',criterion='Service recovered',observed=False)
        with self.assertRaisesRegex(Invalid,'latest'):w.close_incident(self.p,'INC1','RECOVERED','2026-09-10',revision(self.p))

    def test_current_coverage_rejects_proposed_archived_and_unmatched_actors(self):
        self.put(self.p.read()['records']['COV_stakeholder']|dict(steps=['F2']))
        self.assertEqual(w.process_check(self.p.read())['status'],'fail')
        self.put(self.p.read()['records']['COV_stakeholder']|dict(steps=['P2']))
        r=self.p.read()['records']; self.put([r['P4']|dict(actor='finance'),r['P2']|dict(edges=[edge('P3','accepted'),edge('P4','rejected','exception',receiver='finance')])])
        self.assertTrue(any('finance' in e for e in w.process_check(self.p.read())['errors']))
        self.put(record('FINANCE','coverage',status='covered',dimension='stakeholder',value='finance',critical=True,steps=['P4'],owner='finance',evidence=[dict(source='S1',locator='line 1')]))
        self.assertEqual(w.process_check(self.p.read())['status'],'pass')
        self.put(self.p.read()['records']['P4']|dict(status='archived'))
        self.assertTrue(any('active current' in e for e in w.process_check(self.p.read())['errors']))

    def test_missing_payload_sentinel_and_rendered_handoff(self):
        r=self.p.read()['records']; self.put([r['P1']|dict(actor='customer',edges=[edge('P2',kind='handoff',payload=' NONE ')]),
              record('CUSTOMER','coverage',status='covered',dimension='stakeholder',value='customer',critical=True,steps=['P1'],owner='customer',evidence=[dict(source='S1',locator='line 1')])])
        self.assertEqual(w.process_check(self.p.read())['status'],'fail')
        self.put(self.p.read()['records']['P1']|dict(edges=[edge('P2',kind='handoff',payload='handoff-package-Z37')]))
        self.assertEqual(w.process_check(self.p.read())['status'],'pass')
        self.assertIn('handoff-package-Z37',w.render(self.p.read(),DATE))

    def test_data_needs_captured_provenance_for_release(self):
        data=record('TABLE','data',environment='test',schema='main',table='requests',grain='one request',keys=['id'],refresh='daily')
        self.put(data)
        self.assertTrue(any('lacks captured provenance' in e for e in w.readiness(self.p.read(),DATE,'test','HANDOFF')['errors']))
        capture(self.p,'SCHEMA',b'create table requests(id primary key, amount);','schema')
        self.put(data|dict(evidence=[dict(source='SCHEMA',locator='DDL')]))
        self.assertEqual(w.readiness(self.p.read(),DATE,'test','HANDOFF')['status'],'pass')

    def test_sql_parameters_assets_and_asset_drift_cannot_reuse_execution(self):
        capture(self.p,'SCHEMA',b'create table requests(id primary key, amount);','schema')
        data=record('TABLE','data',environment='test',schema='main',table='requests',grain='one request',keys=['id'],refresh='daily',evidence=[dict(source='SCHEMA',locator='DDL')])
        self.put([data,data|dict(id='TABLE2')])
        q=record('Q','query',status='draft',environment='test',sql='select id from requests order by id',assets=['TABLE'],parameters={},join_assumptions='No join',limitations='fixture')
        self.put(q)
        db=sqlite3.connect(':memory:');self.addCleanup(db.close)
        db.executescript('create table requests(id primary key, amount); insert into requests values(1,10),(2,20);')
        result=dict(environment='test',run_on=DATE,command='sqlite3 fixture execution',exit_code=0,query_fingerprint=w.query_fingerprint(self.p.read(),'Q'),rows=[list(row) for row in db.execute(q['sql'])])
        capture(self.p,'ROWS',json.dumps(result).encode(),'query-result')
        w.bind_query(self.p,'Q','ROWS',revision(self.p))
        for delta in (dict(sql='select id from requests where id=1'),dict(parameters={'id':1}),dict(assets=['TABLE2'])):
            before=self.p.head()[0]
            with self.assertRaises(Invalid):self.put(self.p.read()['records']['Q']|delta)
            self.assertEqual(before,self.p.head()[0])
        self.put(q|dict(id='Q2',sql='select id from requests where id=1'))
        with self.assertRaises(Invalid):w.bind_query(self.p,'Q2','ROWS',revision(self.p))
        self.assertEqual([list(row) for row in db.execute('select id from requests where id=1')],[[1]])
        self.put(data|dict(grain='changed assumption'))
        self.assertTrue(any('query dependencies changed' in e for e in w.readiness(self.p.read(),DATE,'test','HANDOFF')['errors']))

    def test_brief_clarification_resumes_with_provenance_and_keeps_history(self):
        p=Project(Path(self.temp.name)/'intake');p.init('Intake','unknown','unknown')
        initial=p.head()[0]
        capture(p,'CLARIFY',b'Alice owns standard requests.','interview')
        value=dict(title='Standard requests',scope='Standard requests only',owner='Alice',rationale='Stakeholder clarification',evidence=[dict(source='CLARIFY',locator='line 1')])
        p.brief(value,revision(p))
        resumed=context(Project(p.path).read(),'scope',DATE)
        self.assertEqual(resumed['brief']['owner'],'Alice');self.assertEqual(resumed['brief']['scope'],'Standard requests only')
        self.assertIn('CLARIFY',{r['id'] for r in resumed['records']})
        self.assertEqual(p.envelope(initial)['state']['owner'],'unknown')
        with self.assertRaises(Invalid):p.brief(value,2)
        self.assertEqual(p.audit()['status'],'pass')

    def test_brief_change_invalidates_evaluations_and_old_release_activation(self):
        release(self.p); old=self.p.read()['releases']['REL1']
        self.p.brief(dict(title='Changed project',scope='Narrowed scope',owner='Alice',rationale='Captured clarification',evidence=[dict(source='S1',locator='line 1')]),revision(self.p))
        self.assertEqual(self.p.read()['releases']['REL1'],old)
        self.assertTrue(w.drift(self.p.read(),'REL1')['brief_changed'])
        self.assertIn('project brief changed',w.applicable(self.p.read(),self.p.read()['records']['EV1'],DATE,'test'))
        with self.assertRaises(Invalid):w.activate(self.p,'REL1',DATE,'test','local',revision(self.p))
        with self.assertRaises(Invalid):w.evaluate(self.p,dict(id='REBOUND',title='bad',description='bad',targets=['REQ','COMP'],result_source='RESULT_EV1',valid_until='2026-10-09',criterion=CRITERION),revision(self.p))

    def test_new_consequential_requirement_blocks_old_snapshot(self):
        release(self.p);r=self.p.read()['records']
        self.put([r['REQ']|dict(id='REQ2',acceptance='Second criterion'),r['DEC']|dict(id='DEC2',requirements=['REQ2']),r['COMP']|dict(id='COMP2',decisions=['DEC2'])])
        run_result(self.p,'EV2',criterion='Second criterion',targets=['REQ2','COMP2'])
        self.assertEqual(w.readiness(self.p.read(),DATE,'test','HANDOFF')['status'],'pass')
        with self.assertRaises(Invalid):w.activate(self.p,'REL1',DATE,'test','local',revision(self.p))

    def test_context_warns_on_changed_evaluation_and_evaluate_reports_failure(self):
        receipt=run_result(self.p,'FAIL',observed=False)
        self.assertEqual(receipt['outcome'],'fail');self.assertEqual(receipt['evaluation'],'FAIL')
        self.put(self.p.read()['records']['COMP']|dict(state='changed'))
        self.assertTrue(any('evaluated dependencies changed' in x for x in context(self.p.read(),'EV1',DATE)['warnings']))


if __name__=='__main__':unittest.main()
