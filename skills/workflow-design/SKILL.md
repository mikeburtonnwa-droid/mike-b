---
name: workflow-design
description: Design a repeatable agent workflow from a recurring task, with explicit inputs, deliverables, action boundaries, and evaluation cases. Use when creating or revising a workflow specification.
---

# Workflow design

Turn the requested recurring task into a specification another agent can execute. This skill designs the workflow; executing external actions requires task-level authorization.

Identify the deliverable, required inputs, available tools, and observable acceptance criteria. Separate known constraints from assumptions. Missing details that affect external actions, required data, or the definition of success need resolution; ordinary presentation choices can use stated defaults.

Start with a single agent and sequential steps. Consult [workflow patterns](../../references/workflow-patterns.md) when choosing between sequential execution, routing, parallel work, or a separate review role. Additional roles need a concrete input/output contract and a reason they improve the task.

Write the specification using [the workflow template](../../templates/workflow-spec.md). For each consequential step, identify its input, result, and completion check. Distinguish creating a draft from sending, publishing, deleting, or changing a live system. Preserve actions already authorized by the user.

Define what happens when inputs are absent, sources conflict, or a tool fails. Bound retries according to the operation: inspect the result of an uncertain external write before retrying it. Avoid retry loops that can create duplicate actions.

Include one representative case and one edge case tied to a plausible failure. Expected outcomes are design criteria, not test evidence. Keep the workflow marked draft until actual evaluation results exist; use [the evaluation template](../../templates/evaluation.md) to record them.
