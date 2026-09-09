# Project record contract, version 1

The canonical record is a JSON document inside a project directory chosen by the adopter, outside this public library by default. Markdown summaries and Mermaid maps are derived from it. The agent application captures and reasons about information; the Python CLI enforces structure, links and consequential transitions. A passing check is structural evidence, not proof of the real world's completeness.

## Common structure

Project metadata contains schema version, ID, title, scope, owner, stage, created/updated timestamps and revision. Named collections contain records with globally unique stable IDs, a type, title, status, description, links, and type-specific fields. IDs use letters/digits/hyphens/underscores. Dates are ISO 8601. Unknown facts are explicitly unknown; absence is never fabricated into a verified fact. Each successful mutation increments the revision and appends an event with before/after hashes and actor. Concurrent writers serialize with a lock; failed mutations do not alter the project. Captured sources, historical revisions and releases are preserved. The audit is locally tamper-evident, not a cryptographic attestation against an administrator who can rewrite the whole directory.

## Sources, claims and knowledge

Sources record kind (interview, observation, document, schema, query-result, research), original locator, captured date, effective date if known, environment, and a project-relative immutable captured file/hash. Sources may be captured from a file or explicitly supplied text. No network fetching or credential storage happens implicitly.

Claims record an assertion, source IDs, exact source locators (page, timestamp, line or section), evidence status (reported, inferred, verified, disputed, superseded), applicability, last verified date, review due date and rationale. Verified claims require verification evidence and dates; the CLI cannot judge whether the evidence is true. Replacing a claim uses an explicit supersession operation linking both records and preserves the older assertion. Different environments and variants do not supersede each other automatically. Contradictions link both claims. Freshness is calculated using an explicit as-of date; it is independent of authority and certainty. Unverified knowledge never silently becomes verified through passage of time or repeated summaries.

Context queries retrieve matching records plus linked prerequisites and relevant conflicts, exclude superseded claims from active recommendations, and disclose stale/unverified evidence. Impact walks reverse dependency links transitively. A task context includes project revision, retrieval date, source pointers, current stage, and unresolved issues. A new session uses this context plus original evidence when needed, not a previous model's hidden thinking.

## Process and data

Process steps record actor, system, boundary, inputs, outputs, kind (start/activity/decision/end), variant, evidence links and outgoing edges. Edges contain destination, condition, kind (normal/exception/handoff), and handoff payload/receiving owner when applicable. Nonterminal steps need paths forward; decision paths must be labeled; declared process coverage dimensions include stakeholder groups, variants and exception scenarios with evidence or explicit gaps. Reachability, dead ends, unknown endpoints and unresolved boundaries are checkable. Actual completeness requires evidence and appropriate stakeholder review. Current-state and future-state records are separate.

Data assets record environment, schema/table, grain, key fields, refresh policy and provenance. Query records store text/file, source assets, parameters, join assumptions, execution date, result evidence and limitations. A executed query must have a result source; merely parsing SQL is not semantic validation. Tests assess multiplicity, missing keys and unintended filters for consequential paths.

## Architecture and operations

Requirements link to process elements and claims and define acceptance criteria plus criticality. Decisions link to requirements/evidence and record alternatives and rationale. Components link to decisions and specify execution method (code/model/human/hybrid), inputs, outputs, tools, persistent state and failure behavior. Architecture concerns (scope, execution, tools/data, state, context, recovery, evaluation, operations) each have a disposition: implemented, platform-provided, deferred or not-applicable, with rationale and evidence. Critical deferred concerns block release.

Evaluations link to requirements/components, define expected behavior and record observed outcome, run time, status, environment, artifact evidence and the record revision or relevant dependency hashes they exercised. Changed dependencies invalidate applicability. A release is an immutable snapshot of checked records and evaluation evidence. Activation records an explicit release ID; newer knowledge cannot silently rewrite the active snapshot. A later change yields drift/impact findings and a candidate release. Rollback activates an existing checked release and records the action. Historical release availability does not imply current fitness; activation checks source/evaluation integrity and reports current drift.

Incidents link to deployed release and affected elements, record symptom, evidence, diagnosis, action, authority, verification and follow-up. Closing requires verification evidence. Permission expansion and acceptance-criterion weakening are not recovery actions. This library records/simulates a deployment decision; real infrastructure release requires the connected runtime and actual authorization.

## Usability contract

One entry skill owns the journey and loads specialist skills only when needed. It accepts incomplete starting context and existing artifacts at any stage. It captures metadata, maintains IDs/links, shows changes and asks focused questions about consequential ambiguity. It does not ask novices to populate JSON. It offers a readable current-state map, evidence/conflict view, architecture coverage and release readiness. Every answer about project facts can expose its source and freshness. Context restart must preserve decisions and unfinished work.

The reusable library and project instances are separate. Professional references are selectively loaded and versioned; local interpretation is distinguished from standards. Standards citations do not establish conformance or professional certification. Synthetic fixtures are labeled and never passed off as stakeholder evidence.

## Journey and resumption

| Stage | Starting inputs | Outputs and advancement | Missing information or interrupted work |
| --- | --- | --- | --- |
| intake | A concern or existing artifacts | Scoped brief, owner, current task, capability inventory and next action; proceed to discovery with a provisional scope | Ask the smallest question needed to identify the concern; record unavailable tools rather than imply access |
| discovery | Notes, interviews, examples, schemas, observations or external research | Attributed sources, provisional map, data records, coverage gaps and conflicts; proceed to design when critical unknowns are resolved or explicitly bounded out of scope | Unknown owner after a first interview creates a gap and focused next question, not an invented owner or an immediate architecture |
| design | Scoped current-state evidence and requirements, or an imported design | Alternatives, decisions, components, concern dispositions, evaluation criteria; proceed to build when intended behaviors and critical interfaces are specified | Imported artifacts are proposals until evidence and coverage are checked; revisit discovery for missing prerequisites |
| build | Accepted design and available tools | Implementation artifacts and executed evaluations; proceed to release when readiness checks pass | Work only on independent implementable parts; record blocking dependencies and exact next action |
| release | Passing applicable evidence and operating handoff | Immutable candidate and explicit local-simulation activation; real deployment remains a separate evidenced action | Failed or missing critical evidence returns to build/design; no display may imply that local activation deploys anything |
| operate | A local simulation or separately evidenced deployment | Incident/change record, diagnosis, verified recovery, dependency impact and candidate updates | A failed verification keeps the incident open; revisit the affected stage without discarding history |

Stage is a navigation aid, not a declaration of readiness. Check commands determine coverage; release and incident transitions enforce their predicates. A checkpoint stores current task, completed work, unresolved questions, next action and relevant IDs. Start/resume reads it and validates referenced evidence before recommending action. Existing work may enter any stage, but does not bypass prerequisite checks. The first-interview acceptance case must leave unknown owner and missing exception paths visible; cold resume must recover pending work without the old conversation.

## Consequential transition predicates

Release creation requires at least one critical requirement, complete architecture concern dispositions, no unresolved critical issue/coverage gap, and a passing applicable evaluation covering every critical requirement. Each critical acceptance criterion is represented as its own requirement record. Evaluations bind their transitive dependency hashes, environment and captured result evidence; missing, failed, dependency-changed, future-dated or expired evidence cannot satisfy critical coverage. Referenced stale, disputed, superseded or unverified claims block critical release coverage. Source/hash integrity failures block every release transition.

Activation and rollback are explicitly **local simulations** in version 1 and every CLI/display labels them as such. They require the pinned snapshot to pass its readiness predicates at the activation date and the chosen environment to match. Critical changes to any pinned dependency since capture block activation/rollback; unrelated new records are informational drift. Historical snapshots stay readable even when no longer fit for activation. The production handoff identifies runtime (or unresolved choice), execution artifact/reference, environment, owner, prerequisites, evaluation evidence, authorization and remaining real deployment steps. No actual deployed state is inferred from a local active release. Real deployment is outside this release's execution scope.

Incident closure requires stated recovery criteria, a successful applicable evaluation of the affected elements, observed result evidence and recorded authority/action. Merely attaching a failed check does not close an incident. G3/G4 must test failing/missing/expired/environment-mismatched evaluations, source tampering, dependency change, stale rollback and unsuccessful incident verification as well as passing paths.

## Review audit operation

Only the orchestrator appends to the development transcript, serially. Reviewers write their own reports. Candidate manifests include this contract, all product files and development/PLAN.md, excluding mutable reports/transcripts and OS/cache metadata. Previous candidates and opinions are retained under distinct filenames. The G2 fault suite must exercise competing writers, stale expected revisions, interrupted persistence, tampered sources, invalid links/cycles and audit corruption.
