---
name: architecture-delivery
description: Turn current-state evidence into proposed architecture, implementation, critical acceptance evaluations and an operating handoff. Use when choosing code, model or human execution and checking architecture coverage.
---

# Architecture delivery

Inputs: scoped current map, coverage/gaps, current claims, data/query paths and constraints. Read [records](../../docs/RECORDS.md), [contract](../../docs/CONTRACT.md) and architecture/evaluation [references](../../references/professional-methods.md).

Each critical acceptance criterion becomes a separate requirement linked to current process and claims. Record two or more plausible alternatives and evidence/rationale per decision. Use code for exact rules/calculations, a model for interpretation, and humans where authority/judgment requires it. Hybrid choices need explicit boundaries. A large context window does not validate facts or enforce transactions.

Create proposed nodes with current baseline links. Components name decisions, proposed steps, method, inputs/outputs, tools, persistent state, artifact and failure behavior. Capture actual implementation artifacts as source dependencies so changes can be represented as new versions. A path string does not monitor file contents.

Cover scope, execution, tools/data, state, context, recovery, evaluation and operations. Give each a disposition, rationale and reference. Implemented/platform-provided claims require actual host evidence. Deferred critical work blocks release; not-applicable needs a reviewable reason.

Implement bounded work using available tools. Define expected outcomes before runs, including missing data, ambiguity, tool failure, duplicate/uncertain writes and authority boundaries. Execute meaningful tests and retain failures. For model steps use representative cases, explicit rubrics, repeated runs where variability matters, and actual model/version/tool configuration. Do not claim cross-provider validation from one host.

Before each run, use `fingerprint` for the requirement and all implementing components. Capture its target_hashes and brief_hash plus the exact criterion in actual result JSON using the [evaluation protocol](../../docs/RECORDS.md). `evaluate` reports computed outcome and checks/binds hashes; it does not execute/authenticate the procedure. Brief/dependency changes or expired evidence require new evaluation. A later matching failure blocks release until a subsequent matching pass resolves it.

Have the actual execution procedure emit a fresh UUID run_id and timezone-aware run_at; derive run_on from its UTC date. A run can be imported once. Source aliases and a new evaluation ID do not create a new execution. Reuse existing evaluation IDs for history, and rerun the test to obtain new evidence. Execution time, including unresolved ties, governs readiness rather than import order.

Outputs/handoff: proposed map, architecture IDs, actual artifacts, captured test evidence, evaluations and runtime handoff with artifact/environment/owner/prerequisites/authority/remaining deployment steps. Run process, architecture and release checks. Return failed checks with repair actions; do not weaken criteria. Transfer to operations with explicit remaining limits.
