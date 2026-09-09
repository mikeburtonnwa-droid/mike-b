# Build evidence and review trail

The [development plan](../development/PLAN.md) defines five bounded gates and twelve observable requirements. Each gate needs three independent opinions and an orchestrator decision for the same candidate. An EDITS or DENY opinion blocks progression until rework and required re-review resolve it. No majority vote substitutes for unresolved findings.

The final outcome is in the [G5 sign-off](../development/gates/G5/signoff.md). The tables below locate evidence; they do not predeclare that a pending gate has passed.

| Gate | Bounded work | Decision and exact messages |
| --- | --- | --- |
| G1 | Journey, requirements, contracts and review protocol | [Decision](../development/gates/G1/decision.json), [transcript](../development/gates/G1/transcript.jsonl) |
| G2 | Sources, claims, context, impact, atomic history and audit | [Decision](../development/gates/G2/decision.json), [transcript](../development/gates/G2/transcript.jsonl) |
| G3 | Process/data/architecture/evaluation/release/incident functions and skills | [Decision](../development/gates/G3/decision.json), [transcript](../development/gates/G3/transcript.jsonl) |
| G4 | Ten-stakeholder exercise, actual SQL, cold resume and recovery | [Evidence index](../development/gates/G4/README.md), [decision](../development/gates/G4/decision.json), [transcript](../development/gates/G4/transcript.jsonl) |
| G5 | Packaging, clean clone, full verification and sign-off | [Gate records](../development/gates/G5/), [sign-off](../development/gates/G5/signoff.md) |

Candidate manifests hash product files. Each decision binds the accepted manifest, reviewer report hashes and preceding decision. Transcripts preserve exact observable dispatches, responses, time, sequence, sender, recipient and a hash chain. Reports preserve reasons, commands, outcomes, limits and rework. Root was this build's decision orchestrator.

## Requirement evidence

| Requirement | Evidence to review |
| --- | --- |
| R01: one guide, novice start/resume | [First session](../development/gates/G4/novice-start.md), [different agent's resume](../development/gates/G4/novice-resume.md), archived projects and independent G4 reviews |
| R02: labeled current-state map and gaps | [Sample map](../examples/order-triage/sample-current-map.md), [preserved incomplete handoff](../development/gates/G4/novice-resume-artifact.md), process checks and G3/G4 negatives |
| R03: captured provenance and knowledge states | [Record protocol](RECORDS.md), [core tests](../tests/test_core.py), G2/G3/G4 integrity opinions |
| R04: freshness, supersession, context and impact | [Core tests](../tests/test_core.py), [G4 integrity review](../development/gates/G4/integrity.md), [sample impact](../examples/order-triage/sample-change-impact.json) |
| R05: schema/query grain, keys and execution | [Raw schema](../examples/order-triage/inputs/setup.sql), [actual rehearsal](../examples/order-triage/README.md), seven independently replayed retained queries in G4 |
| R06: traced architecture and distinct criteria | [Workflow tests](../tests/test_workflow.py), [execution protocol](RECORDS.md), [G4 architecture review](../development/gates/G4/architecture.md) |
| R07: pinned evidence, failure and drift gates | [Workflow tests](../tests/test_workflow.py), [run identity/order regressions](../tests/test_run_identity.py), G3 replay rework and G4 snapshot/rollback probes |
| R08: bounded recovery and fresh verification | [Actual rehearsal](../examples/order-triage/rehearse.py), [G4 architecture second-lifecycle evidence](../development/gates/G4/architecture.md) |
| R09: independent opinions and final gate | [Council checker](../scripts/check_council.py), [adversarial council tests](../tests/test_council.py), all five decision chains |
| R10: traceability of messages, reasons and rework | Transcripts and reports in each gate above; audit limits below |
| R11: private projects and dependency-free local tool | [Anatomy](ANATOMY.md), [example overwrite/integration tests](../tests/test_rehearsal.py), G5 clean-clone and CI evidence in sign-off |
| R12: specialist input/output/handoff contracts | [Skill index](../skills/README.md), [professional references](../references/professional-methods.md), G3/G4 usability reviews and G5 skill checks |

## Rework and audit limits

G1 clarified novice transitions and included normative planning files in candidate hashes. G2 repaired malformed-input, provenance/conflict, council-binding and postcommit error handling. G3 repaired coverage/provenance, immutable query binding, brief updates, latest-result selection, release namespaces and future evidence; a later review exposed old-run replay, which required explicit execution identity/time and another unanimous re-review. G4 repaired example-authoring mistakes and presentation friction found by the first fresh agent. Original failing opinions and attempts remain available in their gate directories.

Observable inter-agent message chains are retained; private internal reasoning is not available. These are locally recorded messages and evidence, not authenticated identities or proof of unseen behavior. Some early failed candidate trees are represented by manifests, reports and probe sources rather than complete standalone source snapshots. Accepted source revisions are preserved in Git. One G4 product-review harness aborted before flushing its initial nested command log; its source/outer exception and subsequent complete captured reruns are retained, and the report discloses the gap. These limits must not be presented as complete replay of every historical internal subprocess.

Historical command paths identify the machine and temporary project used at the time; they are evidence, not portable instructions. Use the worked example to produce fresh paths and execution identities. Synthetic project archives can be extracted into a separate practice directory and audited with the CLI.

To reuse this review method, define your own bounded requirements and roles, freeze the candidate, persist each dispatch before sending it, capture commands/results incrementally (including exception paths), collect independent opinions, and record the orchestrator's decision. Preserve rejected opinions and name rework explicitly. A passing checker verifies the recorded protocol; meaningful independent review remains essential.
