Verdict: APPROVE
Candidate SHA-256: d4daf5f8deec0bc74ec6cf265f81796a4049f61607be56c0c36cc406c8aab8f2

# G2 novice usability and integration re-review, revision 2

This approves the revised G2 evidence-engine and CLI behavior within the product/novice-user remit: onboarding and recovery errors, context and conflict retrieval, checkpoint/resumption, and the exercised council-validator integration. All three original blockers are resolved. This is a reviewer approval for the stated candidate, not an overall council decision or production-readiness sign-off.

## Findings and blocker resolution

1. **Resolved blocker — invalid record shapes now produce structured input errors.** The original `null`, `[5]`, and `{"id":"BAD","type":[]}` cases all return exit 2 with JSON errors and preserve HEAD. The first two report `Each record must be an object`; the discriminator case reports `BAD: unsupported type []`. `src/agent_architect/core.py:103` validates the discriminator before membership testing, and line 345 validates each record before constructing operation IDs. The independent CLI reproductions and new core regression pass. **Requirements:** R01/R11 and the documented agent-facing JSON/error interface.

2. **Resolved blocker — replacement retrieval includes its direct conflict.** The original `retired-route` search now returns active `CNEW`, `COTHER`, and `S01`, with `COLD` retained only in historical dependencies. Both active disputed claims receive warnings. The common expansion loop at `src/agent_architect/core.py:448` follows dependencies, replacements, and conflicts to a fixed point. This preserves the historical/active distinction while supplying the missing alternative assertion. **Requirements:** R03/R04.

3. **Resolved blocker — an explicit denial cannot be overridden by incidental approval text.** The original synthetic denial-plus-prior-approval case now returns exit 2 with `G1: denied or wrong-candidate report`. The revised synthetic fixtures include the authoritative header and dispatch candidate filename required by the new contract. Additional checks reject a wrong report candidate hash, a wrong dispatch candidate filename, and two conflicting header verdicts. A valid approval containing a historical denial example in its findings remains accepted. The header parser at `scripts/check_council.py:24` and verdict/hash comparison at line 95 support these results. **Requirements:** R09/R10.

No blocker or nonblocker finding remains from this re-review. G3 guide, process, architecture, and release implementation remain outside this approval.

## Integrated behavior and requirement coverage

The full synthetic CLI journey was rerun through separate processes from an unrelated working directory with spaces in its path. Initialization with an explicitly unknown owner, relative source-file capture, claims/issues/notes, checkpoint, cold resume, freshness warnings, transitive impact, stale-edit recovery, and audit all passed. The checkpoint retained the first interview's unresolved owner and exception paths, its next action, relevant IDs, stage, and revision. Tampered source content still blocked resumed context. These results cover the exercised G2 portions of R01/R03/R04/R11; they do not substitute for the later actual guide walkthrough.

The integrated core suite also passed the new immutable-applicability and post-publication fault regressions. The updated CLI documentation explains that `committed-durability-uncertain` identifies a visible commit requiring inspection and backup, and must not be blindly retried. This aligns the agent's recovery instructions with the revised commit outcome. The synthetic council tests cover the exercised R09/R10 behavior without reading any real reviewer reports.

All 29 candidate file hashes matched before and after the independent run. The original `product.md`, `product-checks.py`, and `product-cli-evidence.json` were preserved and checked by hash. Revised probes and outputs were saved separately as `product-checks-r2.py` and `product-cli-evidence-r2.json`.

## Exact commands and results

Top-level commands used working directory `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`. All completed with exit 0. The retained revised harness contains the exact fixture setup, including the original negative cases and the new council header/dispatch metadata. Its evidence JSON contains all 29 subprocess argument lists, working directories, stdout, stderr, and exit codes. All tested project and synthetic-council mutations occurred in temporary directories, which were removed on exit.

1. Rework, changed documentation, candidate, and implementation inspection:

```sh
cat development/gates/G2/rework.md docs/CLI.md && cat development/gates/G2/candidate-r2.json && cat src/agent_architect/cli.py scripts/check_council.py && nl -ba src/agent_architect/core.py && rg --files tests
```

Relevant result: rework describes the three original product fixes plus applicability, durability-outcome, and council-binding changes. The CLI documentation now distinguishes visible uncertain durability from precommit failure. The code contains the revised validation, fixed-point retrieval, and authoritative council header parser. The long output was truncated; the next inspection retrieved the relevant contract, tests, discriminator check, and council lines explicitly.

2. Contract, regressions, and focused code inspection:

```sh
cat docs/CONTRACT.md tests/test_core.py tests/test_council.py && sed -n '95,120p' src/agent_architect/core.py && nl -ba scripts/check_council.py
```

Relevant result: the contract explicitly defines authoritative verdict/candidate headers, candidate binding, immutable claim applicability, fixed-point context expansion, and the uncertain durability outcome. The core suite adds regressions for the observed failures. The existing council suite uses real G1 reports, so it was inspected but not run; this review used synthetic council fixtures instead.

3. Core regression suite:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_core.py -v
```

Exact summary:

```text
Ran 30 tests in 0.323s

OK
```

4. Independent revised CLI and council probes:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G2/product-checks-r2.py
```

Exact selected results and complete count:

```text
PASS replacement_context_includes_direct_conflict: {"historical": ["COLD"], "records": ["CNEW", "COTHER", "S01"], "warnings": ["CNEW: disputed, freshness=unknown", "COLD superseded by CNEW; dependent records may need revision", "COTHER: disputed, freshness=unknown"]}
PASS synthetic_council_explicit_denial_rejected: {"message": "G1: denied or wrong-candidate report", "status": "error"}
PASS synthetic_council_wrong_candidate_rejected: {"message": "G1: denied or wrong-candidate report", "status": "error"}
PASS synthetic_council_wrong_dispatch_rejected: {"message": "G1: final review dispatch did not identify accepted candidate", "status": "error"}
PASS synthetic_council_ambiguous_header_rejected: {"message": "Report requires one authoritative verdict and candidate SHA-256 header", "status": "error"}
PASS candidate_after: {"entries": 29}
PASS original_review_evidence_preserved: {"product-checks.py": "eb5d8dff699be6db46132a3002361f83c3cec20fa9d12095f6d07372c067969c", "product-cli-evidence.json": "41f41019a7a98d2c5b959a68edd2ee098f3da1ea80d9c392c108154fbf695383", "product.md": "be142561979ee2d3e7941f8d8a8962fc1de57d1aba2a8e9286175f3f4026ce19"}
{"checks": 26, "commands": 29, "failed": 0, "passed": 26}
```

The three original malformed-record cases each returned exit 2, a structured error, and unchanged HEAD; their complete outputs are retained in `product-cli-evidence-r2.json`.

5. Candidate comparison and evidence-hash verification:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, json
root = Path('.')
folder = root / 'development/gates/G2'
old = json.loads((folder / 'candidate.json').read_text())
new = json.loads((folder / 'candidate-r2.json').read_text())
print(json.dumps({'changed_product_files': sorted(k for k in old.keys() & new.keys() if old[k] != new[k]), 'added': sorted(new.keys() - old.keys()), 'removed': sorted(old.keys() - new.keys())}, indent=2))
for name in ['candidate-r2.json', 'product-checks-r2.py', 'product-cli-evidence-r2.json']:
    print(hashlib.sha256((folder / name).read_bytes()).hexdigest(), name)
data = json.loads((folder / 'product-cli-evidence-r2.json').read_text())
print(json.dumps({'checks': len(data['checks']), 'failed': [c['name'] for c in data['checks'] if not c['passed']], 'commands': len(data['commands'])}, sort_keys=True))
PY
```

Complete output:

```text
{
  "changed_product_files": [
    "docs/CLI.md",
    "docs/CONTRACT.md",
    "scripts/check_council.py",
    "src/agent_architect/core.py",
    "tests/test_core.py",
    "tests/test_council.py"
  ],
  "added": [],
  "removed": []
}
d4daf5f8deec0bc74ec6cf265f81796a4049f61607be56c0c36cc406c8aab8f2 candidate-r2.json
fbc82254b28ab7c354b944d32a8335e48286006c5c68fec01169b9886a8a1e13 product-checks-r2.py
434fb0be69af57d58aa9e951318b928a2619675dbed699f2e8c47bec55e66888 product-cli-evidence-r2.json
{"checks": 26, "commands": 29, "failed": []}
```

Reviewer writes were limited to the separate revised harness, its evidence JSON, and this report. No product file or original review artifact was edited.

## Limits

Testing used synthetic data on the available macOS Python environment. Linux compatibility, actual novice-guide use, external runtime execution, production readiness, and exhaustive persistence/council adversarial behavior were not established. Other reviewer reports were not read. No claim is made that the entire G2 council has approved; this report supplies the product/novice-user approval for the exact candidate identified above.
