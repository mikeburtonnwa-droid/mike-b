Verdict: EDITS
Candidate SHA-256: 0023c1931ce0b089325966a06fbcfa7fbdf851c6cc37eb478cfc16ccc1617be3

# G3 architecture, evaluation and operations review

Date: 2026-09-09  
Candidate: `development/gates/G3/candidate.json`  
Remit: critical coverage, evaluations, immutable releases, activation/rollback, incident closure, malformed inputs and G2 persistence integration.

G3 is not approved. The supplied 66-test suite passes, but independent transition probes expose three blocking defects. Eight of 20 probe expectations failed, representing those three defects. The product manifest still matches the frozen candidate.

## Findings

1. **BLOCKER — A later failed run of a critical criterion does not stop release or activation while an older pass remains applicable.**  
   Requirement: R07, supported by R06's evaluation traceability and the contract's unresolved-critical-coverage gate.  
   Evidence: `src/agent_architect/workflow.py:299`–309 filters candidates through `applicable`, which excludes failures, and then chooses only among remaining passing results. It never accounts for a newer contradictory failure. The probe records a pass on September 9 and a failure on September 10 for the same criterion, targets, dependency hashes and environment. On September 10, readiness still returns pass and selects the September 9 evaluation `EV1`. Both new release creation and activation of an existing release succeed.  
   Required correction: make an unresolved later failure for the same critical criterion and implementing scope block readiness and the corresponding transitions. Define how a subsequent applicable passing run or explicitly supported resolution resolves it, including deterministic ordering for runs on the same date. Do not permanently block on all historical failures. Preserve tests for the old-pass/new-failure sequence and for recovery after a subsequent pass; the latter already succeeds in this probe.

2. **BLOCKER — Release IDs can subsequently be reused by ordinary records, captured sources and evaluations.**  
   Requirements: R03, R06, R07 and `docs/CONTRACT.md:7`'s globally unique stable IDs.  
   Evidence: `create_release` checks both collections at `src/agent_architect/workflow.py:334`, but the reverse checks are absent from `Project.put` at `src/agent_architect/core.py:366`, source capture at line 406, and evaluation creation at `workflow.py:247`. After creating release `REL1`, three independent probes successfully create a note, source or evaluation with ID `REL1`. Each advances HEAD and leaves the same identifier in both `records` and `releases`. This breaks the stable-ID contract and makes a project identifier ambiguous across context, incident and release operations.  
   Required correction: enforce uniqueness across the canonical record/release namespaces in state validation and all creation paths. Reject collisions atomically regardless of which object was created first. Include the three exercised paths and the already guarded reverse order in regressions.

3. **BLOCKER — Incident closure accepts verification evidence captured after the requested as-of date.**  
   Requirement: R08 and the contract's successful applicable verification requirement.  
   Evidence: `applicable` at `src/agent_architect/workflow.py:225`–237 checks the evaluation run/expiry window, environment and hashes, but omits captured-source availability as of the requested date. Release readiness separately rejects future captured sources at lines 318–319; `close_incident` at lines 384–390 does not perform that check. The probe creates a recovery result captured on September 10, with a September 9 run date, and closes an incident as of September 9. Closure succeeds, HEAD changes and the incident becomes closed despite the verification source being future-dated relative to that assessment.  
   Required correction: include the result source and relevant evidence dependencies in the temporal applicability check used by incident closure. Future captured verification evidence must keep the incident open and leave HEAD unchanged. Reuse the same temporal rule where possible so release and incident gates cannot diverge. Retain the valid recovery control, which already closes and audits successfully.

No nonblocking findings are raised in this report.

## Positive evidence and coverage

The independent controls establish that activation is labeled a local simulation, a new note is informational drift, and the pinned release remains unchanged after later component edits. Changed component dependencies block rollback. Stale expected revisions reject release creation without altering HEAD.

The release transition also preserves G2's transaction behavior: an injected pre-HEAD error leaves the release absent and history valid; an injected post-HEAD error returns an explicit visible `committed-durability-uncertain` outcome with the correct commit hash and simulation label. All four malformed evaluation-input probes return exit 2 JSON errors without mutation. Valid incident recovery closes and audits successfully.

The supplied suite additionally exercises missing/failed/expired/future/environment-mismatched evaluation cases, component/criterion coverage, source tampering, stale knowledge, immutable evaluations, incident criteria, process/architecture checks and prior G2 behavior. Its failure-only evaluation cases do not cover the older-pass/newer-failure combination in finding 1.

This review directly covers R06–R08 and their R03/R04 persistence/provenance integration. R01/R02/R05 behavior receives supporting evidence from the supplied suite, but the complete ten-stakeholder and fresh-context rehearsal remains G4. R09/R10's council implementation was not changed by this candidate and is not re-approved on the basis of these transition probes. Packaging and final sign-off remain G5; specialist skill quality is outside this reviewer's remit.

## Exact commands and relevant results

Working directory:

`/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`

All shell commands exited 0 except the independent probe command, which exits 1 when a required protection fails.

### Inspection and supplied suite

```sh
cat development/PLAN.md docs/CONTRACT.md docs/RECORDS.md development/gates/G3/candidate.json
rg --files src tests scripts && git status --short
cat AGENTS.md src/agent_architect/schema.py src/agent_architect/workflow.py
cat tests/support.py tests/test_workflow.py src/agent_architect/cli.py && python3 -m unittest discover -s tests -v
nl -ba src/agent_architect/workflow.py | sed -n '225,445p' && cat tests/support.py
git diff -- src/agent_architect/core.py && sed -n '1,230p' tests/test_workflow.py
```

Relevant suite result:

```text
Ran 66 tests in 1.246s

OK
```

The full test-run output is retained in `development/gates/G3/architecture-suite.txt`. Code inspection confirmed the evaluation-selection, ID-creation and incident-applicability paths cited in the findings.

### Independent probes

The independent mutation scenarios use the supplied small synthetic structural fixture as their starting state. They are not a stakeholder study or evidence of real deployment. The complete harness is retained in `development/gates/G3/architecture-probes.py`.

Exact command:

```sh
python3 development/gates/G3/architecture-probes.py
```

Exit status: 1. Exact output, retained in `development/gates/G3/architecture-probes.txt`:

```text
{"expected": "local simulation, immutable snapshot, no critical drift", "observed": {"active": "REL1", "audit": "pass", "changed": [], "mode": "local-simulation", "snapshot_unchanged": true}, "passed": true, "probe": "release_activation_and_note"}
{"expected": "reject and leave HEAD unchanged", "observed": {"error": "Activation blocked: REQ: no passing applicable evaluation of criterion and implementing components; changed COMP", "head_unchanged": true, "rejected": true}, "passed": true, "probe": "changed_dependency_rollback"}
{"expected": "original release unchanged", "observed": true, "passed": true, "probe": "snapshot_after_component_change"}
{"expected": "reject globally reused stable ID", "observed": {"head_unchanged": false, "id_in_records_and_releases": true, "rejected": false}, "passed": false, "probe": "release_id_collision_put"}
{"expected": "reject globally reused stable ID", "observed": {"head_unchanged": false, "id_in_records_and_releases": true, "rejected": false}, "passed": false, "probe": "release_id_collision_source"}
{"expected": "reject globally reused stable ID", "observed": {"head_unchanged": false, "id_in_records_and_releases": true, "rejected": false}, "passed": false, "probe": "release_id_collision_evaluate"}
{"expected": "fail readiness until a subsequent passing run resolves the failure", "observed": {"later_result": "fail", "readiness": "pass", "selected": ["EV1"]}, "passed": false, "probe": "later_failed_critical_run"}
{"expected": "reject and leave HEAD unchanged", "observed": {"head_unchanged": false, "rejected": false}, "passed": false, "probe": "release_after_later_failed_run"}
{"expected": "new passing run restores readiness", "observed": {"selected": ["RECOVERED_RUN"], "status": "pass"}, "passed": true, "probe": "passing_run_after_failure"}
{"expected": "reject and leave HEAD unchanged", "observed": {"head_unchanged": false, "rejected": false}, "passed": false, "probe": "activate_after_later_failed_run"}
{"expected": "reject and leave HEAD unchanged", "observed": {"head_unchanged": false, "rejected": false}, "passed": false, "probe": "incident_future_captured_evidence"}
{"expected": "incident remains open", "observed": "closed", "passed": false, "probe": "incident_future_capture_status"}
{"expected": "close with applicable recovery evidence", "observed": {"audit": "pass", "status": "closed"}, "passed": true, "probe": "valid_incident_recovery"}
{"expected": "reject and leave HEAD unchanged", "observed": {"error": "Stale revision: expected 4, current 5; reread and reconcile", "head_unchanged": true, "rejected": true}, "passed": true, "probe": "stale_release_revision"}
{"expected": "unapplied release failure preserves history", "observed": {"audit": "pass", "error": true, "release_absent": true, "unchanged": true}, "passed": true, "probe": "pre_head_release_fault"}
{"expected": "explicit visible local-simulation commit uncertainty", "observed": {"commit_matches": true, "mode": "local-simulation", "present": true, "status": "committed-durability-uncertain"}, "passed": true, "probe": "post_head_release_fault"}
{"expected": "exit 2 JSON error without mutation", "observed": {"exit": 2, "head_unchanged": true, "json_error": true}, "passed": true, "probe": "malformed_evaluation_16"}
{"expected": "exit 2 JSON error without mutation", "observed": {"exit": 2, "head_unchanged": true, "json_error": true}, "passed": true, "probe": "malformed_evaluation_17"}
{"expected": "exit 2 JSON error without mutation", "observed": {"exit": 2, "head_unchanged": true, "json_error": true}, "passed": true, "probe": "malformed_evaluation_18"}
{"expected": "exit 2 JSON error without mutation", "observed": {"exit": 2, "head_unchanged": true, "json_error": true}, "passed": true, "probe": "malformed_evaluation_19"}
{"failed": 8, "passed": 12, "total": 20}
```

### Frozen-candidate and probe-source verification

```sh
python3 - <<'PY'
import hashlib,json,runpy
from pathlib import Path
r=Path.cwd(); p=r/'development/gates/G3/candidate.json'; m=json.loads(p.read_text())
print('candidate_sha256='+hashlib.sha256(p.read_bytes()).hexdigest())
print('candidate_entries='+str(len(m)))
print('current_manifest_matches='+str(m==runpy.run_path(str(r/'scripts/record_development.py'))['manifest']()))
p=r/'development/gates/G3/architecture-probes.py'
print('probe_sha256='+hashlib.sha256(p.read_bytes()).hexdigest())
PY
rg -n 'def validate_state|def put|def source|ID already exists|records\]|records.*get|def applicable|def readiness|def evaluate|def create_release|def close_incident|future captured' src/agent_architect/core.py src/agent_architect/workflow.py
```

Exact hash/check output:

```text
candidate_sha256=0023c1931ce0b089325966a06fbcfa7fbdf851c6cc37eb478cfc16ccc1617be3
candidate_entries=42
current_manifest_matches=True
probe_sha256=ddd1b4c64976ce111d23cb9e04288b054fb6292bf1fe8dd47928cfa452617d9f
```

The accompanying search located `validate_state` at core line 167, `put` at 352, source capture at 393, and the workflow functions at the lines cited above.

## Limits

Only this report, the independent probe source and retained outputs were authored in the assigned G3 directory. All probe projects were temporary. No product files were edited, no other current reviewer report text was inspected, and no side-channel communication or delegation occurred.

The probes establish specific local structural and transition behavior. They do not establish real-world process completeness, evidence truth, permission in an external runtime, production reliability, power-loss durability, network-filesystem behavior or performance at scale. Persistence fault cases use controlled exception injection; no real hardware failure is claimed.

The proposed fix for finding 1 requires an explicit policy for resolving newer contradictory runs; the observed defect is that the current implementation ignores them entirely when older passing evidence exists. Approval requires resolving all three blockers, preserving their negative cases and obtaining an explicit re-review.

