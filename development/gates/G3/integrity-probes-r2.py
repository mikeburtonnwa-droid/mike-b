"""Independent G3 r2 review: revised protocols and preserved negative cases."""
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
from support import DATE, CRITERION, ready_project, record, edge, revision, capture, run_result

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
gate = ROOT / 'development/gates/G3'
manifest = json.loads((gate / 'candidate-r2.json').read_text())
assert manifest == runpy.run_path(str(ROOT / 'scripts/record_development.py'))['manifest']()
preserved = {name: sha(gate / name) for name in ('candidate.json', 'integrity.md', 'integrity-probes.py', 'integrity-probe-output.txt')}
print('candidate', json.dumps({'sha256': sha(gate / 'candidate-r2.json'), 'entries': len(manifest), 'matches_current': True}))

def check(p):
    return w.readiness(p.read(), DATE, 'test', 'HANDOFF')

def change(p, rid, **values):
    return p.put(p.read()['records'][rid] | values, revision(p))

def reject_unchanged(p, operation, label):
    before = p.head()[0]
    try:
        operation()
    except Invalid:
        assert p.head()[0] == before
    else:
        raise AssertionError(label + ' accepted')

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    p = ready_project(root / 'coverage')
    assert check(p)['status'] == 'pass'
    for dimension in ('stakeholder', 'variant', 'exception'):
        change(p, 'COV_' + dimension, steps=['F2'])
    assert w.process_check(p.read())['status'] == 'fail'
    assert check(p)['status'] == 'fail'
    print('proposed_only_current_coverage_rejected', True)
    p = ready_project(root / 'archived')
    p.put(p.read()['records']['P3'] | {'id': 'ARCHIVED', 'status': 'archived'}, revision(p))
    change(p, 'COV_exception', steps=['ARCHIVED'])
    assert w.process_check(p.read())['status'] == 'fail'
    print('archived_only_current_coverage_rejected', True)
    p = ready_project(root / 'handoff')
    change(p, 'P1', actor='customer', boundary='external')
    p.put(record('CUSTOMER', 'coverage', status='covered', dimension='stakeholder', value='customer',
                 critical=True, steps=['P1'], owner='customer', evidence=[{'source':'S1','locator':'line 1'}]), revision(p))
    assert w.process_check(p.read())['status'] == 'fail'
    change(p, 'P1', edges=[edge('P2', kind='handoff', receiver='operations', payload='request')])
    assert w.process_check(p.read())['status'] == 'pass'
    change(p, 'P1', edges=[edge('P2', kind='handoff', receiver='operations', payload=' NONE ')])
    assert any('receiving actor' in e for e in w.process_check(p.read())['errors'])
    print('valid_handoff_passes_and_normalized_missing_payload_fails', True)

with tempfile.TemporaryDirectory() as td:
    p = ready_project(Path(td) / 'queries')
    data = record('TABLE', 'data', environment='test', schema='main', table='requests', grain='one request', keys=['id'], refresh='daily')
    p.put(data, revision(p))
    assert any('lacks captured provenance' in e for e in check(p)['errors'])
    capture(p, 'SCHEMA', b'CREATE TABLE requests(id INTEGER PRIMARY KEY, amount INTEGER);', 'schema')
    change(p, 'TABLE', evidence=[{'source':'SCHEMA','locator':'line 1'}])
    assert check(p)['status'] == 'pass'
    print('missing_provenance_fails_and_captured_schema_passes', True)
    p.put(p.read()['records']['TABLE'] | {'id':'TABLE2'}, revision(p))
    sql = 'SELECT id, amount FROM requests ORDER BY id'
    query = record('QUERY', 'query', status='draft', environment='test', sql=sql, assets=['TABLE'],
                   parameters={}, join_assumptions='No join', limitations='In-memory SQLite review fixture')
    p.put(query, revision(p))
    reject_unchanged(p, lambda: change(p, 'QUERY', environment='prod'), 'Wrong query environment')
    reject_unchanged(p, lambda: w.bind_query(p, 'QUERY', 'SCHEMA', revision(p)), 'Wrong result kind')
    with sqlite3.connect(':memory:') as db:
        db.executescript('CREATE TABLE requests(id INTEGER PRIMARY KEY, amount INTEGER); INSERT INTO requests VALUES (1,10),(2,20);')
        before_run = w.query_fingerprint(p.read(), 'QUERY')
        original_rows = db.execute(sql).fetchall()
        result = dict(environment='test',run_on=DATE,command=sql,exit_code=0,query_fingerprint=before_run,rows=original_rows)
        capture(p, 'QUERY_RESULT', json.dumps(result).encode(), 'query-result')
        w.bind_query(p, 'QUERY', 'QUERY_RESULT', revision(p))
        assert check(p)['status'] == 'pass'
        assert {'TABLE', 'QUERY'} <= set(impact(p.read(), 'SCHEMA')['affected'])
        changed_sql = 'SELECT id, amount FROM requests WHERE id = 1'
        for delta in ({'sql':changed_sql}, {'parameters':{'id':1}}, {'assets':['TABLE2']}):
            reject_unchanged(p, lambda d=delta: change(p,'QUERY',**d), 'Executed query identity')
        print('sql_parameters_assets_rewrites_rejected', True)
        p.put(query | {'id':'QUERY2','sql':changed_sql}, revision(p))
        reject_unchanged(p, lambda: w.bind_query(p,'QUERY2','QUERY_RESULT',revision(p)), 'Old result bound to new query')
        pre_run2 = w.query_fingerprint(p.read(), 'QUERY2')
        new_rows = db.execute(changed_sql).fetchall()
        result2 = dict(environment='test',run_on=DATE,command=changed_sql,exit_code=0,query_fingerprint=pre_run2,rows=new_rows)
        capture(p,'QUERY_RESULT2',json.dumps(result2).encode(),'query-result')
        w.bind_query(p,'QUERY2','QUERY_RESULT2',revision(p))
        assert check(p)['status'] == 'pass'
        print('new_query_needs_new_result', json.dumps({'original_rows':original_rows,'new_rows':new_rows,'old_binding_rejected':True,'new_binding_passed':True}))
    change(p, 'TABLE', grain='changed business grain')
    assert any('executed query dependencies changed' in e for e in check(p)['errors'])
    assert any('executed query dependencies changed' in e for e in context(p.read(),'QUERY',DATE)['warnings'])
    print('asset_drift_blocks_readiness_and_warns_in_context', True)

with tempfile.TemporaryDirectory() as td:
    p = ready_project(Path(td)/'evaluation')
    ev = p.read()['records']['EV1']
    assert 'RESULT_EV1' in ev['hashes']
    assert not w.applicable(p.read(),ev,DATE,'test')
    for criterion,targets in [('Different criterion',['REQ','COMP']),(CRITERION,['REQ'])]:
        reject_unchanged(p,lambda c=criterion,t=targets:w.evaluate(p,dict(id='REBIND',title='Rebind',description='Negative',
            targets=t,result_source='RESULT_EV1',valid_until='2026-10-09',criterion=c),revision(p)),'Captured result mismatch')
    change(p,'COMP',artifact='Changed implementation')
    assert 'evaluated dependencies changed' in w.applicable(p.read(),ev,DATE,'test')
    reject_unchanged(p,lambda:w.evaluate(p,dict(id='REBIND',title='Rebind',description='Negative',
        targets=['REQ','COMP'],result_source='RESULT_EV1',valid_until='2026-10-09',criterion=CRITERION),revision(p)),'Old evaluation result')
    receipt = run_result(p,'UPDATED')
    assert receipt['outcome'] == 'pass' and receipt['evaluation'] == 'UPDATED'
    failure = run_result(p,'LATER_FAIL',observed={'decisions':2})
    assert failure['outcome'] == 'fail' and check(p)['status'] == 'fail'
    run_result(p,'LATER_PASS')
    assert check(p)['status'] == 'pass'
    print('evaluation_binding_receipts_and_latest_outcome', True)
    p.brief(dict(title='Revised scope',scope='Narrower request scope',owner='operations',rationale='Synthetic clarification',
                 evidence=[{'source':'S1','locator':'line 1'}]),revision(p))
    assert 'project brief changed' in w.applicable(p.read(),p.read()['records']['LATER_PASS'],DATE,'test')
    reject_unchanged(p,lambda:w.evaluate(p,dict(id='BRIEF_REBIND',title='Rebind',description='Negative',
        targets=['REQ','COMP'],result_source='RESULT_LATER_PASS',valid_until='2026-10-09',criterion=CRITERION),revision(p)),'Changed brief rebind')
    print('brief_binding_invalidates_old_evidence', True)
    p = ready_project(Path(td)/'freshness')
    change(p,'C1',review_due='2026-09-08',verified_on='2026-09-01')
    assert any('freshness=stale' in e for e in check(p)['errors'])
    print('stale_critical_knowledge_rejected', True)

assert all(sha(gate / name) == value for name,value in preserved.items())
assert manifest == runpy.run_path(str(ROOT / 'scripts/record_development.py'))['manifest']()
print('original_artifacts_preserved_and_candidate_unchanged', True)
