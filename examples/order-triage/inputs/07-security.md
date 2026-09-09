# Security reviewer, interview 7

SYNTHETIC training material. No real people, interviews or customer data.
Scenario date: 2026-09-09. Evidence type: attributed simulated interview.

Tenant isolation is mandatory: a request must never be enriched with another tenant's customer. Retain the tenant key at each join and in outputs. The only authorized actions in this exercise are reading supplied synthetic files, running local SQLite/Python, and creating local project artifacts and simulated releases. No production credentials, live customer data, network database access, shipment, or financial mutation is authorized. A real deployment needs its own runtime authorization and controls.
