# Meeting notes to action brief

Status: draft; illustrative fixture, not an executed evaluation.

## Workflow

Convert supplied meeting notes into a Markdown brief containing decisions, action items, and open questions. Use only the supplied notes. No tools or external actions are required.

1. Extract decisions and proposed actions, preserving their wording when interpretation could change meaning.
2. Assign an owner or due date only when explicitly present. Mark missing values as unspecified.
3. Produce the brief and check each assertion against the source notes.

If notes are missing, request them. If notes disagree, preserve the conflict as an open question. Completion means the brief contains all explicit actions and no invented owners, deadlines, or decisions.

## Representative input

```text
The team agreed to pilot the new intake form.
Alex will prepare a draft by September 15, 2026.
We still need someone to review accessibility.
The launch date remains undecided.
```

## Expected brief

Decision: pilot the new intake form.

| Action | Owner | Due |
| --- | --- | --- |
| Prepare intake form draft | Alex | September 15, 2026 |
| Review accessibility | Unspecified | Unspecified |

Open questions: Who will review accessibility? When will the form launch?

## Edge case

Input: “Sam suggested launching Friday. Jordan said the launch date is still pending.”

Expected behavior: report the proposed Friday launch and the unresolved date; do not record Friday as an agreed deadline.

## Evaluation evidence

Not run. Use [the evaluation template](../templates/evaluation.md) to record a real run before changing the status.
