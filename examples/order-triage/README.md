# Order triage: a complete synthetic rehearsal

Use this small worked example to see the library's records in action. The ten interviews, people, systems and data are fictional. Python/SQLite queries and acceptance checks are actually executed.

Start with [interview 1](inputs/01-frontline.md). The frontline account leaves ownership and urgent exceptions unresolved. Later accounts introduce conflicting finance/service-desk ownership, composite tenant identities and multiple events per request. The [operations account](inputs/03-operations.md) and [finance account](inputs/04-finance.md) resolve the fictional policy; the original hearsay remains in history.

The [current map](sample-current-map.md) shows the bounded existing workflow. The [proposed map](sample-proposed-map.md) replaces manual triage with deterministic rules while preserving the receiving responsibilities. An LLM is useful for discovery and interpretation here; the structured routing rules call for code.

## Run it

From the repository root, choose a new output directory **outside** the library:

```sh
python3 examples/order-triage/rehearse.py --output /absolute/private/path/order-triage-practice
```

The output path must not exist. Nothing connects to a real database. The runner uses four attached SQLite databases in memory and requires no packages or API keys.

The script captures all ten sources, schema, SQL, implementation and predefined expectations. It records ownership conflict and explicit supersession, checks both maps and the architecture, executes the intentionally bad join (13 rows for four requests), preserves the failed cardinality evaluation, executes corrected joins (four rows), and separately tests cardinality, tenant isolation and routing. Expected results are declared in [expected.json](expected.json) and [the sponsor account](inputs/10-sponsor.md) before execution.

It then creates and activates local simulation REL1, injects an approval-input fault, refuses unsuccessful recovery, restores the fixture, closes the incident with fresh passing evidence, and activates recovered REL2. Finally, it changes a data dependency to demonstrate impact and refusal of an outdated rollback.

## Inspect or resume

The generated directory contains:

| Artifact | Purpose |
| --- | --- |
| current-map.md / proposed-map.md | Readable derived maps, evidence and coverage |
| ready-project/ | Audited canonical project at successful handoff, with REL2 and closed incident |
| project/ | Separate final project with deliberately changed data; release checks are expected to fail |
| report.json / checks.json | Outcome summary and all 37 expected/observed assertions |
| events.json | Record operations, exact execution arguments, stdout, stderr and exit codes |
| resume-context.json / change-impact.json | Captured recall and dependency-impact views |
| *-binding.json | Fingerprints saved before each actual execution |

Use the normal [start/resume prompt](../../START.md) with the absolute generated ready-project path. Or inspect directly:

```sh
python3 scripts/aa.py --project /absolute/private/path/order-triage-practice/ready-project audit
python3 scripts/aa.py --project /absolute/private/path/order-triage-practice/ready-project context --as-of YYYY-MM-DD
```

Replace the date with your assessment date. Captured claims/evaluations have a 30-day validity window for this practice exercise. Later runs generate new dates and execution identities; old example evidence is intentionally not evergreen.

The retained [sample report](sample-report.json) comes from this build's successful run. [Gate 4 evidence](../../development/gates/G4/) contains exact logs, fresh-context experiment transcripts and a compressed copy of both synthetic projects. Unzip only into a separate practice directory.

These checks establish behavior on four fixed requests. They do not certify other data volumes, missing-customer policy, unknown urgency values, real tenant isolation controls, production availability, or comprehensive stakeholder discovery. The handoff names the work required before real deployment.
