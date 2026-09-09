"""Reproduce the synthetic discovery-to-operations rehearsal, outside the library."""
import argparse
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
LIBRARY = HERE.parents[1]
sys.path.insert(0, str(LIBRARY / 'src'))
from agent_architect.core import Project, Invalid, context, digest, impact
from agent_architect import workflow as w
from agent_architect.schema import CONCERNS
from execute import CRITERIA

DATE = datetime.now(timezone.utc).date()
ASOF = DATE.isoformat()
DUE = (DATE + timedelta(days=30)).isoformat()
ACTOR = 'synthetic-rehearsal'
AUTHORITY = 'Local synthetic SQLite/Python and simulation only; S07, S09'
SCOPE = 'Synthetic intake acceptance through recorded routing disposition; excludes shipment and credit authorization'


def record(rid, record_type, **fields):
    return dict(id=rid, type=record_type, title=rid, description='Synthetic order-triage exercise', status='active') | fields


def evidence(*ids):
    return [dict(source=rid, locator='complete captured fixture document') for rid in ids]


class Rehearsal:
    def __init__(self, output):
        self.output = output.resolve()
        if self.output.exists():
            raise Invalid('Output must be a new directory; previous evidence is never overwritten')
        if self.output == LIBRARY or LIBRARY in self.output.parents:
            raise Invalid('Generate project outside the public library')
        self.output.mkdir(parents=True)
        self.p = Project(self.output / 'project')
        self.events, self.checks = [], []
        self.run('initialize', lambda: self.p.init('Order triage exercise', SCOPE, 'operations', ACTOR))

    def revision(self):
        return self.p.read()['revision']

    def save_logs(self):
        (self.output / 'events.json').write_text(json.dumps(self.events, indent=2) + '\n')
        (self.output / 'checks.json').write_text(json.dumps(self.checks, indent=2) + '\n')

    def run(self, label, fn):
        result = fn()
        self.events.append(dict(action=label, result=result))
        self.save_logs()
        return result

    def check(self, name, observed, expected):
        item = dict(name=name, expected=expected, observed=observed, passed=observed == expected)
        self.checks.append(item)
        self.save_logs()
        if not item['passed']:
            raise AssertionError(json.dumps(item))
        return observed

    def reject(self, label, fn):
        before = self.p.head()
        try:
            fn()
        except Invalid as exc:
            self.events.append(dict(action=label, expected_rejection=str(exc)))
            self.check(label + ' rejects atomically', self.p.head() == before, True)
        else:
            raise AssertionError(label + ' unexpectedly succeeded')

    def capture(self, rid, content, kind='document', locator='synthetic rehearsal'):
        return self.run('capture ' + rid, lambda: self.p.source(
            rid, rid, content, kind, locator, ASOF, 'fixture', self.revision(), ACTOR))

    def put(self, values):
        return self.run('save ' + ', '.join(r['id'] for r in values),
                        lambda: self.p.put(values, self.revision(), ACTOR))

    def execute(self, label, binding, sql, criterion=None, fault='none'):
        path = self.output / (label + '-binding.json')
        path.write_text(json.dumps(binding, indent=2) + '\n')
        argv = [sys.executable, str(HERE / 'execute.py'), '--sql', sql, '--binding', str(path), '--fault', fault]
        if criterion:
            argv.extend(['--criterion', criterion])
        proc = subprocess.run(argv, cwd=self.output, text=True, capture_output=True)
        self.events.append(dict(action='execute ' + label, argv=argv, cwd=str(self.output),
                                stdout=proc.stdout, stderr=proc.stderr, returncode=proc.returncode))
        self.save_logs()
        if proc.returncode not in (0, 1) or not proc.stdout:
            raise RuntimeError(proc.stderr)
        value = json.loads(proc.stdout)
        self.check(label + ' exit faithfully captured', value['exit_code'], proc.returncode)
        self.capture('RESULT_' + label, proc.stdout.encode(), 'query-result', 'Executed command and output in events.json: ' + label)
        return value

    def query(self, rid, sql):
        self.put([record(rid, 'query', status='draft', environment='fixture',
                         sql=(HERE / sql).read_text(), assets=['D_REQUESTS', 'D_CUSTOMERS', 'D_APPROVALS', 'D_HANDOFFS'],
                         parameters={}, join_assumptions='Composite tenant identity and latest event required; naive version intentionally violates these',
                         limitations='Four synthetic requests; daily fixed export; no live database',
                         evidence=evidence('SRC_' + ('NAIVE' if sql == 'naive.sql' else 'SQL'), 'S05', 'S06'))])
        result = self.execute(rid, w.query_fingerprint(self.p.read(), rid), sql)
        self.run('bind ' + rid, lambda: w.bind_query(self.p, rid, 'RESULT_' + rid, self.revision(), ACTOR))
        return result

    def evaluate(self, rid, criterion, sql='routes.sql', fault='none'):
        req = 'REQ_' + criterion.upper()
        binding = dict(target_hashes=w.fingerprints(self.p.read()['records'], [req, 'COMP_ROUTER']),
                       brief_hash=w.brief_hash(self.p.read()))
        value = self.execute(rid, binding, sql, criterion, fault)
        receipt = self.run('evaluate ' + rid, lambda: w.evaluate(self.p, dict(
            id=rid, title=rid, description='Actual local SQLite execution against synthetic fixture',
            targets=[req, 'COMP_ROUTER'], result_source='RESULT_' + rid, valid_until=DUE,
            criterion=CRITERIA[criterion]), self.revision(), ACTOR))
        self.check(rid + ' computed outcome', receipt['outcome'], 'pass' if value['exit_code'] == 0 else 'fail')
        return receipt


def build(r):
    p = r.p
    for index, path in enumerate(sorted((HERE / 'inputs').glob('*.md')), 1):
        r.capture(f'S{index:02}', path.read_bytes(), 'interview', 'examples/order-triage/inputs/' + path.name)
    for rid, path in [('SRC_SETUP', HERE / 'inputs/setup.sql'), ('SRC_NAIVE', HERE / 'naive.sql'),
                      ('SRC_SQL', HERE / 'routes.sql'), ('SRC_RUNNER', HERE / 'execute.py'),
                      ('SRC_EXPECTED', HERE / 'expected.json'), ('SRC_REHEARSAL', HERE / 'rehearse.py')]:
        r.capture(rid, path.read_bytes(), locator=str(path.relative_to(LIBRARY)))
    r.run('clarify authoritative brief', lambda: p.brief(dict(
        title='Order triage exercise', scope=SCOPE, owner='operations',
        rationale='Operations and sponsor define the bounded simulation', evidence=evidence('S03', 'S10')),
        r.revision(), ACTOR))
    old = record('CL_OLD_OWNER', 'claim', status='disputed', assertion='Finance owns urgent exceptions',
                 applicability='Urgent request ownership in fixture current policy', evidence=evidence('S02'), conflicts_with=['CL_OWNER'])
    owner = record('CL_OWNER', 'claim', status='disputed', assertion='Service desk owns urgent manual review',
                   applicability=old['applicability'], evidence=evidence('S03', 'S04'), conflicts_with=['CL_OLD_OWNER'])
    r.put([old, owner])
    disputed = context(p.read(), 'CL_OLD_OWNER', ASOF)
    r.check('conflict retrieved bilaterally', {v['id'] for v in disputed['records'] if v['type'] == 'claim'} == {'CL_OLD_OWNER', 'CL_OWNER'}, True)
    r.run('supersede hearsay with scenario policy', lambda: p.supersede(
        'CL_OLD_OWNER', 'CL_OWNER', 'S02 explicitly hearsay; S03 and S04 confirm current synthetic policy', r.revision(), ACTOR))
    owner = copy.deepcopy(p.read()['records']['CL_OWNER'])
    owner.update(status='verified', verified_on=ASOF, review_due=DUE,
                 verification='Confirmed only within the fictional scenario by S03/S04; not field research')
    r.put([owner])
    r.check('superseded claim excluded from active recall', 'CL_OLD_OWNER' not in [v['id'] for v in context(p.read(), 'CL_OLD_OWNER', ASOF)['records']], True)
    r.put([record('CL_KEYS', 'claim', status='verified', assertion='Tenant is part of request and customer identity; approvals/handoffs have event grain',
                  applicability='Supplied SQLite fixture only', evidence=evidence('S05', 'SRC_SETUP'),
                  verified_on=ASOF, review_due=DUE, verification='Inspected composite primary keys in captured setup.sql against S05')])

    # Record the actual current control flow, including owners, systems and boundaries.
    specs = [
        ('P_INTAKE', 'start', 'frontline', 'intake-queue', 'internal', 'shared', [('P_TRIAGE', 'accepted', 'handoff')]),
        ('P_TRIAGE', 'decision', 'operations', 'operations-email', 'internal', 'shared',
         [('P_URGENT', 'urgent', 'exception'), ('P_CREDIT', 'standard', 'handoff')]),
        ('P_URGENT', 'end', 'service-desk', 'support-queue', 'support', 'urgent', []),
        ('P_CREDIT', 'decision', 'finance', 'credit-export', 'internal', 'standard',
         [('P_FULFILL', 'approved', 'handoff'), ('P_HOLD', 'denied-or-missing', 'exception')]),
        ('P_FULFILL', 'end', 'fulfillment', 'fulfillment-queue', 'internal', 'standard', []),
        ('P_HOLD', 'end', 'finance', 'credit-export', 'internal', 'standard', []),
    ]
    actors = {v[0]: v[2] for v in specs}
    values = []
    for rid, kind, actor, system, boundary, variant, edges in specs:
        values.append(record(rid, 'process', view='current', kind=kind, actor=actor, system=system,
                             boundary=boundary, inputs=['tenant, request ID, customer ID, urgency and available latest credit decision'],
                             outputs=['attributed routing disposition' if kind == 'end' else 'request and routing context'],
                             variant=variant, title={'P_INTAKE': 'Accept request', 'P_TRIAGE': 'Triage urgency', 'P_URGENT': 'Record manual-review disposition', 'P_CREDIT': 'Assess latest credit status', 'P_FULFILL': 'Record fulfillment disposition', 'P_HOLD': 'Record finance-review disposition'}[rid], evidence=evidence('S01', 'S03', 'S04'),
                             edges=[dict(to=dest, condition=condition, kind=edgekind,
                                         payload='tenant, request ID, customer ID, urgency, latest credit status',
                                         receiver=actors[dest]) for dest, condition, edgekind in edges]))
    for dim, items in [('stakeholder', sorted(set(actors.values()))),
                       ('variant', ['shared', 'standard', 'urgent']), ('exception', ['urgent', 'denied-or-missing'])]:
        for index, value in enumerate(items):
            steps = [v[0] for v in specs if (v[2] == value if dim == 'stakeholder' else v[5] == value if dim == 'variant'
                                            else any(e[1] == value and e[2] == 'exception' for e in v[6]))]
            values.append(record(f'COV_{dim}_{index}', 'coverage', status='covered', dimension=dim, value=value,
                                 critical=True, steps=steps, owner='operations', evidence=evidence('S03', 'S04', 'S10')))
    # The proposed map retains all terminal responsibilities and changes the triage execution.
    future_actors = {v[0]: ('routing-service' if v[0] in {'P_TRIAGE', 'P_CREDIT'} else v[2]) for v in specs}
    for current in [v for v in values if v['type'] == 'process']:
        future = copy.deepcopy(current)
        future.update(id=current['id'].replace('P_', 'F_'), view='proposed', baseline=[current['id']],
                      actor=future_actors[current['id']], evidence=evidence('S03', 'S07', 'S10'))
        if current['id'] in {'P_TRIAGE', 'P_CREDIT'}:
            future['system'] = 'local-sqlite-router'
        for e in future['edges']:
            e['receiver'] = future_actors[e['to']]
            e['to'] = e['to'].replace('P_', 'F_')
        values.append(future)
    for rid, schema, table, grain, keys in [
        ('D_REQUESTS', 'intake', 'requests', 'One request per tenant/request', ['tenant', 'request_id']),
        ('D_CUSTOMERS', 'crm', 'customers', 'One customer per tenant/customer', ['tenant', 'customer_id']),
        ('D_APPROVALS', 'finance', 'approvals', 'One decision event per tenant/request/sequence', ['tenant', 'request_id', 'decision_seq']),
        ('D_HANDOFFS', 'operations', 'handoffs', 'One handoff event per tenant/request/sequence', ['tenant', 'request_id', 'event_seq'])]:
        values.append(record(rid, 'data', environment='fixture', schema=schema, table=table, grain=grain, keys=keys,
                             refresh='Fixed synthetic export; models daily refresh; capture a new version before reuse',
                             evidence=evidence('S05', 'S08', 'SRC_SETUP'), depends_on=['CL_KEYS']))
    for criterion, text in CRITERIA.items():
        values.append(record('REQ_' + criterion.upper(), 'requirement', acceptance=text, critical=True,
                             process=['P_TRIAGE', 'P_CREDIT'], claims=['CL_KEYS', 'CL_OWNER'], evidence=evidence('S10')))
    reqs = ['REQ_' + key.upper() for key in CRITERIA]
    values.append(record('DEC_CODE', 'decision', requirements=reqs,
                         alternatives=['Deterministic SQL joins and explicit routing rules', 'LLM selects joins and routes at runtime', 'Manual routing with a checklist'],
                         rationale='Structured identity and policy require exact reproducible behavior; an LLM helps discovery but no runtime inference is needed',
                         evidence=evidence('S03', 'S05', 'S07', 'S10')))
    values.append(record('COMP_ROUTER', 'component', decisions=['DEC_CODE'], process=['F_TRIAGE', 'F_CREDIT'],
                         method='code', inputs=['versioned synthetic four-schema export'], outputs=['one tenant-scoped routing disposition per request'],
                         tools=['Python standard library sqlite3'], state='Ephemeral SQLite for execution; durable project records for evidence',
                         failure='Nonzero criterion test blocks release; missing approval routes finance review and is detected against expectations',
                         artifact='examples/order-triage/execute.py and versioned SQL',
                         evidence=evidence('SRC_RUNNER', 'SRC_EXPECTED', 'SRC_NAIVE'), depends_on=[]))
    concern_detail = {
        'scope': ('S10', 'The sponsor limits acceptance to the four-request routing fixture'),
        'execution': ('SRC_RUNNER', 'Local Python and SQLite execute real read-only queries against synthetic in-memory inputs'),
        'tools/data': ('S07', 'Only supplied local synthetic data and SQLite/Python are authorized'),
        'state': ('SRC_REHEARSAL', 'Canonical project history, sources and releases persist on the local filesystem; SQLite execution is ephemeral'),
        'context': ('SRC_REHEARSAL', 'Resume from saved project; curated claim statuses and source locators are exercised'),
        'recovery': ('S09', 'Bounded fault injection and original-input restoration, with fresh verification before closure'),
        'evaluation': ('SRC_EXPECTED', 'Separate predefined cardinality, tenant isolation and routing expectations'),
        'operations': ('S08', 'Operating handoff is explicitly a local exercise; real hosting and monitoring remain separate'),
    }
    for category in sorted(CONCERNS):
        source, rationale = concern_detail[category]
        values.append(record('CON_' + category.replace('/', '_'), 'concern', category=category,
                             disposition='implemented', critical=True, rationale=rationale,
                             reference=source + ': bounded exercise implementation', evidence=evidence(source)))
    values.append(record('HANDOFF', 'handoff', runtime='Local Python 3.10+ and SQLite with window functions',
                         artifact='examples/order-triage/execute.py; reproduce via rehearse.py', environment='fixture',
                         owner='operations', prerequisites=['Python with sqlite3', 'Captured fixture and expected outcomes'],
                         authorization=AUTHORITY, remaining_steps=['Select and authorize real runtime', 'Validate real stakeholders, schema, volume and input freshness',
                           'Implement identity/access controls, deployment integration, monitoring and service objectives before real deployment'],
                         evidence=evidence('S07', 'S08', 'S10')))
    r.put(values)
    for view in ['current', 'proposed']:
        r.check(view + ' map', w.process_check(p.read(), view)['errors'], [])
    r.check('architecture', w.architecture_check(p.read())['errors'], [])
    naive = r.query('Q_NAIVE', 'naive.sql')
    r.check('naive join cardinality demonstrates defect', len(naive['rows']), 13)
    comp = copy.deepcopy(p.read()['records']['COMP_ROUTER'])
    comp['depends_on'] = ['Q_NAIVE']
    r.put([comp])
    r.evaluate('EV_NAIVE', 'cardinality', 'naive.sql')
    r.check('failed cardinality preserved', p.read()['records']['EV_NAIVE']['status'], 'fail')
    r.reject('failed design cannot release', lambda: w.create_release(p, 'REL_BAD', 'HANDOFF', ASOF, 'fixture', AUTHORITY, r.revision(), ACTOR))
    oldquery = copy.deepcopy(p.read()['records']['Q_NAIVE'])
    oldquery['status'] = 'archived'
    r.put([oldquery])
    corrected = r.query('Q_ROUTES', 'routes.sql')
    r.check('corrected join cardinality', len(corrected['rows']), 4)
    comp = copy.deepcopy(p.read()['records']['COMP_ROUTER'])
    comp.update(depends_on=['Q_ROUTES'], evidence=evidence('SRC_RUNNER', 'SRC_EXPECTED', 'SRC_SQL'))
    r.put([comp])
    for criterion in CRITERIA:
        r.evaluate('EV_' + criterion.upper(), criterion)
    r.check('ready for bounded simulation', w.readiness(p.read(), ASOF, 'fixture', 'HANDOFF')['errors'], [])
    r.run('create REL1', lambda: w.create_release(p, 'REL1', 'HANDOFF', ASOF, 'fixture', AUTHORITY, r.revision(), ACTOR))
    r.run('activate REL1 simulation', lambda: w.activate(p, 'REL1', ASOF, 'fixture', 'Three actual fixture criteria pass', r.revision(), ACTOR))
    snapshot_hash = p.read()['releases']['REL1']['snapshot_hash']
    r.evaluate('EV_OUTAGE', 'routing', fault='drop-approvals')
    r.check('later failure blocks readiness', w.readiness(p.read(), ASOF, 'fixture', 'HANDOFF')['status'], 'fail')
    incident = record('INC_FEED', 'incident', status='open', release='REL1', affected=['COMP_ROUTER', 'REQ_ROUTING'],
                      environment='fixture', symptom='Missing approvals caused fulfillment routes to become finance-review',
                      diagnosis='Injected in-memory loss of approval rows', action='Restore original synthetic input and rerun unchanged criterion',
                      authority=AUTHORITY, recovery_criterion=CRITERIA['routing'],
                      follow_up='Before real deployment, test feed availability/freshness and monitoring with its owner', opened_on=ASOF,
                      evidence=evidence('S09', 'RESULT_EV_OUTAGE'))
    r.put([incident])
    r.evaluate('EV_FAILED_RECOVERY', 'routing', fault='drop-approvals')
    r.reject('failed recovery stays open', lambda: w.close_incident(p, 'INC_FEED', 'EV_FAILED_RECOVERY', ASOF, r.revision(), ACTOR))
    r.check('incident remains open', p.read()['records']['INC_FEED']['status'], 'open')
    r.evaluate('EV_RECOVERED', 'routing')
    r.run('close verified incident', lambda: w.close_incident(p, 'INC_FEED', 'EV_RECOVERED', ASOF, r.revision(), ACTOR))
    r.check('incident closed with fresh evidence', p.read()['records']['INC_FEED']['verification'], 'EV_RECOVERED')
    r.check('readiness restored', w.readiness(p.read(), ASOF, 'fixture', 'HANDOFF')['errors'], [])
    r.check('snapshot unchanged through incident', p.read()['releases']['REL1']['snapshot_hash'], snapshot_hash)
    r.run('create recovered REL2', lambda: w.create_release(p, 'REL2', 'HANDOFF', ASOF, 'fixture', AUTHORITY, r.revision(), ACTOR))
    r.run('activate recovered REL2', lambda: w.activate(p, 'REL2', ASOF, 'fixture', 'Fresh recovery succeeded', r.revision(), ACTOR))
    r.run('save handoff checkpoint', lambda: p.checkpoint(dict(current_task='Bounded simulation complete',
        completed=['Ten-source reconciliation', 'Current/proposed map', 'Actual query and three criterion runs', 'Verified incident recovery'],
        unresolved=['Real deployment, input feed controls and field validation are outside this exercise'],
        next_action='Review operating handoff; validate real inputs and authorization before adapting for production',
        relevant_ids=['HANDOFF', 'INC_FEED', 'Q_ROUTES', 'COMP_ROUTER'], stage='operate'), r.revision(), ACTOR))
    r.check('full project audit', p.audit()['status'], 'pass')
    for view in ['current', 'proposed']:
        (r.output / (view + '-map.md')).write_text(w.render(p.read(), ASOF, view))
    (r.output / 'resume-context.json').write_text(json.dumps(context(p.read(), 'urgent Q_ROUTES HANDOFF', ASOF), indent=2) + '\n')
    # Save an audited clean handoff copy before deliberately invalidating current state.
    import shutil
    shutil.copytree(r.output / 'project', r.output / 'ready-project')
    change = copy.deepcopy(p.read()['records']['D_APPROVALS'])
    change['refresh'] = 'Synthetic changed refresh contract; requires fresh query execution and reevaluation'
    r.put([change])
    changed = impact(p.read(), 'D_APPROVALS')
    r.check('data change reaches query and implementation', {'Q_ROUTES', 'COMP_ROUTER'} <= set(changed['affected']), True)
    r.reject('changed input blocks old rollback', lambda: w.activate(p, 'REL1', ASOF, 'fixture', 'Adversarial stale rollback attempt', r.revision(), ACTOR, rollback=True))
    future = (DATE + timedelta(days=31)).isoformat()
    stale = context(p.read(), 'CL_OWNER', future)
    r.check('expired knowledge exposed on recall', any('CL_OWNER' in v and 'stale' in v for v in stale['warnings']), True)
    r.check('changed project audit', p.audit()['status'], 'pass')
    (r.output / 'change-impact.json').write_text(json.dumps(changed, indent=2) + '\n')
    summary = dict(synthetic=True, deployment_mode='local-simulation', as_of=ASOF,
                   checks=len(r.checks), failed=[c['name'] for c in r.checks if not c['passed']],
                   naive_rows=len(naive['rows']), corrected_rows=len(corrected['rows']),
                   ready_project='ready-project', adversarial_changed_project='project',
                   incident='INC_FEED closed using EV_RECOVERED', final_release='REL2',
                   limits=['Not real stakeholder research', 'Not a production deployment', 'No model-provider performance benchmark',
                           'Fixed four-request dataset does not certify other schemas or policy variants'])
    (r.output / 'report.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(Rehearsal(args.output))


if __name__ == '__main__':
    main()
