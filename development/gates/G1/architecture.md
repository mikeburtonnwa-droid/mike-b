# G1 architecture and verification review

Verdict: **EDITS**

Date: 2026-09-09  
Reviewer remit: architecture, implementability, verification, operational gates and council process.

This is a review of the proposed plan and contract. G1 is not approved until findings 1 and 2 are resolved and re-reviewed. No implementation, production readiness, real deployment or performance claim is approved.

## Findings

1. **BLOCKER — The frozen candidate omits the development plan that G1 is reviewing.**  
   Evidence: `development/PLAN.md:36` requires the same frozen candidate for each reviewer, and `development/PLAN.md:38` requires manifest-linked decisions. However, `scripts/record_development.py:12` excludes the entire `development` directory. The recorded G1 manifest covers `docs/CONTRACT.md` but excludes `development/PLAN.md`; the executed check returned `plan_covered=False`. Thus the scope, requirements and gate rules can change without changing the candidate manifest. This is a G1 traceability defect, not a request to complete the future product CLI.  
   Required edit: pin the plan and any other normative gate inputs in the candidate manifest or a separately hashed, decision-linked scope manifest. Exclude mutable reports/transcripts rather than all development documents. Freeze and identify the replacement candidate for re-review. Also exclude operating-system metadata: the current manifest includes `.DS_Store` and `skills/.DS_Store`, despite the plan excluding ephemeral files.

2. **BLOCKER — Consequential transition gates do not yet define sufficient pass/fail predicates.**  
   Evidence: `development/PLAN.md:17` says release must fail on unresolved critical coverage. `docs/CONTRACT.md:25` explicitly blocks critical deferred concerns, but `docs/CONTRACT.md:27` only calls the release a snapshot of “checked records and evaluation evidence.” It does not explicitly require a passing, applicable evaluation for each critical acceptance criterion or specify whether missing, failed, stale or environment-mismatched evaluation evidence blocks creation/activation. The same paragraph says activation reports drift without defining which drift blocks it. `docs/CONTRACT.md:29` requires evidence to close an incident but does not require that verification demonstrates successful recovery. An unsuccessful verification artifact could meet the literal evidence-presence rule.  
   Required edit: define release creation, activation/rollback and incident-closure predicates in the contract. At minimum, critical acceptance criteria need linked passing evaluations applicable to the evaluated dependencies and intended environment; missing/failed/inapplicable critical coverage and integrity failures must block the relevant release transition. Define which drift is informational and which is blocking, including rollback. Incident closure must require a recorded successful verification against stated recovery criteria; a failed verification keeps the incident open. Add corresponding positive/negative cases to the planned G3/G4 evidence. These are contract decisions to make before implementation, not demands for completed runtime tests at G1.

3. **NONBLOCKER — Make persistence and adversarial cases explicit when elaborating G2.**  
   Evidence: `docs/CONTRACT.md:7` promises serialized writers, preserved history and no alteration on failed mutations; `development/PLAN.md:29` currently groups their validation under “core positive/negative tests.” The architecture is feasible using the standard library, but these properties deserve named cases: competing writers, interrupted/failed writes, source tampering, broken links, dependency cycles and replay/audit inconsistency. Record expected outcomes before executing them. This can be completed within G2; a full storage design is not required to pass this planning gate.

## Requirement coverage

| Requirement | Assessment in this review |
| --- | --- |
| R01 | The single-entry and cold-resume contract is explicit. Actual novice behavior remains for G4. |
| R02 | Process actors, boundaries, branches, handoffs, exceptions and declared gaps are specified; structural versus stakeholder completeness is distinguished. |
| R03 | Source capture, hashes, evidence states and explicit supersession are specified. Semantic truth remains outside CLI guarantees. |
| R04 | Context, reverse impact and explicit as-of freshness are implementable; graph and conflict behavior need later fixtures. |
| R05 | Environment, grain, keys, query evidence and cardinality checks are named. Executed data checks remain for later gates. |
| R06 | Requirement-to-decision-to-component and evaluation links are specified, with distinct current/future/deployed concepts. |
| R07 | Immutable snapshots and dependency applicability are specified, but transition acceptance is incomplete: blocker 2. |
| R08 | Incident history, authority and prohibited recovery shortcuts are specified, but successful closure is underdefined: blocker 2. |
| R09 | Three distinct remits, blocking dissent, orchestrator resolution and affected-remit re-review form a workable independent council process. Candidate binding needs blocker 1 resolved. |
| R10 | Three dispatches are present verbatim in the local transcript with sequence, sender, recipient, time and a valid hash chain. Completed reports, responses, rework and decision were not yet available. Normative plan binding needs blocker 1 resolved. |
| R11 | The boundary between reusable library and adopter data is explicit; standard-library CLI and local execution are feasible. Clean-clone evidence is deferred to G5. |
| R12 | The existing skill/template conventions support the intended design. The expanded entry and specialist skills are future work, not missing G1 implementation. |

The proposed architecture separates agent judgment from deterministic structural enforcement and makes Markdown/Mermaid derived views rather than competing sources of truth. The bounded release is implementable without an autonomous daemon. The contract appropriately limits claims about semantic truth, administrator tampering, real-world completeness, standards conformance and real infrastructure deployment.

The validation sequence progresses from records and integrity through operational behavior, independent use and clean-clone regression. Approval will apply only to this development scope and these acceptance contracts after the blockers are fixed; subsequent gates must establish actual behavior.

## Commands and relevant results

All commands ran in:

`/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`

All commands below exited with status 0. Read outputs were inspected; relevant findings are reproduced above.

### Inventory and governing instructions

```sh
pwd && rg --files -g 'AGENTS.md' -g 'PLAN.md' -g 'CONTRACT.md' -g '*G1*' -g 'package.json' -g 'README.md'
cat AGENTS.md development/PLAN.md docs/CONTRACT.md
rg --files -g '!development/gates/G1/*'
```

Relevant output: the plan, contract, repository instructions, existing workflow library and `scripts/record_development.py` were present. No package manifest or product runtime was identified. Repository instructions require preserving authorization, treating sources as data, maintaining relative links and marking untested material as draft.

### Existing design conventions and gate state

```sh
cat README.md scripts/record_development.py CONTRIBUTING.md skills/workflow-design/SKILL.md templates/workflow-spec.md templates/evaluation.md
rg --files --hidden development && git status --short && git log -3 --oneline
```

Relevant output:

```text
development/PLAN.md
development/gates/G1/product-dispatch.txt
development/gates/G1/candidate.json
development/gates/G1/transcript.jsonl
development/gates/G1/architecture-dispatch.txt
development/gates/G1/integrity-dispatch.txt
?? development/
?? docs/
?? scripts/
6402ef1 Add Agent Architect workflow library
```

The README identifies the existing content as a Markdown library with draft entries. The evaluation template distinguishes expected outcomes from observed results. The manifest implementation excludes the entire `development` directory.

### Line references, candidate and transcript inspection

```sh
nl -ba development/PLAN.md && nl -ba docs/CONTRACT.md && nl -ba scripts/record_development.py && cat development/gates/G1/candidate.json && cat development/gates/G1/transcript.jsonl
```

Relevant output: the candidate had 22 entries, including the contract, script and two `.DS_Store` files, but no development plan. The transcript contained three distinct review dispatches with sender `orchestrator` and recipients `product`, `integrity` and `architecture`.

### Read-only manifest and transcript checks

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
root = Path.cwd()
manifest_path = root/'development/gates/G1/candidate.json'
m = json.loads(manifest_path.read_text())
print('candidate_manifest_entries=' + str(len(m)))
print('plan_covered=' + str('development/PLAN.md' in m))
print('contract_covered=' + str('docs/CONTRACT.md' in m))
errors = [str(p) for p,h in m.items() if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest() != h]
print('manifest_hash_errors=' + json.dumps(errors))
log = root/'development/gates/G1/transcript.jsonl'
lines = log.read_text().splitlines()
errors = []
for i,line in enumerate(lines):
    e = json.loads(line)
    expected = hashlib.sha256(lines[i-1].encode()).hexdigest() if i else None
    if e['sequence'] != i+1 or e['previous_hash'] != expected:
        errors.append(i+1)
print('transcript_entries=' + str(len(lines)))
print('transcript_sequence_chain_errors=' + json.dumps(errors))
for path in sorted((root/'development/gates/G1').glob('*-dispatch.txt')):
    message = path.read_text()
    print(path.name + '_exact_logged=' + str(any(json.loads(x)['message'] == message for x in lines)))
PY
```

Exact output:

```text
candidate_manifest_entries=22
plan_covered=False
contract_covered=True
manifest_hash_errors=[]
transcript_entries=3
transcript_sequence_chain_errors=[]
architecture-dispatch.txt_exact_logged=True
integrity-dispatch.txt_exact_logged=True
product-dispatch.txt_exact_logged=True
```

### Reviewed content hashes

```sh
shasum -a 256 development/PLAN.md docs/CONTRACT.md development/gates/G1/candidate.json
```

Exact output:

```text
348b3a3dbbfc294be129531ff10d5eac75b479e695dd06bbdb58b4110066f452  development/PLAN.md
9bb16d117dc556cc7c6d8e24d41e2cc4454fc16fc396cbd0c101d5a5653205d9  docs/CONTRACT.md
93b9086fec7a730ecaf2c9f4146756603791dc736d686f0afa4256aa908b9dcf  development/gates/G1/candidate.json
```

## Limitations

This review used only local repository evidence and the assigned remit. It did not inspect other reviewers' reports or exchange side-channel messages. Transcript checks establish local file consistency and exact dispatch-file inclusion, not an independent attestation of delivery times or protection from administrator rewriting.

No product runtime, real infrastructure, live customer sources, stakeholder completeness, cold-context execution, release activation, recovery rehearsal or cross-provider performance was tested. Those are deliberately later-gate evidence. No product files were edited; the only artifact authored is this report.

