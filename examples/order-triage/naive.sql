-- Intentionally incorrect: omits tenant at the customer join and keeps all events.
SELECT r.tenant, r.request_id, c.tenant AS customer_tenant, c.name,
       r.urgency, a.approved, h.owner,
       CASE WHEN r.urgency = 'urgent' THEN 'service-desk'
            WHEN a.approved = 1 THEN 'fulfillment' ELSE 'finance-review' END AS route
FROM intake.requests r
JOIN crm.customers c ON c.customer_id = r.customer_id
LEFT JOIN finance.approvals a ON a.tenant = r.tenant AND a.request_id = r.request_id
LEFT JOIN operations.handoffs h ON h.tenant = r.tenant AND h.request_id = r.request_id
ORDER BY r.tenant, r.request_id, c.tenant, a.decision_seq, h.event_seq;
