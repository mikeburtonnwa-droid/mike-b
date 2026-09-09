"""Independent clean-clone, empty-runtime and hostile local-evidence checks."""
import hashlib,json,os,runpy,shutil,subprocess,sys,tempfile,venv,zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];GATE=Path(__file__).resolve().parent
LOG=GATE/'integrity-clone-commands.jsonl'
if LOG.exists():raise SystemExit('Refusing to overwrite prior probe evidence')
env=os.environ.copy()
for name in ('PYTHONPATH','PYTHONHOME'):env.pop(name,None)
env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1')
def run(argv,cwd,code=0):
    entry=dict(argv=list(map(str,argv)),cwd=str(cwd),started_at=datetime.now(timezone.utc).isoformat())
    with LOG.open('a') as f:f.write(json.dumps(entry|{'state':'started'})+'\n')
    result=subprocess.run(entry['argv'],cwd=cwd,env=env,capture_output=True,text=True)
    with LOG.open('a') as f:f.write(json.dumps(entry|dict(state='completed',stdout=result.stdout,stderr=result.stderr,exit_code=result.returncode))+'\n')
    assert result.returncode==code,(argv,result.returncode,result.stdout,result.stderr)
    return result
def state(project):
    key=(project/'HEAD').read_text().strip()
    return json.loads((project/'history'/(key+'.json')).read_text())['state']
with tempfile.TemporaryDirectory(prefix='aa-integrity-g5-') as td:
    work=Path(td);clone=work/'separate library';unrelated=work/'unrelated work';unrelated.mkdir()
    run(['git','clone','--no-hardlinks',ROOT,clone],work)
    commit=run(['git','rev-parse','HEAD'],clone).stdout.strip()
    assert commit=='a0e93349b556709290068ef9aa8d3288de9122af'
    manifest=json.loads((GATE/'candidate.json').read_text())
    assert runpy.run_path(str(clone/'scripts/record_development.py'))['manifest']()==manifest
    runtime=work/'empty venv';venv.EnvBuilder(with_pip=False).create(runtime)
    python=runtime/'bin/python';env['PATH']=str(runtime/'bin')+os.pathsep+env['PATH']
    info=json.loads(run([python,'-c','import json,site,sys;from pathlib import Path;print(json.dumps({"executable":sys.executable,"version":sys.version,"user_site":site.ENABLE_USER_SITE,"site_packages":{p:[x.name for x in Path(p).iterdir()] for p in site.getsitepackages()}}))'],unrelated).stdout)
    assert not info['user_site'] and all(not files for files in info['site_packages'].values())
    print('independent_clone_and_runtime',json.dumps({'commit':commit,'manifest_entries':len(manifest),'runtime':info}))
    library=json.loads(run([python,'-S',clone/'scripts/check_library.py'],unrelated).stdout)
    assert library['status']=='pass' and library['skills']==7
    print('independent_library_check',json.dumps(library))
    assert run([python,'-S',clone/'scripts/aa.py','--version'],unrelated).stdout=='agent-architect 0.1.0\n'
    tests=run([python,'-S','-m','unittest','discover','-s',clone/'tests','-v'],clone)
    assert 'Ran 86 tests' in tests.stderr and tests.stderr.endswith('OK\n')
    print('independent_regression',tests.stderr.split('----------------------------------------------------------------------')[-1].strip())
    out=work/'private scenario'
    summary=json.loads(run([python,'-S',clone/'examples/order-triage/rehearse.py','--output',out],unrelated).stdout)
    assert summary['checks']==37 and not summary['failed']
    assert (summary['naive_rows'],summary['corrected_rows'])==(13,4)
    print('independent_actual_rehearsal',json.dumps(summary))
    ready=out/'ready-project';changed=out/'project';saved=state(ready)
    events=json.loads((out/'events.json').read_text());execution=[e for e in events if 'argv' in e]
    assert len(execution)==9
    assert all(all(k in e for k in ('argv','cwd','stdout','stderr','returncode')) for e in execution)
    for event in execution:
        label=event['action'].split(' ',1)[1]
        blob=ready/saved['records']['RESULT_'+label]['blob']
        assert event['stdout'].encode()==blob.read_bytes()
    print('all_nine_actual_execution_outputs_preserved',True)
    # Archive the complete fresh run before hostile probes.
    with zipfile.ZipFile(GATE/'integrity-rehearsal.zip','x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(out))
    def cli(project,*args,code=0):return run([python,'-S',clone/'scripts/aa.py','--project',project,*args],unrelated,code)
    for project in (ready,changed):assert json.loads(cli(project,'audit').stdout)['status']=='pass'
    resumed=json.loads(cli(ready,'context','urgent HANDOFF','--as-of',summary['as_of']).stdout)
    assert resumed['checkpoint']['stage']=='operate' and resumed['active_release']=='REL2'
    assert saved['records']['INC_FEED']['verification']=='EV_RECOVERED'
    assert saved['records']['EV_FAILED_RECOVERY']['status']=='fail'
    assert json.loads(cli(ready,'check','release','--handoff','HANDOFF','--environment','fixture','--as-of',summary['as_of']).stdout)['status']=='pass'
    assert json.loads(cli(changed,'check','release','--handoff','HANDOFF','--environment','fixture','--as-of',summary['as_of'],code=1).stdout)['status']=='fail'
    head=(ready/'HEAD').read_bytes()
    overwrite=run([python,'-S',clone/'examples/order-triage/rehearse.py','--output',out],unrelated,2)
    assert 'never overwritten' in overwrite.stderr and 'Traceback' not in overwrite.stderr
    assert (ready/'HEAD').read_bytes()==head
    print('expected_overwrite_error_preserves_prior_evidence',overwrite.stderr.strip())
    source=ready/saved['records']['S01']['blob'];original=source.read_bytes();source.write_bytes(original+b'\nHostile mutation\n')
    errors=[]
    for args in [('audit',),('context','CL_OWNER','--as-of',summary['as_of']),('activate','REL2','--environment','fixture','--reason','Integrity negative','--as-of',summary['as_of'],'--expect-revision',str(saved['revision']))]:
        result=cli(ready,*args,code=2);errors.append(json.loads(result.stdout))
        assert (ready/'HEAD').read_bytes()==head
    print('tampered_source_blocks_audit_context_and_activation',json.dumps(errors))
    source.write_bytes(original)
    envelope=ready/'history'/(head.decode().strip()+'.json');raw=envelope.read_bytes();value=json.loads(raw);value['actor']='forged author';envelope.write_text(json.dumps(value))
    bad_history=json.loads(cli(ready,'audit',code=2).stdout)
    print('tampered_history_rejected',json.dumps(bad_history))
    envelope.write_bytes(raw)
    assert json.loads(cli(ready,'audit').stdout)['status']=='pass'
    result=json.loads(run([python,'-S',clone/'scripts/check_council.py','G4'],unrelated).stdout)
    assert result['status']=='pass'
    assert not run(['git','status','--porcelain'],clone).stdout.strip()
    assert runpy.run_path(str(clone/'scripts/record_development.py'))['manifest']()==manifest
    print('private_projects_outside_clean_frozen_clone',True)
assert runpy.run_path(str(ROOT/'scripts/record_development.py'))['manifest']()==json.loads((GATE/'candidate.json').read_text())
print('root_frozen_manifest_preserved',True)
