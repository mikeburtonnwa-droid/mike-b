# G2 data integrity and provenance review

Verdict: **EDITS**

Candidate: `development/gates/G2/candidate.json`, SHA-256 `c3c7d3edc6fc63e3fe8f16d8d23a0aa452cb319fc1945aca7edd781e8d2d47f9`. All 29 manifested files matched their recorded hashes at inspection.

Scope: the evidence engine, CLI, checkpoints and council validator. This review used synthetic temporary projects and gate records. No product files or other reviewers' reports were changed or inspected, respectively.

## Findings

1. **Blocker — replacement claims lose their conflicts during context expansion (R04).** In `src/agent_architect/core.py:435–444`, conflicts are expanded once before replacement claims are added. A task depending on OLD, superseded by NEW, retrieves NEW but omits OTHER even though NEW has a valid bilateral conflict with OTHER. The probe returned active IDs `["NEW", "S1", "TASKROOT"]`, historical OLD, and `other_included: false`. The response exposes the conflict ID inside NEW but omits the conflicting assertion, its evidence and freshness, contrary to the promised retrieval of relevant conflicts and prerequisites. Expand dependencies, conflicts and replacements to a common fixed point, preserving the active/historical distinction. Add regression cases for conflicts introduced by replacements and by newly discovered prerequisites.

2. **Blocker — a verified assertion can acquire different applicability without fresh verification or a separate variant (R03/R04).** `Project.put` protects assertion text and supersession links at `core.py:350–357`, but allows applicability to change while retaining verified status, the original verification statement and its original dates. An isolated probe changed only applicability from `standard` to `urgent production variant`; revision 4 saved successfully and context produced no warnings. The verification still said `Observed original scope in S`. Applicability is part of what the evidence establishes; retaining a historical revision does not justify presenting this newly scoped claim as currently verified. Require a separate claim for a different applicability, or explicitly invalidate verification when semantic scope changes and require a supported verification transition. Add a test changing only applicability, without changing assertion or dates.

3. **Blocker — council approval is not bound to the candidate that received review (R09/R10).** `scripts/check_council.py:34–43` checks the decision's candidate and optionally current files; `:51–76` separately checks dispatch/response pairing and report approval. Nothing connects a review's candidate identity to the decision's candidate. Synthetic dispatches and reports explicitly approved only `prior.json`, but a decision selecting a different contract in `candidate.json` passed validation. It also passed with `current=True`, using an actual generated manifest of the changed synthetic product. This is a detectable protocol omission, separate from the acknowledged limits on authenticating people or message delivery. Record and validate explicit candidate hashes for review dispatches/responses and their decision references; candidate changes must require affected re-review or a recorded, justified retained approval as specified by the plan. Add a negative test for valid approvals attached to an unreviewed candidate.

4. **Nonblocker — the exercised core invariants passed.** The existing 26 core tests passed. Independent probes confirmed immutable captured bytes after editing the original file, explicit stale-verified warnings, rejection of missing verification metadata, atomic rejection of unilateral conflicts and dependency cycles, transitive reverse impact, successful history audit and rejection of source tampering. These checks support substantial R03/R04 infrastructure but do not compensate for findings 1–3.

## Requirement coverage

| Requirements | Assessment |
| --- | --- |
| R01 | Existing cold-resume test passed; full guide usability remains G3/G4 work. |
| R03 | Capture/hash checks and status validation passed; verified applicability mutation blocks approval. |
| R04 | Freshness, reverse impact and ordinary supersession passed; replacement/conflict integration blocks approval. |
| R09/R10 | Validator code and synthetic protocol exercised; candidate/reviewer binding is missing. |
| R11 | Tested through stdlib Python and temporary private projects; clean-clone packaging remains G5. |
| R02/R05–R08/R12 | Process, data/query, architecture, release, incident and guide-skill implementation are outside this G2 remit. |

## Commands and relevant results

All commands ran from `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect` and exited 0. Probe programs intentionally print observed acceptance/rejection; exit 0 does not mean their adversarial scenarios were all correctly rejected.

Exact inspection and baseline commands:

```sh
cat development/PLAN.md docs/CONTRACT.md docs/CLI.md development/gates/G2/candidate.json
rg --files src tests scripts
nl -ba src/agent_architect/core.py
cat src/agent_architect/cli.py scripts/check_council.py tests/test_core.py tests/test_council.py
sed -n '355,540p' src/agent_architect/core.py && cat src/agent_architect/cli.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_core.py -v
```

Relevant inspection output established the APIs and line references cited above. The initially batched listing was truncated in the outer tool output; the source tail and CLI were read again explicitly. The council test source was inspected, but its tests were not executed because they load actual other-reviewer reports. Synthetic council fixtures were used instead.

Baseline result:

```text
Ran 26 tests in 0.158s

OK
```

The complete exact exploratory and isolation commands are retained in the companion evidence file `development/gates/G2/integrity-commands.sh`; it contains the original two executed shell command bodies, including their Python heredocs and line-reference commands. It is review evidence, excluded from the product candidate. Relevant exact probe output:

```text
manifest {"hash": "c3c7d3edc6fc63e3fe8f16d8d23a0aa452cb319fc1945aca7edd781e8d2d47f9", "entries": 29, "mismatches": []}
source_snapshot_survives_original_edit True
stale_verified_warning ['V: verified, freshness=stale']
verified_missing_metadata_rejected BAD.verified_on: nonempty text required
unilateral_conflict_rejected ONE: conflict must be bilateral with a claim: TWO
replacement_conflict_context {"active": ["NEW", "S1", "TASKROOT"], "historical": ["OLD"], "new_conflicts_with": ["OTHER"], "other_included": false}
verified_scope_rewrite {"old_applicability": "standard", "new_applicability": "urgent production variant", "status": "verified", "verification_unchanged": true, "supersession_link": null, "warnings": []}
transitive_impact ["N1", "N2", "NEW", "OLD", "OTHER", "TASKROOT", "V"]
dependency_cycle_rejected Dependency/supersession cycle at X
positive_history_audit pass
source_tampering_rejected S1: missing, replaced or tampered captured source
unreviewed_candidate_gate {"gate": "G1", "status": "pass", "messages": 7, "reviewers": 3, "current_candidate_checked": false, "limit": "Recorded agreement and local integrity; does not prove review quality or message delivery."}
scope_only_rewrite {"saved_revision": 4, "claim": {"applicability": "urgent production variant", "assertion": "Operations owns the process", "description": "Synthetic", "evidence": [{"locator": "line 1", "source": "S"}], "id": "C", "review_due": "2026-10-01", "status": "verified", "title": "Scoped claim", "type": "claim", "verification": "Observed original scope in S", "verified_on": "2026-09-02"}, "warnings": []}
unreviewed_candidate_with_current_check {"gate": "G1", "status": "pass", "messages": 7, "reviewers": 3, "current_candidate_checked": true, "limit": "Recorded agreement and local integrity; does not prove review quality or message delivery."}
```

The final line-reference commands, included in the companion file, were:

```sh
nl -ba src/agent_architect/core.py | sed -n '333,360p;423,470p'
nl -ba scripts/check_council.py | sed -n '20,105p'
```

Their output confirms that applicability is not guarded by `put`, conflict expansion precedes the replacement loop, and the council validator compares reports to latest responses without comparing their reviewed candidate to the decision candidate.

The only persistent writes by this review were this report and its exact-command evidence file, created through `apply_patch`. Test projects and synthetic council files were confined to automatically cleaned temporary directories.

## Limits and disposition

No real stakeholder content, network integrations, SQL execution, release transitions or deployment were evaluated. Existing core tests supplied the lock/crash/checkpoint checks; independent fault exploration focused on provenance, semantic scope, context integration and candidate binding. The tests do not establish resistance to an administrator rewriting a whole directory, source truth, reviewer independence or full communication delivery. The synthetic validator result does not assert that a real gate was improperly approved.

G2 approval is withheld pending fixes and explicit re-review of findings 1–3.
