Verdict: APPROVE
Candidate SHA-256: 0b11c98f3e77f99f304fe545ea57de34a93a5d9e5ddcabe06f8cfd045049bfaf

# G5 skeptical adopter and product review

The frozen version 0.1.0 source supports the documented local adopter path. An independent Git clone at commit `a0e93349b556709290068ef9aa8d3288de9122af` passed the library check, all 86 regression tests, the 37-check worked example, and an additional start/backup/resume/adaptation exercise in an empty virtual environment. The G4 error-presentation finding is resolved without changing saved output. No unresolved blocker or nonblocker remains in this remit.

This approves the final source and local verification for publication within the product-review remit. It does not declare the council gate passed or final delivery signed off. Hosted Linux/macOS results must still be verified after approved publication, as the assignment requires.

## Findings

1. **Resolved nonblocker — the example explains an existing output path without a traceback.** Repeating the example against its completed output directory now exits 2 with `Cannot run rehearsal: Output must be a new directory; previous evidence is never overwritten`. There is no stdout or traceback. All 177 existing output files remain byte-for-byte unchanged. The new top-level error handling and regression assertion address the G4 recommendation directly. **Requirements:** R01/R11/R12. **Evidence:** `g4_error_finding_resolved_without_overwrite`; [example entry point](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/examples/order-triage/rehearse.py:318).

2. **Adopter instructions are executable and distinguish library from project.** README → START → release/anatomy/record instructions identify the host’s required file/terminal capability, absolute library and private-project paths, optional skill installation, and expected artifacts. Version discovery works without a project. The independent clone matches all 72 candidate entries; its documented checks run with site packages disabled and nested Python isolated in a virtual environment without pip. All checks leave the clone clean. **Requirements:** R01/R11/R12.

3. **Start, relocation, resumption and domain adaptation preserve the needed handoff.** A separate synthetic invoice project saved its reported account, explicit owner/exception uncertainty and checkpoint. Context recovered the checkpoint without matching query text or prior chat. Copying the complete private project to another path preserved its audit, source pointers and uncertainty. Captured clarification updated the authoritative owner to Invoice Operations while retaining the historical unknown owner. A stale checkpoint edit returned an actionable error and left HEAD unchanged. The deliberately absent process map remained an explicit gap; neither rendering nor navigation implied readiness. **Requirements:** R01/R02/R04/R11/R12.

4. **Required inputs, outputs and traceability have usable documented locations.** Anatomy maps specifications, retained knowledge, checkpoint memory, decisions, tools, tests and recovery to concrete records and files. It explains whole-project backup and the distinction between canonical history/source bytes and disposable views. The worked example produced every documented output category, its ready project audited across 53 commits, and resumed context supplied REL2, the operating handoff and remaining real-deployment work. Its proposed map retained handoff payload/receiver tables and an explicit infrastructure-deployment disclaimer. **Requirements:** R02/R04/R11/R12; integration with R03/R05/R06/R07/R08.

5. **Final claims match the demonstrated scope and its limits.** The documentation presents professional perspectives as methods, not lived experience or credentials; it does not claim standards conformance or unsupported novelty. “Latest captured knowledge” is distinguished from external freshness, and lexical retrieval limitations are explicit. The two G4 agent experiments support the promised bounded first-session and cold-resume experience; they are not presented as human usability research or provider comparisons. Release documentation names the four-request fixture, local audit limits and adopter-specific implementation/authorization. Sign-off is explicitly pending, and CI configuration is not presented as an executed hosted result. **Requirements:** R01/R04/R11/R12.

## Requirement coverage and prior-gate integration

| Requirement | Final product evidence |
| --- | --- |
| R01 | Clear clone/entry prompt, project-free version check, separate private project, saved next action, relocated resumption and the two previously reviewed G4 agent experiments. |
| R02 | Missing map structure remains visible; the executed example supplies readable current/proposed views, coverage and receiving responsibilities. |
| R04 | Reported evidence stays uncertain, source-linked context survives relocation, clarification preserves prior state, and docs accurately bound captured freshness and lexical retrieval. |
| R11 | Independent clone, empty virtual environment, disabled site packages, complete regression, preserved output, clean checkout and explicit public/private separation. |
| R12 | Guide-driven specialist selection, exact record references, anatomy/adaptation guidance and explicit inputs, outputs, checks and handoff limits. |

Requirements are defined in the [development plan](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/PLAN.md:9). The full regression retains G2 persistence/context protections, G3 query/evaluation/replay/activation safeguards, and G4 execution/recovery behavior. No other current G5 opinion was read. The full suite’s historical council tests are distinct from accepting this pending gate.

## Executed commands and results

The [independent adopter harness](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G5/product-adopter.py) writes each command’s arguments, cwd and start record before execution, then immediately writes complete stdout, stderr and exit code. Its [journal](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G5/product-adopter-commands.jsonl) contains 32 started and 32 completed commands, zero interruptions, and 31 passing assertions. Expected negative commands remain recorded. No failed probe or rerun was discarded.

Top-level command, run from `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`:

```sh
python3 development/gates/G5/run-command.py product-06-adopter-run python3 -S development/gates/G5/product-adopter.py
```

Exit 0. The outer command’s complete output is retained in `product-06-adopter-run.json`. Important commands inside the harness were an independent `git clone --no-local --quiet`, detached checkout of the exact candidate commit, creation of a virtual environment with `--without-pip`, and these documented checks using that environment’s Python:

```sh
python3 -S scripts/aa.py --version
python3 -S scripts/check_library.py
python3 -S -m unittest discover -s tests -v
```

The journal contains the exact absolute interpreter/clone paths and working directories. Relevant exact results:

```text
agent-architect 0.1.0
```

```json
{"documents":44,"local_links":122,"skills":7,"errors":[],"status":"pass"}
```

The JSON above selects the checker’s result fields; its full output also states the checker’s limited scope.

```text
Ran 86 tests in 4.907s

OK
```

Selected exact harness outputs:

```text
PASS whole_project_backup_is_portable: {"commits": 4, "head": "6e2f646106b168178b30f2f65975dc34758f51d81a10fa420cc3deb1ec93f60f", "limit": "Local hash consistency; does not authenticate authors or truth.", "status": "pass"}
PASS relocated_context_keeps_source_and_uncertainty: {"record_ids": ["ACCOUNT", "FIRST"], "warnings": ["ACCOUNT: reported, freshness=unknown"]}
PASS clarified_context_preserves_prior_boundary: {"current_owner": "Invoice Operations", "historical_owner": "unknown"}
PASS stale_resume_edit_is_actionable_and_atomic: {"message": "Stale revision: expected 4, current 6; reread and reconcile", "status": "error"}
PASS g4_error_finding_resolved_without_overwrite: {"exit_code": 2, "stderr": "Cannot run rehearsal: Output must be a new directory; previous evidence is never overwritten\n", "unchanged_files": 177}
PASS adopter_checks_leave_clone_clean: {"stderr": "", "stdout": ""}
{"checks": 31, "commands": 32, "completed": true, "failed": []}
```

Role-prefixed incremental records `product-01-docs.json` through `product-05-code-and-ci.json` preserve document, development-evidence, candidate and code-diff inspection commands/results. `product-07-final-evidence.json` preserves the final journal/count/hash verification. The logger bootstrap read is separately retained. Existing evidence and product files were not edited; mutations occurred in disposable independent clones/projects.

Candidate and artifact hashes:

```text
0b11c98f3e77f99f304fe545ea57de34a93a5d9e5ddcabe06f8cfd045049bfaf candidate.json
116fa6875dc40c9d8c4fdb040a0b733223e3f9e142f5c181a820d19031eaa9ae product-adopter.py
0eb6e810a80ae89db47bee3436cc7a4e7d3642c1bd4b7e0963512dfb065d6f91 product-adopter-commands.jsonl
bd202b04ee36c37e7056abd195cb74f6211e27e728ca1d01a2698cbac3ba2577 product-adopter-summary.json
d78e330dce373f8f26e592489b062e7fb1077d270c19d8c45b69ea9ef9702542 product-06-adopter-run.json
```

All 72 manifest entries matched before and after testing and in the independent clone.

## Limits and delivery boundary

Execution was local macOS with Python 3.12. I cloned the local frozen Git source because the public remote intentionally remains the original scaffold until approval; this does not claim that public publication has happened. Linux/Python 3.10 and hosted CI results remain post-publication verification obligations. The pending G5 council command cannot establish agreement before the orchestrator records the completed decision, so I did not treat it as a current pass.

The additional invoice case is a synthetic CLI adaptation, not another fresh-agent or human study. Full external-link currency, standards conformance, all Mermaid inputs, live data behavior, model performance and production deployment were not established. The library checker’s file-link/basic-metadata limits are accurately disclosed. Final user-facing sign-off must record the actual publication and hosted verification outcomes and retain these scope limits.
