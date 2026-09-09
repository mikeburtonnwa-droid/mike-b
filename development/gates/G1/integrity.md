# G1 data integrity and provenance review

Verdict: **EDITS**

Scope: independent review of the requirements, record contract and traceability protocol. This is a plan gate; it does not certify an implemented CLI, operational deployment or real-world evidence. No product files were changed.

Reviewed candidate SHA-256: `93b9086fec7a730ecaf2c9f4146756603791dc736d686f0afa4256aa908b9dcf`.

Reviewed plan SHA-256: `348b3a3dbbfc294be129531ff10d5eac75b479e695dd06bbdb58b4110066f452`.

## Findings

1. **Blocker — the frozen candidate does not identify the plan under review.** `development/PLAN.md:36` promises the same frozen candidate, but `scripts/record_development.py:12` excludes the entire `development` tree. The manifest contains `docs/CONTRACT.md` but omits `development/PLAN.md`, even though G1 explicitly reviews its requirements and gate rules. The verification command below confirmed the omission. A later plan edit would leave the candidate hash unchanged, so a decision referencing this manifest cannot establish which requirements and review rules received approval. Include the plan and any other normative gate inputs in the frozen manifest while excluding ongoing logs and reports. Exclude ephemeral `.DS_Store` files as promised by `development/PLAN.md:38`; the current manifest includes two. Preserve this candidate and its reports, generate a distinctly identified revised candidate, and explicitly re-review the affected plan/traceability scope. This is the only blocking finding.

2. **Nonblocker — the knowledge semantics have an appropriate separation of evidence, applicability and freshness.** `docs/CONTRACT.md:11–15` requires immutable captured content, source locators, verification evidence, dates, explicit supersession, bilateral conflict links and an explicit freshness as-of date. It also prevents environmental variants from superseding each other automatically and prevents repetition from upgrading evidence. These are suitable G1 commitments. G2 should make their boundary behavior observable: missing review dates must remain unknown, supersession must not create cycles or dangling replacements, and a conflict must remain discoverable from either affected claim. The contract does not yet define these schema-level details; their absence is not treated as an implementation defect at this gate.

3. **Nonblocker — transaction and audit guarantees need failure-oriented evidence at G2.** `docs/CONTRACT.md:7` promises a lock, unchanged state on failed mutations, monotonic revisions, before/after hashes and preserved history. G2 should exercise competing writers, exceptions during persistence, interrupted multi-file updates and recovery of a stale lock. Serializing access alone does not establish atomic persistence of the canonical record, captured content, history and audit event. The acknowledged administrator-rewrite limitation is accurate; a local hash chain must not later be described as an independently trusted attestation.

4. **Nonblocker — release knowledge is pinned, but integrity and current fitness must remain separate in validation evidence.** `docs/CONTRACT.md:25–29` explicitly invalidates evaluation applicability when dependencies change, preserves releases, records activation and rollback, and requires drift reporting. G3/G4 should demonstrate that an evaluation invalidated for the current candidate cannot satisfy its release readiness, while the historical release remains readable with its original evidence. Source integrity checks and current drift reporting must occur on rollback as well as activation. Missing or altered evidence must not be treated as a successful check. The contract correctly limits this to recording/simulating deployment; it does not establish actual runtime authorization or present-day fitness of an old release.

5. **Nonblocker — current transcript entries are internally consistent, with a bounded completeness claim.** At inspection, the three dispatch entries had consecutive sequence numbers, correct previous-entry hashes and exact equality with their dispatch files. `development/PLAN.md:38` accurately excludes hidden reasoning from the traceability claim. This does not independently prove that no unrecorded communication occurred, or that a recorded message was delivered. The current recorder performs an unlocked read-then-append (`scripts/record_development.py:33–41`); gate operation should use one serialized orchestrator writer, or add locking before allowing concurrent transcript writers. Later gate validation must also check responses, rework, follow-ups and the final decision. None existed in the inspected three-entry snapshot, and they were not expected before the reviews finished.

6. **Nonblocker — provenance extends through data and recovery records rather than ending at claims.** `docs/CONTRACT.md:19–21` requires process evidence/gaps, dataset environment/grain/keys and executed-query result sources; `:25–29` carries traceability through requirements, decisions, components, evaluations, releases and incident verification. `:35` distinguishes synthetic fixtures and local interpretation from stakeholder evidence and standards conformance. The existing reference/evaluation templates also require applicability, observed outcomes and limits. These commitments are suitable for this scope; actual join correctness, stakeholder completeness and incident effectiveness remain unproven until their planned exercises run.

## Requirement coverage

| Requirement | G1 integrity assessment |
| --- | --- |
| R01 | Context restart and attributable answers are specified; novice usability is outside this review's main remit. |
| R02 | Evidence, explicit gaps, environment/variant boundaries and current/future separation are specified. |
| R03 | Captured-content attribution, claim status and verification/supersession requirements are covered; G2 tests pending. |
| R04 | Active retrieval, conflict disclosure, freshness and transitive impact are covered; boundary tests pending. |
| R05 | Grain, keys, lineage assumptions, executed-query evidence and limits are covered; data exercises pending. |
| R06 | Requirement-to-evaluation links and separation of current/candidate/deployed knowledge are covered at contract level. |
| R07 | Immutable evaluated releases, dependency invalidation and drift checks are covered; release behavior remains to be demonstrated. |
| R08 | Preserved history, authority and verification are specified; incident rehearsal pending. |
| R09 | Re-review and blocker resolution rules are explicit; the frozen-plan omission blocks evidence sufficient for this gate. |
| R10 | Dispatch transcript checks passed for the inspected snapshot; manifest scope needs correction and full-cycle evidence is pending. |
| R11 | Public-library/project separation and absence of implicit credential/network acquisition are specified; clean-clone evidence pending. |
| R12 | Existing templates preserve inputs, limits and evidence; full specialist skill implementation is outside G1. |

## Commands and relevant outputs

All commands exited successfully with status 0. The first command ran from `/Users/michaelburton/Documents/Codex/2026-09-09/i-w`; the remaining commands ran from its `outputs/agent-architect` directory. Independent reads were batched; none modified product files.

1. `pwd && rg --files outputs/agent-architect`

   Output established the workspace and the presence of `AGENTS.md`, the plan, contract, recorder, templates, candidate manifest and G1 dispatch/transcript files.

2. `cat AGENTS.md docs/CONTRACT.md development/PLAN.md`

   Relevant output: the repository requires draft labels until evidence exists; the contract describes structural rather than real-world validation; G1 is the plan/contract gate; R09/R10 and gate rules require frozen candidates and recorded communication.

3. `cat README.md CONTRIBUTING.md scripts/record_development.py`

   Relevant output: starter entries remain drafts and the library is not a runtime. The recorder excludes `development` in `manifest()` and uses a read-then-append transcript operation without a lock.

4. `cat development/gates/G1/candidate.json development/gates/G1/transcript.jsonl development/gates/G1/integrity-dispatch.txt`

   Relevant output: the manifest includes the contract and two `.DS_Store` files; the transcript contains three dispatches with sequence numbers 1–3; the integrity dispatch defines this review's scope and prohibits product edits and side-channel communication.

5. `nl -ba docs/CONTRACT.md && nl -ba development/PLAN.md && nl -ba scripts/record_development.py`

   Relevant output supplied the line references in findings 1–6, including `excluded = {'.git', '__pycache__', '.venv', 'development', '.pytest_cache'}` at recorder line 12.

6. `cat templates/reference.md templates/evaluation.md templates/workflow-spec.md references/workflow-patterns.md`

   Relevant output: reference templates contain source/review/applicability/limits fields; evaluation templates distinguish expected and observed outcomes and require evidence; workflow specifications include authorization and failure handling; workflow patterns are explicitly unmeasured draft heuristics.

7. Exact verification command:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, json
root=Path('.')
m=json.loads((root/'development/gates/G1/candidate.json').read_text())
mismatches=[p for p,h in m.items() if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]
lines=(root/'development/gates/G1/transcript.jsonl').read_text().splitlines()
errors=[]
for i,line in enumerate(lines):
    e=json.loads(line)
    if e['sequence']!=i+1: errors.append(f'sequence {i+1}')
    expected=hashlib.sha256(lines[i-1].encode()).hexdigest() if i else None
    if e['previous_hash']!=expected: errors.append(f'previous_hash {i+1}')
    if e['kind']=='dispatch':
        f=root/f"development/gates/G1/{e['recipient']}-dispatch.txt"
        if e['message']!=f.read_text(): errors.append(f'dispatch {i+1}')
print(json.dumps({'manifest_entries':len(m),'manifest_mismatches':mismatches,'plan_in_manifest':'development/PLAN.md' in m,'contract_in_manifest':'docs/CONTRACT.md' in m,'ephemeral_manifest_entries':[p for p in m if p.endswith('.DS_Store')],'transcript_entries':len(lines),'transcript_errors':errors,'plan_sha256_at_review':hashlib.sha256((root/'development/PLAN.md').read_bytes()).hexdigest(),'candidate_sha256_at_review':hashlib.sha256((root/'development/gates/G1/candidate.json').read_bytes()).hexdigest()},indent=2))
PY
```

Exact output:

```json
{
  "manifest_entries": 22,
  "manifest_mismatches": [],
  "plan_in_manifest": false,
  "contract_in_manifest": true,
  "ephemeral_manifest_entries": [
    ".DS_Store",
    "skills/.DS_Store"
  ],
  "transcript_entries": 3,
  "transcript_errors": [],
  "plan_sha256_at_review": "348b3a3dbbfc294be129531ff10d5eac75b479e695dd06bbdb58b4110066f452",
  "candidate_sha256_at_review": "93b9086fec7a730ecaf2c9f4146756603791dc736d686f0afa4256aa908b9dcf"
}
```

The sole write was creation of this assigned review report through `apply_patch`.

## Limitations and disposition

No CLI behavior, concurrency fault injection, semantic SQL validation, real stakeholder evidence, external standards conformance or production deployment was tested. The transcript inspection was a point-in-time review of dispatch records. Other reviewer reports were not inspected. The reviewed plan hash above identifies this review's input but does not repair the gate's shared manifest protocol.

Approval is withheld until finding 1 is corrected and explicitly re-reviewed. Findings 2–6 document acceptable contract commitments, audit limits and later-gate verification obligations; they do not independently block G1.
