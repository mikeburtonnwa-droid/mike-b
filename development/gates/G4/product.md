Verdict: APPROVE
Candidate SHA-256: e4a716bd9181b99725a7f05c027970832f7faa7c047652824ce7f9afdf30deb9

# G4 product and novice-operator review

The two independent agent experiments meet their predeclared, bounded acceptance. The preserved first session supports another session without inventing ownership or completeness; the resumed session reconciles sources and produces a useful design handoff while retaining consequential gaps. The revised renderer improves that handoff, and the documented example executes successfully from an unrelated working directory. No unresolved blocker was found in this remit. One error-presentation refinement is nonblocking.

This approves the frozen G4 candidate for R01/R02/R04/R11/R12 and the integration exercised below. It is one council opinion, not an overall gate decision, real-deployment approval, human usability study, or model-provider performance claim.

## Findings

1. **Acceptance met — first-interview uncertainty survives the handoff.** The first archive audits across four commits and contains 22 records, exactly one captured source matching interview 01 byte for byte, and seven claims that all remain reported. Owner stays `unknown`; the provisional scope, urgent-owner gap and incomplete downstream account are explicit. Its readable artifact distinguishes the end of the stakeholder’s account from completion of the overall process and proposes one Operations walkthrough. Context recovers the checkpoint and unknown owner even with a lexical query that matches nothing. The process check correctly fails on the unknown receiving system and declared coverage gaps. This is preserved uncertainty required by acceptance, not unfinished gate work. **Requirements:** R01/R02/R04/R12. **Evidence:** `first_*` checks and the first-session artifact/archive.

2. **Acceptance met — cold resume recovers, reconciles and advances within its boundary.** The resumed archive audits across 40 commits, contains 95 records, and preserves every first-session history envelope and original source. All ten interview captures and the schema match their supplied bytes. The authoritative owner becomes Operations with S03/S10 evidence. Sales’ contrary C08 account is historical and explicitly superseded by C20; earlier bilateral conflict with C09 remains in history. Policy claims remain reported. Composite tenant keys and event grains are recorded. Q04/Q05 are executed; prior query versions remain archived. I independently reran the saved SQL against captured S11: the reconstructed bad join returned 13 rows, and the corrected query returned four tenant-consistent rows with the sponsor’s exact request-to-route mapping. C24 becomes stale on the next assessment day. **Requirements:** R01/R02/R04/R12; integration with R03/R05.

3. **Acceptance met — the next handoff is usable without claiming readiness.** The preserved design handoff explains provenance, the reconstructed nature of the bad query, current evidence, separate requirements, receiver gaps and the next input/output/failure contract. Service-desk and fulfillment coverage still fail; all eight critical architecture concerns remain deferred. Release readiness fails and no release or activation exists in either novice experiment. Missing-standard-credit and unavailable-feed behavior remain named work rather than inferred successes. The cold-resume acceptance did not require implementation or incident rehearsal; those are separately exercised by the scripted fixture. **Requirements:** R01/R02/R11/R12; integration with R06/R07/R08.

4. **Presentation rework verified.** Rendering the original first-session archive now identifies `P03: unknown system`, prints task/stage/next action/completed/unresolved fields, explains what covered means, and states that no local simulation is activated. The resumed archive receives the same truthful activation description. Ready and deliberately changed rehearsal archives both identify the recorded REL2 simulation and explicitly disclaim infrastructure deployment; their readiness checks correctly differ. I visually inspected both retained PNGs: all six nodes, distinct decision shapes, activity labels and labeled branches are legible without clipping. Handoff payloads and receivers remain available in the accompanying tables. **Requirements:** R01/R02/R12.

5. **Nonblocker — expected example-path rejection produces a Python traceback.** Repeating the documented rehearsal command with its existing output directory safely refuses overwrite and preserves the ready-project HEAD. However, it emits a traceback ending in `Output must be a new directory; previous evidence is never overwritten`. Catch this expected user-input error at the example entry point and return a concise explanation. The documentation already requires a new directory and the final error names the remedy, so this does not prevent the exercise or threaten saved work. **Requirements:** R01/R11/R12. **Evidence:** `documented_example_refuses_existing_output`; [example validation](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/examples/order-triage/rehearse.py:38).

## Experiment independence and integration

I inspected the two experiment dispatches, reports, handoffs and complete command logs, not other current council reports. The first log has 19 entries and is consistent with using the entry guide, linked instructions and only interview 01 as business evidence. The resumed log has 105 entries: audit/show/context occur at entries 10/13/14, before the first new-source mutation at 35. Its preserved runner defines expected routes from S10 before execution and captures query fingerprints before SQL execution. The logs do not show reads of the withheld example solutions, tests or implementation source. This supports the specified agent experiment; it cannot independently prove the absence of unrecorded access or reproduce a human’s experience.

The resumed agent’s rejected cross-applicability supersession, invalid dependency batch, stale checkpoint and orchestration syntax error are retained. They are distinguished from product defects and from intentionally failing readiness checks. The final artifacts explain the repairs without erasing earlier records.

The G1 journey boundary, G2 audit/context behavior and G3 evidence/activation safeguards remain integrated. Both preserved rehearsal projects audit successfully: the ready project has 53 commits and passes readiness; the changed project has 54 commits and fails on changed query/evaluation dependencies. A fresh execution of the documented example passes all 37 declared expectations, including retained failed evidence, verified recovery and rejected outdated rollback. The 26 workflow regression tests also pass.

| Requirement | Product-review conclusion |
| --- | --- |
| R01 | Entry-guide use, saved first session, recovered cold context and readable next actions meet the agent-experiment acceptance. Human usability generalization remains untested. |
| R02 | Current/proposed maps, explicit actors/branches/payloads, attributed coverage and honest gaps are visible. The novice handoff does not claim operational completeness. |
| R04 | Superseded hearsay is historical, replacement/source links remain retrievable, and next-day stale fixture evidence is disclosed. |
| R11 | Practice projects run outside the library without credentials or third-party runtime packages. Existing output is preserved. Clean-clone packaging remains G5. |
| R12 | The guide selects specialists and maintains formal records; artifacts identify inspected evidence, checks, constraints and next action. Renderer changes improve the novice-facing handoff. |

Requirement IDs refer to the [development plan](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/PLAN.md:9).

## Exact commands and results

All top-level commands ran from `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`. The [retained harness](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/product-checks.py) records 38 commands with exact arguments, working directories, stdout, stderr and exit codes in [product-evidence.json](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/product-evidence.json). This includes reviewed texts and both original command-log contents. All project CLI probes used absolute paths from an unrelated temporary directory containing spaces. Archives were extracted only into temporary copies.

Main reproducible command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G4/product-checks.py
```

Final exit 0. Exact selected outputs:

```text
PASS first_revision_and_no_release: {"records": 22, "revision": 4}
PASS resumed_revision_and_no_release: {"records": 95, "revision": 40}
PASS first_render_rework_is_readable: {"activation_line": "No local simulation is activated. No infrastructure deployment is recorded here.", "characters": 7420}
PASS resume_preserves_first_history_and_source: {"first_commits": 4}
PASS all_ten_sources_and_schema_are_exact: {"interviews": 10, "schema": "S11"}
PASS saved_queries_reproduce_13_and_4_rows: {"columns": ["tenant", "request_id", "customer_id", "urgency", "customer_tenant", "customer_name", "decision_seq", "approved", "event_seq", "latest_handoff_owner", "routing_disposition"], "corrected": 4, "naive": 13}
PASS ready_rehearsal_readiness_expected: {"errors": [], "status": "pass"}
PASS changed_rehearsal_readiness_expected: {"errors": ["REQ_CARDINALITY: no passing applicable evaluation of criterion and implementing components", "REQ_ISOLATION: no passing applicable evaluation of criterion and implementing components", "REQ_ROUTING: no passing applicable evaluation of criterion and implementing components", "Q_ROUTES: executed query dependencies changed"], "status": "fail"}
PASS example_37_expectations_pass: {"expectations": 37}
{"checks": 42, "commands": 38, "failed": []}
```

The harness ran the workflow suite with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_workflow.py -q
```

Exit 0:

```text
Ran 26 tests in 1.120s

OK
```

The final outer invocation’s full stdout/stderr/exit code is retained in `product-run-final.json`. The example’s actual nested execution arguments and outputs, and all 37 expected/observed checks, are retained within the independent evidence file.

Reviewer probe corrections are preserved separately. The first script assumed the saved SQL column was `disposition`; it is `routing_disposition`, causing a reviewer-side KeyError. A subsequent inspection mistakenly parsed plain-text HEAD as JSON. Their exact error outputs are in `product-probe-errors.json`, and the first script is `product-checks-first.py`. The first abort occurred before its child-command log was flushed; subsequent complete attempts preserve all child commands. The second complete attempt had one overly literal assertion comparing an apostrophe against its correctly escaped HTML entity. Its script/results remain `product-checks-second.py` and `product-evidence-second.json`. Comparing rendered text after entity decoding resolved that assertion; no product file changed.

Candidate verification used SHA-256 for every manifest entry before and after testing. All 66 entries matched, as did the original experiment/archive/image hashes. Selected artifact hashes:

```text
e4a716bd9181b99725a7f05c027970832f7faa7c047652824ce7f9afdf30deb9 candidate.json
5dbfe6c72ad3ecdd14825a3fb82272f12fb628a9c081b66e13e17d4172c35d06 product-checks.py
e90449583def2413c3f2fb28c598391be47b837c576c73b65572cd93e69fcde1 product-evidence.json
d0853393eafaaf6fe666e03803c29aad1cea0b0458183992f27585d3b2471851 product-run-final.json
7461d926b10c12b56ff7313696548b1f6f20243e0f6922561f7d625efc3ad7ae product-checks-first.py
ec84654dbe23cbb99747ce76de08875139c4e682d85e4a51a14a20d43f9ba427 product-checks-second.py
7d5fe77777204c003b30e4e6c61bfd28cdfd04fbcb30ae8031a06cc43a5b942d product-evidence-second.json
```

## Limits

This review used the available macOS Python 3.12 environment and explicitly synthetic stakeholder/data projects. The experiments demonstrate bounded agent-guided start/resume behavior; they do not establish novice-human success rates, model generalization, exhaustive discovery, live data freshness or real tenant-security controls. I inspected the retained Mermaid images and text but did not independently rerender them. I reran the relevant workflow suite and complete worked example, not the council suite or every previously reported regression. No external deployment or messaging occurred. G5 packaging, clean-clone validation and final release sign-off remain later work.
