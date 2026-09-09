import hashlib,json,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[3];gate=Path(__file__).resolve().parent
candidate=gate/'candidate.json';manifest=json.loads(candidate.read_text())
assert hashlib.sha256(candidate.read_bytes()).hexdigest()=='0b11c98f3e77f99f304fe545ea57de34a93a5d9e5ddcabe06f8cfd045049bfaf'
assert runpy.run_path(str(root/'scripts/record_development.py'))['manifest']()==manifest
counts={}
for filename in ['integrity-audit-commands.jsonl','integrity-clone-commands.jsonl','integrity-negatives-r2-commands.jsonl','integrity-negatives-r3-commands.jsonl']:
    rows=[json.loads(x) for x in (gate/filename).read_text().splitlines()]
    assert len(rows)%2==0
    for before,after in zip(rows[::2],rows[1::2]):
        assert before['state']=='started' and after['state']=='completed'
        assert (before['argv'],before['cwd'],before['started_at'])==(after['argv'],after['cwd'],after['started_at'])
        assert all(k in after for k in ('stdout','stderr','exit_code'))
    counts[filename]=len(rows)//2
print(json.dumps({'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'entries':len(manifest),'current_manifest_matches':True,'nested_commands_with_complete_result_channels':counts,'fresh_rehearsal_archive_sha256':hashlib.sha256((gate/'integrity-rehearsal.zip').read_bytes()).hexdigest()},indent=2))
