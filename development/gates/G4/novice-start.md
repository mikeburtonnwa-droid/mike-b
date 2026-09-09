Completed the first-interview session and saved a resumable discovery project at **revision 4**.

The simulated novice would see:

> We have a first draft: intake queue → frontline emails tenant, request ID, customer ID and urgency → operations takes the request. This is the end of the stakeholder's account; the overall workflow's completion remains unknown. Normal requests reportedly continue through a credit check and fulfillment. Urgent handling differs, and status chasing costs time, but those details need further evidence.
>
> Your most useful next step is one normal-request walkthrough with the operations recipient. Follow the handoff email to the actual outcome, recording owners, systems, acknowledgements and status chases. During that conversation, identify the overall process owner and who can explain urgent cases. Your progress is saved for a fresh session.

Only `examples/order-triage/inputs/01-frontline.md` supplied business evidence. I read START, the guide and process-discovery skills, CLI/record documentation, and the linked professional-methods register. I did not read other example inputs, tests, implementation source, development reports or expected answers, and contacted no one.

Saved records are S01, seven reported claims C01–C07, three current process nodes P01–P03, six coverage records CV01–CV06, four open issues I01–I04, and note N01. The checkpoint preserves the task, completed work, unresolved questions, next action, relevant IDs and discovery stage. The owner remains `unknown`. All evidence remains synthetic, recollection-based and unverified; claim freshness is unknown. Capture and scenario dates are recorded separately as 2026-09-09.

Artifact locations:

- Private project and canonical history: `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/work/novice-order-project`
- Novice-facing draft and copyable resume prompt: `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/work/novice-order-project/deliverables/start-here.md`
- Library-rendered map, evidence and checkpoint: `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/work/novice-order-project/deliverables/first-interview-current-state.md`
- Saved context view: `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/work/novice-order-project/deliverables/resume-context.json`
- Checkpoint input, also committed canonically: `/Users/michaelburton/Documents/Codex/2026-09-09/i-w/work/novice-order-project/drafts/first-checkpoint.json`
- [Full command log, including reads, stdout, stderr and exit codes](/Users/michaelburton/Documents/Codex/2026-09-09/i-w/outputs/agent-architect/development/gates/G4/novice-start-commands.json)

Validation: all four mutations reported `saved`. `audit` passed over four commits. `show` and `context` recovered the checkpoint, records and unknown owner. The captured source bytes and SHA-256 match the supplied interview. `render` succeeded. `check process --view current` returned **fail, exit 1**, identifying the unknown operations system, missing operations perspective and declared downstream/urgent/exception gaps. This is an incomplete discovery map, with its missing information preserved. No operational process test, architecture evaluation, release or activation occurred.

The primary question for the simulated novice is: **Who in operations receives these emails and could walk through one normal request with us?** Follow-up prompts for that conversation are: What proves receipt? Who owns the whole process and each downstream step? What counts as completion? Where does urgent handling diverge, and who owns it? Where and why is status chased? These questions are saved without interrupting the independent work.

Library friction was mainly in presentation. The rendered Resume section is a single HTML-escaped JSON paragraph, so I added the readable companion. The generated page says “Deployment mode: local-simulation” even with no release, which could confuse a novice; the companion explains that nothing was deployed. The diagnostic `P03: unknown actor/system/boundary/variant` does not identify that only the system is unknown. “Covered” also needs the guide's caveat that it means an attributed account exists, not complete or verified coverage. The documentation and public schema were sufficient to complete the session without implementation inspection or unexpected command failures.
