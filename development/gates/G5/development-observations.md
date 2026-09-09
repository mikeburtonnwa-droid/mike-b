# G5 packaging and acceptance work

G4 passed unanimously before this scope began. The product reviewer's nonblocking example-path error finding is resolved: the example now catches expected Invalid errors, emits a concise explanation and exits 2, while preserving existing output. The existing no-overwrite regression now checks that exit code and absence of traceback.

Version 0.1.0 was already defined in the package; the CLI now exposes --version without requiring a project. Added MIT license, library/project anatomy, release instructions, requirement/evidence mapping and a candid audit-limit inventory. Public library data and private adopter projects remain separate.

The new standard-library checker validates product Markdown file destinations and basic installed-skill metadata, with its exclusions/limits stated. Full skill-creator quick validation passed all seven skills. The complete 86-test regression passed with the top-level Python interpreter's site packages disabled. Clean-clone acceptance additionally uses an empty virtual environment so nested Python executions cannot rely on installed packages.

GitHub Actions pins verified official checkout v7.0.1 and setup-python v7.0.0 commit SHAs. Their metadata was inspected and retained; both use node24. Hosted verification is configured for Linux Python3.10/3.12 and macOS Python3.12, with read-only content permissions. These jobs have not run before publication; no hosted result is claimed by configuration alone.

Final sign-off remains explicitly pending until the G5 council approves. After the gate passes, publication and actual hosted results will be recorded separately from the frozen product candidate. Original opinions, scripts and failures remain unchanged.
