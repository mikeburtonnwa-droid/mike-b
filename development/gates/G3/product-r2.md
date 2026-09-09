Verdict: APPROVE
Candidate SHA-256: b31b54410b38b01152facc471906a8c6d09bb392ae22513787bcd17c64d3e5fe

# G3 novice usability and skill integration re-review, revision 2

This approves the revised G3 candidate within the novice-usability and skill-integration remit. The original metadata-clarification blocker and both original presentation findings are resolved. The supported brief update, resumption, rendered handoffs, and explicit evaluation outcomes work with the revised protocols. One newly observed error-message improvement is nonblocking. This is a reviewer approval, not the overall council decision or production sign-off.

## Findings and resolution

1. **Resolved blocker — the current brief can be clarified and resumed with provenance.** `Project.brief` at `src/agent_architect/core.py:435` supplies a validated, revision-checked update for title/scope/owner, rationale, and captured source locators. The guide now explicitly instructs the agent to use it when intake facts are clarified. The independent CLI probe starts with unknown owner/scope, captures Alice's clarification, updates the brief, saves remaining discovery work, and resumes from another process. Context exposes Alice, the narrowed scope, rationale, and source pointers even when the lexical query matches nothing. Earlier owner/scope values remain in history. Empty evidence, missing source references, and stale revisions fail. **Requirements:** R01/R03/R04/R12.

2. **Resolved nonblocker — rendered handoffs expose payload and receiver.** The original `handoff-package-Z37` case now appears in the derived Markdown under the added handoff/path table, with its receiver. Current/proposed checks and the expanded coverage declarations still pass for the complete synthetic fixture. **Requirements:** R02/R12.

3. **Resolved nonblocker — evaluation receipts expose the computed outcome.** The original executed failing and passing checks return their evaluation IDs and `outcome: fail` or `outcome: pass`, separately from persistence `status: saved`. The receipt agrees with the committed evaluation record in both cases; failed evidence still blocks release. The implementation reads the exact committed envelope when forming the receipt (`src/agent_architect/workflow.py:325` onward). **Requirements:** R06/R12.

4. **Nonblocker — make the executed-query edit error name the valid recovery path.** Editing an already executed query's SQL correctly returns exit 2, but the message says `Use bind-query to attach matching executed evidence`. For an already executed query, the revised documented path is to create a new query ID and run/bind that version. Mention that path in the error to avoid sending an agent back to binding the immutable old record. The data skill and record documentation already explain the correct procedure, and the attempted edit is rejected. **Requirements:** R05/R12. **Evidence:** `executed_query_edit_rejected` in `product-evidence-r2.json`.

No blocker remains in this remit. Finding 4 can be tracked as a later error-message refinement.

## Integrated verification and requirement coverage

The retained revised harness preserves the original provisional-discovery, unsupported-project-record, failed-evaluation, drift, and missing-incident cases. Positive fixtures were adapted to the revised protocol rather than weakening those negatives: evaluation captures include both pre-run hash fields; the cross-owner fixture declares the newly required customer coverage; the new query probe captures a query fingerprint before actual SQLite execution and binds its result afterward.

All 39 independent assertions passed across 95 recorded subprocess commands. The six integrated skills' frontmatter and local links passed again. Existing core, workflow, and G3 regression suites passed 68 tests. No council tests involving real reviewer reports were run.

| Requirements | Re-review coverage |
| --- | --- |
| R01/R04/R12 | Unknown intake → captured clarification → authoritative brief → checkpoint → resumed source-aware context passes. Missing evidence and stale-revision recovery remain explicit. |
| R02/R03 | Provisional maps retain gaps; current/proposed checks remain separate; handoff payload/receiver and coverage information are visible. Historical brief values and captured clarification survive. |
| R05 | An actual SQLite query produced `[[1], [2]]` and bound through the documented protocol. Editing its executed definition and rebinding its old rows to a changed query were rejected; changed asset assumptions produce a context warning. |
| R06/R07 | Failed/passing evaluation receipts are explicit. Brief changes warn that old evaluations are inapplicable, reject old-result rebinding, preserve the old snapshot, and block old-release activation. Existing implementation-drift and simulation-label checks still pass. |
| R08 | Existing workflow/regression suites cover accepted and rejected incident recovery, including revised source-date/latest-result behavior. The independent missing-incident error case still passes. |
| R09/R10/R11 | Exact candidate/evidence hashes and subprocess outputs are retained. All 43 candidate file hashes matched before and after testing; original review artifacts were unchanged. Only synthetic private temporary projects were mutated. |

The guide, architecture skill, data skill, CLI documentation, and record protocol consistently describe the revised brief/evaluation/query operations. Their limits remain explicit: these commands capture and check evidence; they do not execute/authenticate external procedures, establish stakeholder completeness, or deploy infrastructure.

## Exact commands and results

All top-level commands ran from `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect` and exited 0. Revised probes are retained in `product-checks-r2.py`; all 95 subprocess argument lists, working directories, stdout, stderr, exit codes, assertions, and observations are in `product-evidence-r2.json`. Original scripts/results were not overwritten. All probe CLI calls used absolute script paths from an unrelated temporary working directory containing spaces.

1. Rework, revised protocols, candidate, and CLI:

```sh
cat development/gates/G3/rework.md docs/CLI.md docs/RECORDS.md && cat development/gates/G3/candidate-r2.json && cat src/agent_architect/cli.py
```

Relevant result: the CLI exposes `brief`, `query-fingerprint`, and `bind-query`; the documents specify their inputs, evidence requirements, and the separate evaluation outcome. The candidate contains 43 files.

2. Changed skills, contract refinements, brief/context code, and new regressions:

```sh
cat skills/agent-architect/SKILL.md skills/data-discovery/SKILL.md skills/architecture-delivery/SKILL.md && tail -n 12 docs/CONTRACT.md && rg -n '^def |^    def brief|brief' src/agent_architect/workflow.py src/agent_architect/core.py && sed -n '450,620p' src/agent_architect/core.py && cat tests/test_g3_regressions.py
```

Relevant result: the guide explicitly makes brief clarification authoritative; the data/architecture skills use pre-run fingerprints and documented binding. Context includes the current brief, its source dependencies, and applicability warnings.

3. Focused validators, rendering, binding, and fixture inspection:

```sh
sed -n '167,190p' src/agent_architect/core.py && sed -n '430,450p' src/agent_architect/core.py && sed -n '139,215p' src/agent_architect/workflow.py && sed -n '241,332p' src/agent_architect/workflow.py && sed -n '415,535p' src/agent_architect/workflow.py && cat tests/support.py
```

```sh
sed -n '332,398p' src/agent_architect/workflow.py && cat src/agent_architect/schema.py && rg -n 'brief|outcome|query|def test_' tests/test_workflow.py tests/test_g3_regressions.py
```

Relevant result: confirmed evidence validation and historical brief updates, full handoff rendering, exact committed evaluation receipts, query binding, old-brief invalidation, and revised latest-result readiness rules. The support fixture remains explicitly synthetic.

4. Existing regression suites:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_core.py -q
```

```text
Ran 30 tests in 0.355s

OK
```

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_workflow.py -q
```

```text
Ran 26 tests in 1.086s

OK
```

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_g3_regressions.py -q
```

```text
Ran 12 tests in 0.573s

OK
```

5. Independent adapted integration probes:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G3/product-checks-r2.py
```

Exact selected outputs and count:

```text
PASS brief_rejects_empty_evidence: {"message": "Brief clarification requires captured source evidence", "status": "error"}
PASS brief_rejects_missing_source: {"message": "Brief evidence must reference captured sources", "status": "error"}
PASS brief_clarification_saved: {"status": "saved"}
PASS brief_rejects_stale_revision: {"message": "Stale revision: expected 6, current 7; reread and reconcile", "status": "error"}
PASS render_includes_handoff_payload_and_receiver: {"payload_shown": true}
PASS evaluation_receipt_matches_EVFAIL: {"command_index": 44, "evaluation": "EVFAIL", "exit_code": 0, "name": "evaluate_response_EVFAIL", "outcome": "fail", "record_status": "fail", "response_status": "saved"}
PASS evaluation_receipt_matches_EVPASS: {"command_index": 52, "evaluation": "EVPASS", "exit_code": 0, "name": "evaluate_response_EVPASS", "outcome": "pass", "record_status": "pass", "response_status": "saved"}
PASS brief_change_warns_old_evaluation: {"warnings": ["EVPASS: project brief changed"]}
PASS brief_change_blocks_old_release: {"message": "Activation blocked: REQ: no passing applicable evaluation of criterion and implementing components; changed project brief", "status": "error"}
PASS old_release_preserved_after_brief_change: {"snapshot_unchanged": true}
PASS query_protocol_binds_actual_sqlite_output: {"rows": [[1], [2]], "status": "saved"}
PASS old_rows_cannot_bind_changed_query: {"message": "Query result environment or executed definition/dependencies differ", "status": "error"}
PASS query_drift_visible_on_resume: {"warnings": ["QUERY1: executed query dependencies changed"]}
{"checks": 39, "commands": 95, "failed": 0, "observations": 5}
```

The full evidence also confirms resumed owner `Alice`, scope `Standard requests only`, retained source locators, historical unknown values, preserved original files, and matching candidate hashes.

6. Candidate comparison and artifact hashes:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, json
folder=Path('development/gates/G3')
old=json.loads((folder/'candidate.json').read_text())
new=json.loads((folder/'candidate-r2.json').read_text())
print(json.dumps({'changed':sorted(k for k in old.keys() & new.keys() if old[k] != new[k]),'added':sorted(new.keys()-old.keys()),'removed':sorted(old.keys()-new.keys())},indent=2))
for name in ['candidate-r2.json','product-checks-r2.py','product-evidence-r2.json']:
    print(hashlib.sha256((folder/name).read_bytes()).hexdigest(),name)
evidence=json.loads((folder/'product-evidence-r2.json').read_text())
print(json.dumps({'checks':len(evidence['checks']),'failed':[c['name'] for c in evidence['checks'] if not c['passed']],'commands':len(evidence['commands'])},sort_keys=True))
PY
```

Result: 12 existing product files changed, `tests/test_g3_regressions.py` was added, and no product file was removed. Exact hash/count output:

```text
b31b54410b38b01152facc471906a8c6d09bb392ae22513787bcd17c64d3e5fe candidate-r2.json
bd5b0db022ffe68d8e1315728b13900f20286b5b9e93e99ddf0ecdff3c0a2281 product-checks-r2.py
af915993cb14d68a8ce0cbedd9648f4bc52d9dc147c3852c96b16862ca5461de product-evidence-r2.json
{"checks": 39, "commands": 95, "failed": []}
```

Reviewer writes were limited to the separately adapted harness, its results, and this report. Product files and original review artifacts were preserved.

## Limits

The review used synthetic projects on the available macOS Python environment. The actual small Python/SQLite executions exercise evidence protocols, not a production agent or database. Mermaid output was inspected as text. External-reference currency, Linux compatibility, exhaustive adversarial behavior, and real stakeholder completeness were not established. Other current reviewer reports were not read. The ten-stakeholder/fresh-context user rehearsal remains G4, and packaging/final release sign-off remain G5.
