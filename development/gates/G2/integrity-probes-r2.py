"""Independent G2 r2 integrity probes; synthetic temporary state only."""
import hashlib
import json
import runpy
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src'))
from agent_architect.core import Invalid, Project, context, freshness, impact

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest_path = ROOT / 'development/gates/G2/candidate-r2.json'
manifest = json.loads(manifest_path.read_text())
actual = runpy.run_path(str(ROOT / 'scripts/record_development.py'))['manifest']()
assert manifest == actual
print('candidate', json.dumps({'sha256': sha(manifest_path), 'entries': len(manifest), 'matches_current': True}))
preserved = {name: sha(ROOT / 'development/gates/G2' / name)
             for name in ('candidate.json', 'integrity.md', 'integrity-commands.sh')}

def claim(rid, source='S1', **values):
    return dict(id=rid, type='claim', title=rid, description='Synthetic',
                status='reported', assertion=rid + ' assertion', applicability='standard',
                evidence=[{'source': source, 'locator': 'line 1'}]) | values

def note(rid, deps):
    return dict(id=rid, type='note', title=rid, description='Synthetic', status='active',
                owner='reviewer', next_action='Review', depends_on=deps)

with tempfile.TemporaryDirectory() as td:
    project = Project(Path(td) / 'project')
    project.init('Synthetic', 'Integrated provenance', 'reviewer')
    def put(value):
        return project.put(value, project.read()['revision'])
    for rid in ('S1', 'S2', 'S3'):
        project.source(rid, rid, (rid + ' evidence').encode(), 'document', 'synthetic/' + rid,
                       '2026-09-01', 'prod', project.read()['revision'])
    put([claim('OLD'), claim('NEW', 'S2', status='disputed', conflicts_with=['OTHER']),
         claim('OTHER', status='disputed', conflicts_with=['NEW'], depends_on=['PREREQ']),
         claim('PREREQ', status='disputed', conflicts_with=['LAST']),
         claim('LAST', 'S3', status='disputed', conflicts_with=['PREREQ'], review_due='2026-09-08'),
         note('TASKROOT', ['OLD'])])
    project.supersede('OLD', 'NEW', 'Synthetic supported replacement', project.read()['revision'])
    result = context(project.read(), 'TASKROOT', '2026-09-09')
    active = {r['id'] for r in result['records']}
    historical = {r['id'] for r in result['historical_dependencies']}
    assert active == {'S1', 'S2', 'S3', 'NEW', 'OTHER', 'PREREQ', 'LAST', 'TASKROOT'}
    assert historical == {'OLD'}
    assert any(w == 'LAST: disputed, freshness=stale' for w in result['warnings'])
    print('replacement_prerequisite_conflict_fixed_point', json.dumps({'active': sorted(active), 'historical': sorted(historical), 'stale_conflict_disclosed': True}))
    verified = claim('VERIFIED', status='verified', verified_on='2026-09-02',
                     review_due='2026-10-01', verification='Observed original scope in S1')
    put(verified)
    head = project.head()[0]
    try:
        put(verified | {'applicability': 'urgent production variant'})
    except Invalid as exc:
        assert 'applicability' in str(exc)
        print('scope_only_rewrite_rejected', str(exc))
    else:
        raise AssertionError('Scope rewrite accepted')
    assert project.head()[0] == head
    assert project.read()['records']['VERIFIED'] == verified
    variant = claim('VARIANT', applicability='urgent production variant')
    put(variant)
    assert any(w.startswith('VARIANT: reported') for w in context(project.read(), 'VARIANT', '2026-09-09')['warnings'])
    head = project.head()[0]
    try:
        project.supersede('VERIFIED', 'VARIANT', 'Different scope', project.read()['revision'])
    except Invalid as exc:
        assert 'Different applicability' in str(exc)
    else:
        raise AssertionError('Cross-scope supersession accepted')
    assert project.head()[0] == head
    print('separate_variant_and_cross_scope_rejection', True)
    observed = [freshness(claim('C'), '2026-09-09'),
                freshness(claim('C', review_due='2026-09-08'), '2026-09-09'),
                freshness(claim('C', review_due='2026-09-09'), '2026-09-09'),
                freshness(claim('C', verified_on='2026-09-10'), '2026-09-09')]
    assert observed == ['unknown', 'stale', 'current', 'future-dated']
    print('freshness_boundaries', json.dumps(observed))
    put([note('N1', ['S3']), note('N2', ['N1'])])
    assert {'N1', 'N2'} <= set(impact(project.read(), 'S3')['affected'])
    checkpoint = dict(current_task='Resolve LAST conflict', completed=['Capture'], unresolved=['LAST disputed'],
                      next_action='Inspect S3', relevant_ids=['LAST'], stage='discovery')
    project.checkpoint(checkpoint, project.read()['revision'])
    assert context(Project(project.path).read(), 'TASKROOT', '2026-09-09')['checkpoint'] == checkpoint
    print('impact_checkpoint_and_audit', project.audit()['status'])
    source = project.read()['records']['S3']
    (project.path / source['blob']).write_bytes(b'tampered')
    try:
        project.read()
    except Invalid as exc:
        assert 'tampered' in str(exc)
        print('tampered_source_rejected', True)
    else:
        raise AssertionError('Tampered source accepted')

check = runpy.run_path(str(ROOT / 'scripts/check_council.py'))['check_gate']

def council_case(name, report_candidate='candidate.json', dispatch_candidate='candidate.json',
                 verdict='APPROVE', add_example=False, header=True, expected_error=None):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        gate = root / 'development/gates/G1'
        gate.mkdir(parents=True)
        (root / 'scripts').mkdir()
        (root / 'docs').mkdir()
        shutil.copyfile(ROOT / 'scripts/record_development.py', root / 'scripts/record_development.py')
        (root / 'development/PLAN.md').write_text('Synthetic plan')
        (root / 'docs/CONTRACT.md').write_text('Changed contract')
        current = runpy.run_path(str(root / 'scripts/record_development.py'))['manifest']()
        prior = current | {'docs/CONTRACT.md': hashlib.sha256(b'Prior contract').hexdigest()}
        (gate / 'candidate.json').write_text(json.dumps(current))
        (gate / 'prior.json').write_text(json.dumps(prior))
        lines = []
        def event(sender, recipient, kind, message):
            lines.append(json.dumps(dict(sequence=len(lines) + 1, time='2026-09-09T00:00:00+00:00',
                        sender=sender, recipient=recipient, kind=kind, message=message,
                        previous_hash=hashlib.sha256(lines[-1].encode()).hexdigest() if lines else None)))
        reviews = []
        for role in ('one', 'two', 'three'):
            event('orchestrator', role, 'dispatch', 'Review ' + dispatch_candidate + ' only.')
            body = 'Verdict: ' + verdict + '\n'
            body += ('Candidate SHA-256: ' if header else 'Approved candidate hash: ') + sha(gate / report_candidate) + '\n'
            body += '\n## Findings\nReviewed ' + report_candidate + ' only.\n'
            if add_example:
                body += 'Example prior output: Verdict: APPROVE\n'
            report = gate / (role + '.md')
            report.write_text(body)
            event(role, 'orchestrator', 'response', body)
            reviews.append(dict(role=role, report=report.name, hash=sha(report), verdict='APPROVE'))
        decision = dict(gate='G1', verdict='PASS', candidate='candidate.json',
                        candidate_hash=sha(gate / 'candidate.json'), reviews=reviews, previous_gates=[])
        (gate / 'decision.json').write_text(json.dumps(decision))
        event('orchestrator', 'council', 'decision', json.dumps(decision))
        (gate / 'transcript.jsonl').write_text('\n'.join(lines) + '\n')
        try:
            outcome = check(root, 'G1', current=True)
        except ValueError as exc:
            if not expected_error or expected_error not in str(exc):
                raise
            print(name, str(exc))
        else:
            if expected_error:
                raise AssertionError(name + ' accepted')
            print(name, json.dumps({'status': outcome['status'], 'current_candidate_checked': outcome['current_candidate_checked']}))

council_case('current_candidate_approved')
council_case('original_unreviewed_candidate_rejected', 'prior.json', 'prior.json', expected_error='wrong-candidate')
council_case('wrong_report_hash_rejected', 'prior.json', expected_error='wrong-candidate')
council_case('wrong_dispatch_rejected', dispatch_candidate='prior.json', expected_error='dispatch')
council_case('missing_candidate_header_rejected', header=False, expected_error='authoritative')
council_case('denial_with_approval_example_rejected', verdict='DENY', add_example=True, expected_error='denied')
assert all(sha(ROOT / 'development/gates/G2' / name) == value for name, value in preserved.items())
assert manifest == runpy.run_path(str(ROOT / 'scripts/record_development.py'))['manifest']()
print('original_artifacts_preserved_and_candidate_unchanged', True)
