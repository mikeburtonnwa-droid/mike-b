"""Incremental independent G5 command capture; never overwrite an earlier result."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
name, *command = sys.argv[1:]
if not name.replace('-', '').isalnum() or not command:
    raise SystemExit('Usage: architecture-run.py UNIQUE_NAME COMMAND [ARG ...]')
target = HERE / ('architecture-command-' + name + '.json')
if target.exists():
    raise SystemExit('Refusing to overwrite earlier command evidence')
record = dict(argv=command, cwd=str(ROOT), started=datetime.now(timezone.utc).isoformat(), status='running')
target.write_text(json.dumps(record, indent=2) + '\n')
result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
record.update(finished=datetime.now(timezone.utc).isoformat(), status='finished', exit_code=result.returncode,
              stdout=result.stdout, stderr=result.stderr)
target.write_text(json.dumps(record, indent=2) + '\n')
sys.stdout.write(result.stdout)
sys.stderr.write(result.stderr)
raise SystemExit(result.returncode)
