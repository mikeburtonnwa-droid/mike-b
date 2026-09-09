Your project is resumed and saved at **revision 40**. We now have enough evidence to begin a **fixed-fixture routing design**. Operations owns intake acceptance through a recorded routing disposition; urgent requests route to the service desk, and standard requests use Finance’s latest decision. Operational coverage and architecture remain incomplete.

The novice-facing handoff is saved at:
`/Users/michaelburton/Documents/Codex/2026-09-09/i-w/work/novice-order-project/deliverables/discovery-to-design.md`

It contains a readable map, evidence and conflict table, data findings, three separate requirements, unresolved questions and the next action. The same directory also contains `start-here.md`, `current-state-resumed.md`, `resumed-context.json`, `final-state.json`, `final-checks.json` and `verification-summary.json`. The first-interview artifacts and complete history remain intact.

**Recovered prior context.** I audited the existing project before relying on it, then read its saved brief, checkpoint, context, first-interview handoff and captured S01. Revision 4 had owner unknown, seven reported claims, a map ending at Operations takeover, and open ownership, downstream, urgent-route and status-delay questions. Its next action was an Operations walkthrough. The new supplied accounts answer much of that request without the earlier chat. The original interviewee’s lack of knowledge remains historical evidence, not the project’s current conclusion.

**New conclusions and provenance.**

| Finding | Supporting records and source pointers |
| --- | --- |
| Operations owns accepted intake through disposition, before shipment or financial authorization. | C10; S03 line 6, sentences 1 and 7; S10 line 6, sentences 1–2. Canonical brief updated; I01 resolved. |
| Urgent routing belongs to the service desk. Sales’ contrary account was unchecked last-quarter hearsay. | C09/C20; S03 line 6, sentences 2–7; S04 line 6, sentence 5; S10 line 6, sentence 4. S03 states policy effective 2026-09-01. C08 was explicitly superseded by C20; N02 preserves the reconciliation. |
| Standard routing uses the greatest decision_seq within tenant/request; approved routes fulfillment, denied or missing routes finance-review. | C11; S04 line 6, sentences 1–4; S03 line 6, sentence 5. |
| Customer identity includes tenant; approvals and handoffs are event streams that must be reduced before enrichment. | C12/C14; S05 and S07 line 6; S11 lines 6–13. D01–D04 document grains, keys and refresh limits. |
| The inputs represent daily exports, not demonstrated live freshness. Status-chasing benefits remain unmeasured. | C15/C18, I04; S08 line 6; S02 line 6, sentence 3; S01 line 6, sentence 7. |

All stakeholder material is explicitly synthetic. Policy and practice claims remain reported. Verified claims describe only actual local fixture observations, with same-day review boundaries.

**Executed data checks.** The reconstructed bad joins returned **13 rows for four request keys, including six cross-tenant customer rows** (Q01/S12, C22). This is a labeled reconstruction; the original failed report was not supplied.

The current candidate query returned **four rows, four request keys, zero cross-tenant customer rows**, and these dispositions (Q04/S17, C24):

| Request | Disposition |
| --- | --- |
| north/R1 | fulfillment |
| north/R2 | finance-review |
| north/R3 | service-desk |
| south/R4 | fulfillment |

Q05/S18 found 4 requests, 3 customers, 4 approval events and 5 handoff events, with no checked duplicate keys, required-field nulls or orphan references. Only the urgent request lacks an approval. Consequently, the missing-standard-decision branch has policy support but still lacks a supplied-fixture test case (C25, I07).

Expectations were defined before execution. Queries ran in local in-memory SQLite with pre-run fingerprints and their results were captured and bound. Q01–Q03 remain archived history; Q04/Q05 are the current executed versions. S19 summarizes the current observations and S20 captures their runner.

**Saved design handoff.** The project now has 95 records, including S02–S20, the extended P03–P07 map, updated coverage, C08–C25, D01–D04, separate REQ01–REQ03, decision DEC01, eight concern dispositions AC01–AC08 and H01. DEC01 recommends deterministic rules for the structured routing task. All eight architecture concerns explicitly retain deferred implementation work. No component acceptance evaluation, incident rehearsal, release, activation or production service was created.

**Checks.** The final integrity audit passed across all 40 commits. Current-process checking failed on service-desk and fulfillment receiver coverage. Architecture checking failed on absent implementing components and eight deferred critical concerns. Release checking failed on those gaps, missing proposed map and evaluations, open issues and unverified operational knowledge. These failures are preserved with exact outputs; they do not prevent the narrower design handoff.

**Next action.** Specify a fixture-only input/output/failure contract, then create a proposed map with current-step baselines and a deterministic component design. Keep REQ01 cardinality, REQ02 tenant isolation and REQ03 routing expectations separate. Define missing-standard-credit and unavailable-approval-feed cases before building; a missing per-request event must not silently stand for a failed feed.

Questions saved for the simulated user are: who confirms receipt at service desk and fulfillment; what distinguishes missing data from unavailable input; what measured disposition-time improvement counts as success; and who would operate a future runtime? Nobody was contacted. Receiver acknowledgements, malformed-input behavior, freshness controls, monitoring and recovery remain open.

**Library friction and repairs.** The CLI recovered the project and guarded its history, but large show/context responses needed a curated novice view. Supersession rejected differently worded applicability, requiring an explicit same-scope replacement while retaining the time-specific policy claim. Correcting three source-sentence locators changed dependency fingerprints, so I preserved the earlier executions and ran new query versions. My own substring-edit mistake briefly produced invalid requirement IDs; the CLI rejected that batch and a subsequent stale checkpoint without changing revision 38. I reread the state, repaired the IDs and saved successfully. An initial orchestration syntax failure is also logged. These agent errors are distinguished from library limitations; no implementation source or tests were inspected and no library product files were edited.

The [complete command record](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/novice-resume-commands.json) preserves commands, full stdout, stderr and exit codes, including failures. This exact response is saved as `novice-resume.md` in the same G4 directory.
