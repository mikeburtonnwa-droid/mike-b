Verdict: EDITS
Candidate SHA-256: b31b54410b38b01152facc471906a8c6d09bb392ae22513787bcd17c64d3e5fe

# G3 architecture and operations re-review, revision 2

Date: 2026-09-09  
Candidate: `development/gates/G3/candidate-r2.json`  
Remit: architecture/evaluation, release and incident predicates, malformed inputs and persistence integration.

G3 remains blocked by one evaluation replay defect. All 20 original scenarios pass after adapting their captured result wrappers to the revised protocol. The supplied 78-test suite passes. Four additional probes exercise same-day run replay; two reveal that an older successful result can still hide a later failure.

## Findings

1. **BLOCKER — Re-importing an old passing result gives it a new run order and bypasses the later-failure protection. Original finding 1 is only partially resolved.**  
   Requirements: R06, R07, R08; the revised contract says a later matching failure blocks until a subsequent matching pass resolves it.  
   Evidence: `src/agent_architect/workflow.py:317` assigns a fresh `recorded_revision` whenever `evaluate` creates a new evaluation ID. Lines 304–305 only reject an existing record/release ID; the same previously evaluated result source can be imported again. Readiness at line 369 and recovery verification at line 463 then order same-day runs by that new recorded revision.

   The independent readiness probe records an initial pass, then a failing run on the same date. Readiness correctly fails. It then calls `evaluate` with a new evaluation ID but the original `RESULT_EV1` source, unchanged target/brief hashes, unchanged criterion and unchanged run date. No new execution or result capture occurs. The operation succeeds, and readiness becomes pass with `REPLAY_OLD_PASS` selected.

   The incident probe reproduces the consequence through an actual transition: an old recovery pass correctly cannot close the incident after a later failed recovery check. Re-importing that exact old recovery source as `REPLAY_RECOVERY` then allows closure and advances HEAD.

   Required correction: give captured runs a stable identity/order that survives re-import. Reusing already recorded execution evidence must be rejected or handled idempotently without promoting it to a newer run. Account for content-addressed source aliases so changing the source ID alone cannot manufacture a later run. A subsequent successful execution with new run evidence must still be able to resolve a failure. Add release/readiness and incident regressions for these replay sequences; document the run identity and ordering contract.

2. **RESOLVED — Original finding 2: cross-collection stable-ID collisions.**  
   R03/R06/R07. The original note, source and evaluation collision probes now reject `REL1` with HEAD unchanged and no duplicate namespace entry. The supplied new regression also checks the reverse creation order and direct state validation. The guards and global uniqueness validation address the original defect.

3. **RESOLVED — Original finding 3: incident evidence from after the assessment date.**  
   R08. Shared `applicable` now walks relevant captured sources, including brief evidence, and rejects sources captured after the as-of date. The original future-captured recovery probe now leaves the incident open with HEAD unchanged. The valid recovery control still closes successfully and audits as pass.

No nonblocking findings are raised.

## Integration and requirement coverage

The revised latest-result selection correctly blocks ordinary later failures, rejects release creation/activation while blocked, and accepts a genuinely subsequent passing run in the original scenario. The remaining defect is specifically promotion of an already captured old run through a new evaluation record.

All original persistence and lifecycle controls remain successful: simulation labels, immutable release snapshots, informational note drift, dependency-change rollback rejection, stale-revision rejection, pre-HEAD failure atomicity, explicit post-HEAD commit uncertainty, and structured malformed-input failures.

The architecture and operations skills were inspected with the revised contract and records protocol. They instruct users to retain failures, capture pre-run target/brief hashes and require new evaluation after changes. The replay behavior contradicts that stated run-order policy.

The full suite additionally verifies the query-fingerprint/bind-query protocol using actual SQLite fixture execution, immutable executed query definitions, brief changes, new consequential scope, current coverage and captured data provenance. These support R01–R06 integration; they do not remove the R07/R08 replay blocker. R09/R10 council behavior is unchanged by this re-review's probe artifacts. G4's independent stakeholder/fresh-context rehearsal and G5 packaging/sign-off remain later work.

## Exact commands and relevant results

Working directory:

`/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`

All shell commands exited 0 except the revised independent probe command, which exited 1 for its two failed protections.

### Inspection and supplied suite

```sh
cat development/gates/G3/rework.md docs/CONTRACT.md docs/RECORDS.md src/agent_architect/schema.py && git diff -- src/agent_architect/core.py src/agent_architect/cli.py && cat skills/architecture-delivery/SKILL.md skills/operations-review/SKILL.md
cat src/agent_architect/workflow.py tests/support.py && python3 -m unittest discover -s tests -v
nl -ba src/agent_architect/workflow.py | sed -n '243,465p' && nl -ba src/agent_architect/workflow.py | sed -n '478,533p' && cat skills/architecture-delivery/SKILL.md skills/operations-review/SKILL.md
cat tests/test_g3_regressions.py
```

Relevant suite output:

```text
Ran 78 tests in 1.749s

OK
```

The full test-run output is retained in `development/gates/G3/architecture-suite-r2.txt`. The supplied same-day test covers different run records ordered by revision, but does not re-import a previously used result source after a failure.

### Candidate and original-artifact verification

The following Python command ran after the regression-file inspection above:

```sh
python3 - <<'PY'
import hashlib,json,runpy
from pathlib import Path
r=Path.cwd(); p=r/'development/gates/G3/candidate-r2.json'; m=json.loads(p.read_text())
print('candidate_sha256='+hashlib.sha256(p.read_bytes()).hexdigest())
print('candidate_entries='+str(len(m)))
print('current_manifest_matches='+str(m==runpy.run_path(str(r/'scripts/record_development.py'))['manifest']()))
for name in ['architecture.md','architecture-probes.py','architecture-probes.txt']:
    p=r/'development/gates/G3'/name
    print(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+name)
PY
```

Exact output:

```text
candidate_sha256=b31b54410b38b01152facc471906a8c6d09bb392ae22513787bcd17c64d3e5fe
candidate_entries=43
current_manifest_matches=True
4b75e20e41e70f4a50728d5c805f19c207b96531e35add35da2a02b1ed471c4a  architecture.md
ddd1b4c64976ce111d23cb9e04288b054fb6292bf1fe8dd47928cfa452617d9f  architecture-probes.py
e88cb49a36f47e370678042f32a28fde1afdaf69926fa126cf8e8558cec742b9  architecture-probes.txt
```

### Revised independent probes

The original harness, report and output were preserved. The adapted harness uses the revised synthetic helper for standard evaluations and adds `brief_hash` to its manually constructed recovery-result wrapper. All original negative scenarios remain. Its additional replay probes import the original captured source without capturing or executing a new run.

Exact command:

```sh
python3 development/gates/G3/architecture-probes-r2.py
```

Exit status: 1. Exact output, also retained in `development/gates/G3/architecture-probes-r2.txt`:

```text
{"expected": "local simulation, immutable snapshot, no critical drift", "observed": {"active": "REL1", "audit": "pass", "changed": [], "mode": "local-simulation", "snapshot_unchanged": true}, "passed": true, "probe": "release_activation_and_note"}
{"expected": "reject and leave HEAD unchanged", "observed": {"error": "Activation blocked: REQ: no passing applicable evaluation of criterion and implementing components; changed COMP", "head_unchanged": true, "rejected": true}, "passed": true, "probe": "changed_dependency_rollback"}
{"expected": "original release unchanged", "observed": true, "passed": true, "probe": "snapshot_after_component_change"}
{"expected": "reject globally reused stable ID", "observed": {"error": "Stable ID already belongs to a release", "head_unchanged": true, "id_in_records_and_releases": false, "rejected": true}, "passed": true, "probe": "release_id_collision_put"}
{"expected": "reject globally reused stable ID", "observed": {"error": "ID already exists: REL1", "head_unchanged": true, "id_in_records_and_releases": false, "rejected": true}, "passed": true, "probe": "release_id_collision_source"}
{"expected": "reject globally reused stable ID", "observed": {"error": "Evaluation ID already exists; append a new run", "head_unchanged": true, "id_in_records_and_releases": false, "rejected": true}, "passed": true, "probe": "release_id_collision_evaluate"}
{"expected": "fail readiness until a subsequent passing run resolves the failure", "observed": {"later_result": "fail", "readiness": "fail", "selected": []}, "passed": true, "probe": "later_failed_critical_run"}
{"expected": "reject and leave HEAD unchanged", "observed": {"error": "Release blocked: REQ: no passing applicable evaluation of criterion and implementing components", "head_unchanged": true, "rejected": true}, "passed": true, "probe": "release_after_later_failed_run"}
{"expected": "new passing run restores readiness", "observed": {"selected": ["RECOVERED_RUN"], "status": "pass"}, "passed": true, "probe": "passing_run_after_failure"}
{"expected": "reject and leave HEAD unchanged", "observed": {"error": "Activation blocked: REQ: no passing applicable evaluation of criterion and implementing components", "head_unchanged": true, "rejected": true}, "passed": true, "probe": "activate_after_later_failed_run"}
{"expected": "reject and leave HEAD unchanged", "observed": {"error": "Incident verification failed, expired, changed, premature or environment-mismatched", "head_unchanged": true, "rejected": true}, "passed": true, "probe": "incident_future_captured_evidence"}
{"expected": "incident remains open", "observed": "open", "passed": true, "probe": "incident_future_capture_status"}
{"expected": "close with applicable recovery evidence", "observed": {"audit": "pass", "status": "closed"}, "passed": true, "probe": "valid_incident_recovery"}
{"expected": "reject and leave HEAD unchanged", "observed": {"error": "Stale revision: expected 4, current 5; reread and reconcile", "head_unchanged": true, "rejected": true}, "passed": true, "probe": "stale_release_revision"}
{"expected": "unapplied release failure preserves history", "observed": {"audit": "pass", "error": true, "release_absent": true, "unchanged": true}, "passed": true, "probe": "pre_head_release_fault"}
{"expected": "explicit visible local-simulation commit uncertainty", "observed": {"commit_matches": true, "mode": "local-simulation", "present": true, "status": "committed-durability-uncertain"}, "passed": true, "probe": "post_head_release_fault"}
{"expected": "later same-day failure blocks readiness", "observed": {"outcome": "fail", "status": "fail"}, "passed": true, "probe": "same_day_failure_before_replay"}
{"expected": "re-importing the original result must not resolve a later failed run", "observed": {"latest_failed_run": "SAME_DAY_FAIL", "original_source": "RESULT_EV1", "readiness": "pass", "replay_rejected": false, "selected": ["REPLAY_OLD_PASS"]}, "passed": false, "probe": "old_pass_reimport_after_same_day_failure"}
{"expected": "reject and leave HEAD unchanged", "observed": {"error": "Use the latest matching recovery evaluation; an earlier pass cannot hide a later result", "head_unchanged": true, "rejected": true}, "passed": true, "probe": "old_recovery_after_same_day_failure"}
{"expected": "reject and leave HEAD unchanged", "observed": {"head_unchanged": false, "rejected": false}, "passed": false, "probe": "old_recovery_reimport"}
{"expected": "exit 2 JSON error without mutation", "observed": {"exit": 2, "head_unchanged": true, "json_error": true}, "passed": true, "probe": "malformed_evaluation_20"}
{"expected": "exit 2 JSON error without mutation", "observed": {"exit": 2, "head_unchanged": true, "json_error": true}, "passed": true, "probe": "malformed_evaluation_21"}
{"expected": "exit 2 JSON error without mutation", "observed": {"exit": 2, "head_unchanged": true, "json_error": true}, "passed": true, "probe": "malformed_evaluation_22"}
{"expected": "exit 2 JSON error without mutation", "observed": {"exit": 2, "head_unchanged": true, "json_error": true}, "passed": true, "probe": "malformed_evaluation_23"}
{"failed": 2, "passed": 22, "total": 24}
```

### Final candidate and preservation verification

```sh
python3 - <<'PY'
import hashlib,json,runpy
from pathlib import Path
r=Path.cwd(); m=json.loads((r/'development/gates/G3/candidate-r2.json').read_text())
print('final_current_manifest_matches='+str(m==runpy.run_path(str(r/'scripts/record_development.py'))['manifest']()))
for name in ['architecture.md','architecture-probes.py','architecture-probes.txt','architecture-probes-r2.py','architecture-probes-r2.txt','architecture-suite-r2.txt']:
    p=r/'development/gates/G3'/name
    print(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+name)
PY
```

Exact output:

```text
final_current_manifest_matches=True
4b75e20e41e70f4a50728d5c805f19c207b96531e35add35da2a02b1ed471c4a  architecture.md
ddd1b4c64976ce111d23cb9e04288b054fb6292bf1fe8dd47928cfa452617d9f  architecture-probes.py
e88cb49a36f47e370678042f32a28fde1afdaf69926fa126cf8e8558cec742b9  architecture-probes.txt
3ab25a2807c4287456f09591b3d7dcc984479ba323b233948e47db6095263f9f  architecture-probes-r2.py
ed203acb68f148d9106cd7c06d23c82cc7d0b4c3247a82a6348f2d563e5d2493  architecture-probes-r2.txt
d515f2fdf79e005afdf2b6854dfe8a13703494ecf8e7de9cf623b6ff66cc2d93  architecture-suite-r2.txt
```

## Limits

All test projects were temporary and synthetic. Only separate reviewer artifacts were authored in the assigned gate directory. The original artifacts are unchanged, the product manifest matches the candidate, and no other current reviewer report text was inspected. No side-channel communication or delegation occurred.

These checks establish selected local structural and operational behavior, not source truth, actual deployment, stakeholder completeness, administrator-resistant attestation, power-loss durability or scalability. The replay defect requires no forged hashes or edited evidence: it uses the supported evaluate operation on an existing source. Approval requires resolving that remaining blocker and explicitly re-reviewing the new candidate.

