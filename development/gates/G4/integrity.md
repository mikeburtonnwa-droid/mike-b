Verdict: APPROVE
Candidate SHA-256: e4a716bd9181b99725a7f05c027970832f7faa7c047652824ce7f9afdf30deb9

Reviewer: Integrity council reviewer
Gate: G4
Source commit: 71afb9e4b32d6178daabb91d198098988d122119

This approves the frozen G4 candidate's evidence and data integrity within the synthetic rehearsal and two recorded fresh-context experiments. No unresolved blocker was found in this remit. This is one council opinion; the orchestrator's gate decision remains separate.

## Findings

1. **Nonblocker — Captured provenance and historical project integrity are consistent (R03, R10).** All 66 candidate entries matched the working product before and after verification; all seven registered rehearsal evidence hashes matched. Independently extracted copies of all three project archives passed source/history audits: novice start, 4 commits/22 records; novice resume, 40/95; rehearsal changed project, 54/78; rehearsal ready project, 53/78. Captured stakeholder inputs match the ten frozen source files byte for byte. Captured rehearsal SQL, setup, runner and expected-outcome sources also match the frozen product. The original archives and experiment command logs were preserved. Evidence: `integrity-probes.py`, `integrity-inspect.py`, `integrity-final-verify.py` and their retained outputs.

2. **Nonblocker — Actual query results substantiate the bounded join claims (R05).** I executed all seven retained query definitions against their captured SQLite setup: five novice queries, including archived versions, and two rehearsal queries. Every row matched its retained result source. The naive join returns 13 rows, including six cross-tenant customer matches; corrected queries return four request rows with no cross-tenant customer match. Routes are north/R1 fulfillment, north/R2 finance-review, north/R3 service-desk and south/R4 fulfillment. Independent SQLite primary-key inspection matches all four data records in both completed discovery and rehearsal projects: request and customer composite identities, plus approval decision sequence and handoff event sequence. Table counts are 4 requests, 3 customers, 4 approval events and 5 handoff events. This supports the fixture's event-grain correction without establishing universal SQL correctness.

3. **Nonblocker — Expectations and execution evidence remain attributable (R05, R06).** For all seven rehearsal evaluations, I checked the historical target hashes, brief hash, transitive dependencies and result binding at the recorded revision. Captured setup, runner and expected outcomes are included as prerequisites; the expected source predates each evaluation record. The runner reads predefined expected outcomes before executing SQL. The novice's captured runner also defines its expected outcomes before fingerprinting and execution. Nine independent runner invocations reproduced the retained query rows or evaluation expected/observed values and exit statuses. Original recorded stdout exactly equals the corresponding captured result bytes. New executions generated their own run identities/times; their complete outputs are retained separately in `integrity-execution-replays.json`.

4. **Nonblocker — G2 knowledge semantics remain intact in the fresh-context work (R03, R04).** The first experiment preserves unknown ownership and seven reported claims. The resumed project captures all ten interviews, supports its Operations brief clarification with evidence, preserves the earlier conflict in history, and explicitly supersedes Sales hearsay C08 with C20. Active context excludes C08. The resumed project's verified claims concern local fixture observations; stakeholder policy assertions remain reported. Both novice projects have no release or activation, and incomplete process coverage still fails checks. The resumed report preserves the missing standard-request approval case as an explicit gap instead of claiming it was demonstrated.

5. **Nonblocker — Changed dependencies, expired evidence and reordered historical runs do not gain current authority (R04, R06, R07).** In disposable copies, rewriting executed SQL was rejected without advancing HEAD. Changing handoff event grain affected the query and component, failed readiness, and blocked rollback to REL2. The archived ready project passes at 2026-09-09; the deliberately changed project fails, and assessment at 2026-11-09 exposes stale knowledge and fails readiness. Original evidence and identical-content aliases cannot be evaluated again. An additional independent historical-checkout probe imported the actual outage result first, then the earlier passing routing result with its original bytes, UUID and execution time unchanged. Readiness remained failed specifically for REQ_ROUTING. An alias of that earlier result was rejected atomically. Importing the actual strictly later recovery result then restored readiness. This directly exercises the G3 execution-order fix using G4 execution evidence.

6. **Nonblocker — Experiment conclusions are appropriately limited and failures remain visible (R10).** All ten stakeholder documents explicitly identify themselves as synthetic training material. The acceptance document, experiment reports and development observations distinguish fixture observations from deployment and provider claims. The first and resumed experiment logs contain 19 and 105 entries respectively, each with command, stdout, stderr and exit code. Expected check failures and corrected authoring errors remain present. Both saved experiment reports exactly match their recorded experiment-response messages; the four experiment dispatch/response messages retain sequence, time, sender and recipient. I did not consult other current council reports.

## Requirement coverage and prior-gate integration

The requirement definitions are in [development/PLAN.md](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/PLAN.md:9).

| Requirement | Verified evidence |
| --- | --- |
| R03 | Captured source bytes, claim status boundaries, historical conflict and explicit supersession; findings 1 and 4 |
| R04 | Active-context exclusion, stale retrieval, transitive change impact and execution-time ordering; findings 4 and 5 |
| R05 | Actual SQL replay, composite keys, event grain, environments, source and execution bindings; findings 2 and 3 |
| R06 | Historical requirement/component fingerprints, predeclared criteria and invalidation after dependency change; findings 3 and 5 |
| R07 | Ready versus changed archives, expired evidence and blocked stale rollback; finding 5 |
| R10 | Candidate/evidence preservation, command channels and exact experiment response capture; findings 1 and 6 |

These checks exercise the G1 [sources and knowledge contract](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/docs/CONTRACT.md:9), the G2 audit/context behavior, and G3's [query and evaluation protocols](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/docs/RECORDS.md:31), including [execution identity and ordering](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/docs/RECORDS.md:57). The complete 86-test regression suite also passed, covering the previous claim, concurrency, tampering, query, incident and release negatives.

## Exact verification commands and results

Working directory for all commands:

```text
/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect
```

Commands and separate stdout/stderr/exit-code fields, including document/code inspections, are retained in [integrity-commands.json](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/integrity-commands.json). The logger invocation is `python3 development/gates/G4/integrity-run-command.py '<command>'`. Principal verification commands were:

```text
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G4/integrity-inspect.py
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G4/integrity-probes.py
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G4/integrity-supplement.py
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G4/integrity-import-order.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G4/integrity-final-verify.py
```

All six commands exited 0. Probe stderr was empty. Relevant retained outputs include:

```text
retained_queries_replayed_exactly {"query_count": 7, "naive_rows": 13, "corrected_rows": 4, "naive_cross_tenant_rows": 6, "table_counts": [4, 3, 4, 5]}
all_evaluation_predeclared_expected_code_and_dependency_bindings 7
actual_runner_calls_replayed_and_retained_stdout_matches_sources 9
changed_query_data_stale_knowledge_and_older_source_alias_rejected True
experiment_reports_match_exact_recorded_messages True
older_pass_imported_after_later_failure {"status": "fail", "errors": ["REQ_ROUTING: no passing applicable evaluation of criterion and implementing components"], "evaluations": ["EV_CARDINALITY", "EV_ISOLATION"]}
unchanged_source_alias_rejected Execution evidence already evaluated; reuse its existing evaluation ID, not a new run order
strictly_later_actual_pass_restores_readiness {"status": "pass", "errors": [], "evaluations": ["AUDIT_TRULY_LATER_PASS", "EV_CARDINALITY", "EV_ISOLATION"]}
```

Unittest's stderr reports `Ran 86 tests in 4.724s` followed by `OK`; stdout is empty. The final manifest check reports 66 matching candidate entries, seven matching registered evidence files and the source commit printed above. Full subprocess argv and all nine execution outputs are retained in [integrity-execution-replays.json](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/integrity-execution-replays.json).

One inspection command exited 1 because I requested nonexistent `examples/order-triage/expectations.json`. Its error remains in the command log. The subsequent inspection of the actual `expected.json` succeeded; this was an inspection filename error, not a product failure.

## Limits

The four-request SQLite fixture and two agent experiments do not establish real-human usability, production completeness, provider performance, scale, authorization or external deployment readiness. In particular, the original fixture does not demonstrate every missing-approval branch. Historical query versions and corrected source pointers are preserved, not presented as current executions.

The local hash audit detects inconsistency within the retained project; it does not authenticate authors, externally supplied execution timestamps, source truth or an administrator who rewrites the entire history. Experiment transcripts preserve observable messages, not hidden context or reasoning. Current council completion and G5 packaging/sign-off were outside this review. No product files or earlier evidence were edited; mutations occurred only in disposable project copies.
