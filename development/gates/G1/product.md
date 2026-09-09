# G1 product and novice-user review

Verdict: **EDITS**

Reviewer remit: independently review the requirements and contract for the first-interview through production journey, required inputs and outputs, usability, adaptation, and scope. This is a plan/contract review, not an implementation gate. No product files were edited.

The proposed record model covers substantial discovery, evidence, architecture, and operational needs. Two contract gaps block approval: the entry guide has no defined journey or stage-completion contract, and simulated activation is not distinguished from actual deployment in the required records and user-facing outputs. Both can be resolved without adding a custom runtime or performing a customer deployment.

## Findings

1. **Blocker — define the entry guide's journey and completion rules.** `development/PLAN.md:11` promises one guide for novice start/resume, and `docs/CONTRACT.md:33` promises incomplete inputs, adaptation to any stage, automatic metadata, and readable views. However, the contract defines neither the stages nor the minimum input, expected output, completion condition, and next handoff for each stage. `docs/CONTRACT.md:7` includes a `stage` field without giving it a behavioral meaning. The record types describe what can be stored; they do not tell a novice or a fresh agent what to do next. For example, a first interview with an unknown system owner can be captured, but the contract does not determine whether the next action is a focused question, stakeholder discovery, process validation, data investigation, or architecture work. Likewise, accepting an existing architecture does not establish which discovery and evaluation checks must still run. **Required edit:** add a compact journey contract covering intake/resume, interview and source capture, current-state process/data discovery, gap and conflict resolution, requirements and architecture, evaluation, release handoff, and operation/change recovery. For each, state accepted inputs, outputs, advancement/blocking conditions, and the next action when information or tools are missing. Allow revisiting stages and importing existing artifacts without treating missing evidence as completed work. Define how an interrupted session retains its current task and next action. Add observable acceptance scenarios for an incomplete first interview and an existing-project resume to R01/R12 or their intended evidence.

2. **Blocker — distinguish a simulated active release from a deployed agent in records and outputs.** The bounded scope is clear in `development/PLAN.md:3`, and `docs/CONTRACT.md:29` correctly says the library records/simulates deployment and real deployment requires a runtime and authorization. But `docs/CONTRACT.md:27` defines activation using only a release ID; line 29 then links incidents to a “deployed release.” R06 also promises a distinct deployed view (`development/PLAN.md:16`). There is no required record field or display rule separating an active local simulation from an observed runtime deployment. A novice could therefore see release readiness, activation, and a deployed view and reasonably infer that an agent is running. **Required edit:** define the release/deployment states and their user-facing labels. A local snapshot activation must visibly identify itself as simulated/local and must not establish actual deployment. Specify the production handoff output within this release's scope: selected runtime or an explicit unresolved choice, execution artifact/reference, prerequisites and owner, required evaluation evidence, action authority, and the remaining deployment steps. If actual deployments can be recorded, require runtime/environment and observed deployment evidence before presenting them as deployed. Keep real customer deployment outside this development gate.

3. **Nonblocker — replace the legacy novice entry path during implementation.** `README.md:9` asks the user to choose a seed; line 11 asks them to select skills and references. That conflicts with the planned one-guide experience, but this is existing draft material and G3/G5 are the appropriate implementation/documentation gates. Record migration to one primary start/resume entry point, with the old design/run/improve seeds available as secondary material. This finding does not require implementing the guide before G1 passes.

4. **Nonblocker — make the ten-stakeholder rehearsal test adaptation, not only record volume.** G4 names a ten-stakeholder fixture and cold resume (`development/PLAN.md:31`), while R02 and the process contract recognize variants, exceptions, evidence gaps, and stakeholder coverage. The eventual fixture should deliberately include conflicting stakeholder accounts, an exception crossing a system boundary, an unavailable data source, a resumed partial project, and a later change affecting release fitness. Predetermine expected questions, retained uncertainty, artifacts, and blocked transitions. The fixture need not be authored at G1; its acceptance intent should be recorded before implementation validation.

## Requirement coverage

| Requirement | Product assessment at G1 |
| --- | --- |
| R01 | Partial; blocker 1 prevents an assessable novice journey and resume contract. |
| R02 | Adequate planned representation of actors, systems, boundaries, variants, handoffs, exceptions, and explicit gaps; actual discovery quality remains for G3/G4. |
| R03 | Adequate product contract for attribution, evidence states, explicit supersession, and retained uncertainty; implementation integrity is outside this review. |
| R04 | Adequate planned source/freshness/conflict disclosure and dependency context; next-action continuity needs blocker 1's clarification. |
| R05 | Adequate product fields for environment, grain, keys, provenance, execution evidence, and limitations; no SQL or real data was evaluated. |
| R06 | Architecture traceability is specified; the actual-versus-simulated deployed view needs blocker 2's clarification. |
| R07 | Immutable snapshots and critical deferred concerns are addressed; the meaning of activation to the user needs blocker 2's clarification. |
| R08 | Incident evidence, authority, verification, and follow-up are addressed; identify the release/deployment context as required by blocker 2. |
| R09 | The planned three-reviewer gate protocol, blocking verdicts, and explicit re-review are clear. No completed gate is claimed. |
| R10 | Observable communication and tool evidence are explicitly distinguished from hidden reasoning. This report records its inspection commands; transcript completeness was not audited. |
| R11 | Local adopter data and public reusable material are separated in the contract. Credential-free, dependency-free execution remains untested. |
| R12 | Inputs, methods, outputs, handoffs, and failure behavior are required in the plan; the guide's own contract needs blocker 1's detail. |

## Commands and relevant outputs

All commands completed with exit code 0. Outputs below are relevant excerpts or explicitly identified inspection results, not claims that implementation tests passed.

1. Working directory: `/Users/michaelburton/Documents/Codex/2026-09-09/i-w`.

```sh
pwd && rg --files -g 'AGENTS.md' -g 'PLAN.md' -g 'CONTRACT.md' -g 'README*' -g 'G1*' outputs/agent-architect
```

Relevant output:

```text
/Users/michaelburton/Documents/Codex/2026-09-09/i-w
outputs/agent-architect/AGENTS.md
outputs/agent-architect/skills/README.md
outputs/agent-architect/seeds/README.md
outputs/agent-architect/README.md
outputs/agent-architect/docs/CONTRACT.md
outputs/agent-architect/development/PLAN.md
```

2. All remaining commands used working directory `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`.

```sh
cat AGENTS.md development/PLAN.md docs/CONTRACT.md README.md
```

Read the complete four documents. Relevant output included “One entry skill owns the journey and loads specialist skills only when needed” and “This library records/simulates a deployment decision; real infrastructure release requires the connected runtime and actual authorization.” The README instead directs users to choose a seed and attach skills themselves.

3. Repository inventory and existing workflow inspection:

```sh
rg --files -g '!development/transcripts/**' -g '!development/gates/**' && ls -la development/gates/G1 && cat seeds/design-workflow.md seeds/run-workflow.md seeds/improve-workflow.md skills/README.md skills/workflow-design/SKILL.md references/workflow-patterns.md CONTRIBUTING.md
```

Relevant result: the inventory contained one existing specialist skill, `skills/workflow-design/SKILL.md`, three workflow seeds, templates, a draft example, the new plan/contract, and the development-recording script. The existing skill requires inputs, outputs, completion checks, missing-input handling, explicit action boundaries, and actual evaluation evidence before validation. It does not define the new end-to-end guide. Other reviewer reports were not read.

4. Line-numbered contract inspection and template inspection:

```sh
nl -ba development/PLAN.md && nl -ba docs/CONTRACT.md && cat development/gates/G1/candidate.json && nl -ba README.md && cat templates/workflow-spec.md templates/evaluation.md
```

Relevant result: the line references in findings 1–4 were confirmed. The workflow template supplies input availability/fallback and step-output/completion columns; the evaluation template separates expected from observed outcomes. Neither template supplies the new guide's stage contract. The candidate manifest listed 22 entries.

5. Frozen-candidate verification and review-input hashes:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, json
root = Path('.')
manifest_path = root / 'development/gates/G1/candidate.json'
manifest = json.loads(manifest_path.read_text())
mismatches = []
for name, expected in manifest.items():
    path = root / name
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else 'MISSING'
    if actual != expected:
        mismatches.append({'path': name, 'expected': expected, 'actual': actual})
print(json.dumps({'candidate_entries': len(manifest), 'mismatches': mismatches}, indent=2))
for name in ['development/PLAN.md', 'docs/CONTRACT.md', 'development/gates/G1/candidate.json']:
    print(hashlib.sha256((root / name).read_bytes()).hexdigest(), name)
PY
```

Complete output:

```text
{
  "candidate_entries": 22,
  "mismatches": []
}
348b3a3dbbfc294be129531ff10d5eac75b479e695dd06bbdb58b4110066f452 development/PLAN.md
9bb16d117dc556cc7c6d8e24d41e2cc4454fc16fc396cbd0c101d5a5653205d9 docs/CONTRACT.md
93b9086fec7a730ecaf2c9f4146756603791dc736d686f0afa4256aa908b9dcf development/gates/G1/candidate.json
```

The report itself was added with `apply_patch` at `development/gates/G1/product.md`; this was the only reviewer write.

## Limitations and disposition

This was a static, independent product review of the supplied plan, contract, and relevant existing library files. It used the bounded scope in the plan; it did not validate the original authorization history, source integrity implementation, transcript machinery, runtime execution, a real novice session, or deployment. No implementation or production readiness is approved. The absence of later-gate implementation is not itself a finding.

G1 remains blocked by findings 1 and 2. Re-review the revised plan/contract and corresponding candidate before proceeding. Findings 3 and 4 can be tracked into their stated later gates.
