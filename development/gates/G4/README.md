# G4: discovery, cold resume and operational rehearsal

Gate decision: PASS, with three independent approvals of candidate.json. See decision.json, product.md, integrity.md and architecture.md. Experiment reports are supporting evidence.

| Evidence | Where to inspect |
| --- | --- |
| Predeclared acceptance | experiment-acceptance.md |
| Exact observable inter-agent messages | transcript.jsonl |
| First interview, fresh context | novice-start-dispatch.txt, novice-start.md, novice-start-commands.json |
| First session preserved project/artifact | novice-start-project.zip, novice-start-artifact.md |
| Orchestrator first-session checks | novice-start-orchestrator-check.json |
| Cold resume, different fresh agent | novice-resume-dispatch.txt; report/log added on completion |
| Actual SQLite and lifecycle execution | rehearsal-4-events.json, rehearsal-4-checks.json, rehearsal-fourth.txt |
| Complete synthetic project history | rehearsal-projects-r4.zip: ready-project and deliberately changed project |
| Original failing attempts | rehearse-first.py, rehearse-second.py, rehearsal-first.txt, rehearsal-second.txt, corresponding events/checks |
| Presentation rework and regression | development-observations.md, presentation-test-before-rework.txt, regression-final.txt |
| Rendered diagram verification | current-map.png, proposed-map.png, their .mmd sources and mermaid-*.txt |
| Exact top-level verification commands | validation-commands.json |

The first three gates established the record engine and its predicates. This gate executes a worked journey and tests context transfer. The fixture is intentionally small and fictional; local simulation and passing structural checks do not establish production readiness for an adopter's system.
