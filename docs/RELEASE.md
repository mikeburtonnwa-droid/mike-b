# Version 0.1.0

Agent Architect is a cloneable guide/skill library with a Python standard-library record and validation tool. It supports attributed discovery, separate current/proposed maps, data lineage and query execution, traced architecture and evaluation, resumable handoffs, immutable local release snapshots and verified incident closure.

The final acceptance record is the [release sign-off](../development/gates/G5/signoff.md). [Requirements and gate evidence](DEVELOPMENT.md) explain what was exercised and repaired. A version label alone is not a readiness result.

## Install and use

Clone the repository, then follow [START](../START.md). There is no package installation, model API key, daemon or automatic skill installation required by the local CLI. The host agent needs file and terminal access to maintain canonical records.

```sh
git clone https://github.com/mikeburtonnwa-droid/mike-b.git agent-architect
cd agent-architect
python3 -S scripts/aa.py --version
```

Python 3.10+ on macOS or Linux is required; file locking uses POSIX facilities. Windows is not a tested target. The example additionally uses the standard sqlite3 module with window-function support. Keep adopter data outside the public clone.

## Reproduce verification

From the repository root:

```sh
python3 -S scripts/check_library.py
python3 -S -m unittest discover -s tests -v
python3 -S scripts/check_council.py G5 --current
```

The regression suite includes an actual SQLite discovery-to-recovery rehearsal in a temporary project. The [worked example](../examples/order-triage/README.md) gives a command that retains the generated project for inspection. Site packages are disabled with `-S`; the tests and CLI require only the Python standard library.

The council command validates recorded agreement and hashes. `--current` additionally requires the checkout's product files to match this release's accepted candidate; intentional edits should make that check fail until a new gate reviews them. Historical checks without `--current` preserve the original build audit. Continuous integration verifies the historical G5 audit and the current regression suite; it does not fabricate a new council approval for future edits.

The link checker verifies local file destinations and basic installed-skill name/description metadata. It excludes fenced examples and historical development reports; it does not validate external URLs, heading anchors or full YAML semantics. Full skill validation and Mermaid rendering for this release are recorded in the sign-off.

## Accepted scope

The release tests a four-request synthetic dataset, two fresh-context agent sessions and adversarial local record transitions. It does not establish real-human success rates, cross-model performance, universal process completeness, live source freshness, malicious-runner authenticity or production availability/scale. Exact SQL behavior outside the declared fixture needs new tests.

Real deployment remains an adopter-specific implementation and authorization task. Captured authority text is a record; actual permissions belong to the host tools/runtime. The library does not grant them. Its audit is locally tamper-evident and cannot defeat an administrator who rewrites the entire project and hash chain.

Original library code and documentation are available under the [MIT license](../LICENSE). External references remain governed by their publishers' terms. Citations and local interpretations do not establish standards conformance.
