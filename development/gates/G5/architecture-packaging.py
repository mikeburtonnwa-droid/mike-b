"""Independent YAML inspection and packaging-check negative controls, outside product tree."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime,timezone
import yaml  # Reviewer-only parser; the product does not depend on this package.

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
commands=[]
def run(argv,cwd,code):
    item=dict(argv=[str(v) for v in argv],cwd=str(cwd),started=datetime.now(timezone.utc).isoformat(),status='running')
    commands.append(item)
    log=HERE/'architecture-packaging-commands.json'
    log.write_text(json.dumps(commands,indent=2)+'\n')
    try:
        proc=subprocess.run(argv,cwd=cwd,capture_output=True,text=True)
    except Exception as exc:
        item.update(status='exception',exception=repr(exc));log.write_text(json.dumps(commands,indent=2)+'\n');raise
    item.update(status='finished',exit_code=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,finished=datetime.now(timezone.utc).isoformat())
    log.write_text(json.dumps(commands,indent=2)+'\n')
    assert proc.returncode==code,item
    return proc

workflow=yaml.load((ROOT/'.github/workflows/verify.yml').read_text(),Loader=yaml.BaseLoader)
assert set(workflow['on'])=={'push','pull_request','workflow_dispatch'}
assert workflow['on']['push']['branches']==['main']
assert workflow['permissions']=={'contents':'read'}
job=workflow['jobs']['verify']
assert job['runs-on']=='${{ matrix.os }}'
assert job['strategy']['matrix']['include']==[dict(os='ubuntu-latest',python='3.10'),dict(os='ubuntu-latest',python='3.12'),dict(os='macos-latest',python='3.12')]
assert job['strategy']['fail-fast']=='false' and job['timeout-minutes']=='10'
actions=[s for s in job['steps'] if 'uses' in s]
assert [a['uses'] for a in actions]==['actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1','actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97']
assert actions[0]['with']['persist-credentials']=='false'
assert actions[1]['with']['python-version']=='${{ matrix.python }}'
assert job['env']=={'PYTHONDONTWRITEBYTECODE':'1'}
runs=[s['run'] for s in job['steps'] if 'run' in s]
assert runs==['python -S scripts/check_library.py\npython -S scripts/aa.py --version\n','python -S -m unittest discover -s tests -v','python -S scripts/check_council.py G5','test -z "$(git status --porcelain)"']
print('PASS YAML parses; three declared jobs, official SHA pins, read-only contents, no persisted credentials, timeout and fail-fast policy match reviewed commands')
print('PASS CI verifies historical G5 integrity, not current-product council approval; final release docs separately require --current')
print(json.dumps(workflow,indent=2))

with tempfile.TemporaryDirectory(prefix='g5-architecture-packaging-') as temp:
    base=Path(temp)
    archive=base/'source.tar'
    run(['git','archive','a0e93349b556709290068ef9aa8d3288de9122af','-o',str(archive)],ROOT,0)
    tree=base/'tree';tree.mkdir()
    with tarfile.open(archive) as t:
        assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in t.getmembers())
        t.extractall(tree,filter='data')
    cmd=[sys.executable,'-S',str(tree/'scripts/check_library.py')]
    baseline=run(cmd,base,0)
    assert json.loads(baseline.stdout)['status']=='pass'
    print('PASS archived packaging baseline')
    readme=tree/'README.md';original=readme.read_text()
    readme.write_text(original+'\n[Broken reviewer probe](never-exists-for-review.md)\n')
    result=json.loads(run(cmd,base,1).stdout)
    assert result['status']=='fail' and any('never-exists-for-review.md' in e for e in result['errors'])
    print('PASS broken local destination produces structured fail and exit 1:',json.dumps(result['errors']))
    readme.write_text(original+'\n```markdown\n[Illustrative only](never-exists-for-review.md)\n```\n')
    assert json.loads(run(cmd,base,0).stdout)['status']=='pass'
    print('PASS fenced example links excluded as documented')
    readme.write_text(original)
    skill=tree/'skills/agent-architect/SKILL.md';content=skill.read_text()
    skill.write_text(content.replace('name: agent-architect','name: wrong-name',1))
    result=json.loads(run(cmd,base,1).stdout)
    assert result['status']=='fail' and any('name/directory mismatch' in e for e in result['errors'])
    print('PASS basic installed skill metadata mismatch produces structured fail and exit 1:',json.dumps(result['errors']))
    skill.write_text(content)
    assert json.loads(run(cmd,base,0).stdout)['status']=='pass'
    print('PASS restored packaging baseline')
print('PASS packaging/YAML review complete; hosted execution remains pending')
