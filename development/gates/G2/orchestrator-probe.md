# Orchestrator additional fault probe

Status: blocker to resolve after the frozen-candidate reviews return.

A simulated error after atomic HEAD replacement causes the caller to see an exception although the revision is already committed. The response must explicitly distinguish committed-but-durability-uncertain from precommit failure, so callers inspect state instead of retrying blindly. This is the filesystem equivalent of an uncertain external write.

Exact command, library root:

```sh
python3 - <<'PY'
import sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'src')
from agent_architect.core import Project,atomic
with tempfile.TemporaryDirectory() as d:
 p=Project(d); p.init('Probe','Scope','Owner')
 def after_replace(path,data):
  atomic(path,data)
  if path.name=='HEAD': raise OSError('simulated directory fsync failure after HEAD replacement')
 try:
  with patch('agent_architect.core.atomic', side_effect=after_replace):
   p.put({'id':'N1','type':'note','title':'Note','description':'Probe','status':'active','owner':'Owner','next_action':'Continue'},1)
 except OSError as e:
  print('OBSERVED:',str(e))
 print('REVISION_AFTER_ERROR:',p.read()['revision'])
PY
```

Observed output:

```text
OBSERVED: simulated directory fsync failure after HEAD replacement
REVISION_AFTER_ERROR: 2
```
