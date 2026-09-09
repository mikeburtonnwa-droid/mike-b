import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
GATE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from agent_architect.core import Project

for name in ('novice-start-commands.json','novice-resume-commands.json','rehearsal-4-events.json'):
    value=json.loads((GATE/name).read_text())
    entries=value if isinstance(value,list) else value.get('commands',[])
    print('log',json.dumps({'file':name,'type':type(value).__name__,'entries':len(entries),'keys':list(value)[:4] if isinstance(value,dict) else list(entries[0])}))
    print('log_failures',json.dumps([{'index':i,'keys':list(e),'exit':e.get('exit_code',e.get('returncode')),'command':str(e.get('command',e.get('argv',e.get('action',''))))[:180]} for i,e in enumerate(entries) if e.get('exit_code',e.get('returncode',0)) not in (0,None)]))
with tempfile.TemporaryDirectory() as td:
    base=Path(td)
    for name in ('novice-start-project.zip','novice-resume-project.zip','rehearsal-projects-r4.zip'):
        target=base/name.removesuffix('.zip')
        with zipfile.ZipFile(GATE/name) as archive:
            for item in archive.infolist():
                assert not Path(item.filename).is_absolute() and '..' not in Path(item.filename).parts
            archive.extractall(target)
        for head in sorted(target.rglob('HEAD')):
            p=Project(head.parent); state=p.read(); audit=p.audit()
            print('project',json.dumps({'archive':name,'path':str(head.parent.relative_to(target)),'audit':audit,'revision':state['revision'],'records':len(state['records']),'owner':state['owner'],'releases':list(state['releases']),'active_release':state['active_release']}))
            print('sources',json.dumps([{k:r.get(k) for k in ('id','kind','locator','environment')} for r in state['records'].values() if r['type']=='source']))
            print('queries',json.dumps([{k:r.get(k) for k in ('id','status','environment','sql','result_source','assets')} for r in state['records'].values() if r['type']=='query']))
            print('evaluations',json.dumps([{k:r.get(k) for k in ('id','status','targets','result_source','run_id','run_at')} for r in state['records'].values() if r['type']=='evaluation']))
