"""Reorder unchanged actual rehearsal evidence in a temporary historical checkout."""
import hashlib,json,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; GATE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from agent_architect.core import Project,Invalid
from agent_architect import workflow as w
archive=GATE/'rehearsal-projects-r4.zip'
before=hashlib.sha256(archive.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    with zipfile.ZipFile(archive) as z:z.extractall(td)
    p=Project(Path(td)/'ready-project'); original=p.read()
    labels=['EV_ROUTING','EV_OUTAGE','EV_RECOVERED']
    saved={label:(p.path/original['records'][original['records'][label]['result_source']]['blob']).read_bytes() for label in labels}
    key,env=p.head()
    target=original['records']['EV_ROUTING']['recorded_revision']-1
    while env['state']['revision']!=target:
        key=env['parent'];env=p.envelope(key)
    # Select an existing, valid historical state only in this disposable copy.
    (p.path/'HEAD').write_text(key+'\n')
    assert p.audit()['status']=='pass'
    assert 'EV_ROUTING' not in p.read()['records']
    def add(label,newid):
        source='AUDIT_SOURCE_'+newid
        p.source(source,source,saved[label],'query-result','Unchanged original G4 execution '+label,'2026-09-09','fixture',p.read()['revision'])
        ev=original['records'][label]
        result=w.evaluate(p,dict(id=newid,title=newid,description='Actual retained evidence import-order probe',targets=ev['targets'],criterion=ev['criterion'],result_source=source,valid_until=ev['valid_until']),p.read()['revision'])
        assert (p.path/p.read()['records'][source]['blob']).read_bytes()==saved[label]
        print('import',json.dumps({'original':label,'new':newid,'receipt':result,'run_id':p.read()['records'][newid]['run_id'],'run_at':p.read()['records'][newid]['run_at']}))
        return source
    add('EV_OUTAGE','AUDIT_LATER_FAILURE')
    earlier=add('EV_ROUTING','AUDIT_BACKFILLED_PASS')
    failed=w.readiness(p.read(),'2026-09-09','fixture','HANDOFF')
    assert failed['status']=='fail'
    assert any('REQ_ROUTING: no passing applicable evaluation' in error for error in failed['errors'])
    assert 'AUDIT_BACKFILLED_PASS' not in failed['evaluations']
    print('older_pass_imported_after_later_failure',json.dumps({k:failed[k] for k in ('status','errors','evaluations')}))
    alias='AUDIT_SECOND_ALIAS'
    p.source(alias,alias,saved['EV_ROUTING'],'query-result','Same actual prior run bytes','2026-09-09','fixture',p.read()['revision'])
    head=p.head()[0]; ev=original['records']['EV_ROUTING']
    try:
        w.evaluate(p,dict(id='AUDIT_DUPLICATE',title='Duplicate',description='Source alias replay',targets=ev['targets'],criterion=ev['criterion'],result_source=alias,valid_until=ev['valid_until']),p.read()['revision'])
    except Invalid as error:
        assert 'already evaluated' in str(error) and p.head()[0]==head
        print('unchanged_source_alias_rejected',str(error))
    else:raise AssertionError('Alias replay unexpectedly accepted')
    add('EV_RECOVERED','AUDIT_TRULY_LATER_PASS')
    recovered=w.readiness(p.read(),'2026-09-09','fixture','HANDOFF')
    assert recovered['status']=='pass' and 'AUDIT_TRULY_LATER_PASS' in recovered['evaluations']
    print('strictly_later_actual_pass_restores_readiness',json.dumps({k:recovered[k] for k in ('status','errors','evaluations')}))
    assert p.audit()['status']=='pass'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==before
print('original_archive_preserved',True)
