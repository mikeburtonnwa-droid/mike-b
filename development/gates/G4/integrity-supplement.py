import json,sqlite3,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];GATE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from agent_architect.core import Project
with tempfile.TemporaryDirectory() as td:
    for name,sub,setup in [('novice-resume-project.zip','','S11'),('rehearsal-projects-r4.zip','ready-project','SRC_SETUP')]:
        destination=Path(td)/name
        with zipfile.ZipFile(GATE/name) as archive:archive.extractall(destination)
        p=Project(destination/sub);state=p.read()
        with sqlite3.connect(':memory:') as db:
            db.executescript((p.path/state['records'][setup]['blob']).read_text())
            results=[]
            for record in state['records'].values():
                if record['type']!='data':continue
                info=db.execute('PRAGMA '+record['schema']+'.table_info('+record['table']+')').fetchall()
                actual=[column[1] for column in sorted(info,key=lambda row:row[5]) if column[5]]
                assert actual==record['keys'],(record['id'],record['keys'],actual)
                results.append(dict(id=record['id'],keys=actual,grain=record['grain']))
            print('recorded_keys_match_SQLite_primary_keys',json.dumps({'archive':name,'assets':results}))
        if name=='novice-resume-project.zip':
            code=(p.path/state['records']['S20']['blob']).read_text()
            print('captured_novice_runner',code)
events=json.loads((GATE/'transcript.jsonl').read_text()) if False else [json.loads(x) for x in (GATE/'transcript.jsonl').read_text().splitlines()]
# Read only experiment messages; current council responses are not inspected.
selected=[e for e in events if 'novice' in e.get('sender','') or 'novice' in e.get('recipient','')]
print('experiment_message_metadata',json.dumps([{k:e.get(k) for k in ('sequence','time','sender','recipient','kind')} for e in selected]))
for stem in ('novice-start','novice-resume'):
    body=(GATE/(stem+'.md')).read_text()
    assert any(e.get('message')==body for e in selected),stem
print('experiment_reports_match_exact_recorded_messages',True)
