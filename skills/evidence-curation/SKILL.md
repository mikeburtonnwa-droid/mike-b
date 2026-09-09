---
name: evidence-curation
description: Capture attributable sources, reconcile claims and retrieve current project knowledge with freshness, conflicts, supersession and dependency impact. Use after discovery, before consequential decisions and when resuming a project.
---

# Evidence curation

Inputs: artifacts/new material, task query, environment/applicability and explicit as-of date. Read [records](../../docs/RECORDS.md), [CLI](../../docs/CLI.md) and provenance/context [references](../../references/professional-methods.md).

Capture original bytes and origin/date metadata. For consequential assertions record locators, applicability and reported/inferred/verified/disputed status. Verification requires actual evidence, method/date and a defensible review date. Copying a summary is not fresh verification. Unestablished truth stays reported or disputed.

Run `context QUERY --as-of DATE`, inspect warnings and follow originals. Retrieval follows prerequisites, replacements and conflicts; also inspect map/data records for vocabulary the lexical query may miss. No result is not proof of absence. Separate age, authority, scope and certainty.

Record contradictions bilaterally in one batch. A supported replacement needs a new claim and `supersede`; another environment/variant remains separate. Never rewrite an existing assertion or applicability. Historical dependents may need deliberate migration and retesting.

Run `impact ID` before revising evidence and `drift RELEASE` for pinned releases. Fresh context guides new work; a release stays bound to its evaluated snapshot. External changes are unknown until tools or people supply evidence. Recommend rechecking; do not invent live monitoring.

Outputs/handoff: captured IDs, cited current answer, conflicts/staleness, replacement rationale, affected records, what changed/how learned/dates, release implications and next verification action. If integrity fails, stop dependent work and restore trusted history/source backup; do not relabel corrupted evidence current.
