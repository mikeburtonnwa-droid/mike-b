Verdict: APPROVE
Candidate SHA-256: e4a716bd9181b99725a7f05c027970832f7faa7c047652824ce7f9afdf30deb9

## Scope and findings

I approve this frozen candidate's G4 architecture, evaluation and operations rehearsal, including the bounded first-interview and cold-resume evidence. No unresolved blocker remains in my remit. This is one council opinion; the orchestrator must still record the gate decision. Approval covers the synthetic four-request workflow and local simulations, not real deployment, comprehensive discovery or model-provider performance.

1. **Nonblocker — Architecture and process evidence support the declared fixture.** Independently reproduced current and proposed maps each contain six steps, explicit branches, actors, systems, boundaries, payloads and receivers. Proposed steps retain current baseline links. Three distinct critical requirements cover cardinality, tenant isolation and routing; DEC_CODE compares deterministic code, runtime model inference and manual handling, and traces all three to COMP_ROUTER. The deterministic choice fits the supplied exact keys and routing rules. All eight concerns have dispositions, rationale and captured supporting sources. The operating handoff names runtime, artifact, owner, prerequisites, restricted authorization and remaining deployment work. Process and architecture checks pass for the scripted fixture. Requirements: R02, R06, R12.

2. **Nonblocker — Execution evidence and consequential transitions withstand the exercised failures.** The actual bad join produces 13 rows for four request keys, including six cross-tenant customer rows. Corrected SQL produces four rows and the four predefined dispositions. Cardinality, isolation and routing are evaluated separately; failed executions retain exit code 1. The seven original evaluation captures have unique canonical run IDs and timezone-aware execution dates. The rehearsal rejects failed readiness and unsuccessful recovery, then closes with fresh passing evidence. In an independent second lifecycle, another actual approval-loss run invalidated the earlier passing handoff; both older passing evidence and the latest failure were rejected for closure. An unchanged old result captured under a new source alias could not be promoted. Fresh execution restored readiness and closed the new incident. Requirements: R06, R07, R08; G3 execution-identity integration.

3. **Nonblocker — Releases remain historical snapshots when current fitness changes.** Every REL1 object across its 13 retained post-creation states was identical. The independent second incident cycle preserved both REL1 and REL2. Changed approval-data metadata invalidated the executed query and evaluations; rollback was rejected without changing HEAD. Impact included Q_ROUTES and COMP_ROUTER. A complete, otherwise valid note could be saved under a fresh ID but was atomically rejected under REL1. The ready project audited at revision 53, the deliberately changed project at revision 54, and the independently extended incident project at revision 60. Requirements: R07, R08; G2 persistence integration.

4. **Nonblocker — Cold resume supports a narrower design handoff than the scripted operations rehearsal.** I inspected both experiment reports and their command logs, and independently audited separate extracted copies of both preserved projects. The first interview remains revision 4, with seven reported claims, unknown ownership, explicit gaps and a discovery checkpoint. The resumed project is revision 40 with 95 records, explicit hearsay supersession, three requirements and eight deferred concerns. Its process, architecture and release checks correctly fail; it has no component, evaluation, release or activation. I independently reexecuted its captured Q01, Q04 and Q05 SQL against captured S11 and obtained exactly the retained rows. Q04/Q05 remain current while Q01–Q03 remain archived. Missing-standard-approval coverage remains open as I07. These limits are consistent with the predeclared fixed-fixture discovery-to-design acceptance and the contract's navigation-only stage semantics. They do not establish operating readiness. Requirements: R02, R06, R12, with supporting R01/R04 resumption coverage.

5. **Nonblocker — Presentation and production boundaries are consistent with the evidence.** Independently generated Mermaid text exactly matches both supplied diagram sources. Visual inspection of both PNGs found readable activity labels, decision diamonds, terminal shapes and labeled branches without clipping. Derived maps identify REL2 as an active local simulation, retain coverage caveats, and show a readable checkpoint with unresolved real deployment work. The first experiment predates the presentation refinement; current rendering is supported by the reproduced output, regression checks and subsequent resume evidence. The guide and specialist instructions define inputs, methods, output records, handoffs and failure behavior. Temporary projects ran outside the library using local Python/SQLite without credentials or third-party Python dependencies. Requirements: R02, R11, R12.

## Verification commands and results

All commands below ran from:

`/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`

The reviewer capture helper records exact argument arrays, working directory, timestamps, stdout, stderr and exit code. Full command records are retained as `development/gates/G4/architecture-command-*.json`; nested actual execution commands and outputs are also retained in the probe and reproduced event files.

Before testing:

```sh
python3 development/gates/G4/architecture-run.py manifest-before python3 -c 'import hashlib,json,subprocess; from pathlib import Path; p=Path("development/gates/G4/candidate.json"); m=json.loads(p.read_text()); bad=[k for k,v in m.items() if hashlib.sha256(Path(k).read_bytes()).hexdigest()!=v]; print("candidate_sha256",hashlib.sha256(p.read_bytes()).hexdigest()); print("entries",len(m),"mismatches",bad); print("commit",subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip()); assert not bad'
```

Exit 0, empty stderr: candidate hash matched the report header; `entries 66 mismatches []`; `commit 71afb9e`.

Main independent work:

```sh
python3 development/gates/G4/architecture-run.py probes python3 development/gates/G4/architecture-probes.py
python3 development/gates/G4/architecture-run.py supplement python3 development/gates/G4/architecture-supplement.py
python3 development/gates/G4/architecture-run.py regression python3 -m unittest discover -s tests -v
```

- Probes: exit 0, empty stderr; reproduced all 37 rehearsal assertions; 38 reviewer assertions passed. Its subprocess invocation runs `examples/order-triage/rehearse.py --output <temporary-directory>/rehearsal with spaces` from an unrelated temporary working directory. Exact resolved arguments and all outputs are preserved.
- Supplement: exit 0, empty stderr; nine checks passed, including the valid namespace control, independent cold-resume SQL reexecution and exact Mermaid comparisons.
- Regression: exit 0, empty stdout; unittest stderr ends with `Ran 86 tests in 4.945s` and `OK`. This includes prior persistence, audit, locking, council integrity, coverage, query binding, expiry, environment, immutable release, incident and execution-replay regressions.

Two reviewer limitations were corrected without rewriting the original evidence. The initial namespace probe used an incomplete note and was rejected for missing owner, so that result alone did not establish namespace enforcement; the separately retained supplement adds a valid positive control and receives `Stable ID already belongs to a release`. A preliminary `git diff e0357b8..71afb9e --stat` exited 128 because the first revision did not exist. The separate `changes-rerun` command instead compared the actual G3/G4 manifest entries. Neither was a product failure.

After testing:

```sh
python3 development/gates/G4/architecture-run.py manifest-after python3 -c 'import hashlib,json,runpy,subprocess; from pathlib import Path; p=Path("development/gates/G4/candidate.json"); m=json.loads(p.read_text()); current=runpy.run_path("scripts/record_development.py")["manifest"](); print("candidate_sha256",hashlib.sha256(p.read_bytes()).hexdigest()); print("entries",len(m),"current_entries",len(current),"manifest_exact_match",m==current); print("commit",subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip()); assert m==current'
```

Exit 0, empty stderr: the same candidate hash; `entries 66 current_entries 66 manifest_exact_match True`; `commit 71afb9e`. Product files remained identical to the frozen manifest.

The [probe source](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/architecture-probes.py), [supplement source](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/architecture-supplement.py), [exact subprocess evidence](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/architecture-probe-commands.json), [reproduced events](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/architecture-reproduced-events.json), [reproduced projects](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/architecture-reproduced-projects.zip), [second lifecycle project](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/architecture-second-lifecycle.zip) and [evidence hashes](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/architecture-command-evidence-inventory.json) are retained separately from earlier artifacts.

## Requirement coverage and limits

The [plan](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/PLAN.md) and [contract](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/docs/CONTRACT.md) define this review's requirements.

| Requirement | G4 evidence accepted |
| --- | --- |
| R02 | Attributed bounded current map, distinct proposed map, explicit incomplete novice coverage, reproduced readable diagrams |
| R06 | Three separate criteria; requirement/decision/component trace; eight concerns; actual distinct evaluation runs; current/proposed/local-activation boundaries |
| R07 | Failed readiness, unchanged complete snapshots, release-ID collision rejection, changed dependency impact and atomic rollback refusal |
| R08 | Actual injected fault, retained failed recovery, old-result/replay rejection, fresh closure, unchanged criterion and release history |
| R11 | Public example/private temporary projects, stdlib execution, explicit synthetic storage guidance; G5 clean-clone packaging remains later work |
| R12 | Guide/specialist input and output contracts, evidence protocol, failed-check handoffs and bounded cold-resume next action |

These are fixed synthetic data and agent experiments, not human novice usability research, independent real stakeholder verification, live tenant access-control testing, scale/availability measurements or cross-provider model evaluation. Unknown urgency, malformed business inputs, missing customers and unavailable-versus-legitimately-missing approval data require further design before real adaptation. The fixed fixture does not certify those cases; the cold-resume handoff explicitly retains them.

Hashes and execution timestamps establish the exercised local evidence protocol, not authenticated external truth. The regression suite exercises existing malformed-record and persistence failures; this review does not simulate every filesystem or hardware failure. I inspected the supplied PNGs and compared their source to independently generated Mermaid; I did not reinstall or independently rerun the Mermaid renderer.

No product files, prior reports or earlier probe artifacts were edited. No other current council report was consulted, no work was delegated, and no external deployment or communication was performed.

