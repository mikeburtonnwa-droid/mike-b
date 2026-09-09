Verdict: APPROVE
Candidate SHA-256: e8a00bad2799cdb17ea8dd2567bc9d87984d2e6d94945054d37f138f040478ef

# G3 novice usability and skill integration re-review, revision 3

This approves candidate-r3 within the novice-usability and skill-integration remit, including its revised evaluation identity/time protocol. The replay and import-order cases are rejected or remain blocked as required, actual later successful execution restores readiness and permits verified recovery, and the prior journey behavior still works. No blocker or outstanding nonblocker was found in this remit. This is one reviewer’s approval, not the overall council decision, G4 rehearsal, or production sign-off.

## Findings

1. **Resolved blocker — an existing execution cannot acquire a new evaluation order through replay.** Independent CLI probes attempted to reuse an evaluated successful source after a later failure, captured an alias with the exact original bytes, and captured differently formatted JSON retaining the original execution identity/time. All three evaluation attempts returned exit 2 with the actionable instruction to reuse the existing evaluation ID. HEAD remained unchanged for each rejected evaluation. The implementation retains `run_id`, `run_at`, and `result_hash`, rejects duplicate identity/content, and validates these fields again in canonical state. Evidence: `same_source_replay_atomic_rejection`, `alias_replay_atomic_rejection`, and `formatted_replay_atomic_rejection` in the retained results; [evaluation implementation](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/src/agent_architect/workflow.py:330). Requirements: R03/R06/R07/R08.

2. **Resolved blocker — import order cannot promote a previously unimported older pass.** The probe executed an older passing case and then a later failing case, imported the failure first, and imported the original older result afterward without changing its identity/time/content. The older pass received revision 14 versus the failure’s revision 11, but readiness still failed, old-release activation was rejected, and incident closure with the older pass was rejected. A fresh subsequent execution supplied a new UUID/time, closed the incident, restored readiness with `NEW_RECOVERY`, and allowed the still-fitting prior local simulation to activate. A final audit passed across 21 commits. The timestamp normalizer and shared latest-run selector serve readiness and incident closure; the six-test identity suite additionally covers equal-time pass/fail ties requiring a strictly later success. Evidence: `backfilled_*`, `fresh_later_execution_*`, and `execution_replay_project_audit`; [time selection](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/src/agent_architect/workflow.py:17), [readiness](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/src/agent_architect/workflow.py:368), [incident closure](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/src/agent_architect/workflow.py:488). Requirements: R06/R07/R08.

3. **Resolved nonblocker — executed-query errors now identify a usable recovery path.** Editing an executed query returns `Executed query identity is immutable; archive and create a new query version`. The adjacent guard explicitly requires a new query ID and execution. Documentation and the data skill explain the same workflow. The preserved negative cases still reject changed SQL and binding old rows to a changed query; dependency drift remains visible in resumed context. Evidence: `executed_query_edit_rejected`, `old_rows_cannot_bind_changed_query`, `query_drift_visible_on_resume`; [query guards](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/src/agent_architect/core.py:388). Requirements: R05/R12.

4. **Prior blocker and presentation findings remain resolved.** The adapted harness retains unknown first-interview owner/scope, provisional map gaps, supported clarification with provenance, stale-revision rejection, checkpoint/context resumption, historical metadata, rendered handoff payload/receiver, and explicit failed/passing evaluation receipts. Changed brief or implementation still blocks old-release activation; old snapshots remain unchanged. The guide and architecture skill integrate the new protocol while explicitly limiting it to captured evidence and local simulation. Invalid UUID, missing timezone, and a timezone-aware timestamp whose UTC date differs from `run_on` each return structured exit-2 errors without changing HEAD. Requirements: R01/R02/R03/R04/R06/R07/R12.

## Requirement coverage

Requirement IDs refer to the [approved development plan](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/PLAN.md:9).

| Requirements | Evidence in this re-review |
| --- | --- |
| R01/R04/R12 | Unknown intake, clarified authoritative brief, focused next action, saved checkpoint and source-aware CLI resumption from an unrelated directory; all six skills’ frontmatter/local links pass. |
| R02/R03 | Current/proposed map checks, visible unresolved coverage and handoff metadata, captured sources, preserved history, immutable run identity/content, and atomic rejected imports. |
| R05 | Actual SQLite execution produces `[[1], [2]]`; pre-run query fingerprint and binding work; changed-query reuse and dependency drift remain detected. |
| R06/R07 | Explicit pass/fail receipts, pre-run target/brief binding, actual execution order rather than import order, prior snapshot preservation, readiness and activation checks. |
| R08 | Older verification rejected after a later failure; fresh execution closes the incident and restores readiness; workflow and regression suites retain other incident negatives. |
| R09/R10/R11 | Candidate identity, separate preserved review artifacts, exact subprocess records, and temporary private project mutations. All 44 candidate entries match before and after testing. Overall council acceptance and clean-clone packaging were not evaluated here. |

## Exact verification commands and results

Top-level commands below ran from `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`. The retained [revised probe](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G3/product-checks-r3.py) specifies all fixture creation and assertions. Its [complete evidence](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G3/product-evidence-r3.json) records all 159 subprocess argument lists, working directories, stdout, stderr and exit codes. CLI commands used the absolute script path from an unrelated temporary working directory containing spaces.

Relevant inspection commands included:

```sh
cat development/gates/G3/rework-r3.md docs/RECORDS.md && cat docs/CLI.md && cat development/gates/G3/candidate-r3.json && rg -n 'run_id|run_at|run_on|replay|def test_' src/agent_architect/core.py src/agent_architect/workflow.py src/agent_architect/schema.py tests/test_g3_regressions.py tests/support.py skills/architecture-delivery/SKILL.md skills/data-discovery/SKILL.md docs/CONTRACT.md
```

```sh
sed -n '328,510p' src/agent_architect/workflow.py
```

```sh
cat docs/CONTRACT.md && cat skills/agent-architect/SKILL.md && sed -n '1,190p' tests/support.py && sed -n '165,196p' src/agent_architect/core.py && cat development/PLAN.md
```

These exited 0. The identity tests, G3 regression tests, schema, architecture skill and prior product report were also inspected. An earlier combined read mistakenly requested `skills/guide/SKILL.md` and exited 1 with “No such file or directory”; the actual entry skill is `skills/agent-architect/SKILL.md`, subsequently read successfully. This was an inspection-path mistake, not a product defect.

The four focused suites all exited 0; their full outputs are retained in `product-tests-r3-first.json`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_core.py -q
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_workflow.py -q
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_g3_regressions.py -q
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_run_identity.py -q
```

Exact result lines, respectively:

```text
Ran 30 tests in 0.410s
OK
Ran 26 tests in 1.157s
OK
Ran 12 tests in 0.622s
OK
Ran 6 tests in 0.445s
OK
```

Independent integrated probes:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G3/product-checks-r3.py
```

Final exit 0; selected exact outputs:

```text
PASS same_source_replay_atomic_rejection: {"message": "Execution evidence already evaluated; reuse its existing evaluation ID, not a new run order", "status": "error"}
PASS alias_replay_atomic_rejection: {"message": "Execution evidence already evaluated; reuse its existing evaluation ID, not a new run order", "status": "error"}
PASS formatted_replay_atomic_rejection: {"message": "Execution evidence already evaluated; reuse its existing evaluation ID, not a new run order", "status": "error"}
PASS backfilled_older_pass_keeps_execution_identity: {"later_import_revision": 11, "later_run_at": "2026-09-09T12:04:52.843713+00:00", "older_import_revision": 14, "older_run_at": "2026-09-09T12:04:52.712309+00:00", "older_run_id": "f38c5430-ab40-41c1-8600-fa1420f286be", "result_hash": "d8d58bc82474b3fa7d1bd494dc12faa832d0ca062d0f519efe824153761fbd34"}
PASS backfilled_pass_cannot_close_incident: {"message": "Use the latest matching recovery evaluation; an earlier pass cannot hide a later result", "status": "error"}
PASS bad_uuid_atomic_rejection: {"message": "BAD_UUID: run_id must be a UUID generated for the executed case", "status": "error"}
PASS bad_timezone_atomic_rejection: {"message": "run_at requires a timezone", "status": "error"}
PASS bad_utc_date_atomic_rejection: {"message": "BAD_UTC_DATE: UTC execution timestamp date differs from run_on", "status": "error"}
PASS fresh_later_execution_restores_readiness: {"evaluations": ["NEW_RECOVERY"], "status": "pass"}
PASS executed_query_edit_rejected: {"message": "Executed query identity is immutable; archive and create a new query version", "status": "error"}
{"checks": 54, "commands": 159, "failed": 0, "observations": 5}
```

The first r3 probe run exited 1 because my new error assertion required the literal words `new ID`; the product correctly said `archive and create a new query version`. I corrected only that assertion and reran. All other 53 assertions passed on that first run. Its script, complete evidence and console results remain separately preserved as `product-checks-r3-first.py`, `product-evidence-r3-first.json`, and `product-tests-r3-first.json`. The successful console results are in `product-tests-r3-final.json`. No product change was made for this correction.

Candidate and artifact verification:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib,json
root=Path.cwd(); folder=root/'development/gates/G3'
old=json.loads((folder/'candidate-r2.json').read_text());new=json.loads((folder/'candidate-r3.json').read_text())
print(json.dumps({'changed':sorted(k for k in old.keys() & new.keys() if old[k] != new[k]),'added':sorted(new.keys()-old.keys()),'removed':sorted(old.keys()-new.keys())},indent=2))
for name in ['candidate-r3.json','product-checks-r3.py','product-evidence-r3.json','product-checks-r3-first.py','product-evidence-r3-first.json','product-tests-r3-first.json','product-tests-r3-final.json']:
    print(hashlib.sha256((folder/name).read_bytes()).hexdigest(),name)
evidence=json.loads((folder/'product-evidence-r3.json').read_text())
print(json.dumps({'checks':len(evidence['checks']),'failed':[c['name'] for c in evidence['checks'] if not c['passed']],'commands':len(evidence['commands']),'candidate_mismatches':[p for p,h in new.items() if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]},sort_keys=True))
PY
```

Exit 0. Nine existing candidate files changed, `tests/test_run_identity.py` was added, and none were removed. Exact selected output:

```text
e8a00bad2799cdb17ea8dd2567bc9d87984d2e6d94945054d37f138f040478ef candidate-r3.json
2c14ef7967b61a0b91cceee5eed2a6a370e4610bb832853a22181b6c589b7219 product-checks-r3.py
135d4278ef25004e68f086ee2421183b8d92e071b71ab624ff7afeff5abe7106 product-evidence-r3.json
e11053811f973138a568e18e1dbaa968419e9eda61799a5d280594e023c6a440 product-checks-r3-first.py
600d6e035269ea18f07e4e6ffd84e3266e5ff6598b722a0d9bd5297d5f8e1a99 product-evidence-r3-first.json
325d548cf233a8da79754c9496a0a25208e4b40ae69596958206e3f4db8fd48f product-tests-r3-first.json
30a56e057d1a6c04a4db2cf1c8567a3bda010dad3c78de1ee192ab17e191fb0d product-tests-r3-final.json
{"candidate_mismatches": [], "checks": 54, "commands": 159, "failed": []}
```

The harness also verified the original and r2 product reports, probes and outputs remained byte-for-byte unchanged. Reviewer writes were limited to separate G3 review artifacts; project mutations occurred only in temporary directories.

## Limits

The 54 independent assertions and 74 suite tests ran on the available macOS Python 3.12 environment. New positive evaluation captures used UUIDs and timezone-aware timestamps emitted by the actual small Python runner; SQLite output was also actually executed. The underlying project fixtures, malformed-result cases and equal-time suite scenarios are explicitly synthetic. They do not establish production-agent correctness, database semantics beyond the fixture, stakeholder completeness, or authenticity of externally supplied timestamps/results. The documents state those limits accurately.

Mermaid was inspected as text. No external runtime deployment, cross-provider evaluation, Linux/clean-clone packaging check, or exhaustive adversarial audit was performed. Other current reviewer reports were not read, and council tests involving real reports were not run. The ten-stakeholder/fresh-context user rehearsal remains G4; packaging and final release sign-off remain G5.
