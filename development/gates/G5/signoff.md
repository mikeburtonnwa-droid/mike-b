# Version 0.1.0: final delivery sign-off

**PASS — signed by the build orchestrator, `/root`, on 2026-09-09.** The accepted library is published in the public [mike-b repository](https://github.com/mikeburtonnwa-droid/mike-b). All five bounded development gates passed after three independent reviewers approved the accepted candidate for each gate. No required development rework remains open.

This release supplies a cloneable guide, seven skills, professional reference pointers, formal project records and a dependency-free local checking tool. It supports discovery, current/proposed process maps, evidence freshness and lineage, architecture, actual evaluation, resumable handoffs and simulated release/recovery. Follow [START](../../../START.md); keep adopter records outside the public clone.

## Accepted source and council

- Frozen product source commit: `a0e93349b556709290068ef9aa8d3288de9122af`.
- [Candidate manifest](candidate.json): 72 product files; SHA-256 `0b11c98f3e77f99f304fe545ea57de34a93a5d9e5ddcabe06f8cfd045049bfaf`.
- Published, hosted-tested commit: `883b140447c3aa048150480455433f740cc215e3`, which adds the final council evidence to the same product candidate.
- [G5 decision](decision.json): PASS, with independent APPROVE opinions from [product/adopter](product.md), [integrity/evidence](integrity.md) and [architecture/release engineering](architecture.md).
- [Development evidence index](../../../docs/DEVELOPMENT.md): all five gates, twelve requirements, original dissent, required rework and exact observable message chains. The gate transcripts contain 69 recorded messages in total.

This sign-off and the hosted-result receipts are delivery evidence added after source acceptance. They do not change the frozen product candidate or manufacture another council opinion.

## Verification performed

The [hosted workflow](https://github.com/mikeburtonnwa-droid/mike-b/actions/runs/34356487961) completed successfully on 2026-09-09. All three jobs ran the full 86-test regression suite, library/CLI checks, historical council validation and a clean-checkout check with site packages disabled.

| Hosted target | Actual Python | Outcome |
| --- | --- | --- |
| Ubuntu, Python 3.10 matrix entry | CPython 3.10.21 | PASS: 86 tests |
| Ubuntu, Python 3.12 matrix entry | CPython 3.12.14 | PASS: 86 tests |
| macOS, Python 3.12 matrix entry | CPython 3.12.10 | PASS: 86 tests |

The [run metadata](hosted-ci-result.json) and [complete retrieved job logs](hosted-ci-log.json) preserve the command, timestamps, output and exit status. [Publication metadata](publication-state.json) confirms public visibility and the main branch.

Local and independent reviewer verification also passed: clean clones with empty runtimes, seven full skill validations, 122 local documentation links, council tampering/denial tests, stale or replayed evidence rejection, query binding, release invalidation, and recovery verification. The regression suite includes the [actual SQLite rehearsal](../../../examples/order-triage/README.md), with 37 scenario checks; these are included in the suite, not 37 additional unit tests.

The [G4 evidence](../G4/README.md) additionally preserves two separate agents' fresh-context start/resume sessions across ten synthetic stakeholder accounts, the incomplete map and remaining discovery gaps, executed SQL, failed evaluations, verified recovery and subsequent data drift. These artifacts demonstrate the exercised journey and retain failures for inspection.

## Scope and limits of this sign-off

The library is accepted for cloning, adaptation and the documented local workflow on macOS/Linux with Python 3.10+. Release activation and rollback are **local simulations**. Real production deployment requires the adopter's runtime, access controls, integration, evaluations on real data and operational authorization.

Freshness means the state of captured evidence and explicit rechecking; the tool does not continuously discover changes in external systems. Professional references and role instructions do not establish professional credentials, standards conformance or universal process completeness. No real-human success rate or Astra/Fable cross-provider performance benchmark is claimed.

The [audit limits](../../../docs/DEVELOPMENT.md#rework-and-audit-limits) disclose locally recorded identities, unavailable private reasoning, early rejected-source snapshot limits and one interrupted historical nested-command capture. Exact observable inter-agent messages and subsequent captured reruns remain available. This sign-off does not claim complete replay of every historical internal subprocess.
