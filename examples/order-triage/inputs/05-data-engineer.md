# Data engineer, interview 5

SYNTHETIC training material. No real people, interviews or customer data.
Scenario date: 2026-09-09. Evidence type: attributed simulated interview.

The supplied SQLite setup represents four exports: intake.requests, crm.customers, finance.approvals and operations.handoffs. Requests have one row per (tenant, request_id). Customer identity is (tenant, customer_id), not customer_id alone. Approvals have one row per (tenant, request_id, decision_seq). Handoffs have one row per (tenant, request_id, event_seq). Only the most recent approval and handoff should enrich a request. There are four requests across north and south tenants. The schema and rows are synthetic, checked exports for this exercise.
