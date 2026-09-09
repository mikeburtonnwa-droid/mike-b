"""Preserved supplemental probes: repair reviewer fixture and replay cold-resume SQL."""
import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import zipfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'src'))
from agent_architect.core import Project,Invalid

with tempfile.TemporaryDirectory(prefix='g4-architecture-supplement-') as temp:
    dest=Path(temp)/'rehearsal'
    with zipfile.ZipFile(HERE/'architecture-reproduced-projects.zip') as z:
        z.extractall(dest)
    p=Project(dest/'ready-project')
    note=dict(id='ARCH_NOTE_CONTROL',type='note',title='Valid collision control',description='Independent namespace probe',status='active',owner='architecture',next_action='none')
    p.put([note],p.read()['revision'],'architecture')
    print('PASS otherwise identical complete note saves with unused ID')
    before=p.head()
    note['id']='REL1'
    try:
        p.put([note],p.read()['revision'],'architecture')
    except Invalid as e:
        assert 'ID' in str(e) or 'release' in str(e).lower(),str(e)
        assert p.head()==before
        print('PASS complete note with REL1 ID rejected atomically:',e)
    else:
        raise AssertionError('release ID replacement succeeded')
    assert p.audit()['status']=='pass'
    print('PASS full audit after positive control and negative collision')

with zipfile.ZipFile(HERE/'novice-resume-project.zip') as z:
    key=z.read('HEAD').decode().strip()
    s=json.loads(z.read('history/'+key+'.json'))['state']
    setup=z.read(s['records']['S11']['blob']).decode()
    with sqlite3.connect(':memory:') as c:
        c.executescript(setup)
        c.row_factory=sqlite3.Row
        for qid in ['Q01','Q04','Q05']:
            q=s['records'][qid]
            rows=[dict(row) for row in c.execute(q['sql'],q['parameters'])]
            recorded=json.loads(z.read(s['records'][q['result_source']]['blob']))['rows']
            assert rows==recorded
            print('PASS archived cold-resume',qid,'independently reexecuted from captured S11; exact rows match:',json.dumps(rows))
        standard_missing=c.execute("SELECT COUNT(*) FROM intake.requests r WHERE r.urgency='standard' AND NOT EXISTS (SELECT 1 FROM finance.approvals a WHERE a.tenant=r.tenant AND a.request_id=r.request_id)").fetchone()[0]
        assert standard_missing==0 and s['records']['I07']['status']=='open'
        print('PASS missing-standard-decision case is absent and remains explicit open I07')

for view in ['current','proposed']:
    text=(HERE/('architecture-reproduced-'+view+'-map.md')).read_text()
    mermaid=text.split('```mermaid\n',1)[1].split('```',1)[0]
    assert mermaid==(HERE/(view+'-map.mmd')).read_text()
    print('PASS independently generated',view,'Mermaid exactly matches supplied rendered diagram source')

print('PASS 9 supplemental checks')
