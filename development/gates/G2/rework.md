# G2 rework, round 1

All three reviewers returned EDITS; gate FAIL pending re-review. Retained original reports, commands, probe harnesses and observed failures.

1. Retrieval now expands dependency, replacement and conflict links to one fixed point (all remits).
2. Claim applicability is immutable; new scope requires a separate claim and verification (integrity).
3. Record object/discriminator shape is validated before use; invalid JSON shapes return exit 2 JSON errors (product/architecture).
4. A post-HEAD flush failure returns explicit committed-durability-uncertain with visible commit/revision, unlike an unapplied precommit failure (architecture and orchestrator probe).
5. Council checking now parses the authoritative header verdict, binds final report candidate SHA-256 to the chosen manifest and final dispatch filename, enforces a final orchestrator decision after completed reviews, timestamp order, and the immediate predecessor gate (all remits).
6. Added regressions for all observed failures. Local suite: 40 tests passed; log development/G2-tests-r2.txt. This is implementation evidence, not council approval.

The G1 logs remain immutable; header parsing supports the equivalent original G1 candidate header. Revised docs explicitly distinguish publication from durability. No G3 development has begun.
