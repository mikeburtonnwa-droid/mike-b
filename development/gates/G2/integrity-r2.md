Verdict: APPROVE
Candidate SHA-256: d4daf5f8deec0bc74ec6cf265f81796a4049f61607be56c0c36cc406c8aab8f2

G2 data integrity and provenance re-review of `candidate-r2.json`.

Approved scope: the G2 evidence engine, source/claim integrity, context and impact retrieval, checkpoint behavior and council validation within this reviewer's remit, for progression to G3. All 29 candidate entries matched the current generated manifest. This is a reviewer approval, not the orchestrator's gate decision or production sign-off.

## Findings and resolution

1. **Resolved blocker — conflict retrieval now reaches the required fixed point (R04).** `src/agent_architect/core.py:438–455` expands dependencies, replacements and conflicts together until the selected set stops changing. The revised independent probe retains the original OLD → NEW replacement/conflict case and extends it through OTHER's prerequisite PREREQ to a second conflict LAST and its distinct source S3. Context includes all three sources and both conflict relationships, places OLD only in historical dependencies, and discloses LAST's stale disputed evidence. Original finding 1 is resolved.

2. **Resolved blocker — applicability cannot inherit verification through an in-place scope edit (R03/R04).** `Project.put` now rejects changed applicability at `core.py:367–368`. The revised probe changes only the applicability of a currently verified claim; it is rejected and both HEAD and the original record remain unchanged. A separately identified variant is accepted with reported status and a warning, while cross-applicability supersession is rejected without changing HEAD. The contract now explicitly treats assertion and applicability as immutable identity. Original finding 2 is resolved.

3. **Resolved blocker — council reviews now bind to the accepted candidate (R09/R10).** `scripts/check_council.py` parses an authoritative verdict and candidate hash from the report header, requires the hash to match the decision manifest, and checks that the final dispatch identifies the accepted filename. The revised synthetic fixtures use this protocol. A matching current-candidate approval passes with `current=True`; the original scenario approving only a prior candidate is rejected. Separate wrong-report-hash, wrong-dispatch, missing-header and denial-with-an-approval-example cases also fail as expected. These are protocol checks, with identity and message-delivery limitations still disclosed. Original finding 3 is resolved.

4. **Nonblocker — integrated core behavior and preservation checks passed.** All 30 core tests passed, including the added malformed-input, scope, replacement-conflict and post-publication uncertainty regressions. Independent probes also passed explicit freshness boundaries, transitive impact, checkpoint restoration, audit and tampered-source rejection. The distinction between an unapplied precommit failure and visible-but-durability-uncertain publication is now consistent between code and the amended CLI/contract documentation. The original candidate, integrity report and original probe command file remained byte-identical during the probes. The revised probe is saved separately.

No blockers remain in this review. R03/R04 and R09/R10 have the targeted implementation evidence required by this remit. R01 checkpoint behavior was exercised; full guide usability, process/data/architecture/release work and packaging remain assigned to later gates.

## Exact commands and results

Working directory: `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`. All executed shell commands exited 0. Independent reads and the baseline test run were batched where appropriate.

Exact inspection commands:

```sh
cat development/gates/G2/rework.md docs/CLI.md scripts/check_council.py development/gates/G2/candidate-r2.json
rg -n 'applicability|fixed|conflict|context|atomic|except|candidate|header' src/agent_architect/core.py src/agent_architect/cli.py tests/test_core.py tests/test_council.py && cat docs/CONTRACT.md
sed -n '295,377p' src/agent_architect/core.py && sed -n '433,483p' src/agent_architect/core.py && sed -n '236,290p' tests/test_core.py && cat tests/test_council.py
```

Relevant outputs confirmed the new applicability guard, combined context expansion loop, authoritative report-header parser, candidate comparisons, final-decision ordering and predecessor checks. The tests' source was inspected. The repository council suite was not executed because it reads actual other-reviewer reports; all independently executed council cases used synthetic temporary fixtures.

Exact baseline command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_core.py -v
```

Relevant output:

```text
Ran 30 tests in 0.306s

OK
```

The revised independent probe source is retained separately as `development/gates/G2/integrity-probes-r2.py`. It uses temporary project directories, asserts expected outcomes and preserves the original negative cases with updated header/dispatch metadata.

Exact probe command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G2/integrity-probes-r2.py
```

Exact output:

```text
candidate {"sha256": "d4daf5f8deec0bc74ec6cf265f81796a4049f61607be56c0c36cc406c8aab8f2", "entries": 29, "matches_current": true}
replacement_prerequisite_conflict_fixed_point {"active": ["LAST", "NEW", "OTHER", "PREREQ", "S1", "S2", "S3", "TASKROOT"], "historical": ["OLD"], "stale_conflict_disclosed": true}
scope_only_rewrite_rejected Changed applicability requires a separate claim and verification
separate_variant_and_cross_scope_rejection True
freshness_boundaries ["unknown", "stale", "current", "future-dated"]
impact_checkpoint_and_audit pass
tampered_source_rejected True
current_candidate_approved {"status": "pass", "current_candidate_checked": true}
original_unreviewed_candidate_rejected G1: denied or wrong-candidate report
wrong_report_hash_rejected G1: denied or wrong-candidate report
wrong_dispatch_rejected G1: final review dispatch did not identify accepted candidate
missing_candidate_header_rejected Report requires one authoritative verdict and candidate SHA-256 header
denial_with_approval_example_rejected G1: denied or wrong-candidate report
original_artifacts_preserved_and_candidate_unchanged True
```

The only persistent writes were the new probe and this re-review report, created through `apply_patch`. Original reports, original probe commands/results and product files were not edited.

## Limits

This re-review did not inspect other reviewers' reports, validate the evolving real G2 council decision, or independently authenticate reviewer identity, source truth or complete message delivery. It did not test real SQL semantics, production deployments, release/incident transitions or the future guide skills. Lock/crash/CLI coverage here comes from the executed core suite; independent probes focused on provenance integration and candidate binding. Local hash consistency remains evidence against accidental or partial alteration, not an administrator capable of rewriting the complete directory. Approval is limited to this frozen G2 candidate and remit.
