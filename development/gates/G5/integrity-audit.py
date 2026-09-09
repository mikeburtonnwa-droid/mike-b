"""Independent final-gate provenance, council and packaging evidence audit."""
import copy,hashlib,json,os,runpy,shutil,subprocess,sys,tarfile,tempfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];GATE=Path(__file__).resolve().parent
LOG=GATE/'integrity-audit-commands.jsonl'
if LOG.exists():raise SystemExit('Refusing to overwrite existing evidence')
def run(argv,cwd=ROOT,code=0):
    entry=dict(argv=list(map(str,argv)),cwd=str(cwd),started_at=datetime.now(timezone.utc).isoformat())
    with LOG.open('a') as f:f.write(json.dumps(entry|{'state':'started'})+'\n')
    p=subprocess.run(entry['argv'],cwd=cwd,text=True,capture_output=True)
    with LOG.open('a') as f:f.write(json.dumps(entry|dict(state='completed',stdout=p.stdout,stderr=p.stderr,exit_code=p.returncode))+'\n')
    assert p.returncode==code,(argv,p.returncode,p.stderr,p.stdout)
    return p.stdout
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='0b11c98f3e77f99f304fe545ea57de34a93a5d9e5ddcabe06f8cfd045049bfaf'
manifest=json.loads((GATE/'candidate.json').read_text())
def frozen():
    assert sha(GATE/'candidate.json')==expected
    assert runpy.run_path(str(ROOT/'scripts/record_development.py'))['manifest']()==manifest
frozen();print('frozen_product_before',json.dumps({'candidate_sha256':expected,'entries':len(manifest)}))
assert run(['git','rev-parse','HEAD']).strip()=='a0e93349b556709290068ef9aa8d3288de9122af'
checker=runpy.run_path(str(ROOT/'scripts/check_council.py'))
accepted={'G1':'2a0f211529c7f23448d3e238ee534ec7c7eb0707','G2':'f01a6655eb0f88cc1f6ca6b455de49e920e1a1ff','G3':'bd4e40eb199b05094dc2092fc57ba6bd2a3410f6','G4':'71afb9e4b32d6178daabb91d198098988d122119'}
with tempfile.TemporaryDirectory() as td:
    work=Path(td)
    for gate,commit in accepted.items():
        decision=json.loads((ROOT/f'development/gates/{gate}/decision.json').read_text())
        result=json.loads(run([sys.executable,'-S','scripts/check_council.py',gate]))
        assert result['status']=='pass' and result['reviewers']==3
        candidate=json.loads((ROOT/f'development/gates/{gate}'/decision['candidate']).read_text())
        tar=work/(gate+'.tar');run(['git','archive','--format=tar','--output='+str(tar),commit])
        with tarfile.open(tar) as tree:
            actual={name:hashlib.sha256(tree.extractfile(name).read()).hexdigest() for name in candidate}
        assert actual==candidate
        events=[json.loads(line) for line in (ROOT/f'development/gates/{gate}/transcript.jsonl').read_text().splitlines()]
        responses=[e for e in events if e['kind']=='response']
        dissent=[]
        for e in responses:
            body=e['message'];header=body.split('\n## ',1)[0]
            if 'Verdict: EDITS' in header or 'Verdict: DENY' in header or '**EDITS**' in header or '**DENY**' in header:dissent.append(e['sequence'])
            assert any(p.read_text()==body for p in (ROOT/f'development/gates/{gate}').glob('*.md')),e['sequence']
        assert gate=='G4' or dissent
        print('accepted_gate',json.dumps({'gate':gate,'candidate':decision['candidate'],'candidate_hash':decision['candidate_hash'],'matching_source_commit':commit,'files':len(candidate),'messages':len(events),'preserved_dissent_sequences':dissent}))
    # Copy prior gate evidence only; never inspect current G5 opinions.
    base=work/'gate-negative';(base/'development/gates').mkdir(parents=True)
    for gate in accepted:shutil.copytree(ROOT/f'development/gates/{gate}',base/f'development/gates/{gate}')
    def reject(label,change):
        case=work/label;shutil.copytree(base,case);change(case)
        try:checker['check_gate'](case,'G4')
        except (ValueError,KeyError,OSError,TypeError) as error:print('council_negative',json.dumps({'case':label,'rejected':str(error)}))
        else:raise AssertionError('Council accepted '+label)
    def edit_json(root,path,fn):
        p=root/path;value=json.loads(p.read_text());fn(value);p.write_text(json.dumps(value))
    reject('candidate_tamper',lambda r:(r/'development/gates/G4/candidate.json').write_text('{}'))
    reject('report_tamper',lambda r:(r/'development/gates/G4/integrity.md').write_text('Verdict: APPROVE\n'))
    reject('missing_review',lambda r:edit_json(r,'development/gates/G4/decision.json',lambda d:d['reviews'].pop()))
    reject('predecessor_tamper',lambda r:(r/'development/gates/G3/decision.json').write_text('{}'))
    def broken_chain(r):
        p=r/'development/gates/G4/transcript.jsonl';lines=p.read_text().splitlines();event=json.loads(lines[1]);event['message']+=' tampered';lines[1]=json.dumps(event);p.write_text('\n'.join(lines)+'\n')
    reject('transcript_tamper',broken_chain)
    # A malicious local decision rewrite that keeps all hashes consistent still
    # cannot use an authoritative DENY with an APPROVE example in its body.
    def hidden_denial(r):
        directory=r/'development/gates/G4';decision=json.loads((directory/'decision.json').read_text());report=directory/'integrity.md'
        body=report.read_text().replace('Verdict: APPROVE','Verdict: DENY',1)+'\n## Example only\nVerdict: APPROVE\n'
        report.write_text(body)
        next(x for x in decision['reviews'] if x['role']=='integrity')['hash']=sha(report)
        (directory/'decision.json').write_text(json.dumps(decision))
        events=[json.loads(x) for x in (directory/'transcript.jsonl').read_text().splitlines()]
        lines=[]
        for e in events:
            if e['kind']=='response' and e['sender']=='integrity':e['message']=body
            if e['kind']=='decision':e['message']=json.dumps(decision)
            e['previous_hash']=hashlib.sha256(lines[-1].encode()).hexdigest() if lines else None
            lines.append(json.dumps(e))
        (directory/'transcript.jsonl').write_text('\n'.join(lines)+'\n')
    reject('authoritative_denial',hidden_denial)

skills=sorted((ROOT/'skills').glob('*/SKILL.md'))
assert len(skills)==7
validator=Path('/Users/michaelburton/.codex/skills/.system/skill-creator/scripts/quick_validate.py')
for skill in skills:
    output=run([sys.executable,validator,skill.parent])
    assert output=='Skill is valid!\n'
print('independent_full_skill_validation',len(skills))
evidence=json.loads((GATE/'clean-clone-commands.json').read_text())
assert len(evidence)==14
assert all(e.get('state')=='completed' and all(k in e for k in ('argv','cwd','stdout','stderr','returncode')) for e in evidence)
report=json.loads((GATE/'clean-clone-report.json').read_text())
assert report['commit']=='a0e93349b556709290068ef9aa8d3288de9122af'
assert all(not value for value in report['runtime']['site_packages'].values())
print('provided_clean_clone_evidence',json.dumps({'commands':len(evidence),'commit':report['commit'],'empty_site_packages':True,'expected_nonzero_exit_codes':[e['returncode'] for e in evidence if e['returncode']]}))
tracked=run(['git','ls-files']).splitlines()
assert not [p for p in tracked if set(Path(p).parts)&{'.env','.venv','private','scratch','__pycache__'}]
print('public_private_inventory',json.dumps({'tracked_files':len(tracked),'prohibited_private_runtime_paths':0,'synthetic_source_files':len(list((ROOT/'examples/order-triage/inputs').glob('*.md')))}))
frozen();print('frozen_product_after',True)
