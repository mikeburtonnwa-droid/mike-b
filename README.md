# Agent Architect

A cloneable workspace that helps an agent builder turn discovery into an evidence-linked process map, an evaluated architecture, and an operating handoff that another session can resume.

Start with [START.md](START.md). Give your tool-enabled agent the [guide skill](skills/agent-architect/SKILL.md), your problem or existing notes, and a private project directory. The guide manages records and specialist handoffs; you review the map, gaps, decisions and proposed actions. You do not need to write JSON or select professional roles.

Version **0.1.0**. See the [release and verification instructions](docs/RELEASE.md), [repository/project anatomy](docs/ANATOMY.md), and [release sign-off](development/gates/G5/signoff.md).

The library supplies instructions and a local Python record/checking tool. Your existing agent application supplies reasoning, file access, research and implementation tools. Cloning does not start an agent, install skills, connect data sources or deploy infrastructure.

## What stays with your project

- A current-state map with actors, systems, boundaries, handoffs, variants, exception paths and evidence gaps.
- Captured sources and claims with provenance, conflicts, verification dates and explicit supersession.
- Data assets and queries with grain, keys, environment and execution evidence.
- Requirements, decisions, components, architecture concerns and evaluations linked through stable IDs.
- A checkpoint for the next session, immutable release snapshots and verified recovery records.

Checks expose missing declared structure and outdated evidence. They cannot prove that you have discovered every real-world exception or that a stakeholder statement is true. Context uses the latest **captured** knowledge; external changes require fresh discovery. Releases and activation in this version are explicitly **local simulations**. Actual deployment requires the adopter's runtime, tools and authorization.

## Navigate

| Need | Entry |
| --- | --- |
| Start or resume with an agent | [Start guide](START.md) |
| Professional perspectives and handoffs | [Skills](skills/README.md) |
| Record model and commands | [Records](docs/RECORDS.md), [CLI](docs/CLI.md), [contract](docs/CONTRACT.md) |
| Methods and their limits | [Professional references](references/professional-methods.md) |
| Reproduce the ten-stakeholder journey | [Executed order-triage example](examples/order-triage/README.md) |
| This build's requirements, reviews and rework | [Evidence and review trail](docs/DEVELOPMENT.md), [development plan](development/PLAN.md) |
| Lightweight, standalone prompts | [Seeds](seeds/README.md), [templates](templates/) |

Requires Python 3.10+ on macOS or Linux, with no third-party Python packages or API keys for the local CLI. Tested environments and release evidence are recorded with the final sign-off. Keep real interviews, schemas, query results and credentials outside this public repository; only synthetic examples belong here. Back up the whole private project directory.

Professional perspectives are reusable methods and review criteria. They do not reproduce a person's lived experience, grant credentials, or establish standards conformance. See [contribution guidance](CONTRIBUTING.md) before adapting the library.

Original code and documentation are [MIT licensed](LICENSE) so others can clone and adapt them. External reference materials retain their own terms.
