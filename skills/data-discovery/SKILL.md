---
name: data-discovery
description: Map schemas and query paths to workflow stages with environment, grain, keys, refresh, joins and executed result evidence. Use when a workflow reads, transforms or writes structured data.
---

# Data discovery

Inputs: process/requirements, source access or exported schema/samples, environment and permitted operations. Consult [records](../../docs/RECORDS.md) and data/evaluation [references](../../references/professional-methods.md).

Inspect real metadata when available; otherwise label exports and access limits. Capture versioned evidence. Record schema/table, business grain, keys/uniqueness assumptions, environment and refresh. Link assets to their workflow stage with dependencies; matching names do not establish identity.

For each query preserve SQL, parameters, assets, join assumptions and limitations. Execute before consequential use through an authorized tool on a safe representative fixture or authorized environment. Test uniqueness, nulls, join multiplicity, orphans, time/tenant filters and reconciliation totals. Valid SQL can duplicate business events. Trace raw, intermediate and final outputs explicitly.

Before execution run `query-fingerprint`; capture its object with actual query output using the protocol in records. Use `bind-query` to attach matching evidence. Executed queries are immutable apart from archival; changes need a new query version and run. The CLI checks definition/dependencies/environment, but does not run SQL or prove semantics. Samples/exports do not establish production freshness. Without execution access, retain a draft and blocking issue.

Outputs/handoff: workflow-linked data/query records, captured execution evidence, cardinality/reconciliation findings, usable paths, keys/grain, refresh expectations, authorized operations and limits. Changes require impact analysis and applicable reevaluation.
