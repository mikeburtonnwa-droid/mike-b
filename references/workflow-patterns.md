# Workflow patterns

Status: draft. These are local design heuristics, not measured performance claims.

| Pattern | Useful when | Cost or failure to watch |
| --- | --- | --- |
| Single agent, sequential steps | Later steps depend on earlier results | A bad assumption may propagate; check at consequential transitions |
| Routing | Inputs clearly belong to different workflows | Ambiguous inputs need a fallback instead of a forced classification |
| Parallel independent work | Subtasks can proceed without shared edits or intermediate results | Coordination and reconciliation may cost more than the time saved |
| Separate reviewer | A concrete review rubric can expose errors in a draft | Review without source evidence may repeat the same error |
| Human decision point | A choice requires user judgment or authorization not already supplied | Ask about the concrete decision after preparing enough evidence to review |

Choose the simplest pattern that satisfies the task. Separate roles only when each has a clear responsibility, bounded inputs, and a useful output. Specify who reconciles conflicting findings.

When a process touches an external system, define how to determine whether a write succeeded before retrying an uncertain operation. A draft-producing workflow can often be evaluated using local fixtures before connecting live tools.
