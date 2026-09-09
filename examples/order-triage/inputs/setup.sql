-- SYNTHETIC fixture. Four isolated in-memory schemas; no external database.
ATTACH DATABASE ':memory:' AS intake;
ATTACH DATABASE ':memory:' AS crm;
ATTACH DATABASE ':memory:' AS finance;
ATTACH DATABASE ':memory:' AS operations;
CREATE TABLE intake.requests(tenant TEXT, request_id TEXT, customer_id INTEGER, urgency TEXT, PRIMARY KEY(tenant,request_id));
CREATE TABLE crm.customers(tenant TEXT, customer_id INTEGER, name TEXT, PRIMARY KEY(tenant,customer_id));
CREATE TABLE finance.approvals(tenant TEXT, request_id TEXT, decision_seq INTEGER, approved INTEGER, PRIMARY KEY(tenant,request_id,decision_seq));
CREATE TABLE operations.handoffs(tenant TEXT, request_id TEXT, event_seq INTEGER, owner TEXT, PRIMARY KEY(tenant,request_id,event_seq));
INSERT INTO intake.requests VALUES ('north','R1',7,'standard'),('north','R2',8,'standard'),('north','R3',7,'urgent'),('south','R4',7,'standard');
INSERT INTO crm.customers VALUES ('north',7,'Alpha'),('south',7,'Beta'),('north',8,'Gamma');
INSERT INTO finance.approvals VALUES ('north','R1',1,0),('north','R1',2,1),('north','R2',1,0),('south','R4',1,1);
INSERT INTO operations.handoffs VALUES ('north','R1',1,'frontline'),('north','R1',2,'operations'),('north','R2',1,'operations'),('north','R3',1,'operations'),('south','R4',1,'operations');
