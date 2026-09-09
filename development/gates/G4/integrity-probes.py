"""Independent G4 archive, SQL, execution and provenance audit."""
import copy, hashlib, json, runpy, shutil, sqlite3, subprocess, sys, tempfile, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
GATE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from agent_architect.core import Project, Invalid, context, digest, impact
from agent_architect import workflow as w
ASOF='2026-09-09'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((GATE/'candidate.json').read_text())
assert sha(GATE/'candidate.json')=='e4a716bd9181b99725a7f05c027970832f7faa7c047652824ce7f9afdf30deb9'
assert manifest==runpy.run_path(str(ROOT/'scripts/record_development.py'))['manifest']()
preserve_names=['novice-start-project.zip','novice-resume-project.zip','rehearsal-projects-r4.zip','novice-start-commands.json','novice-resume-commands.json','rehearsal-4-events.json']
preserved={n:sha(GATE/n) for n in preserve_names}
registry=json.loads((GATE/'rehearsal-evidence-hashes.json').read_text())
assert all(sha(GATE/n)==value for n,value in registry.items())
print('manifest_and_registered_evidence_hashes',json.dumps({'candidate_entries':len(manifest),'registry_entries':len(registry),'pass':True}))
inputs=sorted((ROOT/'examples/order-triage/inputs').glob('*.md'))
assert len(inputs)==10 and all('SYNTHETIC training material' in p.read_text() for p in inputs)
print('ten_explicitly_fictional_stakeholder_inputs',True)

def source_bytes(p,rid,state=None):
    state=state or p.read()
    return (p.path/state['records'][rid]['blob']).read_bytes()

def historical_states(p):
    key,env=p.head()
    result={}
    while True:
        result[env['state']['revision']]=env['state']
        if env['parent'] is None:break
        env=p.envelope(env['parent'])
    return result

def reject(p,fn):
    head=p.head()[0]
    try:fn()
    except Invalid:assert p.head()[0]==head
    else:raise AssertionError('Expected rejection')

executions=[]
with tempfile.TemporaryDirectory() as td:
    base=Path(td); projects={}
    for name in preserve_names[:3]:
        destination=base/name.removesuffix('.zip')
        with zipfile.ZipFile(GATE/name) as archive:
            for entry in archive.infolist():
                assert not Path(entry.filename).is_absolute() and '..' not in Path(entry.filename).parts
            archive.extractall(destination)
        for head in sorted(destination.rglob('HEAD')):
            key=name+':'+str(head.parent.relative_to(destination))
            p=Project(head.parent); state=p.read()
            audit=p.audit()
            projects[key]=p
            print('archive_audit',json.dumps({'project':key,'commits':audit['commits'],'records':len(state['records']),'status':audit['status']}))
    start=projects['novice-start-project.zip:.']
    resume=projects['novice-resume-project.zip:.']
    ready=projects['rehearsal-projects-r4.zip:ready-project']
    changed=projects['rehearsal-projects-r4.zip:project']
    assert start.read()['owner']=='unknown'
    assert all(r['status']=='reported' for r in start.read()['records'].values() if r['type']=='claim')
    assert source_bytes(start,'S01')==inputs[0].read_bytes()
    assert not start.read()['releases'] and not resume.read()['releases']
    assert w.process_check(start.read())['status']=='fail' and w.process_check(resume.read())['status']=='fail'
    assert resume.read()['records']['C08']['superseded_by']=='C20'
    assert 'C08' not in {r['id'] for r in context(resume.read(),'C08',ASOF)['records']}
    assert any(any(r.get('conflicts_with') for r in s['records'].values()) for s in historical_states(resume).values())
    assert all(source_bytes(resume,f'S{i:02}')==path.read_bytes() for i,path in enumerate(inputs,1))
    assert all(source_bytes(ready,f'S{i:02}')==path.read_bytes() for i,path in enumerate(inputs,1))
    print('fresh_context_attribution_supersession_and_incomplete_scope',True)
    print('resume_verified_claims',json.dumps([{'id':r['id'],'assertion':r['assertion']} for r in resume.read()['records'].values() if r['type']=='claim' and r['status']=='verified']))

    # Independently execute retained SQL against the exact retained schema bytes.
    query_count=0
    for p,setup_id in ((resume,'S11'),(ready,'SRC_SETUP')):
        with sqlite3.connect(':memory:') as db:
            db.executescript(source_bytes(p,setup_id).decode());db.row_factory=sqlite3.Row
            counts={table:db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0] for table in ('intake.requests','crm.customers','finance.approvals','operations.handoffs')}
            assert list(counts.values())==[4,3,4,5]
            for q in [r for r in p.read()['records'].values() if r['type']=='query']:
                retained=json.loads(source_bytes(p,q['result_source']))
                rows=[dict(r) for r in db.execute(q['sql'],q['parameters'])]
                assert rows==retained['rows'],q['id']
                query_count+=1
                if q['id'] in ('Q01','Q_NAIVE'):
                    assert len(rows)==13
                    assert sum(r['tenant']!=r['customer_tenant'] for r in rows)==6
                if q['id'] in ('Q04','Q_ROUTES'):
                    expected=json.loads((ROOT/'examples/order-triage/expected.json').read_text())['routing']
                    route_field='route' if q['id']=='Q_ROUTES' else 'routing_disposition'
                    assert sorted([[r['tenant'],r['request_id'],r[route_field]] for r in rows])==expected
                    assert len(rows)==4 and all(r['tenant']==r['customer_tenant'] for r in rows)
    print('retained_queries_replayed_exactly',json.dumps({'query_count':query_count,'naive_rows':13,'corrected_rows':4,'naive_cross_tenant_rows':6,'table_counts':[4,3,4,5]}))
    state=ready.read(); history=historical_states(ready)
    for r in state['records'].values():
        if r['type']=='source' and r['locator'].startswith('examples/'):
            assert source_bytes(ready,r['id'])==(ROOT/r['locator']).read_bytes()
    print('captured_input_sql_runner_and_expected_bytes_match_frozen_product',True)
    evals=[r for r in state['records'].values() if r['type']=='evaluation']
    for ev in evals:
        at=history[ev['recorded_revision']]
        result=json.loads(source_bytes(ready,ev['result_source']))
        assert result['target_hashes']==w.fingerprints(at['records'],ev['targets'])
        assert result['brief_hash']==w.brief_hash(at)
        assert ev['hashes']==w.fingerprints(at['records'],ev['targets']+[ev['result_source']])
        assert {'SRC_RUNNER','SRC_SETUP','SRC_EXPECTED'}<=set(ev['hashes'])
        assert 'SRC_EXPECTED' in history[ev['recorded_revision']-1]['records']
        assert ev['run_id']==result['run_id'] and ev['run_at']==result['run_at']
    print('all_evaluation_predeclared_expected_code_and_dependency_bindings',len(evals))

    # Replay actual execute.py calls with the retained pre-run binding.
    events=json.loads((GATE/'rehearsal-4-events.json').read_text())
    for event in events:
        if not event['action'].startswith('execute '):continue
        label=event['action'].split(' ',1)[1]
        assert event['stdout'].encode()==source_bytes(ready,'RESULT_'+label)
        old=json.loads(event['stdout']); args=event['argv']
        binding=old.get('query_fingerprint') or {k:old[k] for k in ('target_hashes','brief_hash')}
        bind=base/(label+'-binding.json');bind.write_text(json.dumps(binding))
        command=[sys.executable,str(ROOT/'examples/order-triage/execute.py'),'--sql',args[args.index('--sql')+1],'--binding',str(bind),'--fault',args[args.index('--fault')+1]]
        if '--criterion' in args:command+=['--criterion',args[args.index('--criterion')+1]]
        proc=subprocess.run(command,text=True,capture_output=True)
        executions.append(dict(argv=command,stdout=proc.stdout,stderr=proc.stderr,exit_code=proc.returncode))
        replay=json.loads(proc.stdout)
        assert proc.returncode==event['returncode']==old['exit_code']==replay['exit_code']
        for field in ('rows','expected','observed','criterion'):
            if field in old:assert replay[field]==old[field],(label,field)
    (GATE/'integrity-execution-replays.json').write_text(json.dumps(executions,indent=2)+'\n')
    print('actual_runner_calls_replayed_and_retained_stdout_matches_sources',len(executions))
    assert w.readiness(state,ASOF,'fixture','HANDOFF')['status']=='pass'
    assert w.readiness(changed.read(),ASOF,'fixture','HANDOFF')['status']=='fail'
    assert w.readiness(state,'2026-11-09','fixture','HANDOFF')['status']=='fail'
    assert any('freshness=stale' in x for x in context(state,'CL_OWNER','2026-11-09')['warnings'])
    reject(ready,lambda:ready.put(state['records']['Q_ROUTES']|{'sql':'SELECT 1'},ready.read()['revision']))
    ev=state['records']['EV_RECOVERED']
    def reimport(source,rid):
        return w.evaluate(ready,dict(id=rid,title=rid,description='Independent replay negative',targets=ev['targets'],
              criterion=ev['criterion'],result_source=source,valid_until=ev['valid_until']),ready.read()['revision'])
    reject(ready,lambda:reimport(ev['result_source'],'AUDIT_REPLAY'))
    ready.source('AUDIT_ALIAS','Audit alias',source_bytes(ready,ev['result_source']),'query-result','Identical retained evidence',ASOF,'fixture',ready.read()['revision'])
    reject(ready,lambda:reimport('AUDIT_ALIAS','AUDIT_ALIAS_REPLAY'))
    d=ready.read()['records']['D_HANDOFFS']
    ready.put(d|{'grain':'Changed event-grain assumption for integrity probe'},ready.read()['revision'])
    assert {'Q_ROUTES','COMP_ROUTER'}<=set(impact(ready.read(),'D_HANDOFFS')['affected'])
    assert w.readiness(ready.read(),ASOF,'fixture','HANDOFF')['status']=='fail'
    reject(ready,lambda:w.activate(ready,'REL2',ASOF,'fixture','Independent stale rollback probe',ready.read()['revision'],rollback=True))
    print('changed_query_data_stale_knowledge_and_older_source_alias_rejected',True)
    assert ready.audit()['status']=='pass'

# The experiment command logs retain every command's three result channels.
for name in ('novice-start-commands.json','novice-resume-commands.json'):
    entries=json.loads((GATE/name).read_text())
    assert all(all(k in e for k in ('command','stdout','stderr','exit_code')) for e in entries)
print('experiment_command_channel_completeness',True)
assert all(sha(GATE/name)==value for name,value in preserved.items())
assert manifest==runpy.run_path(str(ROOT/'scripts/record_development.py'))['manifest']()
print('original_archives_logs_and_frozen_candidate_preserved',True)
