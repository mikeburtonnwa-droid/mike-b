# G2 architecture and reliability review

Verdict: **EDITS**

Date: 2026-09-09  
Remit: reliability and verification of the evidence engine, CLI, checkpoint, transaction/lock/audit behavior and council validator.  
Candidate: `development/gates/G2/candidate.json`  
Candidate SHA-256: `c3c7d3edc6fc63e3fe8f16d8d23a0aa452cb319fc1945aca7edd781e8d2d47f9`

The supplied 31-test suite passes. Independent adversarial probes found four blocking areas and one nonblocking input-handling defect. G2 is not approved. The recorded candidate matched the current product manifest both before and after testing.

## Findings

1. **BLOCKER — Council approval is not bound to the candidate the reviewers actually reviewed.**  
   Requirements: R09, R10; frozen-candidate and relevant re-review rules in `development/PLAN.md:36`–38.  
   Evidence: `scripts/check_council.py:34`–43 validates the decision's candidate and optionally the current files, but lines 51–76 never bind dispatches or reviewer approvals to that candidate. In the independent `council_candidate_substitution` probe, all dispatches and reports explicitly identified candidate A. The synthetic contract was then changed, candidate B was generated, and the decision named B using the unchanged A reports. `check_gate(..., current=True)` returned `pass`. No local hash was broken; the validator accepted internally consistent evidence for the wrong candidate.  
   Required correction: bind each review round to a candidate hash and validate the final approvals against the accepted candidate. If an earlier approval is retained for an unaffected remit, require the explicit, recorded scope justification permitted by the plan. Add a negative regression where current product hashes are valid but approvals name the preceding candidate.

2. **BLOCKER — A report whose actual verdict is DENY can satisfy the approval check.**  
   Requirements: R09, R10; no concealed dissent or majority override.  
   Evidence: `scripts/check_council.py:75` uses an unanchored search for any occurrence of `Verdict: APPROVE`. The `council_contradictory_verdict` probe submitted a report beginning `Verdict: DENY`, with an unresolved blocker and a later example containing `Verdict: APPROVE`. With that exact report preserved in the response transcript and its correct hash in the decision, the checker returned `pass`.  
   Required correction: define and parse one authoritative report verdict, reject missing/ambiguous verdicts, and cross-check it with the decision metadata. A quoted example or later substring must not override a denied report. Preserve a regression reproducing this case.

3. **BLOCKER — The council checker does not enforce decision ordering or required prior gates. It also accepts missing message times.**  
   Requirements: R09, R10; sequential gate execution and timestamped traceability.  
   Evidence: `scripts/check_council.py:45`–62 collects decisions without checking that approvals preceded them; lines 77–83 merely find an equal decision and validate whichever dependencies happen to be listed. The `council_early_decision` probe placed the PASS decision before every dispatch/response and passed. The `council_missing_previous` probe created a G2 decision with no G1 artifact and an empty `previous_gates` list and passed. The `council_missing_time` probe omitted `time` from every event and passed.  
   Required correction: validate gate execution as ordered rounds, require an authorized orchestrator decision after the applicable completed reviews, enforce the required prior-gate chain, and validate mandatory transcript fields including parseable timestamps. Add negative tests for each observed bypass. This concerns the checker’s promised protocol validation, not authentication of reviewer identity.

4. **BLOCKER — A post-HEAD persistence error is reported as an ordinary failure after the mutation has become visible.**  
   Requirements: R03 and the G2 persistence obligations in `docs/CONTRACT.md:7` and `:60`; documented transaction outcomes in `docs/CLI.md`.  
   Evidence: `src/agent_architect/core.py:217` replaces the file before the directory `fsync` at line 220. `Project.commit` uses this operation to replace HEAD at line 307, while `src/agent_architect/cli.py:67`–69 maps every `OSError` to an ordinary JSON error and exit 2. The `post_head_fsync_failure` probe injected an error at the directory flush immediately after HEAD replacement. The operation raised an error, but HEAD changed, revision advanced from 1 to 2, and the new record was present. The pre-HEAD interruption probe, by contrast, preserved the old revision and recovered correctly.  
   Required correction: distinguish pre-commit failure from a committed or uncertain post-commit outcome. Reconcile HEAD while holding the lock and return explicit commit/revision and durability information where observable; direct the caller to inspect/reconcile an uncertain outcome before retrying. Document the actual boundary instead of promising that every reported failure leaves the project unchanged. Add fault tests after the commit point as well as before it. Do not attempt an unsafe silent rollback of an already published revision.

5. **NONBLOCKER — A valid JSON value with an invalid record shape escapes the documented CLI error contract.**  
   Requirements: R01 and G2 CLI failure behavior.  
   Evidence: `src/agent_architect/core.py:338` inserts `None` into the ID list for a non-object record, and construction of the operation text fails before record validation. The `malformed_cli_record` probe supplied `[null]`; the CLI exited 1 with a Python traceback instead of exit 2 with a JSON error. Revision remained 1, so no data corruption was observed.  
   Required correction: validate every incoming record's object shape before extracting/joining IDs, and add a malformed-shape CLI regression. Prefer explicit validation to a broad exception handler that could conceal programming defects.

## Positive evidence and requirement coverage

The independently executed competing-writers probe started six processes against the same expected revision. Exactly one committed and five were rejected; the project ended at revision 2 with two audited commits. A writer terminated after creating its history object but before replacing HEAD left the prior state visible, released its lock on process death, and allowed a subsequent valid commit. Tampering with a historical envelope caused both audit and a later mutation to reject it without changing HEAD.

The supplied suite passed source integrity, historical evidence, atomic batches, link/cycle checks, stale expected revisions, conflict/supersession behavior, checkpoint resumption and CLI execution from another working directory. This supports the implemented portions of R01, R03, R04 and R11, subject to finding 4 and the stated limits. R09/R10 remain blocked by findings 1–3.

R02, R05–R08 and R12 are outside this G2 implementation remit except for their underlying storage/audit foundation. Process, architecture, release/incident functions and guide skills remain G3 work. No missing G3 functionality is treated as a G2 defect here.

## Exact commands and results

All commands ran from:

`/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`

Runtime: Python 3.12.7. Shell commands exited 0 except the independent probe command, which intentionally exits 1 when expected protections fail.

### Inspection commands

```sh
cat development/PLAN.md docs/CONTRACT.md docs/CLI.md development/gates/G2/candidate.json
rg --files -g '!development/gates/*/*' && git status --short
cat src/agent_architect/core.py src/agent_architect/cli.py scripts/check_council.py
cat tests/test_core.py tests/test_council.py scripts/aa.py && python3 -m unittest discover -s tests -v
nl -ba scripts/check_council.py && nl -ba src/agent_architect/cli.py && sed -n '350,490p' src/agent_architect/core.py
nl -ba src/agent_architect/core.py | sed -n '205,355p' && python3 --version && shasum -a 256 development/gates/G2/architecture-probes.py
```

Relevant suite result:

```text
Ran 31 tests in 0.181s

OK
```

Relevant inspection results: the immutable-envelope/HEAD design, nonblocking POSIX lock, audit-before-mutation sequence, council-check implementation and CLI exception handling were inspected at the lines cited above. The review probe source hash was:

```text
Python 3.12.7
529612510ae35c38b769098554df573f0e38ef206b954e5bd15711dff2c4c87a  development/gates/G2/architecture-probes.py
```

### Candidate verification before probes

```sh
python3 - <<'PY'
import hashlib,json,runpy
from pathlib import Path
r=Path.cwd(); p=r/'development/gates/G2/candidate.json'; m=json.loads(p.read_text())
print('candidate_sha256='+hashlib.sha256(p.read_bytes()).hexdigest())
print('candidate_entries='+str(len(m)))
print('current_manifest_matches='+str(m==runpy.run_path(str(r/'scripts/record_development.py'))['manifest']()))
PY
```

Exact output:

```text
candidate_sha256=c3c7d3edc6fc63e3fe8f16d8d23a0aa452cb319fc1945aca7edd781e8d2d47f9
candidate_entries=29
current_manifest_matches=True
```

### Independent adversarial probes

The complete reproducible harness is retained in `development/gates/G2/architecture-probes.py` with the SHA-256 above. It creates fresh synthetic projects and synthetic council artifacts in temporary directories, uses actual competing/killed processes for lock tests, and injects the specific post-HEAD `fsync` failure. It does not copy or inspect other reviewers' reports.

Exact command:

```sh
python3 development/gates/G2/architecture-probes.py
```

Exit status: 1. Exact output:

```text
{"expected": "one saved, five rejected, revision/commits 2", "observed": {"commits": 2, "rejected": 5, "revision": 2, "saved": 1}, "passed": true, "probe": "competing_writers"}
{"expected": "no partial commit; lock recovers", "observed": {"commits": 2, "pre_head_unchanged": true, "recovery_revision": 2}, "passed": true, "probe": "killed_pre_head_writer"}
{"expected": "failure must not be presented as an unapplied mutation", "observed": {"error": "injected post-HEAD directory fsync failure", "head_changed": true, "record_present": true, "revision": 2}, "passed": false, "probe": "post_head_fsync_failure"}
{"expected": "audit and mutation reject; HEAD unchanged", "observed": {"head_unchanged": true, "rejected": [true, true]}, "passed": true, "probe": "historical_tampering"}
{"expected": "exit 2 with JSON error and unchanged revision 1", "observed": {"exit": 1, "revision": 1, "structured_error": false, "traceback": true}, "passed": false, "probe": "malformed_cli_record"}
{"expected": "pass", "observed": "pass", "passed": true, "probe": "council_valid"}
{"expected": "reject", "observed": "pass", "passed": false, "probe": "council_candidate_substitution"}
{"expected": "reject", "observed": "pass", "passed": false, "probe": "council_contradictory_verdict"}
{"expected": "reject", "observed": "pass", "passed": false, "probe": "council_early_decision"}
{"expected": "reject", "observed": "pass", "passed": false, "probe": "council_missing_time"}
{"expected": "reject", "observed": "pass", "passed": false, "probe": "council_missing_previous"}
{"failed": 7, "passed": 4, "total": 11}
```

### Candidate verification after probes

```sh
python3 - <<'PY'
import json,runpy
from pathlib import Path
r=Path.cwd()
print('final_current_manifest_matches='+str(json.loads((r/'development/gates/G2/candidate.json').read_text())==runpy.run_path(str(r/'scripts/record_development.py'))['manifest']()))
PY
```

Exact output:

```text
final_current_manifest_matches=True
```

## Limits

The probes cover selected failure boundaries on the available local filesystem. They do not establish power-loss durability, network-filesystem behavior, Windows support, large-project performance, protection from an administrator rewriting all history, or external runtime reliability. The injected post-HEAD failure proves outcome misclassification under that fault; it does not claim that a real disk failure occurred.

The council adversarial cases are entirely synthetic and demonstrate acceptance of invalid protocol records. They make no claim that the actual orchestrator substituted candidates, concealed dissent or skipped a gate. The supplied council tests used historical G1 artifacts as fixtures; no other G2 reviewer report text was inspected.

Only this report and its independent probe harness were authored in the assigned gate directory. No product files were changed. Approval requires correction of blockers 1–4, relevant regressions and explicit re-review.

