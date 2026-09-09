Verdict: EDITS
Candidate SHA-256: 0023c1931ce0b089325966a06fbcfa7fbdf851c6cc37eb478cfc16ccc1617be3

# G3 novice usability and skill integration review

The new start guide and six integrated skills provide a coherent entry point, explicit inputs/outputs/handoffs, and honest limits. The exercised provisional-discovery, evaluation, simulation-release, and error paths work from an unrelated working directory. One integration gap blocks approval: the guide accepts an unknown owner or provisional scope but provides no documented supported way to update the canonical project brief when those facts are clarified. Two presentation improvements are nonblocking.

## Findings

1. **Blocker — incomplete intake metadata has no supported clarification path.** The guide explicitly initializes missing title/scope/owner facts as `unknown` (`skills/agent-architect/SKILL.md:16`) and later permits evidence-supported scope narrowing (line 40). However, `src/agent_architect/core.py:335` sets the canonical title/scope/owner only during initialization. The CLI exposes no metadata-update command, `schema` exposes no project/brief record type, and checkpoint accepts only its six specified fields. In the probe, an attributed clarification says Alice owns the project and scope is standard requests only. Saving that clarification as a supported note succeeds, but a subsequent `show` still reports canonical owner and scope as `unknown`. Attempting a project record returns `META: unsupported type 'project'`. A freeform note can preserve the statement, but no documented convention makes it authoritative over the stale root fields on resume. **Required correction:** provide and document a supported, validated, revision-checked way to revise the current project brief, or an explicit authoritative brief-record convention that the guide and resumed context use. Preserve provenance and historical values; scope changes must retain the evaluated-release boundary. Wire clarification into the guide and test unknown intake → captured clarification → updated current brief → cold resume. This does not require changing records by hand or restarting the project. **Requirements:** R01/R04/R12 and the approved intake/adaptation journey. **Evidence:** probe commands 17–19 and static CLI/core/schema inspection.

2. **Nonblocker — the derived map omits handoff payloads.** A valid cross-owner edge with payload `handoff-package-Z37` passes `check process`, but `render` omits that payload. `src/agent_architect/workflow.py:408` renders only edge kind/condition; the node table does not show edge payload/receiver fields. The canonical record retains the information, and the receiving actor appears on its node, so this is a presentation gap rather than lost evidence. Add an edge/handoff table or labels so a novice can review exactly what crosses the boundary in the standard artifact. **Requirements:** R02/R12. **Evidence:** probe command 25.

3. **Nonblocker — `evaluate` does not return the computed evaluation outcome.** An executed synthetic check with expected one decision and observed two is correctly saved as a failed evaluation and blocks release. However, the command returns exit 0 with `status: saved`, exactly as it does for a passing evaluation. The actual `fail`/`pass` appears only after a separate `show`. `src/agent_architect/workflow.py:269` returns the mutation receipt without the evaluation outcome. Include the evaluation ID and computed result in the receipt, or explicitly instruct the guide to read the saved evaluation before reporting its outcome. The current release predicate prevents this from granting readiness. **Requirements:** R06/R12. **Evidence:** probe commands 32 and 40, followed by their saved-record reads.

## Requirement coverage and observed behavior

| Requirement | G3 product/skill assessment |
| --- | --- |
| R01 | One primary start/resume guide replaces manual specialist selection. Unknown intake, provisional map, and saved next action work; finding 1 prevents completing the supported clarification journey. |
| R02 | Current/proposed maps, source links, visible missing-owner/exception gaps, and process-error explanations work. Handoff payload presentation can improve under finding 2. |
| R03/R04 | Skills require originals, locators, explicit evidence status, applicability, conflicts, and freshness. The exercised resume recovers checkpoint and uncertainty. Current project-brief authority needs finding 1's correction. |
| R05 | Data skill explicitly requires grain/key/cardinality and executed-result evidence; it accurately states the CLI does not execute SQL or prove semantics. No real database was tested. |
| R06/R07 | Architecture checks, pre-run fingerprints, captured failed/passing results, release blocking, and explicit local-simulation activation pass exercised cases. Changed implementation blocks activation. |
| R08 | Operations skill preserves authority and recovery criteria. The CLI gives a concrete missing-incident/evaluation error; existing workflow regressions exercise successful and rejected closure. |
| R09/R10 | This independent report retains commands/results and a candidate hash. Existing council machinery was not re-reviewed or run against other reports. |
| R11/R12 | Six skill frontmatters and all their local links pass. Inputs, methods, outputs, references, formal handoffs, and missing-capability behavior are explicit. Runtime, live monitoring, standards-conformance, and professional-credential limits are candid. |

The independent harness recorded 22 passing behavior assertions and five additional observations used in the findings. The metadata finding concerns an absent supported capability, not a failing assertion that saving a note should implicitly mutate project metadata. All 42 candidate hashes matched before and after testing.

## Exact commands and results

All top-level commands used working directory `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`. All exited 0. `product-checks.py` is the retained executable probe; `product-evidence.json` retains all 52 subprocess argument lists, working directories, stdout, stderr, exit codes, assertions, and observations. Its projects and working directory were temporary and contained spaces in their paths. Each CLI invocation used the absolute script path.

1. Governing documents, record protocol, candidate, and inventory:

```sh
cat AGENTS.md development/PLAN.md docs/CONTRACT.md docs/RECORDS.md development/gates/G3/candidate.json && rg --files skills seeds docs src tests
```

Relevant result: inspected the G3 boundary, approved journey, formal record/evaluation protocol, and 42-file manifest.

2. Start/resume and all six integrated skills:

```sh
cat START.md README.md skills/README.md skills/agent-architect/SKILL.md skills/evidence-curation/SKILL.md skills/process-discovery/SKILL.md skills/data-discovery/SKILL.md skills/architecture-delivery/SKILL.md skills/operations-review/SKILL.md docs/CLI.md && cat src/agent_architect/cli.py
```

Relevant result: the guide selects specialists and saves checkpoints; each specialist declares inputs and outputs/handoffs. Missing tools produce provisional artifacts and stated blockers. The CLI has schema/process/architecture/evaluation/release/incident commands but no project-brief update route.

3. Implementation, fixtures, and tests:

```sh
nl -ba src/agent_architect/workflow.py && cat src/agent_architect/schema.py tests/support.py tests/test_workflow.py
```

The long output was truncated. The consequential-transition/render portion, schema, and reference-limit language were retrieved explicitly:

```sh
sed -n '294,470p' src/agent_architect/workflow.py && cat src/agent_architect/schema.py && cat references/professional-methods.md
```

Relevant result: inspected rendering, evaluation receipts, readiness/activation/closure behavior, record types, the labeled synthetic fixture, and the professional reference register's local-interpretation/conformance limits.

4. Focused intake-metadata and guide inspection:

```sh
rg -n '^    def |^def |owner|scope' src/agent_architect/core.py src/agent_architect/cli.py skills/agent-architect/SKILL.md && sed -n '300,430p' src/agent_architect/core.py && nl -ba skills/agent-architect/SKILL.md && nl -ba START.md
```

Relevant result: confirmed the initialization-only root metadata and the guide's explicit unknown-intake/scope-narrowing instructions cited in finding 1.

5. Existing regression suites:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_core.py -q
```

```text
Ran 30 tests in 0.334s

OK
```

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_workflow.py -q
```

```text
Ran 26 tests in 0.999s

OK
```

6. Independent skill/CLI integration probes:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 development/gates/G3/product-checks.py
```

Exact observation lines and count:

```text
OBSERVATION {"canonical_owner": "unknown", "canonical_scope": "unknown", "command_index": 17, "name": "clarified_metadata_after_supported_note", "note_owner": "Alice", "note_scope": "Project scope is standard requests only", "project_record_supported": false}
OBSERVATION {"command_index": 19, "exit_code": 2, "name": "project_metadata_record_attempt", "output": {"message": "META: unsupported type 'project'", "status": "error"}}
OBSERVATION {"command_index": 25, "exit_code": 0, "name": "render_handoff_metadata", "owner_shown": true, "payload_shown": false}
OBSERVATION {"command_index": 32, "exit_code": 0, "name": "evaluate_response_EVFAIL", "record_status": "fail", "response_status": "saved"}
OBSERVATION {"command_index": 40, "exit_code": 0, "name": "evaluate_response_EVPASS", "record_status": "pass", "response_status": "saved"}
{"checks": 22, "commands": 52, "failed": 0, "observations": 5}
```

Passing assertions include provisional saving/rendering, meaningful process-gap errors, cold resume, current/proposed and architecture checks, failed-evaluation blocking, passing-evaluation recording, local-simulation labels, changed-implementation blocking, and actionable incident errors. Full results are retained in `product-evidence.json`.

7. Line references and artifact hashes:

```sh
rg -n '^def render|out.append|return project.mutate|^    def init|^    def checkpoint|scope=scope|^def main' src/agent_architect/workflow.py src/agent_architect/core.py src/agent_architect/cli.py && python3 - <<'PY'
from pathlib import Path
import hashlib, json
folder = Path('development/gates/G3')
for name in ['candidate.json', 'product-checks.py', 'product-evidence.json']:
    print(hashlib.sha256((folder / name).read_bytes()).hexdigest(), name)
data = json.loads((folder / 'product-evidence.json').read_text())
print(json.dumps({'checks': len(data['checks']), 'failed': [c['name'] for c in data['checks'] if not c['passed']], 'commands': len(data['commands']), 'observations': data['observations']}, indent=2))
PY
```

Exact hash output:

```text
0023c1931ce0b089325966a06fbcfa7fbdf851c6cc37eb478cfc16ccc1617be3 candidate.json
f67c25af3e2b8ff66c7c79878a76230d20dc8ead5b52e4d4585f21c399a6f9a3 product-checks.py
c270cf1fa00d2ae6f2997a7f9b9419203a1c01c1cc8ac5726d1a657dc2f7d3c9 product-evidence.json
```

The same command confirmed 22 checks, no failed assertions, 52 commands, and the five observations reproduced above. Reviewer writes were limited to this report and its retained harness/evidence. No product file was edited.

## Limits and disposition

This is a G3 integration review on the available macOS Python environment. The complete-project scaffold is explicitly synthetic. Two small Python programs were actually executed to exercise result capture/evaluation; they do not validate a real agent implementation. Mermaid text was inspected, not rendered by an independent Mermaid engine. Professional-reference currency and full standards content were not independently verified. Other current reviewer reports were not read.

The ten-stakeholder/fresh-context human-facing rehearsal remains G4; clean packaging and final release sign-off remain G5. G3 is blocked by finding 1. Re-review its supported clarification/resume path after the candidate is revised. Findings 2 and 3 may be tracked as nonblocking presentation improvements.
