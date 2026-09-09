"""Small structural unit fixture. Not a real deployment or stakeholder study."""
import json
import uuid
from datetime import datetime, timezone
from agent_architect.core import Project
from agent_architect.schema import CONCERNS
from agent_architect import workflow as w

DATE = '2026-09-09'
CRITERION = 'Each request has exactly one decision'


def record(rid, record_type, **fields):
    return dict(id=rid, type=record_type, title=rid, description='Synthetic unit fixture', status='active') | fields


def edge(to, condition='always', kind='normal', receiver='operations', payload='request'):
    return dict(to=to, condition=condition, kind=kind, receiver=receiver, payload=payload)


def revision(p):
    return p.read()['revision']


def capture(p, rid, content, kind='document', environment='test', date=DATE):
    return p.source(rid, rid, content, kind, 'synthetic fixture ' + rid, date, environment, revision(p))


def run_result(p, rid='EV1', observed=None, expected=None, exit_code=0, environment='test', run_on=DATE,
               valid_until='2026-10-09', criterion=CRITERION, targets=None):
    stamp=datetime.now(timezone.utc).replace(year=int(run_on[:4]),month=int(run_on[5:7]),day=int(run_on[8:]))
    result = dict(environment=environment, run_on=run_on, run_id=str(uuid.uuid4()), run_at=stamp.isoformat(), command='synthetic unit assertion', exit_code=exit_code,
                  criterion=criterion, target_hashes=w.fingerprints(p.read()['records'], ['REQ','COMP'] if targets is None else targets), brief_hash=w.brief_hash(p.read()),
                  expected={'decisions': 1} if expected is None else expected,
                  observed={'decisions': 1} if observed is None else observed)
    capture(p, 'RESULT_' + rid, json.dumps(result).encode(), 'query-result', environment, max(DATE, run_on))
    return w.evaluate(p, dict(id=rid, title=rid, description='Synthetic predicate evidence',
                             targets=['REQ', 'COMP'] if targets is None else targets,
                             result_source='RESULT_' + rid, valid_until=valid_until, criterion=criterion), revision(p))


def ready_project(path, evaluation=True):
    p = Project(path)
    p.init('Synthetic request decision', 'Request arrival through disposition', 'operations')
    capture(p, 'S1', b'Synthetic observation: operations records one decision per request.\n', 'observation')
    evidence = [dict(source='S1', locator='line 1')]
    values = [record('C1', 'claim', status='verified', assertion='Operations records a decision', applicability='test workflow',
                     verified_on=DATE, review_due='2026-10-09', verification='Synthetic unit observation S1', evidence=evidence)]
    for view, prefix in [('current', 'P'), ('proposed', 'F')]:
        for suffix, kind, edges in [('1', 'start', [edge(prefix+'2')]),
                                    ('2', 'decision', [edge(prefix+'3', 'accepted'), edge(prefix+'4', 'rejected', 'exception')]),
                                    ('3', 'end', []), ('4', 'end', [])]:
            values.append(record(prefix+suffix, 'process', view=view, kind=kind, actor='operations', system='requests', boundary='internal',
                                 inputs=['request'], outputs=['decision'], variant='standard', edges=edges,
                                 evidence=evidence if view == 'current' else [], baseline=['P'+suffix] if view == 'proposed' else []))
    for dim, value in [('stakeholder', 'operations'), ('variant', 'standard'), ('exception', 'rejected')]:
        values.append(record('COV_'+dim, 'coverage', status='covered', dimension=dim, value=value, critical=True,
                             steps=['P2'], owner='operations', evidence=evidence))
    values += [record('REQ', 'requirement', acceptance=CRITERION, critical=True, process=['P2'], claims=['C1']),
               record('DEC', 'decision', requirements=['REQ'], alternatives=['manual entry', 'code validation'], rationale='Exact cardinality is deterministic'),
               record('COMP', 'component', decisions=['DEC'], process=['F2'], method='code', inputs=['request'], outputs=['decision'],
                      tools=['Python'], state='request store', failure='quarantine missing decision', artifact='synthetic fixture'),
               record('HANDOFF', 'handoff', runtime='Python local simulation', artifact='synthetic fixture', environment='test', owner='operations',
                      prerequisites=['local interpreter'], authorization='unit simulation only', remaining_steps=['Actual deployment outside fixture'])]
    for category in sorted(CONCERNS):
        values.append(record('CON_'+category.replace('/', '_'), 'concern', category=category, disposition='platform-provided', critical=True,
                             rationale='Synthetic unit fixture only', reference='S1 synthetic observation', evidence=evidence))
    p.put(values, revision(p))
    if evaluation:
        run_result(p)
    return p


def release(p, rid='REL1'):
    return w.create_release(p, rid, 'HANDOFF', DATE, 'test', 'Synthetic local simulation authority', revision(p))


def query_result(p, rid, result_id='QUERY_RESULT', rows=None):
    value=dict(environment='test',run_on=DATE,command='Synthetic query protocol fixture',exit_code=0,
               query_fingerprint=w.query_fingerprint(p.read(),rid),rows=[[1]] if rows is None else rows)
    capture(p,result_id,json.dumps(value).encode(),'query-result')
    return w.bind_query(p,rid,result_id,revision(p))


def incident(p):
    return record('INC1', 'incident', status='open', release='REL1', affected=['COMP'], environment='test',
                  symptom='Synthetic outage', diagnosis='unknown', action='unknown', authority='bounded fixture recovery',
                  recovery_criterion='Service recovered', follow_up='unknown', opened_on=DATE)
