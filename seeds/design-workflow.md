# Design a workflow

Status: draft

Copy the prompt below and replace the bracketed fields. Supporting capability: [workflow-design](../skills/workflow-design/SKILL.md).

```text
Design a repeatable agent workflow for this task: [task].

Inputs available: [files, data, links, or user information].
Desired deliverable: [format and audience].
Available tools: [tools, or unknown].
Constraints: [time, cost, privacy, quality, and scope].
Authorized external actions: [list, or none].
Success looks like: [observable acceptance criteria].

Use the workflow-design skill if attached or accessible. Produce a workflow
specification with inputs, steps, deliverables, validation, and failure handling.
Prefer a single agent unless separate roles have a concrete benefit.
Ask about missing information only when it materially changes the design;
otherwise state assumptions. Include a typical evaluation case and a relevant
edge case. Label the design draft until it has been exercised.
```
