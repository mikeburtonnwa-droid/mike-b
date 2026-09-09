"""Record exact development messages and generate candidate manifests (stdlib only)."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def manifest():
    excluded = {'.git', '__pycache__', '.venv', '.pytest_cache', '.DS_Store'}
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(ROOT.rglob('*')) if p.is_file()
            and not excluded.intersection(p.relative_to(ROOT).parts)
            and (p.relative_to(ROOT).parts[0] != 'development'
                 or p.relative_to(ROOT).as_posix() == 'development/PLAN.md')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['message', 'manifest'])
    parser.add_argument('gate')
    parser.add_argument('--sender', default='orchestrator')
    parser.add_argument('--recipient', default='council')
    parser.add_argument('--kind', default='dispatch')
    parser.add_argument('--file')
    parser.add_argument('--name', default='candidate.json')
    args = parser.parse_args()
    directory = ROOT / 'development' / 'gates' / args.gate
    directory.mkdir(parents=True, exist_ok=True)
    if args.action == 'manifest':
        (directory / args.name).write_text(json.dumps(manifest(), indent=2) + '\n')
        return
    log = directory / 'transcript.jsonl'
    previous = log.read_text().splitlines() if log.exists() else []
    event = dict(sequence=len(previous) + 1,
                 time=datetime.now(timezone.utc).isoformat(), sender=args.sender,
                 recipient=args.recipient, kind=args.kind,
                 message=Path(args.file).read_text(),
                 previous_hash=hashlib.sha256(previous[-1].encode()).hexdigest() if previous else None)
    with log.open('a') as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
