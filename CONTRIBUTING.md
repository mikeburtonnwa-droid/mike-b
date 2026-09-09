# Maintaining the library

## Choose the right entry

| You have… | Add… |
| --- | --- |
| A useful starting prompt | A seed copied from `templates/workflow-seed.md` |
| A repeatable capability with task-specific judgment | A skill copied from `templates/skill/SKILL.md` into `skills/<name>/SKILL.md` |
| Facts, schemas, source material, or design tradeoffs | A reference copied from `templates/reference.md` |
| A concrete input and expected outcome | An example with an evaluation record |

## Lifecycle

- **Draft:** ready to try, with assumptions visible.
- **Validated:** exercised on recorded cases; include evidence and limits.
- **Deprecated:** retain the entry when existing links depend on it and point to its replacement.

Validation is specific to the cases and environment recorded. A successful run does not establish reliability for every task.

## Review an addition

Check that another person can identify when to use it, supply the inputs, and recognize completion. Remove generic advice that does not change the agent's decisions. Include missing-input behavior and external action boundaries where relevant.

Open relative links and check any skill's frontmatter. For behavioral validation, run one typical case and one relevant edge case, then record what actually happened using [the evaluation template](templates/evaluation.md). Never invent test results.
