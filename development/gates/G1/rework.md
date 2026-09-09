# G1 rework

Round 1: all three reviewers requested edits. Gate remains FAIL pending re-review.

- Product blockers 1/2: added stage inputs/outputs, next-action/resume rules and explicit local-simulation labels plus production handoff contract.
- Integrity blocker 1 and architecture blocker 1: manifest now includes normative PLAN.md and excludes .DS_Store. Original candidate is retained; candidate-r2.json identifies revision.
- Architecture blocker 2: specified critical evaluation coverage, time/environment/dependency applicability, drift-blocked activation/rollback and successful verification before incident closure.
- Nonblocking cases are recorded in the contract for later gates: competing writers, persistence failure, contradictory interviews, incomplete first interview, unavailable data and cold resume. Legacy README migration remains G3/G5 work.

Orchestrator: no implementation gate has started. All three remits are re-reviewed because these contract changes intersect.
