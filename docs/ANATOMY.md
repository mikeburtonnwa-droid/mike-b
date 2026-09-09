# Library and project anatomy

This repository is the reusable library. Each adopter's discovery and implementation belong in a separate private project. Start with the [guide](../START.md); the agent manages the records and presents readable artifacts.

| Location in this library | Responsibility |
| --- | --- |
| skills/agent-architect/ | Entry guide; recovers context and selects the next bounded method |
| skills/process-discovery/, evidence-curation/, data-discovery/ | Current process, source/claim stewardship and data discovery |
| skills/architecture-delivery/, operations-review/ | Design, implementation evidence, release and recovery handoffs |
| references/ | Selective professional methods, versions, links and local interpretations |
| seeds/, templates/ | Lightweight reusable prompts and document shapes |
| src/agent_architect/, scripts/aa.py | Local canonical records, checks and consequential transitions |
| tests/ | Behavioral regressions for persistence, provenance, queries, evaluations, releases and recovery |
| examples/order-triage/ | Executable synthetic journey with ten stakeholder accounts and real SQLite tests |
| development/ | This build's plans, candidates, opinions, exact messages, failed attempts and decisions |
| .github/workflows/ | Regression automation for maintainers; no model credentials required |

The [record reference](RECORDS.md) specifies required inputs and outputs; [CLI documentation](CLI.md) gives exact operations.

## Inside a private project

The CLI creates HEAD, history and sources. The guide can add drafts and deliverables alongside them:

```text
my-private-project/
  HEAD                    # Current immutable history-envelope hash
  history/<hash>.json      # Full state, parent, before/after hashes and operation
  sources/<hash>.blob      # Captured original bytes
  .lock                   # Local writer coordination
  drafts/                 # Agent-authored mutation inputs; optional
  deliverables/           # Derived maps, briefs and handoffs; optional
```

Do not edit HEAD, envelopes or source blobs manually. Back up the complete project. A derived map is replaceable; its source evidence and record history are not. There is no automatic external synchronization or schema migration in version 0.1.0 (project schema 1).

The concerns often called “specs,” “memory,” “reasoning” and “tools” have explicit homes:

| Concern | Canonical records and practice |
| --- | --- |
| Specifications | Scope/owner brief, current and proposed process, requirements and acceptance criteria |
| Working memory | Checkpoint: current task, completed work, unresolved questions, next action and relevant IDs |
| Retained knowledge | Captured sources, claims, status, verification/review dates, conflicts and supersession |
| Decision reasoning | Alternatives, rationale, evidence and tradeoffs in decision records; private model reasoning is not captured |
| Data and tools | Asset grain/keys/refresh, versioned query execution, component tool declarations and actual host capabilities |
| Tests | Predefined expected outcomes, executed observations and evaluations bound to code, data, brief and dependencies |
| Runtime/state/recovery | Component and concern dispositions, handoff, immutable local releases and verified incidents |
| Changes | Source recapture, explicit record revisions, impact, drift, reevaluation and a new checked release |

Source dates express captured knowledge. An agent must inspect or recapture externally changed material before calling it current. Search is lexical plus linked dependencies; a relevant item can be missed if it has no matching text or links. Use the checkpoint and curated IDs, then inspect original sources.

## Adapting the workflow

Choose a small real boundary and capture its inputs before adding roles or folders. Keep each critical criterion separate. Use code for exact rules and transactions; use model reasoning where interpretation is needed and define an explicit evaluation rubric. Keep human decisions and actual authorization visible. Change the methods and reference set to fit the profession and domain; a persona label does not supply credentials or replace field evidence.

An adopter's implementation repository/runtime contains the actual service code, tool configuration, identity/access controls, deployment integration and monitoring. Capture the relevant versioned artifacts as evidence and link them through components and the handoff. This library's local release IDs do not deploy that service. The [worked example](../examples/order-triage/README.md) demonstrates the complete local protocol and preserves the remaining real deployment work.
