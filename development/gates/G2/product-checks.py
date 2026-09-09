"""Independent G2 product-review evidence; all project mutations use temp dirs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CLI = ROOT / 'scripts/aa.py'
events, checks = [], []
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')


def run(args, cwd):
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)
    event = dict(command=args, cwd=str(cwd), exit_code=result.returncode,
                 stdout=result.stdout, stderr=result.stderr)
    events.append(event)
    return event


def check(name, passed, details):
    checks.append(dict(name=name, passed=bool(passed), details=details,
                       last_command_index=len(events)))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parsed(event):
    try:
        return json.loads(event['stdout'] or event['stderr'])
    except ValueError:
        return None


manifest = json.loads((OUT / 'candidate.json').read_text())
check('candidate_before', all((ROOT / p).is_file() and sha(ROOT / p) == h
                            for p, h in manifest.items()), {'entries': len(manifest)})

with tempfile.TemporaryDirectory(prefix='aa-g2-product-') as temporary:
    base = Path(temporary)
    cwd = base / 'unrelated working directory'
    cwd.mkdir()
    project = base / 'private project'
    revision = 0

    def cli(*args):
        return run([sys.executable, str(CLI), '--project', str(project), *args], cwd)

    def save(*args):
        global revision
        result = cli(*args)
        value = parsed(result)
        if result['exit_code'] != 0:
            raise RuntimeError(result)
        revision = value['revision']
        return value

    def write(name, value):
        (cwd / name).write_text(json.dumps(value), encoding='utf-8')
        return name

    result = cli('show')
    check('missing_project', result['exit_code'] == 2 and parsed(result)['status'] == 'error'
          and 'run init first' in parsed(result)['message'] and not project.exists(), parsed(result))
    result = cli('--help')
    check('help_from_unrelated_directory', result['exit_code'] == 0 and 'checkpoint' in result['stdout'],
          {'exit_code': result['exit_code'], 'checkpoint_listed': 'checkpoint' in result['stdout']})
    save('init', '--title', 'Account onboarding', '--scope', 'Provisional scope', '--owner', 'unknown')
    check('init_accepts_explicit_unknown_owner', revision == 1, {'revision': revision})
    original_head = (project / 'HEAD').read_text()
    result = cli('init', '--title', 'Again', '--scope', 'Again', '--owner', 'Again')
    check('repeat_init_preserves_project', result['exit_code'] == 2 and (project / 'HEAD').read_text() == original_head,
          parsed(result))
    result = cli('source', '--id', 'S01', '--title', 'Interview', '--file', 'missing.txt', '--kind', 'interview',
                 '--locator', 'Meeting 1', '--environment', 'operations', '--expect-revision', str(revision))
    check('missing_input_preserves_project', result['exit_code'] == 2 and (project / 'HEAD').read_text() == original_head,
          parsed(result))
    (cwd / 'interview notes.txt').write_text('Operations creates accounts.\nOwner and exception paths remain unknown.\n', encoding='utf-8')
    save('source', '--id', 'S01', '--title', 'Interview', '--file', 'interview notes.txt', '--kind', 'interview',
         '--locator', 'Meeting 1, lines 1-2', '--environment', 'operations', '--captured-on', '2026-09-01',
         '--expect-revision', str(revision))

    def claim(rid, assertion, **extra):
        return dict(id=rid, type='claim', title=rid, description='Synthetic interview interpretation',
                    status='reported', assertion=assertion, applicability='standard onboarding',
                    evidence=[dict(source='S01', locator='line 1')], **extra)

    old = claim('C01', 'Operations creates accounts')
    stale = claim('CSTALE', 'Legacy evidence remains applicable', verified_on='2026-08-01', review_due='2026-09-01',
                  verification='Synthetic observed case')
    stale['status'] = 'verified'
    note = dict(id='N01', type='note', title='Account follow-up', description='Follow-up', status='active',
                owner='unknown', next_action='Ask who owns rejected requests', depends_on=['C01'])
    issue = dict(id='I01', type='issue', title='Missing owner', description='Owner unknown', status='open',
                 critical=True, owner='unknown', next_action='Ask operations', evidence=[dict(source='S01', locator='line 2')])
    save('put', write('records.json', [old, stale, note, issue]), '--expect-revision', str(revision))
    checkpoint = dict(current_task='Map exception paths', completed=['First interview captured'],
                      unresolved=['Owner unknown', 'Exception paths missing'],
                      next_action='Ask operations for a rejected request example', relevant_ids=['C01', 'I01'], stage='discovery')
    save('checkpoint', write('checkpoint.json', checkpoint), '--expect-revision', str(revision))
    result = cli('context', '--as-of', '2026-09-09')
    resumed = parsed(result)
    check('cold_resume_and_freshness', result['exit_code'] == 0 and resumed['checkpoint'] == checkpoint
          and resumed['stage'] == 'discovery' and resumed['revision'] == 4
          and 'CSTALE: verified, freshness=stale' in resumed['warnings']
          and 'C01: reported, freshness=unknown' in resumed['warnings']
          and resumed['deployment_mode'] == 'local-simulation',
          {k: resumed[k] for k in ['revision', 'stage', 'checkpoint', 'warnings', 'deployment_mode']})
    result = cli('impact', 'S01')
    check('transitive_impact', parsed(result)['affected'] == ['C01', 'CSTALE', 'I01', 'N01'], parsed(result))
    before_invalid = (project / 'HEAD').read_text()
    result = cli('put', 'records.json', '--expect-revision', '2')
    check('stale_edit_has_recovery_instruction', result['exit_code'] == 2 and 'reread and reconcile' in parsed(result)['message']
          and (project / 'HEAD').read_text() == before_invalid, parsed(result))
    (cwd / 'syntax.json').write_text('{broken')
    result = cli('put', 'syntax.json', '--expect-revision', str(revision))
    check('malformed_json_has_structured_error', result['exit_code'] == 2 and parsed(result)['status'] == 'error', parsed(result))
    for name, data in [('null_record', None), ('nonobject_batch', [5]), ('unhashable_type', {'id': 'BAD', 'type': []})]:
        result = cli('put', write(name + '.json', data), '--expect-revision', str(revision))
        check(name + '_has_structured_error', result['exit_code'] == 2 and parsed(result) is not None,
              {'exit_code': result['exit_code'], 'structured': parsed(result) is not None,
               'stderr_last_line': result['stderr'].splitlines()[-1],
               'head_unchanged': (project / 'HEAD').read_text() == before_invalid})
    invalid_checkpoint = dict(checkpoint, relevant_ids=['MISSING'])
    result = cli('checkpoint', write('missing-ref.json', invalid_checkpoint), '--expect-revision', str(revision))
    check('checkpoint_missing_reference_rejected', result['exit_code'] == 2
          and 'missing record MISSING' in parsed(result)['message'] and (project / 'HEAD').read_text() == before_invalid,
          parsed(result))

    legacy = claim('COLD', 'retired-route')
    replacement = claim('CNEW', 'Operations owns current routing', conflicts_with=['COTHER'])
    alternative = claim('COTHER', 'Compliance owns current routing', conflicts_with=['CNEW'])
    replacement['status'] = alternative['status'] = 'disputed'
    save('put', write('replacement-conflict.json', [legacy, replacement, alternative]), '--expect-revision', str(revision))
    save('supersede', 'COLD', 'CNEW', '--reason', 'New interview interpretation', '--expect-revision', str(revision))
    result = cli('context', 'retired-route', '--as-of', '2026-09-09')
    value = parsed(result)
    ids = sorted(r['id'] for r in value['records'])
    check('replacement_context_includes_direct_conflict', {'CNEW', 'COTHER', 'S01'} <= set(ids),
          {'records': ids, 'historical': [r['id'] for r in value['historical_dependencies']], 'warnings': value['warnings']})
    result = cli('audit')
    check('completed_journey_audits', result['exit_code'] == 0 and parsed(result)['commits'] == 6,
          {k: parsed(result)[k] for k in ['status', 'commits']})
    state = parsed(cli('show'))
    blob = project / state['records']['S01']['blob']
    original = blob.read_bytes()
    blob.write_bytes(b'Synthetic tampering')
    result = cli('context', '--as-of', '2026-09-09')
    check('resume_rejects_tampered_source', result['exit_code'] == 2 and 'tampered' in parsed(result)['message'], parsed(result))
    blob.write_bytes(original)

    council_root = base / 'synthetic council'
    gate = council_root / 'development/gates/G1'
    gate.mkdir(parents=True)
    (council_root / 'scripts').mkdir()
    shutil.copy2(ROOT / 'scripts/check_council.py', council_root / 'scripts/check_council.py')
    candidate = {'development/PLAN.md': 'synthetic-plan', 'docs/CONTRACT.md': 'synthetic-contract'}
    (gate / 'candidate.json').write_text(json.dumps(candidate))
    roles = ['synthetic-a', 'synthetic-b', 'synthetic-c']

    def build_council(first_body='Verdict: APPROVE\n'):
        bodies = [first_body, 'Verdict: APPROVE\n', 'Verdict: APPROVE\n']
        reviews = []
        for role, body in zip(roles, bodies):
            path = gate / (role + '.md')
            path.write_text(body)
            reviews.append(dict(role=role, report=path.name, verdict='APPROVE', hash=sha(path)))
        decision = dict(gate='G1', verdict='PASS', candidate='candidate.json', candidate_hash=sha(gate / 'candidate.json'),
                        reviews=reviews, previous_gates=[])
        (gate / 'decision.json').write_text(json.dumps(decision))
        lines = []

        def event(sender, recipient, kind, message):
            value = dict(sequence=len(lines) + 1, time='2026-09-09T10:00:00+00:00', sender=sender, recipient=recipient,
                         kind=kind, message=message,
                         previous_hash=hashlib.sha256(lines[-1].encode()).hexdigest() if lines else None)
            lines.append(json.dumps(value))

        for role, body in zip(roles, bodies):
            event('orchestrator', role, 'dispatch', 'Review synthetic candidate.')
            event(role, 'orchestrator', 'response', body)
        event('orchestrator', 'council', 'decision', json.dumps(decision))
        (gate / 'transcript.jsonl').write_text('\n'.join(lines) + '\n')

    def council():
        return run([sys.executable, str(council_root / 'scripts/check_council.py'), 'G1'], cwd)

    build_council()
    result = council()
    check('synthetic_council_positive', result['exit_code'] == 0 and parsed(result)['reviewers'] == 3, parsed(result))
    (gate / 'synthetic-a.md').write_text('Verdict: DENY\n')
    result = council()
    check('synthetic_council_tampered_report_rejected', result['exit_code'] == 2, parsed(result))
    build_council('Verdict: DENY\n\nThe prior review said: Verdict: APPROVE\n')
    result = council()
    check('synthetic_council_explicit_denial_rejected', result['exit_code'] == 2, parsed(result))

check('candidate_after', all((ROOT / p).is_file() and sha(ROOT / p) == h for p, h in manifest.items()),
      {'entries': len(manifest)})
payload = dict(checks=checks, commands=events)
(OUT / 'product-cli-evidence.json').write_text(json.dumps(payload, indent=2) + '\n')
for result in checks:
    print(('PASS' if result['passed'] else 'FAIL') + ' ' + result['name'] + ': ' + json.dumps(result['details'], sort_keys=True))
print(json.dumps({'checks': len(checks), 'passed': sum(c['passed'] for c in checks),
                  'failed': sum(not c['passed'] for c in checks), 'commands': len(events)}, sort_keys=True))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
