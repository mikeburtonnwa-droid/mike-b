Verdict: APPROVE
Candidate SHA-256: b31b54410b38b01152facc471906a8c6d09bb392ae22513787bcd17c64d3e5fe

G3 process/data/provenance re-review of `candidate-r2.json`.

Approved scope: current-map coverage and handoffs, consequential data provenance, query execution binding, freshness and evaluation evidence integration within this reviewer's G3 remit, for progression to G4. The 43-entry manifest matched the current generated candidate before and after the probes. This is reviewer approval, not the orchestrator's gate decision or production certification.

## Findings and resolution

1. **Resolved blocker — current coverage is now tied to active current steps (R02/R06).** `workflow.process_check` rejects proposed-only and archived-only current coverage. The adapted independent probe retained both original negative cases and verified failure. The implementation additionally checks that mapped actors, variants and exception conditions have matching covered evidence. Ordinary valid current coverage remains accepted. Original finding 1 is resolved.

2. **Resolved blocker — missing data provenance now blocks consequential readiness (R03/R05).** `workflow.readiness` requires a captured source in each consequential data asset's prerequisite closure. The original source-free TABLE remains saveable for discovery but fails readiness. Capturing schema evidence and linking it restores the passing baseline. The independent probe exercised both paths, preserving the distinction between incomplete discovery and consequential use. Original finding 2 is resolved.

3. **Resolved blocker — execution evidence is bound to the query that actually ran (R05/R07).** The dedicated `query_fingerprint`/`bind_query` protocol binds query identity, definition and asset/dependency hashes to the captured result. Executed query SQL, parameters and assets cannot be rewritten through `put`. The revised SQLite probe retained the original two-row/one-row case: all execution-identity edits fail without changing HEAD, the old result cannot bind to the new query, and a separately fingerprinted/executed one-row query binds successfully to its own result. Subsequent asset drift fails readiness and produces context warnings. Original finding 3 is resolved.

4. **Resolved nonblocker — handoff payload normalization is consistent (R02).** The original `" NONE "` payload now fails the cross-boundary check. The probe includes explicit customer coverage so the result tests payload handling rather than an unrelated coverage failure; a real payload and correct receiver pass. Original finding 4 is resolved.

5. **Nonblocker — evaluation and prior-core integration passed the exercised checks (R03/R04/R06/R07).** The evaluation fixture now supplies pre-run target hashes and brief hash, as required by the revised protocol. Independent negatives still reject changed criteria, targets, implementation dependencies and brief boundaries. Receipts distinguish saved status from computed pass/fail. A later matching failure blocks readiness, followed by recovery after a later matching pass. Stale critical knowledge remains blocked. All 68 executed repository tests passed. The original candidate, report, probe script and probe output remained byte-identical during the independent checks.

No blockers remain in this review.

## Requirement coverage

| Requirements | Evidence within this remit |
| --- | --- |
| R02 | Proposed/archived coverage negatives, valid current coverage and normalized handoff tests. |
| R03/R04 | Data source attribution, core source/claim regressions, explicit freshness and context drift checks. |
| R05 | Actual SQLite results, pre-run query binding, SQL/parameter/asset immutability and asset-drift rejection. |
| R06/R07 | Evaluation result/target/brief binding, latest outcome and consequential readiness integration. |
| R08 | Existing workflow and added regression tests passed; independent operational rehearsal remains G4. |
| R09/R10 | Candidate identity, original artifacts, revised probe source/output and commands are retained. |
| R01/R11/R12 | Broader novice, packaging and specialist-skill acceptance remain with their assigned remits/later gates. |

## Exact commands and results

Working directory: `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`.

Inspection commands:

```sh
cat development/gates/G3/rework.md docs/RECORDS.md docs/CONTRACT.md && cat src/agent_architect/schema.py
rg -n '^def |coverage|provenance|query|brief_hash|outcome|payload' src/agent_architect/workflow.py src/agent_architect/core.py tests/support.py tests/test_workflow.py && cat skills/data-discovery/SKILL.md skills/process-discovery/SKILL.md
sed -n '180,214p;239,330p;332,397p' src/agent_architect/workflow.py && sed -n '376,401p;489,537p' src/agent_architect/core.py && tail -n 8 docs/CONTRACT.md
rg --files tests && sed -n '1,220p' tests/test_g3_rework.py
cat tests/test_g3_regressions.py
```

The fourth command exited 1 because the guessed filename `tests/test_g3_rework.py` did not exist. Its output listed the actual `tests/test_g3_regressions.py`, which was then read successfully. This was an inspection-path error, not a product failure. Other inspection commands exited 0. Relevant implementation sections were read separately after the initial batched output was truncated.

Test commands:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*flow.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_g3_regressions.py -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_core.py -v
```

All exited 0. Relevant outputs, respectively:

```text
Ran 26 tests in 0.953s

OK
```

```text
Ran 12 tests in 0.463s

OK
```

```text
Ran 30 tests in 0.296s

OK
```

The separately retained adapted probe is `development/gates/G3/integrity-probes-r2.py`; results are in `development/gates/G3/integrity-probe-output-r2.txt`. It uses synthetic temporary projects, the revised positive protocols, and an in-memory SQLite database. Original negative scenarios are preserved as rejection assertions.

Exact probe command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G3/integrity-probes-r2.py > development/gates/G3/integrity-probe-output-r2.txt
cat development/gates/G3/integrity-probe-output-r2.txt
```

The shell invocation exited 0. Exact output:

```text
candidate {"sha256": "b31b54410b38b01152facc471906a8c6d09bb392ae22513787bcd17c64d3e5fe", "entries": 43, "matches_current": true}
proposed_only_current_coverage_rejected True
archived_only_current_coverage_rejected True
valid_handoff_passes_and_normalized_missing_payload_fails True
missing_provenance_fails_and_captured_schema_passes True
sql_parameters_assets_rewrites_rejected True
new_query_needs_new_result {"original_rows": [[1, 10], [2, 20]], "new_rows": [[1, 10]], "old_binding_rejected": true, "new_binding_passed": true}
asset_drift_blocks_readiness_and_warns_in_context True
evaluation_binding_receipts_and_latest_outcome True
brief_binding_invalidates_old_evidence True
stale_critical_knowledge_rejected True
original_artifacts_preserved_and_candidate_unchanged True
```

Only the new probe, its output and this re-review report were persistently written in the assigned gate directory. Product files and original review artifacts were not edited.

## Limits

Other current reviewer reports were not inspected, and the real council decision was not validated here. The tests establish structural evidence binding and specific positive/negative behavior, not truthful stakeholder accounts, real database completeness, authenticated external command execution or general SQL correctness. Repository synthetic helpers provide the baseline; independent modifications and SQLite execution supply the targeted adversarial cases. Core concurrency/crash behavior was exercised through the repository core suite. G4 ten-stakeholder/fresh-context/operational rehearsal and G5 packaging remain later work. Approval applies only to this frozen candidate and remit.
