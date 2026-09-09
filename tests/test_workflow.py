import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from agent_architect.core import Invalid, Project, impact
from agent_architect import workflow as w
from support import DATE, CRITERION, record, edge, revision, capture, run_result, ready_project, release, incident, query_result


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.p = ready_project(Path(self.temp.name)/'project')

    def put(self, value):
        return self.p.put(value, revision(self.p))

    def change(self, rid, **values):
        return self.put(self.p.read()['records'][rid] | values)

    def check(self, **values):
        return w.readiness(self.p.read(), values.get('date', DATE), values.get('environment', 'test'), 'HANDOFF')

    def blocked_release(self):
        before = self.p.head()[0]
        with self.assertRaises(Invalid):
            release(self.p)
        self.assertEqual(self.p.head()[0], before)

    def test_complete_structural_fixture_passes_and_renders(self):
        self.assertEqual(self.check()['errors'], [])
        view = w.render(self.p.read(), DATE)
        for text in ('local-simulation', 'P2', 'operations / requests / internal', 'S1 line 1', 'rejected'):
            self.assertIn(text, view)
        self.assertEqual(self.p.audit()['status'], 'pass')

    def test_partial_first_interview_cannot_pass(self):
        self.change('P2', actor='unknown', edges=[])
        result = w.process_check(self.p.read())
        self.assertEqual(result['status'], 'fail')
        self.assertTrue(any('unknown actor' in x for x in result['errors']))
        self.assertTrue(any('dead end' in x for x in result['errors']))
        self.blocked_release()

    def test_cross_view_edges_and_wrong_reference_types_rejected_atomically(self):
        for rid, changes in [('P1', {'edges':[edge('F2')]}), ('REQ', {'claims':['S1']}), ('COMP', {'decisions':['C1']})]:
            old = self.p.head()[0]
            with self.assertRaises(Invalid):
                self.change(rid, **changes)
            self.assertEqual(old, self.p.head()[0])

    def test_boundary_handoff_payload_and_owner_required(self):
        self.change('P1', actor='customer', boundary='external')
        self.assertTrue(any('receiving actor' in x for x in w.process_check(self.p.read())['errors']))
        self.change('P1', edges=[edge('P2', kind='handoff')])
        self.put(record('COV_CUSTOMER','coverage',status='covered',dimension='stakeholder',value='customer',critical=True,
                        steps=['P1'],owner='operations',evidence=[dict(source='S1',locator='line 1')]))
        self.assertEqual(w.process_check(self.p.read())['errors'], [])

    def test_unreachable_and_nonterminating_cycle_reported(self):
        self.change('P2', edges=[edge('P1', 'retry'), edge('P2', 'wait')])
        errors = w.process_check(self.p.read())['errors']
        self.assertTrue(any('unreachable' in x for x in errors))
        self.assertTrue(any('no route' in x for x in errors))

    def test_coverage_gap_and_critical_issue_block(self):
        self.change('COV_exception', status='gap', gap='Need failed request example')
        self.blocked_release()
        self.change('COV_exception', status='covered')
        self.put(record('ISSUE', 'issue', status='open', critical=True, owner='operations', next_action='Investigate missing path'))
        self.blocked_release()

    def test_missing_or_deferred_concern_blocks(self):
        self.change('CON_state', disposition='deferred')
        self.blocked_release()
        self.change('CON_state', status='archived')
        self.assertTrue(any('missing state' in x for x in self.check()['errors']))

    def test_queries_have_environment_and_execution_evidence(self):
        self.put(record('TABLE', 'data', environment='test', schema='main', table='requests', grain='one request', keys=['id'], refresh='daily', evidence=[dict(source='S1', locator='line 1')]))
        query = record('QUERY', 'query', status='draft', environment='test', sql='select id from requests', assets=['TABLE'],
                       parameters={}, join_assumptions='No join', limitations='Synthetic data only')
        with self.assertRaises(Invalid):
            self.put(query | dict(status='executed'))
        with self.assertRaises(Invalid):
            self.put(query | dict(environment='prod'))
        self.put(query)
        self.blocked_release()
        query_result(self.p,'QUERY')
        self.assertEqual(self.check()['errors'], [])

    def test_semantic_reference_fields_participate_in_impact(self):
        affected = impact(self.p.read(), 'S1')['affected']
        self.assertTrue({'C1','REQ','DEC','COMP','EV1'} <= set(affected))

    def test_evaluation_status_is_computed_and_immutable(self):
        run_result(self.p, 'FAIL', observed={'decisions':2})
        ev = self.p.read()['records']['FAIL']
        self.assertEqual(ev['status'], 'fail')
        with self.assertRaisesRegex(Invalid, 'immutable'):
            self.put(ev | dict(status='pass'))
        with self.assertRaises(Invalid):
            run_result(self.p, 'EV1')

    def test_old_captured_result_cannot_be_rebound_to_changed_targets(self):
        source = self.p.read()['records']['RESULT_EV1']
        self.change('COMP', artifact='a different implementation')
        with self.assertRaisesRegex(Invalid, 'Captured result'):
            w.evaluate(self.p,dict(id='REBIND',title='Rebind',description='Invalid stale evidence',targets=['REQ','COMP'],
                                  result_source=source['id'],valid_until='2026-10-09',criterion=CRITERION),revision(self.p))

    def test_result_cannot_be_relabelled_as_another_criterion(self):
        with self.assertRaisesRegex(Invalid, 'Captured result'):
            w.evaluate(self.p,dict(id='RELABEL',title='Relabel',description='Invalid criterion change',targets=['REQ','COMP'],
                                  result_source='RESULT_EV1',valid_until='2026-10-09',criterion='Another criterion'),revision(self.p))

    def test_exit_code_failure_cannot_pass_equal_observations(self):
        run_result(self.p, 'FAIL', exit_code=1)
        self.assertEqual(self.p.read()['records']['FAIL']['status'], 'fail')

    def test_missing_failed_expired_future_and_wrong_environment_evals(self):
        for variant in ('missing','failed','expired','future','environment'):
            with self.subTest(variant=variant):
                p = ready_project(Path(self.temp.name)/variant, evaluation=False)
                if variant != 'missing':
                    args = {'observed':{'decisions':2}} if variant == 'failed' else {'valid_until':'2026-09-08','run_on':'2026-09-08'} if variant == 'expired' else {'run_on':'2026-09-10'} if variant == 'future' else {'environment':'other'}
                    run_result(p, **args)
                with self.assertRaises(Invalid):
                    release(p)

    def test_critical_criterion_and_implementing_component_coverage(self):
        p = ready_project(Path(self.temp.name)/'partial-eval', evaluation=False)
        run_result(p, criterion='A different criterion')
        with self.assertRaises(Invalid):
            release(p)
        run_result(p, 'PARTIAL', targets=['REQ'])
        with self.assertRaises(Invalid):
            release(p)

    def test_dependency_change_invalidates_evaluation(self):
        self.change('COMP', state='new durable state')
        self.assertIn('evaluated dependencies changed', w.applicable(self.p.read(), self.p.read()['records']['EV1'], DATE, 'test'))
        self.blocked_release()
        run_result(self.p, 'EV2')
        self.assertEqual(self.check()['errors'], [])

    def test_stale_reported_disputed_and_superseded_knowledge_blocks(self):
        for status in ('reported', 'disputed', 'verified'):
            self.change('C1', status=status, review_due='2026-09-08', verified_on='2026-09-01')
            self.blocked_release()
        replacement = self.p.read()['records']['C1'] | dict(id='C2', status='verified', review_due='2026-10-09')
        self.put(replacement)
        self.p.supersede('C1','C2','New captured scope evidence',revision(self.p))
        self.blocked_release()

    def test_release_is_immutable_and_activation_is_only_simulation(self):
        release(self.p)
        before = copy.deepcopy(self.p.read()['releases']['REL1'])
        result = w.activate(self.p, 'REL1', DATE, 'test', 'Local test', revision(self.p))
        self.assertEqual(result['deployment_mode'], 'local-simulation')
        self.assertEqual(self.p.read()['active_release'], 'REL1')
        self.change('COMP', state='different')
        self.assertEqual(self.p.read()['releases']['REL1'], before)
        self.assertIn('COMP', w.drift(self.p.read(), 'REL1')['changed'])
        with self.assertRaises(Invalid):
            w.activate(self.p, 'REL1', DATE, 'test', 'retry', revision(self.p))

    def test_unrelated_note_is_informational_drift(self):
        release(self.p)
        self.put(record('NOTE','note',owner='builder',next_action='Next project'))
        self.assertEqual(w.drift(self.p.read(),'REL1')['changed'], [])
        w.activate(self.p,'REL1',DATE,'test','Local test',revision(self.p))

    def test_new_critical_issue_blocks_activation(self):
        release(self.p)
        self.put(record('ISSUE','issue',status='open',critical=True,owner='builder',next_action='Investigate'))
        with self.assertRaises(Invalid):
            w.activate(self.p,'REL1',DATE,'test','Local test',revision(self.p))

    def test_expired_and_environment_mismatch_activation_and_rollback(self):
        release(self.p)
        w.activate(self.p,'REL1',DATE,'test','Local test',revision(self.p))
        for asof, env, rollback in [('2026-11-01','test',False),(DATE,'prod',False),('2026-11-01','test',True)]:
            with self.assertRaises(Invalid):
                w.activate(self.p,'REL1',asof,env,'Local test',revision(self.p),rollback=rollback)
        w.activate(self.p,'REL1',DATE,'test','Rehearse rollback',revision(self.p),rollback=True)
        self.assertEqual(self.p.read()['activations'][-1]['action'],'rollback')

    def test_source_tampering_blocks_release_activation(self):
        release(self.p)
        source = self.p.read()['records']['RESULT_EV1']
        (self.p.path/source['blob']).write_text('altered')
        with self.assertRaises(Invalid):
            w.activate(self.p,'REL1',DATE,'test','Local test',5)

    def test_failed_missing_and_inapplicable_incident_verification_remain_open(self):
        release(self.p)
        inc = incident(self.p) | dict(diagnosis='Fixture fault', action='Restore fixture', follow_up='Retest changes')
        self.put(inc)
        with self.assertRaises(Invalid):
            w.close_incident(self.p,'INC1','MISSING',DATE,revision(self.p))
        for rid, kwargs in [('FAIL',dict(observed=False)),('ENV',dict(environment='other')),('OLD',dict(run_on='2026-09-08')),
                            ('EXP',dict(run_on='2026-09-08',valid_until='2026-09-08')),('WRONG',dict(criterion='Wrong recovery'))]:
            run_result(self.p, rid, **(dict(criterion='Service recovered') | kwargs))
            with self.assertRaises(Invalid):
                w.close_incident(self.p,'INC1',rid,DATE,revision(self.p))
        self.assertEqual(self.p.read()['records']['INC1']['status'],'open')
        with self.assertRaisesRegex(Invalid, 'immutable'):
            self.change('INC1', recovery_criterion='Weaker criterion')

    def test_successful_incident_closure_and_immutable_history(self):
        release(self.p)
        self.put(incident(self.p))
        run_result(self.p,'RECOVERY',criterion='Service recovered')
        with self.assertRaises(Invalid):
            w.close_incident(self.p,'INC1','RECOVERY',DATE,revision(self.p))
        self.change('INC1', diagnosis='Fixture fault', action='Restore fixture', follow_up='Retest on change')
        w.close_incident(self.p,'INC1','RECOVERY',DATE,revision(self.p))
        self.assertEqual(self.p.read()['records']['INC1']['status'],'closed')
        with self.assertRaises(Invalid):
            self.change('INC1',status='open')
        self.assertEqual(self.p.audit()['status'],'pass')

    def test_changed_dependency_blocks_incident_closure(self):
        release(self.p)
        self.put(incident(self.p) | dict(diagnosis='fault',action='restore',follow_up='recheck'))
        run_result(self.p,'RECOVERY',criterion='Service recovered')
        self.change('COMP',artifact='changed artifact')
        with self.assertRaises(Invalid):
            w.close_incident(self.p,'INC1','RECOVERY',DATE,revision(self.p))

    def test_cli_check_fails_with_nonzero_and_schema_is_discoverable(self):
        self.change('P2',actor='unknown')
        proc = subprocess.run([sys.executable,str(ROOT/'scripts/aa.py'),'--project',str(self.p.path),'check','process'],capture_output=True,text=True)
        self.assertEqual(proc.returncode,1)
        self.assertEqual(json.loads(proc.stdout)['status'],'fail')
        proc = subprocess.run([sys.executable,str(ROOT/'scripts/aa.py'),'--project',str(self.p.path),'schema'],capture_output=True,text=True)
        self.assertEqual(proc.returncode,0)
        self.assertIn('acceptance',json.loads(proc.stdout)['requirement']['required'])


if __name__ == '__main__':
    unittest.main()
