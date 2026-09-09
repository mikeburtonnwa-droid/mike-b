Verdict: EDITS
Candidate SHA-256: 0023c1931ce0b089325966a06fbcfa7fbdf851c6cc37eb478cfc16ccc1617be3

G3 process, data and provenance review. The 42-entry frozen candidate matched the current generated manifest before and after the independent probes. Scope covers current-map coverage, handoffs, schema/query provenance, freshness and evaluation source binding. No product files or other current reviewer reports were edited or read.

## Findings

1. **Blocker — current-state coverage can be satisfied entirely by proposed steps (R02/R06).** `workflow.py:43–49` requires some evidence and step IDs for covered dimensions, while `:184–191` checks only that the three dimensions exist and are not gaps. Neither checks that the coverage's steps belong to the active current map. Replacing all stakeholder/variant/exception coverage step lists with `["F2"]`, a proposed step, leaves both current process checking and release readiness at pass. A separate archived-current-step case also passes the process check, although readiness correctly detects the archived prerequisite. This is a structural view/status error, not the unavoidable limitation of proving real-world completeness. Require covered current dimensions to reference active current steps; retain incomplete mappings as explicit gaps. Add proposed-only and archived-only coverage regressions.

2. **Blocker — a consequential data asset can pass readiness without any provenance (R03/R05).** The data record fields in `schema.py` and the checks at `workflow.py:50–51,320–321` require keys and known descriptive values but no captured schema/source lineage. An active TABLE with schema, table, grain, keys and refresh, but no evidence or dependencies, passes readiness. Its task context contains only TABLE, so none of its asserted schema facts can be traced to captured material. The contract explicitly requires data-asset provenance, and the data-discovery skill requires captured metadata. Permit incomplete assets during discovery, but block consequential readiness when attributable schema/source provenance is absent. Include a negative readiness test and a passing captured-schema case.

3. **Blocker — changed SQL retains executed status and the old result source (R05, with R07 readiness impact).** `Project.put` in `core.py:352–390` does not protect an executed query's execution identity. Query checks at `workflow.py:52–58,103–109` validate presence, type, environment and chronology of a result source, but do not bind it to the SQL/parameters/assets it exercised. An actual SQLite probe captured the two rows returned by `SELECT id, amount FROM requests ORDER BY id`, then changed only SQL to filter `WHERE id = 1`. SQLite returned one row, while the saved query remained executed against the original two-row result source and readiness still passed. This requires no alteration of a captured blob. Changing the query must invalidate its execution state, or require a new immutable execution record whose result binds the query and relevant asset fingerprints. Add SQL/parameter/asset-change regressions. Evaluation-record fingerprints are correctly enforced, but they do not repair an executed query's separate evidence claim.

4. **Nonblocker — normalize the missing-payload sentinel in handoff checking (R02).** `workflow.py:168–170` rejects the exact payload `none` across a boundary, but the independent probe's `" NONE "` passes. The surrounding unknown-value helper already normalizes case and whitespace. Apply equivalent normalization to the missing-payload check. Ordinary invalid-boundary and valid-handoff cases behaved correctly.

5. **Nonblocker — evaluation binding and the exercised prior invariants passed.** The 26 workflow tests and 30 core tests passed. Independent probes confirmed rejection of wrong query environments and non-result source kinds, evaluation criterion/target mismatches, rebinding old evaluation results after dependency changes, and stale critical knowledge. Evaluation hashes include the captured result source. Valid captured schema lineage participates in reverse impact. These positive results bound the findings to the specific coverage/data/query gaps above.

## Requirement coverage

| Requirements | Assessment |
| --- | --- |
| R02 | Ordinary map/handoff/dead-end checks pass their tests; current coverage view/status validation is incomplete. |
| R03/R04 | Core source/claim/freshness tests passed; missing data provenance remains a consequential gap. |
| R05 | Environment/source-kind checks and lineage traversal passed; provenance absence and executed-query rebinding block approval. |
| R06/R07 | Evaluation dependency/source binding passed independent negatives; readiness incorrectly accepts the demonstrated coverage/data/query cases. |
| R08 | Existing workflow incident tests passed; independent operational rehearsal remains G4. |
| R09/R10 | This review preserves candidate identity, commands, probe source and output; no council decision is issued here. |
| R01/R11/R12 | Full novice walkthrough, packaging and broader specialist-skill review are outside this remit. |

## Exact commands and results

Working directory: `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`. Independent commands were batched. All shell invocations returned exit 0.

Inspection commands:

```sh
cat development/PLAN.md docs/CONTRACT.md docs/RECORDS.md development/gates/G3/candidate.json
rg --files src tests scripts docs
cat src/agent_architect/schema.py src/agent_architect/workflow.py
cat tests/support.py tests/test_workflow.py
nl -ba src/agent_architect/workflow.py | sed -n '125,385p' && sed -n '68,110p;175,217p' src/agent_architect/core.py && cat skills/data-discovery/SKILL.md skills/process-discovery/SKILL.md
nl -ba src/agent_architect/workflow.py | sed -n '38,65p;90,114p'
rg -n 'def put|immutable|record\[.type.\]|state\[.records.\]\[rid\]' src/agent_architect/core.py
```

Relevant outputs established the field schemas, the exact validation locations cited above, the absence of a query-specific mutation guard, and the skills' requirements for captured metadata/current-state evidence. The initial batched workflow listing was truncated in the outer tool output; the relevant checker/evaluation/readiness sections were read again with line numbers.

Baseline commands:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_workflow.py -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_core.py -v
```

Relevant outputs, respectively:

```text
Ran 26 tests in 0.889s

OK
```

```text
Ran 30 tests in 0.288s

OK
```

Independent probe source is retained in `development/gates/G3/integrity-probes.py`; its exact output is retained in `development/gates/G3/integrity-probe-output.txt`. The probe uses the repository's explicitly synthetic baseline fixture, makes independent adversarial modifications in temporary projects, and executes the query comparison against an in-memory SQLite database.

Exact probe command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G3/integrity-probes.py > development/gates/G3/integrity-probe-output.txt
cat development/gates/G3/integrity-probe-output.txt
```

Exact output:

```text
candidate {"sha256": "0023c1931ce0b089325966a06fbcfa7fbdf851c6cc37eb478cfc16ccc1617be3", "entries": 42, "matches_current": true}
baseline {"process": "pass", "readiness": "pass"}
current_coverage_using_only_proposed_steps {"process_status": "pass", "errors": [], "readiness": "pass"}
current_coverage_using_archived_step {"process_status": "pass", "readiness": "fail"}
boundary_change_requires_valid_handoff True
normalized_missing_handoff_payload pass
data_without_provenance {"readiness": "pass", "context_ids": ["TABLE"], "data_has_evidence": false}
executed_query_positive {"rows": [[1, 10], [2, 20]], "readiness": "pass", "schema_impact": ["QUERY", "TABLE"]}
query_environment_and_source_kind_negative_checks True
executed_query_reuses_result_after_sql_change {"old_rows": [[1, 10], [2, 20]], "actual_new_rows": [[1, 10]], "stored_status": "executed", "result_source": "QUERY_RESULT", "readiness": "pass"}
evaluation_result_criterion_targets_and_dependency_binding True
stale_critical_knowledge_rejected True
candidate_unchanged True
```

The only persistent writes were this report, the independent probe script and its output in the assigned G3 directory. All synthetic project/database mutations were temporary.

## Limits and disposition

These tests do not establish real stakeholder completeness, the truth of captured evidence, production-database semantics or runtime deployment. The SQLite comparison demonstrates a specific execution-evidence mismatch, not general SQL verification. The probe's baseline is a synthetic unit fixture and is not represented as a ten-stakeholder rehearsal. G4 fresh-context/operational work and G5 packaging remain later work. Other current reviewer reports were not inspected.

Approval is withheld until findings 1–3 are corrected and explicitly re-reviewed. Finding 4 is a smaller, nonblocking normalization defect; finding 5 records passing evidence.
