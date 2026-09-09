# Local project tools

Requires Python 3.10+ on macOS or Linux (uses POSIX file locking). No third-party Python packages, model API keys or network calls. The agent-facing interface is JSON; the guide skill will manage it for the user.

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

## Storage and recovery

HEAD points to an immutable hashed history envelope containing canonical state and its audit event. Sources are content-addressed blobs. The commit point is the atomic HEAD replacement. A process killed before that point may leave an unreachable history/source object; it cannot expose a partial revision. Unreachable objects are not active evidence. Do not delete historical source blobs: audit checks every committed revision. File locks release when the process exits; no manual stale-lock deletion is needed. Busy writers fail explicitly.

Local hashes detect accidental or partial tampering, not an administrator who rewrites the entire history. Back up the whole project directory. No credentials are stored by these commands, but supplied source content may itself contain sensitive data; the adopter controls capture and access. Do not put real source material into the public library.
