"""Independent G5 frozen clone and empty-runtime verification, with incremental evidence."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
COMMIT='a0e93349b556709290068ef9aa8d3288de9122af'
manifest=json.loads((HERE/'candidate.json').read_text())
commands=[]
checks=[]

def save():
    (HERE/'architecture-clone-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    (HERE/'architecture-clone-checks.json').write_text(json.dumps(checks,indent=2)+'\n')

def run(argv,cwd,env,expected=0):
    item=dict(argv=[str(a) for a in argv],cwd=str(cwd),environment=env,
              started=datetime.now(timezone.utc).isoformat(),status='running')
    commands.append(item)
    save()
    try:
        proc=subprocess.run(argv,cwd=cwd,env=env,capture_output=True,text=True)
    except Exception as exc:
        item.update(status='exception',exception=repr(exc),finished=datetime.now(timezone.utc).isoformat())
        save()
        raise
    item.update(stdout=proc.stdout,stderr=proc.stderr,exit_code=proc.returncode,
                status='finished',finished=datetime.now(timezone.utc).isoformat())
    save()
    assert proc.returncode==expected,(item['argv'],proc.returncode,proc.stdout,proc.stderr)
    return proc

def check(name,condition,detail=None):
    checks.append(dict(name=name,passed=bool(condition),detail=detail))
    save()
    print(('PASS ' if condition else 'FAIL ')+name+(': '+json.dumps(detail) if detail is not None else ''))
    assert condition,name

with tempfile.TemporaryDirectory(prefix='g5-architecture-') as tmp:
    base=Path(tmp)
    home=base/'empty home';home.mkdir()
    scratch=base/'temp';scratch.mkdir()
    clone=base/'independent clone'
    env=dict(PATH='/usr/bin:/bin:/usr/sbin:/sbin',HOME=str(home),TMPDIR=str(scratch),
             PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',LC_ALL='C',GIT_CONFIG_NOSYSTEM='1',GIT_TERMINAL_PROMPT='0')
    run(['/usr/bin/git','clone','--no-local','--no-checkout',str(ROOT),str(clone)],base,env)
    run(['/usr/bin/git','checkout','--detach',COMMIT],clone,env)
    got=run(['/usr/bin/git','rev-parse','HEAD'],clone,env).stdout.strip()
    check('independent clone is exact frozen commit',got==COMMIT,got)
    hashes={k:hashlib.sha256((clone/k).read_bytes()).hexdigest() for k in manifest}
    check('all 72 candidate product files match clone',hashes==manifest,len(hashes))
    check('clone starts clean',run(['/usr/bin/git','status','--porcelain'],clone,env).stdout=='')
    check('clone object store has no alternates',not (clone/'.git/objects/info/alternates').exists())
    venv=base/'empty runtime'
    run([sys.executable,'-m','venv','--without-pip',str(venv)],base,env)
    python=venv/'bin/python'
    env['PATH']=str(venv/'bin')+':/usr/bin:/bin:/usr/sbin:/sbin'
    runtime=run([str(python),'-c','import importlib.util,json,platform,site,sys; from pathlib import Path; print(json.dumps(dict(executable=sys.executable,version=sys.version,platform=platform.platform(),prefix=sys.prefix,base_prefix=sys.base_prefix,user_site_enabled=site.ENABLE_USER_SITE,site_packages={p:sorted(x.name for x in Path(p).iterdir()) for p in site.getsitepackages()},pip_available=importlib.util.find_spec("pip") is not None)))'],base,env)
    runtime=json.loads(runtime.stdout)
    check('nested interpreter uses empty virtual environment without pip or user site',runtime['prefix']!=runtime['base_prefix'] and not runtime['user_site_enabled'] and not runtime['pip_available'] and all(not x for x in runtime['site_packages'].values()),runtime)
    version=run([str(python),'-S',str(clone/'scripts/aa.py'),'--version'],base,env)
    check('CLI version works from unrelated cwd without project',version.stdout=='agent-architect 0.1.0\n' and version.stderr=='',version.stdout.strip())
    missing=run([str(python),'-S',str(clone/'scripts/aa.py'),'--project',str(base/'absent'),'show'],base,env,2)
    check('missing project has structured exit 2 without traceback',json.loads(missing.stderr)['status']=='error' and not missing.stdout and 'Traceback' not in missing.stderr)
    noargs=run([str(python),'-S',str(clone/'scripts/aa.py')],base,env,2)
    check('missing CLI arguments preserve parser exit 2',not noargs.stdout and 'required' in noargs.stderr and 'Traceback' not in noargs.stderr)
    library=json.loads(run([str(python),'-S','scripts/check_library.py'],clone,env).stdout)
    check('packaging links and seven basic skill metadata checks pass',library['status']=='pass' and library['skills']==7,library)
    suite=run([str(python),'-S','-m','unittest','discover','-s','tests','-v'],clone,env)
    check('complete regression runs in empty environment','Ran 86 tests' in suite.stderr and suite.stderr.rstrip().endswith('OK'),suite.stderr.splitlines()[-4:])
    out=base/'actual rehearsal'
    rehearsal=run([str(python),'-S',str(clone/'examples/order-triage/rehearse.py'),'--output',str(out)],base,env)
    report=json.loads(rehearsal.stdout)
    check('independent actual SQLite rehearsal passes all 37 assertions',report['checks']==37 and report['failed']==[] and report['naive_rows']==13 and report['corrected_rows']==4,report)
    for name in ['report.json','checks.json','events.json','change-impact.json','resume-context.json']:
        shutil.copyfile(out/name,HERE/('architecture-clone-rehearsal-'+name))
    shutil.make_archive(str(HERE/'architecture-clone-rehearsal'),'zip',out)
    for name in ['ready-project','project']:
        audit=json.loads(run([str(python),'-S',str(clone/'scripts/aa.py'),'--project',str(out/name),'audit'],base,env).stdout)
        check(name+' retained project audits through unrelated-cwd CLI',audit['status']=='pass',audit)
    ready=run([str(python),'-S',str(clone/'scripts/aa.py'),'--project',str(out/'ready-project'),'check','release','--handoff','HANDOFF','--environment','fixture','--as-of',report['as_of']],base,env)
    changed=run([str(python),'-S',str(clone/'scripts/aa.py'),'--project',str(out/'project'),'check','release','--handoff','HANDOFF','--environment','fixture','--as-of',report['as_of']],base,env,1)
    check('CLI differentiates passing readiness and deliberate dependency failure',json.loads(ready.stdout)['status']=='pass' and json.loads(changed.stdout)['status']=='fail' and ready.stderr==changed.stderr=='')
    before={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
    overwrite=run([str(python),'-S',str(clone/'examples/order-triage/rehearse.py'),'--output',str(out)],base,env,2)
    after={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
    check('existing output rejection is concise exit 2 and byte-preserving',before==after and not overwrite.stdout and 'never overwritten' in overwrite.stderr and 'Traceback' not in overwrite.stderr,overwrite.stderr.strip())
    forbidden=clone/'reviewer-must-not-create'
    internal=run([str(python),'-S',str(clone/'examples/order-triage/rehearse.py'),'--output',str(forbidden)],base,env,2)
    check('example rejects project inside library without creating directory',not forbidden.exists() and 'outside the public library' in internal.stderr and 'Traceback' not in internal.stderr,internal.stderr.strip())
    history=json.loads(run([str(python),'-S','scripts/check_council.py','G4'],clone,env).stdout)
    check('recorded G4 council and G1-G3 predecessor chain pass',history['status']=='pass' and history['reviewers']==3 and history['current_candidate_checked'] is False,history)
    drift=run([str(python),'-S','scripts/check_council.py','G4','--current'],clone,env,2)
    check('historical approval does not approve current changed product','current product differs from reviewed candidate' in json.loads(drift.stdout)['message'],json.loads(drift.stdout))
    pending=run([str(python),'-S','scripts/check_council.py','G5','--current'],clone,env,2)
    check('pending G5 does not falsely pass before final decision','G5/decision.json' in json.loads(pending.stdout)['message'],json.loads(pending.stdout))
    syntax=run([str(python),'-S','-c','import ast,json; from pathlib import Path; paths=[p for d in ["src","scripts","tests","examples"] for p in Path(d).rglob("*.py")]; [ast.parse(p.read_text(),filename=str(p),feature_version=(3,10)) for p in paths]; print(json.dumps(dict(python_310_syntax_files=len(paths),status="pass")))'],clone,env)
    check('product Python parses under 3.10 grammar',json.loads(syntax.stdout)['status']=='pass',json.loads(syntax.stdout))
    check('all verification leaves tracked checkout clean',run(['/usr/bin/git','status','--porcelain'],clone,env).stdout=='')
    check('candidate hashes unchanged after clone verification',all(hashlib.sha256((clone/k).read_bytes()).hexdigest()==v for k,v in manifest.items()))
    summary=dict(status='pass',commit=COMMIT,checks=len(checks),commands=len(commands),runtime=runtime,
                 limits='Actual local macOS Python 3.12 execution only. Python 3.10 grammar is not execution proof. Hosted Linux/macOS matrix and final G5 decision are pending publication.')
    (HERE/'architecture-clone-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
