"""Check the locally recorded council protocol; does not attest to human identity."""
import argparse
import hashlib
import json
import re
import runpy
from datetime import datetime
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(directory, name):
    if not isinstance(name, str) or Path(name).name != name or name in {'.', '..'}:
        raise ValueError('Gate references must be local filenames')
    path = directory / name
    if path.is_symlink():
        raise ValueError('Symlinked gate artifact')
    return path


def report_header(body):
    header = body.split('\n## ', 1)[0]
    verdicts = re.findall(r'^Verdict:\s*(?:\*\*)?(APPROVE|DENY|EDITS)(?:\*\*)?\s*$', header, re.M)
    candidates = re.findall(r'^Candidate(?: manifest)? SHA-256:\s*`?([a-f0-9]{64})`?\.?\s*$', header, re.M)
    if len(verdicts) != 1 or len(candidates) != 1:
        raise ValueError('Report requires one authoritative verdict and candidate SHA-256 header')
    return verdicts[0], candidates[0]


def check_gate(root, gate, current=False, visiting=None):
    if not re.fullmatch(r'G[1-9][0-9]*', gate):
        raise ValueError('Invalid gate identifier')
    visiting = set() if visiting is None else visiting
    if gate in visiting:
        raise ValueError('Gate dependency cycle')
    visiting.add(gate)
    directory = root / 'development' / 'gates' / gate
    decision = json.loads((directory / 'decision.json').read_text())
    if decision['gate'] != gate or decision['verdict'] != 'PASS':
        raise ValueError(f'{gate}: no PASS decision')
    candidate = safe(directory, decision['candidate'])
    if sha(candidate) != decision['candidate_hash']:
        raise ValueError(f'{gate}: candidate manifest altered')
    manifest = json.loads(candidate.read_text())
    if 'development/PLAN.md' not in manifest or 'docs/CONTRACT.md' not in manifest:
        raise ValueError(f'{gate}: normative inputs missing')
    if current:
        actual = runpy.run_path(str(root / 'scripts/record_development.py'))['manifest']()
        if manifest != actual:
            raise ValueError(f'{gate}: current product differs from reviewed candidate')
    lines = (directory / 'transcript.jsonl').read_text().splitlines()
    pending, latest, dispatched, event_decisions = {}, {}, {}, []
    previous_time = None
    for i, line in enumerate(lines):
        event = json.loads(line)
        if not all(field in event for field in ('sequence', 'time', 'sender', 'recipient', 'kind', 'message', 'previous_hash')):
            raise ValueError(f'{gate}: incomplete transcript event')
        event_time = datetime.fromisoformat(event['time'])
        if event_time.tzinfo is None or (previous_time and event_time < previous_time):
            raise ValueError(f'{gate}: timestamps must be timezone-aware and ordered')
        previous_time = event_time
        previous = hashlib.sha256(lines[i-1].encode()).hexdigest() if i else None
        if event['sequence'] != i + 1 or event['previous_hash'] != previous:
            raise ValueError(f'{gate}: transcript chain/sequence invalid at {i+1}')
        if event['kind'] in ('dispatch', 'rework-dispatch'):
            if event['sender'] != 'orchestrator' or event['recipient'] in pending:
                raise ValueError(f'{gate}: overlapping or non-orchestrator dispatch')
            pending[event['recipient']] = i
            dispatched[event['recipient']] = event['message']
        if event['kind'] == 'response':
            role = event['sender']
            if role not in pending or event['recipient'] != 'orchestrator':
                raise ValueError(f'{gate}: response without matching dispatch')
            pending.pop(role)
            latest[role] = event['message']
        if event['kind'] == 'decision':
            if event['sender'] != 'orchestrator' or pending or len(latest) < 3 or i != len(lines)-1:
                raise ValueError(f'{gate}: decision must follow completed council reviews and be final')
            event_decisions.append(json.loads(event['message']))
    reviews = decision['reviews']
    if len(reviews) < 3 or len({r['role'] for r in reviews}) != len(reviews):
        raise ValueError(f'{gate}: at least three distinct reviewers required')
    if pending or len(latest) != len(reviews):
        raise ValueError(f'{gate}: missing responses or unrepresented opinions')
    for review in reviews:
        report = safe(directory, review['report'])
        if review['verdict'] != 'APPROVE' or sha(report) != review['hash']:
            raise ValueError(f'{gate}: nonapproval or altered report')
        body = report.read_text()
        if latest.get(review['role']) != body:
            raise ValueError(f'{gate}: report is not the last exact recorded response')
        verdict, reviewed_hash = report_header(body)
        if verdict != 'APPROVE' or reviewed_hash != decision['candidate_hash']:
            raise ValueError(f'{gate}: denied or wrong-candidate report')
        if decision['candidate'] not in dispatched[review['role']]:
            raise ValueError(f'{gate}: final review dispatch did not identify accepted candidate')
    if not event_decisions or event_decisions[-1] != decision:
        raise ValueError(f'{gate}: exact decision absent from transcript')
    expected_previous = [] if gate == 'G1' else [f'G{int(gate[1:])-1}']
    if [d['gate'] for d in decision['previous_gates']] != expected_previous:
        raise ValueError(f'{gate}: immediately preceding passed gate required')
    for dependency in decision['previous_gates']:
        other = dependency['gate']
        if sha(root / 'development' / 'gates' / other / 'decision.json') != dependency['hash']:
            raise ValueError(f'{gate}: previous gate decision changed')
        check_gate(root, other, False, visiting)
    visiting.remove(gate)
    return {'gate': gate, 'status': 'pass', 'messages': len(lines), 'reviewers': len(reviews),
            'current_candidate_checked': current,
            'limit': 'Recorded agreement and local integrity; does not prove review quality or message delivery.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('gate')
    parser.add_argument('--current', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(check_gate(Path(__file__).resolve().parents[1], args.gate, args.current), indent=2))
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
