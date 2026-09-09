"""Incremental, per-command release evidence. Arguments are executed without a shell."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[3]
name,*command=sys.argv[1:]
path=Path(__file__).parent/(name+'.json')
if path.exists():
 raise SystemExit('Refusing to overwrite command evidence: '+str(path))
record={'argv':command,'cwd':str(root),'started_at':datetime.now(timezone.utc).isoformat(),'state':'started'}
path.write_text(json.dumps(record,indent=2)+'\n')
try:
 result=subprocess.run(command,cwd=root,capture_output=True,text=True)
 record.update(state='completed',returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
except BaseException as exc:
 record.update(state='interrupted',error=repr(exc))
 raise
finally:
 record['finished_at']=datetime.now(timezone.utc).isoformat()
 path.write_text(json.dumps(record,indent=2)+'\n')
print(result.stdout,end='')
print(result.stderr,end='',file=sys.stderr)
raise SystemExit(result.returncode)
