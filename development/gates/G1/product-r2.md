# G1 product and novice-user re-review, revision 2

Verdict: **APPROVE**

This approves the product and usability plan/contract in `candidate-r2.json`, including the first-interview through production-handoff journey, incomplete-input and resume behavior, and the boundary between local simulation and actual deployment. It approves proceeding to implementation under those requirements. It does not approve an implemented product, a real deployment, production readiness, or the overall council gate.

Candidate manifest SHA-256: `9dabbb66c03d0ef4610f39bc08ceabeb84daeab9fc7010fd66b428a84db98a63`.

## Resolution of original blockers

1. **Resolved — journey and completion contract.** `docs/CONTRACT.md:39` now supplies intake, discovery, design, build, release, and operate stages, each with starting inputs, outputs/advancement conditions, and missing-information behavior. Line 42 explicitly turns an unknown interview owner into a gap and focused next question. Line 43 treats imported designs as proposals until prerequisite evidence is checked. Line 48 defines checkpoint contents, evidence-aware resume, and observable first-interview and cold-resume acceptance cases. This resolves original finding 1 without requiring novices to choose specialist roles, supply complete initial metadata, or follow a rigid one-way sequence.

2. **Resolved — simulation versus actual deployment.** `docs/CONTRACT.md:45` requires release output to identify local simulation. Line 54 applies that label to every CLI/display for activation and rollback, prohibits inferring actual deployment, and specifies the production handoff's runtime, execution artifact/reference, environment, owner, prerequisites, evaluation evidence, authorization, and remaining deployment steps. Actual deployment remains outside this release's execution scope. This resolves original finding 2. The earlier generic “deployed release” wording at line 29 is now bounded by the explicit simulation rules and the operate-stage distinction at line 46.

## Remaining findings

1. **Nonblocker — retain the planned entry-path migration in G3/G5.** The README and existing seeds are unchanged, as confirmed by the manifest comparison. The existing README still asks a novice to choose a seed and select supporting skills. Original finding 3 therefore remains implementation/documentation work: make the new guide the primary start/resume entry and retain the old seeds as secondary material. Their present absence is not a G1 defect.

2. **Nonblocker — finish the adaptation fixture in G4.** The new first-interview and cold-resume cases at `docs/CONTRACT.md:48`, plus the negative evaluation/recovery cases at line 56, substantially improve the acceptance intent behind original finding 4. The later ten-stakeholder fixture should still include conflicting accounts, a cross-system exception, and unavailable data, with expected questions, retained uncertainty, and blocked transitions. Actual fixture construction and execution remain G4 work.

No product/novice-user blockers remain in this revision.

## Integration and requirement coverage

The journey connects source capture and process/data discovery to requirements, design, implementation artifacts, evaluations, release handoff, and incident/change recovery. Stage is explicitly a navigation aid rather than a readiness claim. The consequential predicates at `docs/CONTRACT.md:52` prevent an apparently complete stage from satisfying critical release coverage with missing, failed, stale, disputed, or otherwise inapplicable evidence. Lines 54–56 connect activation, rollback, and incident closure to applicable evidence and preserve unfinished recovery work. These additions fit the existing bounded scope and uncertainty-preservation rules.

| Requirements | Re-review result |
| --- | --- |
| R01, R12 | Adequate G1 contract for guide inputs, outputs, advancement, failure behavior, specialist handoffs, and adaptation; implementation remains to be exercised. |
| R04 | Checkpoint and evidence-validation requirements now make next-action continuity explicit. |
| R06, R07, R08 | Adequate G1 distinction between proposed work, checked releases, simulated activation, production handoff, and evidence-based recovery. |
| R09, R10 | The added serial transcript ownership and candidate-retention rules fit the gate protocol. The revised manifest includes the plan and excludes OS metadata. Full audit behavior was not tested. |
| R02, R03, R05, R11 | Prior product-level assessment remains: adequate planned representation and boundaries; discovery quality, data integrity, and clean-clone execution remain later-gate evidence. |

## Exact verification commands and results

All commands used working directory `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect` and completed with exit code 0. Inspection results are distinguished below from executable checks.

1. Read the governing guidance, complete plan, revised contract, and frozen candidate:

```sh
cat AGENTS.md development/PLAN.md docs/CONTRACT.md development/gates/G1/candidate-r2.json
```

Relevant inspection result: the contract contains the added “Journey and resumption,” “Consequential transition predicates,” and “Review audit operation” sections. The plan retains the local-first, existing-agent-runtime scope and excludes real customer deployment. The manifest includes `development/PLAN.md` and omits both former `.DS_Store` entries.

2. Confirm line references and inspect the revised manifest-generation logic:

```sh
nl -ba docs/CONTRACT.md && cat scripts/record_development.py
```

Relevant inspection result: the journey table occupies lines 39–46; checkpoint and acceptance behavior is at line 48; release, simulation/handoff, and incident predicates are at lines 52, 54, and 56; audit operation is at line 60. The script's manifest function excludes OS/cache metadata and mutable development files while including `development/PLAN.md`.

3. Verify every candidate hash, compare the revised manifest with its generator and original candidate, and record review-input hashes:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, json, runpy
root = Path('.')
old = json.loads((root / 'development/gates/G1/candidate.json').read_text())
new_path = root / 'development/gates/G1/candidate-r2.json'
new = json.loads(new_path.read_text())
mismatches = []
for name, expected in new.items():
    path = root / name
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else 'MISSING'
    if actual != expected:
        mismatches.append({'path': name, 'expected': expected, 'actual': actual})
computed = runpy.run_path(str(root / 'scripts/record_development.py'))['manifest']()
print(json.dumps({
    'candidate_entries': len(new),
    'mismatches': mismatches,
    'manifest_function_matches_candidate': computed == new,
    'added_since_r1': sorted(new.keys() - old.keys()),
    'removed_since_r1': sorted(old.keys() - new.keys()),
    'changed_since_r1': sorted(k for k in new.keys() & old.keys() if new[k] != old[k]),
}, indent=2))
for name in ['development/PLAN.md', 'docs/CONTRACT.md', 'development/gates/G1/candidate-r2.json', 'development/gates/G1/product.md']:
    print(hashlib.sha256((root / name).read_bytes()).hexdigest(), name)
PY
```

Complete output:

```text
{
  "candidate_entries": 21,
  "mismatches": [],
  "manifest_function_matches_candidate": true,
  "added_since_r1": [
    "development/PLAN.md"
  ],
  "removed_since_r1": [
    ".DS_Store",
    "skills/.DS_Store"
  ],
  "changed_since_r1": [
    "docs/CONTRACT.md",
    "scripts/record_development.py"
  ]
}
348b3a3dbbfc294be129531ff10d5eac75b479e695dd06bbdb58b4110066f452 development/PLAN.md
a97e05f6e191e1dc99b44202546d9903c234ae7c56b6657da94dd48fbab94352 docs/CONTRACT.md
9dabbb66c03d0ef4610f39bc08ceabeb84daeab9fc7010fd66b428a84db98a63 development/gates/G1/candidate-r2.json
5feb9142c155bdfdd4a5e28cfb2d151f035ff467ba1ed7f8b31fb6c46db9c01f development/gates/G1/product.md
```

This report was added with `apply_patch` at `development/gates/G1/product-r2.md`. It was the only reviewer write; the original `product.md` was preserved.

## Limitations

This was an independent static product/novice-user re-review plus read-only candidate-manifest verification. Other reviewer reports were not read. No actual novice walkthrough, production runtime, query execution, incident exercise, persistence fault suite, or complete transcript audit was performed. The checks establish the identity of the reviewed candidate and resolution of the product contract blockers; later gates must establish implementation behavior.
