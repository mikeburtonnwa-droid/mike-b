Verdict: APPROVE
Candidate SHA-256: 0b11c98f3e77f99f304fe545ea57de34a93a5d9e5ddcabe06f8cfd045049bfaf

## Approval scope and findings

I approve the frozen version 0.1.0 source and local verification for publication within the declared G5 scope. No unresolved blocker remains in my release-engineering remit. This is one council opinion, not the orchestrator's gate decision or final delivery sign-off. Actual hosted Linux/macOS CI results remain required after approved publication and before final user-facing delivery acceptance.

1. **Nonblocker — The frozen source reproduces in an independent clone and empty runtime.** I cloned without local object sharing, detached at commit `a0e93349b556709290068ef9aa8d3288de9122af`, and verified all 72 candidate product hashes. The clone had no object alternates and remained clean after verification. A new virtual environment contained no packages or pip; user-site loading was disabled. With a deliberately limited environment and site packages disabled for top-level Python commands, all 86 regression tests passed. The separately executed SQLite rehearsal passed all 37 assertions. Actual local runtime: Python 3.12.7, macOS 26.2, arm64. Requirements: R05–R08, R11.

2. **Nonblocker — Runtime behavior and error exits integrate with prior gates.** The CLI works from an unrelated working directory. `--version` succeeds without a project and reports `agent-architect 0.1.0`. Missing projects and missing arguments return exit 2 without traceback. The ready rehearsal project passes release checking; deliberately changed dependencies produce exit 1 and failed readiness. Both projects audit successfully at revisions 53 and 54. Existing rehearsal output is rejected with concise exit 2 and identical retained file hashes; an output path inside the library is rejected without creating it. The actual rehearsal retains the failed join, three distinct criteria, approval-loss failure, unsuccessful recovery, fresh verified closure and changed-dependency rollback rejection. Requirements: R05–R08, R11.

3. **Nonblocker — CI configuration is reviewable, but configuration is not hosted execution evidence.** YAML parsing confirmed the three matrix combinations: Ubuntu/Python 3.10, Ubuntu/Python 3.12 and macOS/Python 3.12. The workflow grants only `contents: read`, disables persisted checkout credentials, uses a ten-minute job timeout, disables matrix fail-fast and runs packaging checks, the complete regression, historical council verification and a clean-checkout assertion. I independently resolved both official version tags and inspected action metadata at the pinned commits: [checkout v7.0.1](https://github.com/actions/checkout/tree/3d3c42e5aac5ba805825da76410c181273ba90b1) and [setup-python v7.0.0](https://github.com/actions/setup-python/tree/5fda3b95a4ea91299a34e894583c3862153e4b97). Both metadata files specify Node 24. These checks support publication of the configuration; successful hosted jobs must still be observed. Requirements: R09, R11.

4. **Nonblocker — Historical council integrity remains distinct from current-product approval.** In the frozen clone, the G4 historical checker passes with three reviewers and recursively validates the G1–G3 predecessor chain. G4 with `--current` correctly rejects this later product. G5 with `--current` correctly rejects the absent final decision at this preapproval stage. CI intentionally uses historical G5 verification, while release instructions require `G5 --current` for the accepted release. The pending sign-off explicitly avoids declaring G5 passed. Publication must include the final recorded decision and supporting evidence before hosted verification can pass; future product edits require their own review. Requirements: R09, with supporting R10 traceability.

5. **Nonblocker — Packaging checks and documentation expose their actual limits.** The cloned library checker passes across 44 documents, 122 local links and seven installed skills. Independent negative controls reject a broken local destination and a skill-name/directory mismatch with structured failure and exit 1. A fenced illustrative link is ignored as documented, and restoring the inputs restores passing status. Release/anatomy/development documentation separates public library files from private adopter data, explains POSIX locking and Python requirements, distinguishes local simulation from deployment, and states historical audit limits. Product imports remain standard-library or local modules. All 18 product Python files parse under Python 3.10 grammar; this is compatibility inspection, not a Python 3.10 execution result. Requirements: R11, R12.

## Executed verification

Commands ran from:

`/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect`

Read commands, failures and test commands are preserved in role-prefixed command records. The main reproducible commands are:

```sh
python3 development/gates/G5/architecture-run.py clone-probes python3 development/gates/G5/architecture-clean-clone.py
python3 development/gates/G5/architecture-run.py packaging-probes python3 development/gates/G5/architecture-packaging.py
```

Both exited 0 with empty stderr. The clone harness records 23 subprocesses and 22 passing assertions. Its exact nested argument arrays, working directories, stdout, stderr and exit codes are retained incrementally in [architecture-clone-commands.json](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G5/architecture-clone-commands.json). The regression output ends:

```text
Ran 86 tests in 4.852s

OK
```

The separate rehearsal reports:

```json
{"checks": 37, "failed": [], "naive_rows": 13, "corrected_rows": 4}
```

Selected negative outcomes were expected and retained:

| Operation | Exit | Relevant result |
| --- | --- | --- |
| Missing project | 2 | Structured error on stderr |
| Missing CLI arguments | 2 | Parser identifies required arguments |
| Changed project release check | 1 | Failed readiness |
| Rehearsal into existing output | 2 | `Cannot run rehearsal: Output must be a new directory; previous evidence is never overwritten` |
| Rehearsal inside library | 2 | `Cannot run rehearsal: Generate project outside the public library` |
| Historical G4 with current check | 2 | `G4: current product differs from reviewed candidate` |
| Pending G5 current check | 2 | Missing G5 decision.json |
| Broken local documentation link | 1 | Missing/nonportable local link |
| Skill-name mismatch | 1 | Name/directory mismatch or missing description |

Official pin verification:

```sh
python3 development/gates/G5/architecture-run.py checkout-ref git ls-remote https://github.com/actions/checkout.git refs/tags/v7.0.1
python3 development/gates/G5/architecture-run.py python-ref git ls-remote https://github.com/actions/setup-python.git refs/tags/v7.0.0
python3 development/gates/G5/architecture-run.py checkout-metadata gh api 'repos/actions/checkout/contents/action.yml?ref=3d3c42e5aac5ba805825da76410c181273ba90b1' -H 'Accept: application/vnd.github.raw+json'
python3 development/gates/G5/architecture-run.py python-metadata gh api 'repos/actions/setup-python/contents/action.yml?ref=5fda3b95a4ea91299a34e894583c3862153e4b97' -H 'Accept: application/vnd.github.raw+json'
```

All four exited 0 with empty stderr. Tag outputs matched the workflow's complete commit SHAs; metadata outputs are preserved verbatim.

Before and after testing I ran this exact manifest check, using capture names `manifest-before` and `manifest-after`:

```sh
python3 development/gates/G5/architecture-run.py manifest-after python3 -c 'import hashlib,json,runpy,subprocess; from pathlib import Path; p=Path("development/gates/G5/candidate.json"); m=json.loads(p.read_text()); current=runpy.run_path("scripts/record_development.py")["manifest"](); print("candidate_sha256",hashlib.sha256(p.read_bytes()).hexdigest()); print("entries",len(m),"current_entries",len(current),"manifest_exact_match",m==current); print("commit",subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()); assert m==current'
```

Both exited 0 with empty stderr and returned the candidate hash in this report's header, `entries 72 current_entries 72 manifest_exact_match True`, and the exact frozen commit. Source status showed only new G5 development evidence; product hashes were unchanged.

The [clone harness](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G5/architecture-clean-clone.py), [clone summary](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G5/architecture-clone-summary.json), [retained rehearsal projects and events](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G5/architecture-clone-rehearsal.zip), [packaging harness](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G5/architecture-packaging.py), [packaging command results](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G5/architecture-packaging-commands.json) and [evidence hashes](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G5/architecture-command-evidence-summary.json) are preserved separately.

## Requirement coverage and limits

The [plan](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/PLAN.md), [release instructions](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/docs/RELEASE.md) and [development evidence guide](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/docs/DEVELOPMENT.md) define the acceptance boundary.

| Requirement | Final review evidence |
| --- | --- |
| R05 | Actual bad/corrected SQL, retained query bindings, schema and data dependency checks |
| R06 | Separate critical criteria and architecture coverage exercised by full regression and rehearsal |
| R07 | Immutable release, failed readiness, drift and rollback checks reproduced |
| R08 | Failed recovery retained; fresh verification closes incident in actual rehearsal |
| R09 | G1–G4 recorded chain validated; pending G5 fails closed; historical/current CI semantics verified |
| R11 | Independent frozen clone, empty runtime, unrelated-cwd CLI, platform boundary and clean checkout |
| R12 | Seven skills checked; packaging links, anatomy and release handoffs verified within documented validator limits |

Only local macOS/Python 3.12 execution is established here. Python 3.10 and hosted Linux/macOS execution remain required post-publication checks. I did not publish, trigger hosted CI, claim final delivery sign-off, or validate Windows. PyYAML 6.0.3 was used only by the independent reviewer to inspect workflow structure; the product and empty-runtime regression do not depend on it. Parsing YAML does not replace the hosted workflow run.

These tests cover the declared synthetic fixture and local record protocol. They do not establish real stakeholder completeness, model-provider performance, production availability, external authorization or malicious-runner authenticity.

Two evidence details are explicitly retained. The initial instruction read is preserved from its original tool output in `architecture-bootstrap-read.json`; it preceded the persistent logger and is not presented as a replayed original. Extra environment metadata for the first five clone setup commands inherited a later PATH value through a mutable dictionary; [architecture-clone-environment-note.json](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G5/architecture-clone-environment-note.json) records the actual setup PATH. Original argument arrays, working directories, outputs and exit codes are unaffected, and runtime commands used the recorded virtual-environment PATH. No original evidence was rewritten to conceal these limits.

No product files or prior evidence were edited. No other current G5 opinion was consulted, no work was delegated, and no side-channel communication occurred.

