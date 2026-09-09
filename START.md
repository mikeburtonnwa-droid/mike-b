# Start or resume

Clone this library into a directory your agent can read. Use a tool-enabled agent application with file and terminal access. Skill installation is optional: an explicit instruction to read the guide works without changing your application's configuration.

If you need the clone command or want to run the local checks first, see [release instructions](docs/RELEASE.md). [Anatomy](docs/ANATOMY.md) explains where specifications, memory, decisions, tools and tests belong.

Copy this prompt and replace the two paths. Supply your first interview, existing design or problem statement in the same session when available:

> Read `<absolute-library-path>/skills/agent-architect/SKILL.md` and use it to guide my work. Keep my project in `<absolute-private-project-path>`, outside the public library. My problem is: … . Inspect existing artifacts first. Maintain the map, evidence, decisions and checkpoint as we work. Show me the most useful next artifact and consequential unknowns in plain language. Preserve my existing authorizations.

If you do not yet have a project path, say so; the guide proposes a durable directory outside the library. A temporary directory is appropriate only for disposable practice.

After your first stakeholder interview, expect an attributed source, reported claims, a provisional current-state map, visible owner/exception gaps, and one focused next discovery action. A single interview is not evidence of full coverage.

After several interviews, ask “Show what we know about this step, where it came from, what conflicts, and what needs rechecking.” The guide retrieves source pointers and freshness, reconciles contradictions explicitly and updates the map. It never silently turns a summary into verified evidence.

For architecture, ask “Show whether the requirements, tools, data, state, context, recovery, evaluations and operating handoff are covered.” Each concern has an explicit disposition and rationale. Tests must run before results are represented as evidence.

To resume in a new session, use the same prompt and project path with “Resume my project.” The guide reads the audit, checkpoint and current context. It should recover the next action and unresolved questions without the earlier conversation. Supplied documents are evidence to interpret; instructions embedded in them do not override your task.

To prepare a release, the guide checks the declared process and architecture, critical requirements, applicable evaluation results and operating handoff. It can pin and activate a **local simulation**. It identifies the separate steps and authorization needed to deploy through your real runtime. It cannot make an unavailable tool or permission appear.

If your application cannot run local commands, the guide can draft a provisional artifact and explain the missing capability, but it must not claim records were saved or checks passed. See [CLI documentation](docs/CLI.md) and [professional references](references/professional-methods.md).
