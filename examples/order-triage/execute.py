"""Execute the synthetic SQLite case. JSON stdout is actual observed evidence.

No Agent Architect internals are imported here. The caller saves fingerprints
before execution. The fixture and expected outcomes are versioned inputs.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shlex
import sqlite3
import sys
import uuid

ROOT = Path(__file__).resolve().parent
CRITERIA = {
    'cardinality': 'Exactly one output per supplied tenant/request',
    'isolation': 'No customer data crosses tenant boundaries',
    'routing': 'Routing dispositions match the declared fixture',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sql', choices=['naive.sql', 'routes.sql'], required=True)
    parser.add_argument('--binding', type=Path, required=True)
    parser.add_argument('--criterion', choices=sorted(CRITERIA))
    parser.add_argument('--fault', choices=['none', 'drop-approvals'], default='none')
    args = parser.parse_args()
    binding = json.loads(args.binding.read_text())
    # Establish expectations before executing the SQL.
    expected = json.loads((ROOT / 'expected.json').read_text())
    timestamp = datetime.now(timezone.utc)
    run_id = str(uuid.uuid4())
    with sqlite3.connect(':memory:') as connection:
        connection.executescript((ROOT / 'inputs/setup.sql').read_text())
        if args.fault == 'drop-approvals':
            connection.execute('DELETE FROM finance.approvals')
        connection.row_factory = sqlite3.Row
        rows = [dict(row) for row in connection.execute((ROOT / args.sql).read_text())]
    command = shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])
    common = dict(environment='fixture', run_on=timestamp.date().isoformat(), command=command)
    if not args.criterion:
        result = common | dict(exit_code=0, query_fingerprint=binding, rows=rows)
        code = 0
    else:
        observed = {
            'cardinality': sorted([[r['tenant'], r['request_id']] for r in rows]),
            'isolation': sorted([[r['tenant'], r['request_id'], r['customer_tenant']]
                                 for r in rows if r['customer_tenant'] != r['tenant']]),
            'routing': sorted([[r['tenant'], r['request_id'], r['route']] for r in rows]),
        }[args.criterion]
        code = 0 if observed == expected[args.criterion] else 1
        result = common | dict(run_id=run_id, run_at=timestamp.isoformat(), exit_code=code,
                               criterion=CRITERIA[args.criterion], expected=expected[args.criterion],
                               observed=observed, target_hashes=binding['target_hashes'],
                               brief_hash=binding['brief_hash'])
    print(json.dumps(result, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
