-- Correct for this declared fixture: composite identities and latest event per request.
WITH approvals AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY tenant, request_id ORDER BY decision_seq DESC) AS rn
  FROM finance.approvals
), handoffs AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY tenant, request_id ORDER BY event_seq DESC) AS rn
  FROM operations.handoffs
)
SELECT r.tenant, r.request_id, c.tenant AS customer_tenant, c.name,
       r.urgency, a.approved, h.owner,
       CASE WHEN r.urgency = 'urgent' THEN 'service-desk'
            WHEN a.approved = 1 THEN 'fulfillment' ELSE 'finance-review' END AS route
FROM intake.requests r
LEFT JOIN crm.customers c ON c.tenant = r.tenant AND c.customer_id = r.customer_id
LEFT JOIN approvals a ON a.tenant = r.tenant AND a.request_id = r.request_id AND a.rn = 1
LEFT JOIN handoffs h ON h.tenant = r.tenant AND h.request_id = r.request_id AND h.rn = 1
ORDER BY r.tenant, r.request_id;
