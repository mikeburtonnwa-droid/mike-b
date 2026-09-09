# Bounded development plan

Date: 2026-09-09. Scope: a cloneable, local-first agent-building workspace. This release supplies skills, canonical project records, derived views, deterministic validation, release snapshots, and a council audit protocol. An existing tool-enabled agent application executes the skills. No custom autonomous daemon, real customer deployment, or cross-provider performance claim is included.

The user authorized sequential development with independent multi-role reviews, an orchestrator decision, full inter-agent message traceability, rework records, integration checks, and final testing/sign-off. This plan is the execution boundary, not a claim of completion.

## Requirements

| ID | Observable requirement | Intended evidence |
| --- | --- | --- |
| R01 | A novice starts or resumes through one guide without selecting specialist roles or manually managing metadata | Fresh-context evaluator walkthrough |
| R02 | Current-state records identify actors, systems, boundaries, inputs, outputs, handoffs, branches, variants, exceptions, evidence and gaps | Process checks and rendered map |
| R03 | Sources remain attributable to captured content; claims distinguish reported, inferred, verified, disputed and superseded knowledge | Hash/provenance and transition tests |
| R04 | Context retrieval excludes superseded claims, exposes stale and disputed evidence, and follows dependencies | Deterministic context/impact tests |
| R05 | Schema and query records preserve environment, grain, keys, lineage, execution evidence and limitations | Data fixture and join-cardinality checks |
| R06 | Requirements trace to decisions, components, and evaluation evidence; current/proposed/deployed views stay distinct | Architecture checks and negative tests |
| R07 | A release pins evaluated knowledge and fails on unresolved critical coverage; later edits do not silently mutate it | Snapshot/activation/change tests |
| R08 | Recovery records cause, authorized action, verification and follow-up without rewriting history or weakening criteria | Incident rehearsal |
| R09 | Three independent reviewers per gate deliver approve/deny/edits; orchestrator resolves every blocker and records rework before proceeding | Gate transcript and gate-check command |
| R10 | All inter-agent dispatches, responses and follow-ups are preserved verbatim, with sender, recipient, sequence and time; reports and commands/results are retained | Transcript validation and linked reports |
| R11 | Public reusable material is separated from adopter project data; local CLI needs no credentials or third-party Python packages | Clean-clone smoke test and storage guidance |
| R12 | Skills have clear inputs, methods, outputs, references, handoffs and failure behavior | Skill validation and specialist review |

## Gates

| Gate | Bounded scope | Council roles | Exit evidence |
| --- | --- | --- | --- |
| G1 | Requirements, contracts, usability and traceability protocol | Product/novice advocate; data/provenance reviewer; architecture/verification reviewer | Three reports, resolved findings, decision |
| G2 | CLI, persistent records, sources, claims, context, impact, audit | Data integrity; adversarial reliability; novice usability | Core positive/negative tests and council agreement |
| G3 | Process/architecture/release/incident functions, skills and professional references | Process/discovery; architecture/operations; usability/integration | Linked views, checks, skills and tests |
| G4 | Ten-stakeholder fixture, independent fresh-context use, operational rehearsal | Novice operator; evidence auditor; production/evaluation reviewer | Executed fixture, cold resume, incident/release checks |
| G5 | Packaging, documentation, complete regression, clean clone and release sign-off | Release engineering; requirements auditor; skeptical user advocate | Reproducible tests, all prior gates verified, scoped sign-off |

## Gate rules

The parent agent is the decision orchestrator; reviewers do not edit the implementation. Each reviewer receives the same frozen candidate plus a distinct review remit and writes its report and command/result evidence to its assigned gate folder. The report includes verdict, findings with severity and file/evidence references, requirement coverage, tests run, and limits. A deny or edits verdict blocks the gate. Rework is followed by explicit re-review; unrelated reviewer approvals are retained only if the change demonstrably does not affect their remit, otherwise all affected reviewers re-review. The orchestrator cannot pass by majority or conceal a denied opinion. Unresolved disagreement returns to development or is reported as blocked, not silently waived.

Before dispatch the exact message is stored. On receipt, the exact response is stored. Side-channel inter-agent exchanges are prohibited unless copied into the transcript. Reviewer tool commands and results belong in their evidence reports. Transcript means observable communication and recorded tool evidence; private internal reasoning is not available and is not claimed. Gate candidate manifests hash implementation artifacts, excluding ongoing development logs and ephemeral files. A gate decision references the manifest and reports. Any post-review product change requires relevant re-review.

Work remains local through the gates. The final accepted release is committed and pushed to the already authorized public repository. Only synthetic examples and development evidence may be published.
