# Exact executed exploratory command.
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 - <<'PY'
import copy, hashlib, json, runpy, tempfile
from pathlib import Path
from agent_architect.core import Project, Invalid, context, impact
root=Path.cwd()
manifest_path=root/'development/gates/G2/candidate.json'
m=json.loads(manifest_path.read_text())
print('manifest', json.dumps({'hash':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),'entries':len(m),'mismatches':[p for p,h in m.items() if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]}))

def claim(rid, source='S1', **kw):
    return dict(id=rid,type='claim',title=rid,description='Synthetic evidence probe',status='reported',assertion=rid+' assertion',applicability='standard',evidence=[{'source':source,'locator':'line 1'}]) | kw

def note(rid, deps):
    return dict(id=rid,type='note',title=rid,description='Synthetic note',status='active',owner='reviewer',next_action='Review',depends_on=deps)

with tempfile.TemporaryDirectory() as td:
    base=Path(td)
    p=Project(base/'project')
    p.init('Synthetic review','Provenance probes','reviewer')
    def put(records): return p.put(records,p.read()['revision'])
    original=base/'original.txt'
    original.write_bytes(b'Original captured content\n')
    p.source('S1','Original',original.read_bytes(),'document',str(original),'2026-09-01','prod',1)
    original.write_bytes(b'Edited original\n')
    source=p.read()['records']['S1']
    assert (p.path/source['blob']).read_bytes()==b'Original captured content\n'
    print('source_snapshot_survives_original_edit', True)
    verified=claim('V',status='verified',verified_on='2026-09-02',review_due='2026-09-08',verification='Observed S1 line 1')
    put(verified)
    vctx=context(p.read(),'V','2026-09-09')
    print('stale_verified_warning', [w for w in vctx['warnings'] if w.startswith('V:')])
    before=p.head()[0]
    try: put(claim('BAD',status='verified'))
    except Invalid as exc: print('verified_missing_metadata_rejected',str(exc))
    assert p.head()[0]==before
    before=p.head()[0]
    try: put([claim('ONE',conflicts_with=['TWO']),claim('TWO')])
    except Invalid as exc: print('unilateral_conflict_rejected',str(exc))
    assert p.head()[0]==before
    put([claim('OLD'),claim('NEW',status='disputed',conflicts_with=['OTHER']),claim('OTHER',status='disputed',conflicts_with=['NEW']),note('TASKROOT',['OLD'])])
    p.supersede('OLD','NEW','Synthetic replacement',p.read()['revision'])
    result=context(p.read(),'TASKROOT','2026-09-09')
    ids={r['id'] for r in result['records']}
    print('replacement_conflict_context',json.dumps({'active':sorted(ids),'historical':[r['id'] for r in result['historical_dependencies']],'new_conflicts_with':p.read()['records']['NEW']['conflicts_with'],'other_included':'OTHER' in ids}))
    old=copy.deepcopy(p.read()['records']['V'])
    changed=old | {'applicability':'urgent production variant','review_due':'2026-10-01'}
    put(changed)
    new=p.read()['records']['V']
    print('verified_scope_rewrite',json.dumps({'old_applicability':old['applicability'],'new_applicability':new['applicability'],'status':new['status'],'verification_unchanged':old['verification']==new['verification'],'supersession_link':new.get('supersedes'),'warnings':[w for w in context(p.read(),'V','2026-09-09')['warnings'] if w.startswith('V:')]}))
    put([note('N1',['S1']),note('N2',['N1'])])
    affected=impact(p.read(),'S1')['affected']
    assert {'N1','N2'}<=set(affected)
    print('transitive_impact',json.dumps(affected))
    before=p.head()[0]
    try: put([note('X',['Y']),note('Y',['X'])])
    except Invalid as exc: print('dependency_cycle_rejected',str(exc))
    assert p.head()[0]==before
    print('positive_history_audit',p.audit()['status'])
    (p.path/source['blob']).write_bytes(b'tampered')
    try: p.read()
    except Invalid as exc: print('source_tampering_rejected',str(exc))

with tempfile.TemporaryDirectory() as td:
    fake=Path(td)
    gate=fake/'development/gates/G1'
    gate.mkdir(parents=True)
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    prior={'development/PLAN.md':'a'*64,'docs/CONTRACT.md':'b'*64}
    current=prior | {'docs/CONTRACT.md':'c'*64}
    (gate/'prior.json').write_text(json.dumps(prior))
    (gate/'candidate.json').write_text(json.dumps(current))
    lines=[]
    def message(sender,recipient,kind,body):
        event=dict(sequence=len(lines)+1,time='2026-09-09T00:00:00+00:00',sender=sender,recipient=recipient,kind=kind,message=body,previous_hash=hashlib.sha256(lines[-1].encode()).hexdigest() if lines else None)
        lines.append(json.dumps(event))
    reviews=[]
    for role in ['one','two','three']:
        message('orchestrator',role,'dispatch','Review prior.json only. SHA256 '+sha(gate/'prior.json'))
        body='Verdict: APPROVE\nApproved prior.json only. SHA256 '+sha(gate/'prior.json')+'\n'
        report=gate/(role+'.md')
        report.write_text(body)
        message(role,'orchestrator','response',body)
        reviews.append(dict(role=role,report=report.name,hash=sha(report),verdict='APPROVE'))
    decision=dict(gate='G1',verdict='PASS',candidate='candidate.json',candidate_hash=sha(gate/'candidate.json'),reviews=reviews,previous_gates=[])
    (gate/'decision.json').write_text(json.dumps(decision))
    message('orchestrator','council','decision',json.dumps(decision))
    (gate/'transcript.jsonl').write_text('\n'.join(lines)+'\n')
    check=runpy.run_path(str(root/'scripts/check_council.py'))['check_gate']
    print('unreviewed_candidate_gate',json.dumps(check(fake,'G1')))
PY

# Exact executed isolation/current-candidate command.
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 - <<'PY'
import hashlib, json, runpy, shutil, tempfile
from pathlib import Path
from agent_architect.core import Project, context
root=Path.cwd()
with tempfile.TemporaryDirectory() as td:
    p=Project(Path(td)/'project')
    p.init('Synthetic','Scope rewrite','reviewer')
    p.source('S','Evidence',b'Original scope only','document','synthetic','2026-09-01','prod',1)
    c=dict(id='C',type='claim',title='Scoped claim',description='Synthetic',status='verified',assertion='Operations owns the process',applicability='standard',verified_on='2026-09-02',review_due='2026-10-01',verification='Observed original scope in S',evidence=[{'source':'S','locator':'line 1'}])
    p.put(c,2)
    p.put(c | {'applicability':'urgent production variant'},3)
    print('scope_only_rewrite',json.dumps({'saved_revision':p.read()['revision'],'claim':p.read()['records']['C'],'warnings':context(p.read(),'C','2026-09-09')['warnings']}))
with tempfile.TemporaryDirectory() as td:
    fake=Path(td)
    gate=fake/'development/gates/G1'
    gate.mkdir(parents=True)
    (fake/'scripts').mkdir()
    (fake/'docs').mkdir()
    shutil.copyfile(root/'scripts/record_development.py',fake/'scripts/record_development.py')
    (fake/'development/PLAN.md').write_text('Synthetic plan')
    (fake/'docs/CONTRACT.md').write_text('Changed contract not reviewed')
    current=runpy.run_path(str(fake/'scripts/record_development.py'))['manifest']()
    prior=current | {'docs/CONTRACT.md':hashlib.sha256(b'Prior reviewed contract').hexdigest()}
    (gate/'candidate.json').write_text(json.dumps(current))
    (gate/'prior.json').write_text(json.dumps(prior))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    lines=[]
    def event(sender,recipient,kind,message):
        lines.append(json.dumps(dict(sequence=len(lines)+1,time='2026-09-09T00:00:00+00:00',sender=sender,recipient=recipient,kind=kind,message=message,previous_hash=hashlib.sha256(lines[-1].encode()).hexdigest() if lines else None)))
    reviews=[]
    for role in ['one','two','three']:
        event('orchestrator',role,'dispatch','Review prior.json only: '+sha(gate/'prior.json'))
        body='Verdict: APPROVE\nReviewed prior.json only: '+sha(gate/'prior.json')+'\n'
        report=gate/(role+'.md')
        report.write_text(body)
        event(role,'orchestrator','response',body)
        reviews.append(dict(role=role,report=report.name,hash=sha(report),verdict='APPROVE'))
    decision=dict(gate='G1',verdict='PASS',candidate='candidate.json',candidate_hash=sha(gate/'candidate.json'),reviews=reviews,previous_gates=[])
    (gate/'decision.json').write_text(json.dumps(decision))
    event('orchestrator','council','decision',json.dumps(decision))
    (gate/'transcript.jsonl').write_text('\n'.join(lines)+'\n')
    check=runpy.run_path(str(root/'scripts/check_council.py'))['check_gate']
    print('unreviewed_candidate_with_current_check',json.dumps(check(fake,'G1',current=True)))
PY
nl -ba src/agent_architect/core.py | sed -n '333,360p;423,470p'
nl -ba scripts/check_council.py | sed -n '20,105p'
