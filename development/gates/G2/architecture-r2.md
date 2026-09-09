Verdict: APPROVE
Candidate SHA-256: d4daf5f8deec0bc74ec6cf265f81796a4049f61607be56c0c36cc406c8aab8f2

# G2 architecture and reliability re-review, revision 2

Date: 2026-09-09  
Candidate: `development/gates/G2/candidate-r2.json`  
Remit: evidence engine, CLI, checkpoint, transactions, locks, audit and council-check integrity.

I approve this G2 candidate within the defined local implementation scope for progression to G3. All four original blockers and the original nonblocker are resolved in the exercised cases. The supplied 40-test suite and all 13 revised independent probes passed. The orchestrator must still collect the other required opinions and record the gate decision; this report does not approve G3 functionality or production deployment.

## Findings and resolution

1. **RESOLVED — Candidate binding, original blocker 1; R09/R10.**  
   `scripts/check_council.py` now parses the report's candidate SHA-256, compares it with the decision manifest hash, and requires the final dispatch to identify the accepted candidate filename. The retained candidate-substitution case uses valid current product hashes but reports for the preceding candidate; it now fails with `denied or wrong-candidate report`. The valid synthetic council still passes, so rejection is not merely a broken fixture.

2. **RESOLVED — Authoritative verdict, original blocker 2; R09/R10.**  
   `report_header` requires one opening-header verdict and candidate hash. The revised negative fixture follows that protocol: its authoritative verdict is DENY, and an APPROVE example appears in the findings body. The checker rejects it. The supplied suite also verifies rejection of conflicting verdicts within the header. The original negative case has been preserved rather than removed.

3. **RESOLVED — Ordering, predecessor gates and message times, original blocker 3; R09/R10.**  
   The checker now validates timezone-aware ordered timestamps and mandatory message fields, requires an orchestrator decision after completed reviews as the final event, and requires the immediate predecessor's passed decision for G2 and later. The original early-decision, missing-time and missing-predecessor probes all reject for their intended reasons. Historical G1 validation also passes through the supplied suite.

4. **RESOLVED — Post-publication failure classification, original blocker 4; R03 and persistence contract.**  
   `Project.commit` now reconciles HEAD after an `OSError` while the mutation lock remains held. For the tested error immediately after HEAD replacement, it returns `committed-durability-uncertain` with the visible commit and revision. The revised docs distinguish that outcome from an unapplied precommit failure and instruct callers to inspect rather than blindly retry.  
   The independent probe injected the actual directory-`fsync` failure point. Both the API and integrated CLI returned the explicit uncertainty status with the correct commit/revision; the CLI exited 0 with structured output. Repeating the same expected revision was rejected as stale without a duplicate commit. The real-process pre-HEAD interruption and lock-recovery probe still passed.

5. **RESOLVED — Malformed CLI record, original nonblocker 5; R01.**  
   `Project.put` validates incoming records before extracting IDs, and the record discriminator is checked before schema lookup. The original `[null]` case now returns exit 2 with a JSON error, no traceback, and no revision change. The supplied tests cover additional scalar and discriminator shapes.

**Remaining findings: none in this re-review's tested G2 scope.**

## Integration and coverage

The fixed-point context expansion and immutable claim applicability changes were inspected alongside the reliability fixes. Their new regressions passed with the existing provenance, supersession, conflict, dependency, source-integrity and checkpoint tests, supporting the integrated R01/R03/R04 behavior. The concurrency probe again produced exactly one accepted write from six competing writers, and historical tampering still blocked audit and mutation.

R09/R10 now reject the original council bypasses while accepting a conforming synthetic council and the recorded historical G1 fixture. R11's existing local standard-library execution remains intact. R02, R05–R08 and R12 remain outside this G2 implementation approval except for their shared storage/audit foundation; their specialist functionality and skills remain later-gate work.

## Exact commands and relevant results

Working directory:

`/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`

All shell commands below exited 0. The revised probe harness creates only disposable synthetic projects/councils in temporary directories and retains its source and output separately from revision 1.

### Inspection and supplied regression suite

```sh
cat development/gates/G2/rework.md scripts/check_council.py docs/CLI.md && git diff -- src/agent_architect/core.py src/agent_architect/cli.py docs/CONTRACT.md tests/test_core.py tests/test_council.py && cat development/gates/G2/candidate-r2.json
rg -n 'Committed|Uncertain|uncertain|def atomic|def commit|def put|def context|except|post_head|candidate|authoritative' src scripts tests docs/CONTRACT.md && python3 -m unittest discover -s tests -v
sed -n '85,115p' src/agent_architect/core.py && sed -n '298,385p' src/agent_architect/core.py && sed -n '438,492p' src/agent_architect/core.py && sed -n '230,310p' tests/test_core.py && cat tests/test_council.py
```

Relevant output:

```text
Ran 40 tests in 0.352s

OK
```

The inspected rework record identifies all original review areas and the new regressions. The code and documentation contain the header/candidate protocol, ordered gate checks, post-publication uncertainty handling, input-shape validation, claim-scope protection and context fixed point described above.

### Candidate and original-artifact verification before probes

```sh
python3 - <<'PY'
import hashlib,json,runpy
from pathlib import Path
r=Path.cwd(); p=r/'development/gates/G2/candidate-r2.json'; m=json.loads(p.read_text())
print('candidate_sha256='+hashlib.sha256(p.read_bytes()).hexdigest())
print('candidate_entries='+str(len(m)))
print('current_manifest_matches='+str(m==runpy.run_path(str(r/'scripts/record_development.py'))['manifest']()))
for name in ['architecture.md','architecture-probes.py']:
    p=r/'development/gates/G2'/name
    print(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+name)
PY
```

Exact output:

```text
candidate_sha256=d4daf5f8deec0bc74ec6cf265f81796a4049f61607be56c0c36cc406c8aab8f2
candidate_entries=29
current_manifest_matches=True
5ca0d11f1f6e416f5a81f0cc510437aea0663852a75aae681e6122f838e97b8d  architecture.md
529612510ae35c38b769098554df573f0e38ef206b954e5bd15711dff2c4c87a  architecture-probes.py
```

### Revised independent probes

Exact command:

```sh
python3 development/gates/G2/architecture-probes-r2.py
```

Exact output, also retained in `development/gates/G2/architecture-probes-r2.txt`:

```text
{"expected": "one saved, five rejected, revision/commits 2", "observed": {"commits": 2, "rejected": 5, "revision": 2, "saved": 1}, "passed": true, "probe": "competing_writers"}
{"expected": "no partial commit; lock recovers", "observed": {"commits": 2, "pre_head_unchanged": true, "recovery_revision": 2}, "passed": true, "probe": "killed_pre_head_writer"}
{"expected": "explicit committed-durability-uncertain with visible revision/hash", "observed": {"commit_matches": true, "error": null, "head_changed": true, "record_present": true, "revision": 2, "status": "committed-durability-uncertain"}, "passed": true, "probe": "post_head_fsync_failure"}
{"expected": "exit 0 with explicit uncertainty and visible revision/hash", "observed": {"commit_matches": true, "exit": 0, "revision": 2, "status": "committed-durability-uncertain", "stderr": ""}, "passed": true, "probe": "cli_post_head_fsync_failure"}
{"expected": "reject stale retry without duplicate commit", "observed": {"commits": 2, "exit": 2, "revision": 2, "stale": true}, "passed": true, "probe": "retry_after_visible_commit"}
{"expected": "audit and mutation reject; HEAD unchanged", "observed": {"head_unchanged": true, "rejected": [true, true]}, "passed": true, "probe": "historical_tampering"}
{"expected": "exit 2 with JSON error and unchanged revision 1", "observed": {"exit": 2, "revision": 1, "structured_error": true, "traceback": false}, "passed": true, "probe": "malformed_cli_record"}
{"expected": "pass", "observed": "pass", "passed": true, "probe": "council_valid"}
{"expected": "reject", "observed": "rejected: G1: denied or wrong-candidate report", "passed": true, "probe": "council_candidate_substitution"}
{"expected": "reject", "observed": "rejected: G1: denied or wrong-candidate report", "passed": true, "probe": "council_contradictory_verdict"}
{"expected": "reject", "observed": "rejected: G1: decision must follow completed council reviews and be final", "passed": true, "probe": "council_early_decision"}
{"expected": "reject", "observed": "rejected: G1: incomplete transcript event", "passed": true, "probe": "council_missing_time"}
{"expected": "reject", "observed": "rejected: G2: immediately preceding passed gate required", "passed": true, "probe": "council_missing_previous"}
{"failed": 0, "passed": 13, "total": 13}
```

The revised harness preserves all original negative cases, adds the required authoritative candidate header to conforming synthetic reports, and keeps candidate filenames in dispatches. It additionally verifies CLI delivery of the uncertainty result and rejection of a stale retry after that visible commit.

### Final candidate and preservation check

```sh
python3 - <<'PY'
import hashlib,json,runpy
from pathlib import Path
r=Path.cwd()
current=json.loads((r/'development/gates/G2/candidate-r2.json').read_text())
print('final_current_manifest_matches='+str(current==runpy.run_path(str(r/'scripts/record_development.py'))['manifest']()))
for name in ['architecture.md','architecture-probes.py','architecture-probes-r2.py','architecture-probes-r2.txt']:
    p=r/'development/gates/G2'/name
    print(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+name)
PY
```

Exact output:

```text
final_current_manifest_matches=True
5ca0d11f1f6e416f5a81f0cc510437aea0663852a75aae681e6122f838e97b8d  architecture.md
529612510ae35c38b769098554df573f0e38ef206b954e5bd15711dff2c4c87a  architecture-probes.py
9b42699ebb5c872a87374550a9c3d522fffa0872f591a3d5b8583deb3f425b50  architecture-probes-r2.py
bd08ecf592f61b52467a82c8fd3c024aaa0049b41888fa3b697897f8bbe00922  architecture-probes-r2.txt
```

## Limits

The original report, its embedded probe output and the original probe source were preserved. This re-review authored only separate reviewer artifacts in the assigned G2 directory. The product manifest remained unchanged. No other current reviewer report text was inspected, and no side-channel communication or delegation occurred. The supplied historical council tests used G1 artifacts as fixtures.

The results establish selected local transaction, CLI and recorded-protocol behavior. They do not establish power-loss durability, network-filesystem behavior, Windows support, large-project performance, reviewer identity, message delivery, source truth, resistance to an administrator rewriting all evidence, or real deployment reliability. The post-HEAD probe covers a flush failure with the published HEAD still readable; it is not an exhaustive test of simultaneous storage faults.

