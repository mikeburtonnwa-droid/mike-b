# Record anatomy and handoffs

Run `python3 scripts/aa.py --project PRIVATE_PATH schema` for exact field types, required fields and statuses. Common required fields are `id`, `type`, `title`, `description`, `status`. Optional common fields are `depends_on` (ID list), `evidence` (`[{"source":"S01","locator":"lines 3-5"}]`) and `tags` (text list). Unknown fields fail. `put` replaces full records; preserve optional fields deliberately.

The guide writes records; the user reviews readable artifacts. IDs start with a letter and use letters, digits, hyphens or underscores. No delete operation exists. Archive eligible records deliberately; archived prerequisites block release. Dates use `YYYY-MM-DD`. Use `unknown` plus a gap/issue for absent facts.

| Type | Required specialist fields beyond common fields | Meaning |
| --- | --- | --- |
| source | Created by `source`: kind, locator, captured_on, environment, content_hash, blob; optional effective_on | Immutable captured bytes/metadata |
| claim | assertion, applicability; verified additionally needs verified_on, review_due, verification | Evidence required; bilateral conflicts_with optional; use supersede for replacement |
| note | owner, next_action | active / archived |
| issue | critical, owner, next_action | open / resolved; resolution requires text and evidence |
| process | view, kind, actor, system, boundary, inputs, outputs, variant, edges | current / proposed; proposed needs baseline current-step IDs to pass |
| coverage | dimension, value, critical, steps, owner | stakeholder/variant/exception; covered requires evidence/steps; gap requires gap text |
| data | environment, schema, table, grain, keys, refresh | Key text list, schema evidence and workflow dependencies |
| query | environment, sql, assets, parameters, join_assumptions, limitations | draft/executed/archived; bind-query adds executed_on, result_source, execution_hash |
| requirement | acceptance, critical, process, claims | One criterion per critical requirement; current process/claim IDs |
| decision | requirements, alternatives, rationale | At least two alternatives and requirement IDs |
| component | decisions, process, method, inputs, outputs, tools, state, failure, artifact | code/model/human/hybrid; proposed process IDs |
| concern | category, disposition, critical, rationale, reference | Eight categories; implemented/platform-provided require evidence |
| evaluation | Created by `evaluate` from input below | Immutable pass/fail, run identity/time/content hash, targets, brief/dependency hashes and recorded_revision |
| handoff | runtime, artifact, environment, owner, prerequisites, authorization, remaining_steps | Active handoff required; real deployment work explicit |
| incident | release, affected, environment, symptom, diagnosis, action, authority, recovery_criterion, follow_up, opened_on | open/closed; closure adds verification; scope/criterion immutable |

Unless otherwise stated, workflow records use active/archived. Named references use ID lists except single result_source/verification. They, depends_on and evidence sources participate in context, impact and hashes. Control-flow edges are not knowledge dependencies: loops are allowed but need a path to an end. Baselines and knowledge dependencies must be acyclic.

Process kind is start/activity/decision/end. Every edge has exactly `to`, `condition`, `kind` (normal/exception/handoff), `payload`, `receiver`. Use the receiving actor and actual payload on an owner/system/boundary change, with handoff or exception kind. Decisions need distinct labeled alternatives. Covered steps must be active current steps. Stakeholder values match mapped actors; variant values match mapped variants; exception values match exception-edge conditions and name the originating step. All mapped actors/variants/exception edges require matching coverage. All declared current gaps block conservatively, including noncritical ones. Real-world completeness still needs stakeholder/evidence judgment.

Concern category is scope, execution, tools/data, state, context, recovery, evaluation or operations. One active disposition per category: implemented/platform-provided/deferred/not-applicable. A string does not establish a real capability; evidence/rationale must support the actual environment.

## Project brief and query execution

Use `brief FILE --expect-revision N` to clarify the authoritative current title/scope/owner. Input has exactly title, scope, owner, rationale and evidence (nonempty source/locator list). Capture the clarification first. Old values remain in history; context exposes the current brief and its sources. The brief is included in evaluation/release fingerprints. Clarification or scope change cannot silently alter a pinned release or reuse evaluations against a different brief.

Create a query as draft with `put`. Run `query-fingerprint QUERY1` **before executing** and retain the object. Execute through the authorized database tool, then capture JSON of kind query-result with exactly environment, run_on, command, exit_code, query_fingerprint (the full pre-run object), and rows (array). `bind-query QUERY1 --result SOURCE_ID --expect-revision N` verifies a successful run, definition and asset/dependency fingerprints and attaches immutable execution evidence. It does not execute or authenticate SQL. Preserve raw execution logs as additional evidence when needed.

An executed query can be archived, but its definition/evidence cannot be rewritten. Create a new query ID for changed SQL, parameters or assets and execute it anew. Changed asset dependencies invalidate an old execution at readiness/context checks. Attributable source provenance is required for consequential data assets; incomplete assets can still be saved during discovery.

## Evaluation protocol

Before the run, execute `fingerprint REQ1 COMP1` and retain both returned fields: target_hashes and brief_hash. Define expected outcomes, then execute the test/observation through an authorized host tool. Capture output and a JSON source of kind `query-result` with exactly the fields below (replace both hash placeholders with the actual fingerprint output):

```json
{"environment":"fixture","run_on":"2026-09-09","run_at":"2026-09-09T14:00:00+00:00","run_id":"80b12f3b-7a75-4569-99c9-e90eeecab041","command":"python3 tests/check_routes.py","exit_code":0,"criterion":"Each request has exactly one route","target_hashes":{"REQ1":"replace-with-actual-hash-and-include-all-dependencies"},"brief_hash":"replace-with-actual-brief-hash","expected":{"unique_requests":3},"observed":{"unique_requests":3}}
```

Procedure and values must faithfully represent the run. Preserve raw logs as additional sources/dependencies when the wrapper omits evidence. The CLI neither executes nor authenticates the command. It computes pass only for exit_code 0 and canonical expected/observed JSON equality. Define expected outcomes before observing. Human/model judgments need explicit rubrics and preserved observation evidence; equality does not prove judge correctness.

Save this input and invoke `evaluate`:

```json
{"id":"EV1","title":"Route cardinality","description":"Executed fixture check","targets":["REQ1","COMP1"],"result_source":"RESULT1","valid_until":"2026-10-09","criterion":"Each request has exactly one route"}
```

Criterion must equal the critical requirement's acceptance and captured criterion. Targets include that requirement and every implementing component. Add prerequisites and captured implementation sources before running. Evaluation checks the pre-run target and brief hashes, then binds the result source too. Old results cannot be rebound after a dependency/brief change. Each criterion/run gets its own record; failures remain available. The receipt includes evaluation ID and computed outcome separately from persistence status.

The execution procedure generates a fresh canonical UUID run_id for each executed case and a timezone-aware run_at timestamp; run_on is its UTC date. In Python use `str(uuid.uuid4())` and `datetime.now(timezone.utc).isoformat()` inside the actual runner. The displayed UUID/time are examples; never copy them into new runs. A run's ID and captured content hash can be evaluated only once, including through source aliases or differently formatted JSON retaining the run ID. Reuse its existing evaluation ID when retrieving historical evidence.

For the same criterion, environment, current brief and implementing scope, readiness uses execution time, not import order. All runs tied at the latest timestamp must pass applicable checks; a tied failure requires a strictly later passing execution. A later failure blocks an earlier pass, while a subsequent matching pass can resolve it. Re-importing old evidence or backfilling an older run cannot promote it. recorded_revision remains audit metadata and only selects a representative among equally timed passing runs. Missing/expired/future evidence cannot qualify. Incident closure uses the same policy and requires all captured supporting sources to exist as of assessment.

Captured hashes identify saved bytes, not a live database, URL or file merely named by a path. Inspect the actual runtime/artifact and capture changes before reusing old results. Review dates reflect change rate and stakes; dates do not independently verify truth.

## Releases, incidents and views

Releases store checked records, selected evaluations, environment, handoff, authority, brief and snapshot hashes. They conservatively pin all active consequential process/data/design records. New notes are informational; new consequential records, changed brief/pinned records and live critical blockers prevent activation. `activate --rollback` also rechecks present fitness. Record and release IDs are globally unique in both creation directions.

Incident affected IDs must be requirements/components in its release. Recovery criterion, affected scope, environment, release and opened date cannot change after opening. Closure requires successful applicable evaluation, run no earlier than opening, covering affected elements and the exact criterion. Further work becomes another linked incident.

`render` prints Markdown with a Mermaid map, process metadata, coverage errors, claim freshness/source locators and a readable checkpoint. It shows the actual local simulation activation state and names the next action and unresolved work. Covered steps have attributed evidence; coverage is not a completeness or truth guarantee. Views are derived; HEAD, history and captured sources are canonical. Back up the complete private project. Never manually edit hashed blobs/envelopes.
