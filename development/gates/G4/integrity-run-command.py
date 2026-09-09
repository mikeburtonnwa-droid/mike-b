"""Retain exact review command, stdout, stderr and exit status."""
import json
import subprocess
import sys
from pathlib import Path

log = Path(__file__).with_name('integrity-commands.json')
command = sys.argv[1]
process = subprocess.run(command, shell=True, text=True, capture_output=True)
entry = dict(command=command, stdout=process.stdout, stderr=process.stderr, exit_code=process.returncode)
entries = json.loads(log.read_text()) if log.exists() else []
entries.append(entry)
log.write_text(json.dumps(entries, indent=2) + '\n')
print(process.stdout, end='')
print(process.stderr, file=sys.stderr, end='')
raise SystemExit(process.returncode)
