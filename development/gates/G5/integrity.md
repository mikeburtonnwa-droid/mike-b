Verdict: APPROVE
Candidate SHA-256: 0b11c98f3e77f99f304fe545ea57de34a93a5d9e5ddcabe06f8cfd045049bfaf

Reviewer: Integrity council reviewer
Gate: G5, version 0.1.0
Source commit: a0e93349b556709290068ef9aa8d3288de9122af

I approve the frozen source and its bounded local verification evidence for the final council publication decision. No unresolved blocker remains in my remit. This opinion does not declare G5 passed, hosted CI successful, or final delivery complete.

## Findings

1. **Nonblocker — Accepted candidates and review history are traceable (R09, R10).** All 72 G5 product entries match the frozen manifest before and after testing. G1–G4 council checks independently pass, with three accepted opinions per gate and intact predecessor, report and transcript bindings. I compared every accepted candidate entry against an archived Git tree, rather than accepting commit labels as evidence:

   | Gate | Accepted candidate | Matching source commit | Files / messages |
   | --- | --- | --- | --- |
   | G1 | candidate-r2.json | 2a0f211529c7f23448d3e238ee534ec7c7eb0707 | 21 / 14 |
   | G2 | candidate-r2.json | f01a6655eb0f88cc1f6ca6b455de49e920e1a1ff | 29 / 14 |
   | G3 | candidate-r3.json | bd4e40eb199b05094dc2092fc57ba6bd2a3410f6 | 44 / 21 |
   | G4 | candidate.json | 71afb9e4b32d6178daabb91d198098988d122119 | 66 / 12 |

   Earlier dissent remains in the transcripts and exact saved reports: three initial opinions each for G1/G2, and four blocking opinions across G3's first two rounds. The rework records explain the corresponding changes, including G3's replay defect after two reviewers had approved revision 2. Original failed opinions are not replaced by later approvals.

2. **Nonblocker — Council integrity rejects adversarial changes (R09, R10).** Independent disposable-copy probes reject candidate tampering, report tampering, a missing reviewer, a changed predecessor decision and a broken transcript chain. A stronger probe rewrote all affected report/decision/transcript hashes consistently but placed an authoritative DENY in the header and an APPROVE example later in the body. The checker still rejected it as a denied or wrong-candidate report. These checks establish the recorded protocol's behavior, not reviewer identity or independence beyond observable evidence.

3. **Nonblocker — Local runtime and clean-clone claims are supported within the tested environment (R11).** An independent `git clone --no-hardlinks` resolved to the exact G5 source commit and matched all 72 product entries. Python 3.12.7 on local macOS, in a virtual environment created without pip and with empty site-packages, ran the CLI with `-S`, all 86 regression tests, the library checker and the actual rehearsal. Nested Python executions used the empty runtime. The checker found 44 documents, 122 local file links and seven skills, with no errors. `--version` returned `agent-architect 0.1.0` from an unrelated working directory. Runtime imports are standard-library/local modules; no runtime model credentials or network integration are implemented. This does not independently establish execution on Linux or Python 3.10.

4. **Nonblocker — Representative end-to-end evidence remains substantive (R02–R08).** The independent fresh rehearsal passed all 37 declared checks, reproduced 13 naive rows versus four corrected rows, retained failed cardinality and recovery evidence, closed INC_FEED using EV_RECOVERED, and recorded REL2 only as a local simulation. Both resulting projects audited successfully. The ready project passed readiness and resumed at stage `operate`; its deliberately changed counterpart failed readiness. All nine actual execution subprocess records retain argv, cwd, stdout, stderr and exit status, and their stdout exactly matches captured result-source bytes. The complete fresh run is preserved in `integrity-rehearsal.zip`.

5. **Nonblocker — Tampering and public/private boundaries are enforced or accurately described (R03, R07, R11).** In disposable projects, altered source bytes blocked audit, context and activation with structured exit-2 errors and unchanged HEAD. Altered history was rejected; restoring the original bytes restored a passing audit. The example refused an existing output directory without a traceback or overwriting evidence, resolving G4's presentation finding. It also refused creation inside the cloned public library. A separate final disposable clone remained clean and matched the frozen product. The tracked-file inventory contains no configured private/runtime paths; example inputs are explicitly synthetic. General CLI source capture still relies on the adopter to choose private storage and avoid supplying secrets, as the documentation states.

6. **Nonblocker — Guide, specialist and attribution claims are bounded (R01, R12).** All seven skills passed independent runs of the recorded skill validator. I also read their operational content: inputs, methods, evidence outputs, handoffs, missing-input behavior and action boundaries are present. The guide owns startup/resumption and keeps metadata handling with the agent. G4's two distinct agent experiments substantiate the narrower start/resume claim, including preserved unknown ownership, later source reconciliation and an incomplete design handoff. They do not establish real-human usability rates. The MIT license applies to original library material; the reference register names sources/editions and labels adaptations as local interpretations. External materials retain their publishers' terms; standards conformance and professional credentials are not claimed.

7. **Nonblocker — Audit and delivery limits are disclosed (R09, R10).** The development documentation explicitly identifies the G4 product harness that aborted before flushing its first nested command log. Its original script and outer error remain; later runs are identified as separate attempts. Some early rejected candidates have manifests/reports/probes without complete standalone source snapshots. These gaps prevent a claim that every historical internal subprocess can be replayed. The accepted source trees are preserved and independently matched above. G5 sign-off remains pending, and hosted Linux/macOS jobs are described as configured, not executed. Final user-facing delivery must retain these distinctions and record actual publication/CI results separately.

## Requirement coverage

Definitions: [development/PLAN.md](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/PLAN.md:9). The [development evidence map](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/docs/DEVELOPMENT.md) points to the underlying artifacts; this assessment checks those artifacts and execution results rather than treating the map itself as proof.

| ID | Evidence assessed and practical limit |
| --- | --- |
| R01 | Entry-guide content, G4 first-session and different-agent resume reports/archives; two agent experiments only |
| R02 | Current/proposed process records, declared coverage gaps, G4 handoffs and fresh 37-check rehearsal; declared structure does not prove complete discovery |
| R03 | Captured originals and knowledge statuses, prior integrity tests, new source/history tamper negatives; hashes do not establish truth |
| R04 | Supersession/conflict/freshness/context regressions, saved checkpoint and resumed context; lexical retrieval and supplied dates have stated limits |
| R05 | Composite-key/event-grain fixture, G4's independent SQL replays, new actual 13/4-row execution and captured bindings; fixed dataset only |
| R06 | Requirement/component/criterion tracing and dependency/brief binding regressions; observed fixture behavior does not validate arbitrary architectures |
| R07 | Immutable release, drift/rollback and latest-evidence regressions, new readiness/tamper probes; local simulation only |
| R08 | Retained failed verification and successful recovery in the new rehearsal, incident regressions and G4 lifecycle evidence; no live incident response |
| R09 | G1–G4 exact candidate/report/decision chain checks and six independent council negatives; G5 orchestration remains pending |
| R10 | Exact prior responses, preserved dissent/rework, incremental current command records and explicitly disclosed historical gaps |
| R11 | Independent clone/empty runtime, private-path refusal, storage guidance and inventory; no comprehensive secret or legal audit |
| R12 | Seven validator passes plus substantive review of skill inputs, methods, outputs, references, handoffs and failure behavior |

## Executed commands, results and retained failures

Working directory:

```text
/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect
```

Exact shell commands, cwd, stdout, stderr and exit codes are retained in [integrity-commands.jsonl](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G5/integrity-commands.jsonl). The initial assignment read, before logger setup, is separately transcribed and labeled in `integrity-initial-read.json`. Principal commands were executed through `python3 development/gates/G5/integrity-run.py '<command>'`:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -S development/gates/G5/integrity-audit.py
PYTHONDONTWRITEBYTECODE=1 python3 -S development/gates/G5/integrity-clone.py
PYTHONDONTWRITEBYTECODE=1 python3 -S development/gates/G5/integrity-negatives-r2.py
PYTHONDONTWRITEBYTECODE=1 python3 -S development/gates/G5/integrity-negatives-r3.py
PYTHONDONTWRITEBYTECODE=1 python3 -S development/gates/G5/integrity-final-check.py
```

The audit command exited 0: four accepted source-tree matches, six rejected council attacks and seven `Skill is valid!` results. It also verified the supplied clean-clone record's 14 completed commands, exact commit and empty site-packages.

The first independent clone harness exited 1 after its successful regression (`Ran 86 tests in 4.762s`, `OK`), 37-check rehearsal and overwrite negative. My harness mistakenly parsed an integrity error from stdout; the CLI correctly emitted JSON on stderr and exited 2. Its complete subprocess outputs and fresh rehearsal archive were already saved. The separate r2 harness confirmed all three source-tamper rejections, then exited 1 because my assertion expected the word `hash`; the actual error was `History integrity failure`. The original scripts/logs remain unchanged. The separate r3 harness corrected that assertion and exited 0, completing the history, private-path, restoration and clean-clone checks. These were reviewer assertion errors, not product failures.

The nested command logs retain matched started/completed records with full result channels: 17 commands in `integrity-audit-commands.jsonl`, 14 in `integrity-clone-commands.jsonl`, seven in `integrity-negatives-r2-commands.jsonl`, and 11 in `integrity-negatives-r3-commands.jsonl`. No initiated subprocess in these reviewer harnesses lost its result record. Unit-test output is retained as the test runner's output, not represented as a separate transcript of every internal test operation.

The final check exited 0 and confirmed all 72 manifest entries still match. The fresh rehearsal archive SHA-256 is `b72a4e97094dcb193d1ab5e2e8e69a0b0dddb796200e7555e865461640b5852e`.

## Scope of defensible sign-off

The evidence supports publication of a local, standard-library guide/record/checking library with a tested synthetic example and disclosed review history. It does not support claims of real deployment, real-human success rates, provider performance, universal data correctness, continuous source freshness or authenticated execution. Source dates, authority text and external run metadata remain supplied evidence; local hashes cannot defeat an administrator who rewrites the complete history.

I did not run hosted CI, publish anything, inspect other current G5 opinions, delegate, or edit product files or prior evidence. The orchestrator must complete the current council record and verify actual post-publication hosted results before final delivery sign-off. Any intervening product change requires the relevant re-review.
