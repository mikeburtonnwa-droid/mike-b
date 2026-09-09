# G2 novice usability and integration review

Verdict: **EDITS**

Scope: evidence engine, CLI onboarding and errors, context, checkpoint/resumption, and council-validator integration. Process, architecture, release functions, and the guide skills remain G3 work. The reviewed candidate is `candidate.json`, SHA-256 `c3c7d3edc6fc63e3fe8f16d8d23a0aa452cb319fc1945aca7edd781e8d2d47f9`.

The ordinary onboarding and cold-resume journey works from an unrelated working directory, including paths containing spaces. Unknown owner and missing exception paths survive a checkpoint; stale and unverified evidence is disclosed; stale edits and tampered sources fail with useful errors. However, three defects block approval: valid JSON with invalid record shapes crashes the CLI, replacement retrieval omits a direct conflict, and the council validator accepts an explicit denial containing a reference to an earlier approval.

## Findings

1. **Blocker — malformed record shapes escape the documented JSON error interface.** `put` with `null` or `[5]` exits 1 with `TypeError: sequence item 0: expected str instance, NoneType found`. A record containing `{"id":"BAD","type":[]}` exits 1 with `TypeError: unhashable type: 'list'`. All three emit Python tracebacks rather than the documented exit 2 and structured error. `src/agent_architect/core.py:338` permits a temporary `None` ID before the operation label is joined at line 359; line 103 tests membership before validating the type field. `src/agent_architect/cli.py:67` does not contain these exceptions. HEAD remained unchanged in every reproduction, so this is an interface/recovery defect, not observed data loss. **Required correction:** validate top-level record shapes and the type discriminator before using them; return the normal structured input error with a useful field/record explanation. Add CLI regression cases for null, non-object batch elements, and wrong discriminator types. **Requirements:** R01/R11, the agent-facing interface and error contract at `docs/CLI.md:3` and line 17. **Evidence:** commands 13–15 in `product-cli-evidence.json`.

2. **Blocker — retrieving an old assertion loses the replacement's direct conflicting claim.** The fixture creates `COLD` with the unique assertion `retired-route`, a replacement `CNEW`, and `COTHER` with a valid bilateral conflict against `CNEW`. After explicit supersession, `context retired-route --as-of 2026-09-09` returns active records `CNEW` and `S01`, historical `COLD`, and a disputed warning; it omits `COTHER`. Thus the new session sees the replacement and its conflict ID without receiving the other assertion. `src/agent_architect/core.py:437` expands conflicts before the replacement loop at line 439, and never expands conflicts introduced by replacements. **Required correction:** expand dependencies, relevant conflicts, and replacement chains together until no new relevant records are added; retain the existing active-versus-historical separation. Add a regression for a replacement with a conflict that does not match the query text. **Requirements:** R03/R04 and the linked-prerequisites/relevant-conflicts context contract at `docs/CONTRACT.md:15`. **Evidence:** command 19 in `product-cli-evidence.json`.

3. **Blocker — the council validator can pass an explicitly denied opinion.** A synthetic three-reviewer gate with exact message/report equality and correct local hashes passes when the first report is `Verdict: DENY`, followed by `The prior review said: Verdict: APPROVE`. The decision incorrectly labels that report APPROVE; the validator accepts the incidental approval text anywhere in the body (`scripts/check_council.py:75`) instead of checking the actual verdict. The positive fixture passes and an altered report is correctly rejected, so this reproduction specifically demonstrates verdict interpretation failure. **Required correction:** define and parse one authoritative verdict field, require it to match the decision, and reject ambiguous or denied reports regardless of quoted prior approvals. Add a regression containing a denial plus quoted/historical approval. **Requirements:** R09/R10 and the no-denial-waiver rule in `development/PLAN.md:36`. **Evidence:** commands 23–25 in `product-cli-evidence.json`; command 25 incorrectly returns exit 0 and `status: pass`.

No additional nonblocker finding is needed to explain this verdict. The absent G3 guide and process/release features were not treated as G2 defects.

## Requirement coverage and observed journey

| Requirement | Observed G2 evidence |
| --- | --- |
| R01 | CLI startup/help, explicit unknown owner, checkpoint, and a fresh-process resume work from an unrelated directory. Finding 1 blocks consistent error recovery; the actual novice guide remains G3. |
| R03 | Capture, attributable claims, immutable assertions, supersession/history, and source-tampering rejection pass exercised cases. The replacement/conflict integration fails in finding 2. |
| R04 | Cold resume retains completed work, unresolved questions, next action, relevant IDs, stage, and revision. Freshness warnings and transitive impact pass. Finding 2 prevents complete relevant-conflict retrieval. |
| R09/R10 | Synthetic three-reviewer agreement passes; an altered report fails. Finding 3 prevents the validator from reliably enforcing an actual approve/deny outcome. No real council reports were read. |
| R11 | Execution uses the system Python and standard library, private temporary project directories, and absolute script paths; no credentials or network calls were required. All 29 candidate hashes matched before and after testing. |
| R02/R05/R06/R07/R08/R12 | Their later process/data-architecture/release/recovery/skill deliverables were outside this implementation gate. Existing core tests do exercise some prerequisite persistence and evidence behavior. |

The independent walkthrough also verified repeated initialization preserves the project, a missing source file leaves HEAD unchanged, malformed JSON syntax yields a structured error, stale revision errors direct the agent to reread/reconcile, a checkpoint with a missing ID is rejected, six committed revisions audit successfully, and source tampering blocks resumed context rather than substituting a blank project.

## Exact commands and results

All inspection and top-level test commands used working directory `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`. The independent harness invoked each CLI command in a new subprocess from a separate temporary directory containing spaces. All mutations targeted disposable synthetic projects. The complete 25 subprocess argument lists, working directories, stdout, stderr, and exit codes are retained in `product-cli-evidence.json`; the exact runnable harness is `product-checks.py`. These are reviewer evidence artifacts, not product changes.

1. Governing documents and inventory, exit 0:

```sh
cat AGENTS.md development/PLAN.md docs/CONTRACT.md docs/CLI.md development/gates/G2/candidate.json && rg --files scripts tests
```

Relevant result: the candidate contains 29 files. The CLI documentation states Python 3.10+, macOS/Linux, no third-party packages, absolute-path operation, structured agent-facing JSON, revision preconditions, and checkpoint fields. Inventory identified `scripts/aa.py`, `scripts/check_council.py`, `scripts/record_development.py`, `tests/test_core.py`, and `tests/test_council.py`.

2. Implementation inspection, exit 0:

```sh
cat src/agent_architect/cli.py scripts/aa.py scripts/check_council.py && nl -ba src/agent_architect/core.py
```

Relevant result: verified the absolute-path import bootstrap, CLI error handler, record validation, checkpoint validation, context expansion order, and council verdict matching referenced in findings 1–3.

3. Existing test and documentation inspection, exit 0:

```sh
cat tests/test_core.py tests/test_council.py && nl -ba src/agent_architect/cli.py && nl -ba docs/CLI.md
```

Relevant result: the existing core suite tests ordinary record validation, source/history protection, supersession, bilateral conflict, checkpoint/resume, CLI location independence, locking, and interrupted persistence. The existing council suite reads real G1 reports, so it was not executed in this independent review; the harness uses wholly synthetic reports instead.

4. Existing core regression suite, exit 0:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_core.py -v
```

Result:

```text
Ran 26 tests in 0.171s

OK
```

5. Independent CLI and synthetic council tests, exit 1 because five assertions exposed the three findings:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G2/product-checks.py
```

Exact failing result lines and summary:

```text
FAIL null_record_has_structured_error: {"exit_code": 1, "head_unchanged": true, "stderr_last_line": "TypeError: sequence item 0: expected str instance, NoneType found", "structured": false}
FAIL nonobject_batch_has_structured_error: {"exit_code": 1, "head_unchanged": true, "stderr_last_line": "TypeError: sequence item 0: expected str instance, NoneType found", "structured": false}
FAIL unhashable_type_has_structured_error: {"exit_code": 1, "head_unchanged": true, "stderr_last_line": "TypeError: unhashable type: 'list'", "structured": false}
FAIL replacement_context_includes_direct_conflict: {"historical": ["COLD"], "records": ["CNEW", "S01"], "warnings": ["CNEW: disputed, freshness=unknown", "COLD superseded by CNEW; dependent records may need revision"]}
FAIL synthetic_council_explicit_denial_rejected: {"current_candidate_checked": false, "gate": "G1", "limit": "Recorded agreement and local integrity; does not prove review quality or message delivery.", "messages": 7, "reviewers": 3, "status": "pass"}
{"checks": 21, "commands": 25, "failed": 5, "passed": 16}
```

The 16 passing assertions and their observed details are retained alongside the failures in `product-cli-evidence.json`. Both candidate-hash checks passed with 29 entries.

6. Council line references, evidence hashes, and failing-command indices, exit 0:

```sh
nl -ba scripts/check_council.py && python3 - <<'PY'
from pathlib import Path
import hashlib, json
root = Path('.')
for name in ['development/gates/G2/candidate.json', 'development/gates/G2/product-checks.py', 'development/gates/G2/product-cli-evidence.json']:
    print(hashlib.sha256((root / name).read_bytes()).hexdigest(), name)
evidence = json.loads((root / 'development/gates/G2/product-cli-evidence.json').read_text())
for check in evidence['checks']:
    if not check['passed']:
        print(json.dumps({'case': check['name'], 'command_index': check['last_command_index']}))
PY
```

Exact hash/index output following the line-numbered source:

```text
c3c7d3edc6fc63e3fe8f16d8d23a0aa452cb319fc1945aca7edd781e8d2d47f9 development/gates/G2/candidate.json
eb5d8dff699be6db46132a3002361f83c3cec20fa9d12095f6d07372c067969c development/gates/G2/product-checks.py
41f41019a7a98d2c5b959a68edd2ee098f3da1ea80d9c392c108154fbf695383 development/gates/G2/product-cli-evidence.json
{"case": "null_record_has_structured_error", "command_index": 13}
{"case": "nonobject_batch_has_structured_error", "command_index": 14}
{"case": "unhashable_type_has_structured_error", "command_index": 15}
{"case": "replacement_context_includes_direct_conflict", "command_index": 19}
{"case": "synthetic_council_explicit_denial_rejected", "command_index": 25}
```

`apply_patch` created the reviewer harness and this report. The harness wrote its evidence JSON and removed its temporary directories on exit. No product file was changed.

## Limits and disposition

This review used synthetic evidence on the available macOS Python environment. It did not establish Linux compatibility, real stakeholder discovery quality, guide usability, external runtime execution, production readiness, or exhaustive persistence/audit integrity. Other reviewer reports were not read. Council tests concerned a synthetic local record; they do not claim that a real gate was improperly approved.

G2 is blocked by findings 1–3. Correct them, freeze the revised candidate, and re-review the affected CLI/context/council paths with the retained reproductions.
