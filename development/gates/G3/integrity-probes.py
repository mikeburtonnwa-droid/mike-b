"""Independent synthetic G3 process/data/provenance probes."""
import hashlib
import json
import runpy
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
from agent_architect.core import Invalid, context, impact
from agent_architect import workflow as w
from support import DATE, CRITERION, ready_project, record, edge, revision, capture

candidate = ROOT / 'development/gates/G3/candidate.json'
manifest = json.loads(candidate.read_text())
assert manifest == runpy.run_path(str(ROOT / 'scripts/record_development.py'))['manifest']()
print('candidate', json.dumps({'sha256': hashlib.sha256(candidate.read_bytes()).hexdigest(), 'entries': len(manifest), 'matches_current': True}))

def check(p):
    return w.readiness(p.read(), DATE, 'test', 'HANDOFF')

def change(p, rid, **values):
    return p.put(p.read()['records'][rid] | values, revision(p))

def dataset(rid='TABLE', **values):
    return record(rid, 'data', environment='test', schema='main', table='requests',
                  grain='one request', keys=['id'], refresh='daily') | values

with tempfile.TemporaryDirectory() as td:
    p = ready_project(Path(td) / 'coverage')
    print('baseline', json.dumps({'process': w.process_check(p.read())['status'], 'readiness': check(p)['status']}))
    for dimension in ('stakeholder', 'variant', 'exception'):
        change(p, 'COV_' + dimension, steps=['F2'])
    result = w.process_check(p.read())
    print('current_coverage_using_only_proposed_steps', json.dumps({'process_status': result['status'], 'errors': result['errors'], 'readiness': check(p)['status']}))
    p = ready_project(Path(td) / 'archived-coverage')
    step = p.read()['records']['P3'] | {'id': 'ARCHIVED', 'status': 'archived'}
    p.put(step, revision(p))
    change(p, 'COV_exception', steps=['ARCHIVED'])
    result = w.process_check(p.read())
    print('current_coverage_using_archived_step', json.dumps({'process_status': result['status'], 'readiness': check(p)['status']}))
    p = ready_project(Path(td) / 'handoff')
    change(p, 'P1', actor='customer', boundary='external')
    assert w.process_check(p.read())['status'] == 'fail'
    change(p, 'P1', edges=[edge('P2', kind='handoff', receiver='operations', payload='request')])
    assert w.process_check(p.read())['status'] == 'pass'
    print('boundary_change_requires_valid_handoff', True)
    change(p, 'P1', edges=[edge('P2', kind='handoff', receiver='operations', payload=' NONE ')])
    print('normalized_missing_handoff_payload', w.process_check(p.read())['status'])

with tempfile.TemporaryDirectory() as td:
    p = ready_project(Path(td) / 'no-provenance')
    p.put(dataset(), revision(p))
    data_context = context(p.read(), 'TABLE', DATE)
    print('data_without_provenance', json.dumps({'readiness': check(p)['status'], 'context_ids': [r['id'] for r in data_context['records']], 'data_has_evidence': bool(p.read()['records']['TABLE'].get('evidence'))}))
    connection = sqlite3.connect(':memory:')
    connection.executescript('CREATE TABLE requests(id INTEGER PRIMARY KEY, amount INTEGER); INSERT INTO requests VALUES (1,10),(2,20);')
    original_sql = 'SELECT id, amount FROM requests ORDER BY id'
    original_rows = connection.execute(original_sql).fetchall()
    capture(p, 'SCHEMA', b'CREATE TABLE requests(id INTEGER PRIMARY KEY, amount INTEGER);', 'schema')
    change(p, 'TABLE', evidence=[{'source': 'SCHEMA', 'locator': 'line 1'}])
    capture(p, 'QUERY_RESULT', json.dumps({'sql': original_sql, 'rows': original_rows}).encode(), 'query-result')
    query = record('QUERY', 'query', status='executed', environment='test', sql=original_sql, assets=['TABLE'],
                   parameters={}, join_assumptions='No join', limitations='Synthetic in-memory SQLite fixture',
                   executed_on=DATE, result_source='QUERY_RESULT')
    p.put(query, revision(p))
    print('executed_query_positive', json.dumps({'rows': original_rows, 'readiness': check(p)['status'], 'schema_impact': impact(p.read(), 'SCHEMA')['affected']}))
    for rid, changes in [('QUERY', {'environment': 'prod'}), ('QUERY', {'result_source': 'SCHEMA'})]:
        before = p.head()[0]
        try:
            change(p, rid, **changes)
        except Invalid:
            assert p.head()[0] == before
        else:
            raise AssertionError('Invalid query environment/source accepted')
    print('query_environment_and_source_kind_negative_checks', True)
    changed_sql = 'SELECT id, amount FROM requests WHERE id = 1'
    changed_rows = connection.execute(changed_sql).fetchall()
    change(p, 'QUERY', sql=changed_sql)
    q = p.read()['records']['QUERY']
    print('executed_query_reuses_result_after_sql_change', json.dumps({'old_rows': original_rows, 'actual_new_rows': changed_rows, 'stored_status': q['status'], 'result_source': q['result_source'], 'readiness': check(p)['status']}))
    connection.close()

with tempfile.TemporaryDirectory() as td:
    p = ready_project(Path(td) / 'evaluation-binding')
    state = p.read()
    evaluation = state['records']['EV1']
    assert 'RESULT_EV1' in evaluation['hashes']
    assert not w.applicable(state, evaluation, DATE, 'test')
    for criterion, targets in [('Different criterion', ['REQ', 'COMP']), (CRITERION, ['REQ'])]:
        before = p.head()[0]
        try:
            w.evaluate(p, dict(id='REBIND', title='Rebind', description='Synthetic negative', targets=targets,
                               result_source='RESULT_EV1', valid_until='2026-10-09', criterion=criterion), revision(p))
        except Invalid as exc:
            assert 'Captured result' in str(exc)
            assert p.head()[0] == before
        else:
            raise AssertionError('Mismatched result rebound')
    change(p, 'COMP', artifact='Changed implementation')
    assert 'evaluated dependencies changed' in w.applicable(p.read(), evaluation, DATE, 'test')
    try:
        w.evaluate(p, dict(id='REBIND', title='Rebind', description='Synthetic negative', targets=['REQ', 'COMP'],
                           result_source='RESULT_EV1', valid_until='2026-10-09', criterion=CRITERION), revision(p))
    except Invalid as exc:
        assert 'Captured result' in str(exc)
    else:
        raise AssertionError('Old captured evaluation rebound to changed targets')
    print('evaluation_result_criterion_targets_and_dependency_binding', True)
    p = ready_project(Path(td) / 'freshness')
    change(p, 'C1', review_due='2026-09-08', verified_on='2026-09-01')
    assert check(p)['status'] == 'fail'
    assert any('freshness=stale' in error for error in check(p)['errors'])
    print('stale_critical_knowledge_rejected', True)

assert manifest == runpy.run_path(str(ROOT / 'scripts/record_development.py'))['manifest']()
print('candidate_unchanged', True)
