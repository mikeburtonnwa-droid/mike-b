# Local project tools

Requires Python 3.10+ on macOS or Linux (uses POSIX file locking). No third-party Python packages, model API keys or network calls. The agent-facing interface is JSON; the [guide skill](../skills/agent-architect/SKILL.md) manages it for the user. `render` prints Markdown. Exit 1 denotes a completed check with blockers; exit 2 denotes an input/integrity/precommit error. Inspect JSON status even for exit 0.

Run from the library root, or use the absolute path to `scripts/aa.py` from anywhere. Choose a project directory outside the public repository. The examples below use `/tmp/aa-project` for disposable practice; use a durable private directory for real work.

```sh
python3 scripts/aa.py --project /tmp/aa-project init --title 'Onboarding' --scope 'Request to account creation' --owner 'Project owner'
python3 scripts/aa.py --project /tmp/aa-project show
python3 scripts/aa.py --project /tmp/aa-project source --id S01 --title 'Interview' --file notes.txt --kind interview --locator 'Meeting 1, notes' --environment operations --expect-revision 1
python3 scripts/aa.py --project /tmp/aa-project put claim.json --expect-revision 2
python3 scripts/aa.py --project /tmp/aa-project context 'account creation' --as-of 2026-09-09
python3 scripts/aa.py --project /tmp/aa-project impact S01
python3 scripts/aa.py --project /tmp/aa-project audit
```

Each mutation returns a new revision. Supply the revision you actually read; a stale edit fails and requires rereading/reconciliation. Batch mutually related records in one JSON array so bilateral conflicts and forward links validate atomically. Exit 0 means the command completed; inspect its status. `committed-durability-uncertain` means HEAD already changed but its durability flush failed: audit and back up the visible commit before continuing, and never blindly retry it. Exit 2 means an input/integrity or precommit failure. Read failures never substitute a blank project.

Example claim after capturing S01:

```json
{"id":"C01","type":"claim","title":"Account creation owner","description":"Reported in first interview","status":"reported","assertion":"Operations creates accounts","applicability":"standard onboarding","evidence":[{"source":"S01","locator":"lines 3-5"}],"tags":["onboarding"]}
```

`put` replaces a complete record; omitted optional fields are removed. Assertions and superseded claims cannot be rewritten. Capture a new claim and use `supersede OLD NEW --reason TEXT --expect-revision N`. Different applicability requires a separate variant. Verified claims require `verified_on`, `review_due`, `verification`, and evidence; the tool validates their presence, not their truth. Missing review dates remain unknown.

For bilateral conflict, update both records in a single batch with reciprocal `conflicts_with` lists and a non-verified status (normally disputed). Retain the conflict until a supported resolution. Supersession resolves only a direct conflict between its endpoints.

Checkpoint JSON contains exactly `current_task`, `completed` (text list), `unresolved` (text list), `next_action`, `relevant_ids` (ID list), and `stage` (intake/discovery/design/build/release/operate). Save with `checkpoint FILE --expect-revision N`.

Clarify the authoritative project brief with `brief FILE --expect-revision N`. Input is `{"title":"Standard requests","scope":"Standard requests only","owner":"Alice","rationale":"Stakeholder clarification","evidence":[{"source":"S01","locator":"lines 1-2"}]}`. Capture the clarification first. History preserves prior values; changed brief fingerprints invalidate old evaluations and activation of old releases. Resume context displays the current brief and source pointers.

## Storage and recovery

HEAD points to an immutable hashed history envelope containing canonical state and its audit event. Sources are content-addressed blobs. The commit point is the atomic HEAD replacement. A process killed before that point may leave an unreachable history/source object; it cannot expose a partial revision. Unreachable objects are not active evidence. Do not delete historical source blobs: audit checks every committed revision. File locks release when the process exits; no manual stale-lock deletion is needed. Busy writers fail explicitly.

Local hashes detect accidental or partial tampering, not an administrator who rewrites the entire history. Back up the whole project directory. No credentials are stored by these commands, but supplied source content may itself contain sensitive data; the adopter controls capture and access. Do not put real source material into the public library.

## Process, architecture and operations

Read [record inputs and evaluation protocol](RECORDS.md) before creating specialized records. `schema` prints exact fields/types/statuses without requiring an initialized project (the global project argument still identifies the intended location).

```sh
python3 scripts/aa.py --project /tmp/aa-project schema
python3 scripts/aa.py --project /tmp/aa-project check process --view current
python3 scripts/aa.py --project /tmp/aa-project render --view current --as-of 2026-09-09
python3 scripts/aa.py --project /tmp/aa-project check architecture
python3 scripts/aa.py --project /tmp/aa-project fingerprint REQ1 COMP1
python3 scripts/aa.py --project /tmp/aa-project query-fingerprint QUERY1
python3 scripts/aa.py --project /tmp/aa-project bind-query QUERY1 --result QUERY_RESULT1 --expect-revision 11
python3 scripts/aa.py --project /tmp/aa-project evaluate evaluation-input.json --expect-revision 12
python3 scripts/aa.py --project /tmp/aa-project check release --handoff HANDOFF1 --environment fixture --as-of 2026-09-09
python3 scripts/aa.py --project /tmp/aa-project release REL1 --handoff HANDOFF1 --environment fixture --authority 'Authorized local rehearsal' --as-of 2026-09-09 --expect-revision 13
python3 scripts/aa.py --project /tmp/aa-project activate REL1 --environment fixture --reason 'Local rehearsal' --as-of 2026-09-09 --expect-revision 14
python3 scripts/aa.py --project /tmp/aa-project drift REL1
python3 scripts/aa.py --project /tmp/aa-project close-incident INC1 --evaluation RECOVERY1 --as-of 2026-09-09 --expect-revision 20
```

These show command syntax, not a runnable sequence: use IDs and the actual current revision from your project. `release` and `activate` record a **local-simulation**, and run no deployment commands. `activate --rollback` requires a previously activated simulation and repeats current validity/drift checks. An old snapshot is readable even when it no longer passes activation. Actual deployment steps remain in the handoff.

`fingerprint` returns target_hashes and brief_hash for capture before the run. The executed procedure supplies run_id (fresh canonical UUID) and run_at (timezone-aware execution timestamp), with run_on equal to its UTC date. `evaluate` verifies/binds evidence and returns evaluation ID and outcome separately from save status; it does not execute tests. Duplicate run IDs/content aliases are rejected; retrieve the existing evaluation instead. Execution time governs latest results, and tied failures require a later successful run. Equality with exit_code 0 computes pass. Direct `put` cannot create/change evaluations or label new queries executed; use the documented binding protocols. Direct `put` cannot close/rewrite a closed incident.

Checks are conservative: every declared map gap and active consequential process/data/design record participates in release review. Noncritical deferred architecture concerns may remain documented, but critical deferred concerns, open critical issues, open incidents in the environment, bad claim freshness and missing applicable critical tests block.
