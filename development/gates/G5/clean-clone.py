"""Independent clone and empty-venv acceptance runner. Saves evidence incrementally."""
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT=Path(__file__).resolve().parents[3]
WORK=Path(sys.argv[1]).resolve()
if WORK.exists():
 raise SystemExit('Refusing to reuse clean-clone evidence directory')
WORK.mkdir(parents=True)
LOG=Path(__file__).with_name('clean-clone-commands.json')
if LOG.exists():
 raise SystemExit('Refusing to overwrite the clean-clone command record')
commands=[]
env=os.environ.copy()
for name in ('PYTHONPATH','PYTHONHOME'):
 env.pop(name,None)
env.update(PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')

def run(argv,cwd,code=0):
 record=dict(argv=[str(x) for x in argv],cwd=str(cwd),started_at=datetime.now(timezone.utc).isoformat(),state='started')
 commands.append(record);LOG.write_text(json.dumps(commands,indent=2)+'\n')
 try:
  result=subprocess.run(record['argv'],cwd=cwd,env=env,capture_output=True,text=True)
  record.update(state='completed',stdout=result.stdout,stderr=result.stderr,returncode=result.returncode)
 finally:
  LOG.write_text(json.dumps(commands,indent=2)+'\n')
 assert result.returncode==code,record
 return result.stdout

clone=WORK/'clean library clone'
run(['git','clone','--no-hardlinks',str(ROOT),str(clone)],WORK)
commit=run(['git','rev-parse','HEAD'],clone).strip()
assert commit==run(['git','rev-parse','HEAD'],ROOT).strip()
runtime=WORK/'empty runtime'
venv.EnvBuilder(with_pip=False).create(runtime)
python=runtime/'bin/python'
unrelated=WORK/'unrelated cwd';unrelated.mkdir()
runtime_info=json.loads(run([python,'-c','import json,site,sys;from pathlib import Path;print(json.dumps({"executable":sys.executable,"version":sys.version,"user_site_enabled":site.ENABLE_USER_SITE,"site_packages":{p:[x.name for x in Path(p).iterdir()] for p in site.getsitepackages()}}))'],unrelated))
assert not runtime_info['user_site_enabled']
assert all(not value for value in runtime_info['site_packages'].values())
run([python,'-S',clone/'scripts/check_library.py'],unrelated)
assert run([python,'-S',clone/'scripts/aa.py','--version'],unrelated).strip()=='agent-architect 0.1.0'
run([python,'-S','-m','unittest','discover','-s',clone/'tests','-v'],clone)
out=WORK/'private exercise'
summary=json.loads(run([python,'-S',clone/'examples/order-triage/rehearse.py','--output',out],unrelated))
assert summary['checks']==37 and summary['failed']==[]
run([python,'-S',clone/'scripts/aa.py','--project',out/'ready-project','audit'],unrelated)
context=json.loads(run([python,'-S',clone/'scripts/aa.py','--project',out/'ready-project','context','urgent HANDOFF','--as-of',summary['as_of']],unrelated))
assert context['checkpoint']['stage']=='operate'
assert context['active_release']=='REL2'
run([python,'-S',clone/'scripts/aa.py','--project',out/'project','check','release','--handoff','HANDOFF','--environment','fixture','--as-of',summary['as_of']],unrelated,1)
before=(out/'ready-project/HEAD').read_bytes()
run([python,'-S',clone/'examples/order-triage/rehearse.py','--output',out],unrelated,2)
assert 'Traceback' not in commands[-1]['stderr']
assert (out/'ready-project/HEAD').read_bytes()==before
run([python,'-S',clone/'scripts/check_council.py','G4'],unrelated)
assert not run(['git','status','--porcelain'],clone).strip()
report=dict(status='pass',commit=commit,clone=str(clone),runtime=runtime_info,commands=len(commands),
            tests=86,rehearsal_checks=37,site_packages_disabled_for_top_level_python_commands=True,
            nested_interpreter_has_empty_site_packages=True,checkout_clean=True,
            limits='Actual local macOS clone and empty virtual environment. Hosted Linux/macOS jobs run after approved publication; no CI outcome is inferred here.')
Path(__file__).with_name('clean-clone-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
