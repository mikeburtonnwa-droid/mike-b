"""Finish hostile probes, parsing the documented CLI error channel correctly.
The original clone run, script, archive and subprocess evidence remain intact.
"""
import hashlib,json,os,runpy,subprocess,sys,tempfile,venv,zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];GATE=Path(__file__).resolve().parent
LOG=GATE/'integrity-negatives-r2-commands.jsonl'
if LOG.exists():raise SystemExit('Refusing to overwrite prior evidence')
env=os.environ.copy()
for key in ('PYTHONPATH','PYTHONHOME'):env.pop(key,None)
env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1')
def run(argv,cwd,code=0):
    e=dict(argv=list(map(str,argv)),cwd=str(cwd),started_at=datetime.now(timezone.utc).isoformat())
    with LOG.open('a') as f:f.write(json.dumps(e|{'state':'started'})+'\n')
    p=subprocess.run(e['argv'],cwd=cwd,env=env,text=True,capture_output=True)
    with LOG.open('a') as f:f.write(json.dumps(e|dict(state='completed',stdout=p.stdout,stderr=p.stderr,exit_code=p.returncode))+'\n')
    assert p.returncode==code,(e,p.returncode,p.stdout,p.stderr)
    return p
archive=GATE/'integrity-rehearsal.zip';original_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='aa-integrity-g5-negatives-') as td:
    work=Path(td);clone=work/'library';project=work/'private project';project.mkdir()
    run(['git','clone','--no-hardlinks',ROOT,clone],work)
    assert run(['git','rev-parse','HEAD'],clone).stdout.strip()=='a0e93349b556709290068ef9aa8d3288de9122af'
    runtime=work/'empty runtime';venv.EnvBuilder(with_pip=False).create(runtime);python=runtime/'bin/python'
    with zipfile.ZipFile(archive) as z:z.extractall(project)
    ready=project/'ready-project';head=(ready/'HEAD').read_bytes()
    envelope=ready/'history'/(head.decode().strip()+'.json');raw=envelope.read_bytes();state=json.loads(raw)['state']
    summary=json.loads((project/'report.json').read_text());date=summary['as_of']
    def cli(*args,code=0):return run([python,'-S',clone/'scripts/aa.py','--project',ready,*args],work,code)
    assert json.loads(cli('audit').stdout)['status']=='pass'
    source=ready/state['records']['S01']['blob'];source_bytes=source.read_bytes();source.write_bytes(source_bytes+b'\nHostile mutation\n')
    errors=[]
    for args in [('audit',),('context','CL_OWNER','--as-of',date),('activate','REL2','--environment','fixture','--reason','Integrity negative','--as-of',date,'--expect-revision',str(state['revision']))]:
        response=cli(*args,code=2);error=json.loads(response.stderr)
        assert error['status']=='error' and 'tampered captured source' in error['message']
        assert not response.stdout and (ready/'HEAD').read_bytes()==head
        errors.append({'operation':args[0],'error':error})
    print('source_tamper_blocks_audit_context_activation',json.dumps(errors))
    source.write_bytes(source_bytes)
    forged=json.loads(raw);forged['actor']='forged author';envelope.write_text(json.dumps(forged))
    result=cli('audit',code=2);error=json.loads(result.stderr)
    assert 'hash' in error['message'].lower()
    print('history_tamper_rejected',json.dumps(error))
    envelope.write_bytes(raw)
    assert json.loads(cli('audit').stdout)['status']=='pass'
    result=run([python,'-S',clone/'examples/order-triage/rehearse.py','--output',clone/'adopter data'],work,2)
    assert 'outside the public library' in result.stderr and not (clone/'adopter data').exists()
    print('public_library_project_creation_rejected',result.stderr.strip())
    assert json.loads(cli('check','release','--handoff','HANDOFF','--environment','fixture','--as-of',date).stdout)['status']=='pass'
    assert not run(['git','status','--porcelain'],clone).stdout.strip()
    manifest=json.loads((GATE/'candidate.json').read_text())
    assert runpy.run_path(str(clone/'scripts/record_development.py'))['manifest']()==manifest
    print('independent_disposable_clone_clean_and_exact',True)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==original_hash
assert runpy.run_path(str(ROOT/'scripts/record_development.py'))['manifest']()==manifest
print('original_rehearsal_archive_and_product_preserved',True)
