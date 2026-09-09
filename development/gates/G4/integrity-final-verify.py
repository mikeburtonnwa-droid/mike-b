import hashlib,json,runpy,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[3];gate=Path(__file__).resolve().parent
candidate=gate/'candidate.json'
actual=hashlib.sha256(candidate.read_bytes()).hexdigest()
expected='e4a716bd9181b99725a7f05c027970832f7faa7c047652824ce7f9afdf30deb9'
manifest=json.loads(candidate.read_text())
assert actual==expected
assert manifest==runpy.run_path(str(root/'scripts/record_development.py'))['manifest']()
registry=json.loads((gate/'rehearsal-evidence-hashes.json').read_text())
assert all(hashlib.sha256((gate/p).read_bytes()).hexdigest()==h for p,h in registry.items())
commit=subprocess.run(['git','rev-parse','HEAD'],cwd=root,text=True,capture_output=True,check=True).stdout.strip()
assert commit=='71afb9e4b32d6178daabb91d198098988d122119'
print(json.dumps({'candidate_sha256':actual,'candidate_entries':len(manifest),'manifest_matches_current':True,'registered_evidence_files':len(registry),'registered_evidence_hashes_match':True,'source_commit':commit},indent=2))
