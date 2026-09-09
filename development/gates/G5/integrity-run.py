"""Append each review command and its unmodified process outputs immediately."""
import json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
log=Path(__file__).with_name('integrity-commands.jsonl')
command=sys.argv[1]
p=subprocess.run(command,shell=True,capture_output=True,text=True)
entry={'time':datetime.now(timezone.utc).isoformat(),'command':command,'cwd':os.getcwd(),'stdout':p.stdout,'stderr':p.stderr,'exit_code':p.returncode}
with log.open('a') as f:f.write(json.dumps(entry)+'\n')
print(p.stdout,end='');print(p.stderr,file=sys.stderr,end='')
raise SystemExit(p.returncode)
