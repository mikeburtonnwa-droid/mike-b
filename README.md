# Agent Architect

A personal library for designing, running, and improving agent workflows.

Keep the reusable parts of good work here: starting prompts, focused skills, reference material, and examples of what success looks like. Start with a single agent; add orchestration when a workflow demonstrates a need for it.

## Start here

1. Choose a [workflow seed](seeds/README.md).
2. Copy it into a new agent conversation and replace its input fields.
3. Attach only the skills and references the task needs.
4. Save useful results as a sanitized example, then refine the seed or skill based on what happened.

This is a Markdown library, not an agent runtime. Cloning it does not install skills or start automations. Load files explicitly or use your agent tool's supported skill installation mechanism.

## Library

| Folder | Purpose | Starting point |
| --- | --- | --- |
| `seeds/` | Prompts that start a specific workflow | [Design a workflow](seeds/design-workflow.md) |
| `skills/` | Reusable instructions for a bounded capability | [Workflow design skill](skills/workflow-design/SKILL.md) |
| `references/` | Context and design decisions to consult as needed | [Workflow patterns](references/workflow-patterns.md) |
| `templates/` | Copyable formats for new entries | [Workflow seed template](templates/workflow-seed.md) |
| `examples/` | Worked examples and evaluation cases | [Meeting notes to action brief](examples/meeting-notes-to-action-brief.md) |

## Common workflows

- [Design a new workflow](seeds/design-workflow.md): turn a recurring task into an executable specification.
- [Run an existing workflow](seeds/run-workflow.md): apply a specification to concrete inputs.
- [Improve a workflow](seeds/improve-workflow.md): use a real run to make a targeted correction.

## Add to the library

Use lowercase, hyphenated filenames and descriptive names. Keep one capability per skill and one starting objective per seed. Link to supporting material instead of copying it into every prompt.

See [contribution guidance](CONTRIBUTING.md) and the [reference record template](templates/reference.md). Starter entries are drafts; they have not been validated against a production agent runtime. Record evidence before labeling an entry validated.

## Publishing and reuse

Keep credentials, private source documents, and identifiable customer examples outside this repository. No license has been selected yet; choose one before inviting broader reuse.
