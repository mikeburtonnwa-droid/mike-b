---
name: operations-review
description: Check release readiness, pin and activate a local simulation, inspect drift and record verified incident recovery. Use for operating handoffs or investigating a failure.
---

# Operations review

Inputs: handoff/architecture, captured evaluations, environment/as-of date, existing releases or incident. Read [contract](../../docs/CONTRACT.md), [CLI](../../docs/CLI.md) and operations/evaluation [references](../../references/professional-methods.md).

Audit, check process/architecture, then check release readiness. Resolve blockers instead of overriding them. Pin with `release`; activation/rollback here are always **local-simulation**. Show that label with active release status. Actual deployment is separate work requiring runtime access, authorization, results and monitoring evidence.

Use `drift`/`impact` when knowledge or implementation changes. Recheck present fitness before activation/rollback. Old snapshots remain historical evidence even when activation fails. New critical gaps and changed pinned dependencies block; unrelated notes are informational.

Before repair, capture incident symptoms/evidence, release, affected elements, environment, opened date and recovery criterion. Record diagnosis, bounded action, existing authority and follow-up. Inspect uncertain external writes before retrying. Do not expand permission or weaken criteria as recovery.

Execute recovery verification, capture results and evaluate affected elements against the incident's exact criterion. Failed, missing, premature, expired or changed evidence keeps it open. Use `close-incident` only after success and diagnosis/action/authority/follow-up. Closed history is immutable; further work becomes another linked incident.

Outputs/handoff: readiness report and simulation release/activation IDs, or incident/action/verification IDs, residual risks, real deployment steps, follow-up and checkpoint. Missing tools/evidence leave that work blocked while independent investigation continues.
