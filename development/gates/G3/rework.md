# G3 rework, revision 2

The initial candidate was blocked by all three reviewers. Original reports, candidate, scripts and results are retained. The orchestrator also recorded six independent failing reproductions in orchestrator-probes.json. No G4 work has begun.

| Finding | Correction | Regression evidence |
| --- | --- | --- |
| Integrity 1; root uncovered actor | Covered steps must be active/current; match each mapped actor/variant/exception condition to coverage | Current/proposed/archived/missing-actor tests |
| Integrity 2 | Consequential assets require attributable captured provenance | Missing lineage fails; captured schema passes |
| Integrity 3; root changed SQL | Dedicated query-fingerprint / bind-query protocol checks pre-run query and asset hashes; executed query identity immutable except archive; new definition needs new ID/run | Actual SQLite two-row/one-row case; SQL/parameters/assets edits reject; old result cannot bind new query; asset drift fails |
| Integrity 4; product 2 | Normalize missing payload; render full paths/payload/receiver and coverage tables | Sentinel and rendered package regression |
| Architecture 1; root later failure | Latest matching run by run_on then recorded_revision governs critical readiness; later failure blocks; later matching pass resolves | New release/activation and same-day ID-order tests; recovery after pass |
| Architecture 2; root ID collision | State and creation guards enforce record/release ID uniqueness in both directions | Put/source/evaluate/release collisions, unchanged HEAD and direct state validation |
| Architecture 3 | Shared evaluation applicability checks captured source dates, including incident verification | Future capture cannot close; valid recovery retained |
| Product 1 | Provenance-backed, revision-checked brief updates current title/scope/owner; context exposes current authority; history preserves old values; evaluation/release fingerprints include brief | Unknown intake → captured clarification → updated brief → cold resume; stale revision; old release/old result reject changed brief |
| Product 3 | Evaluation receipt contains ID and computed outcome separately from save status | Failed and passing receipt tests |
| Root stale evaluation context | Context exposes evaluation applicability errors, archived history and query dependency drift | Changed dependency warning regression |
| Root new critical scope | New consequential records and changed brief block old-snapshot activation | Evaluated new critical requirement cannot activate old release |

The query/evaluation input protocols changed intentionally to close evidence rebinding gaps. Re-review fixtures must capture query fingerprints before execution and bind results through bind-query; evaluation result JSON includes both target_hashes and brief_hash from fingerprint. Preserve original negative cases and save adapted probes separately. Tests/support.py provides explicitly synthetic protocol helpers; independent reviewers should still challenge behavior rather than merely reuse expected assertions.

Incident closure also requires the latest matching recovery evaluation so an earlier pass cannot hide a later failed recovery check. Critical knowledge still requires actual verification; hashes cannot authenticate source truth or an external command's execution. No actual deployment is claimed.

Validation: 78 regression tests passed (development/G3-rework-tests-final.txt); all seven skill frontmatters passed the skill-creator validator (development/G3-skills-r2.txt). The initial 24 fixture-setup errors and subsequent passing runs remain recorded. All three reviewers must explicitly re-review the revised frozen candidate before the orchestrator can pass G3.
