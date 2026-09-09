"""Capture exact independent G4 review commands and separated outputs."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
name, *command = sys.argv[1:]
if not name.replace("-", "").isalnum() or not command:
    raise SystemExit("Usage: architecture-run.py NAME COMMAND [ARGS...]")
target = HERE / ("architecture-command-" + name + ".json")
if target.exists():
    raise SystemExit("Refusing to overwrite earlier command evidence")
started = datetime.now(timezone.utc).isoformat()
result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
target.write_text(json.dumps(dict(argv=command, cwd=str(ROOT), started=started,
    finished=datetime.now(timezone.utc).isoformat(), exit_code=result.returncode,
    stdout=result.stdout, stderr=result.stderr), indent=2)+"\n")
sys.stdout.write(result.stdout)
sys.stderr.write(result.stderr)
raise SystemExit(result.returncode)

