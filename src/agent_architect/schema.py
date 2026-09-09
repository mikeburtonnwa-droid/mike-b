"""Declarative workflow fields; behavioral checks live in workflow.py."""
SPECS = {
    'process': dict(view=str, kind=str, actor=str, system=str, boundary=str,
                    inputs=list, outputs=list, variant=str, edges=list, baseline=list),
    'coverage': dict(dimension=str, value=str, critical=bool, steps=list, gap=str, owner=str),
    'data': dict(environment=str, schema=str, table=str, grain=str, keys=list, refresh=str),
    'query': dict(environment=str, sql=str, assets=list, parameters=dict,
                  join_assumptions=str, executed_on=str, result_source=str, execution_hash=str, limitations=str),
    'requirement': dict(acceptance=str, critical=bool, process=list, claims=list),
    'decision': dict(requirements=list, alternatives=list, rationale=str),
    'component': dict(decisions=list, process=list, method=str, inputs=list, outputs=list,
                      tools=list, state=str, failure=str, artifact=str),
    'concern': dict(category=str, disposition=str, critical=bool, rationale=str, reference=str),
    'evaluation': dict(targets=list, environment=str, run_on=str, valid_until=str,
                       result_source=str, hashes=dict, criterion=str, brief_hash=str, recorded_revision=int,
                       run_id=str, run_at=str, result_hash=str),
    'handoff': dict(runtime=str, artifact=str, environment=str, owner=str, prerequisites=list,
                    authorization=str, remaining_steps=list),
    'incident': dict(release=str, affected=list, environment=str, symptom=str, diagnosis=str,
                     action=str, authority=str, recovery_criterion=str, verification=str,
                     follow_up=str, opened_on=str),
}
REQUIRED = {kind: list(fields) for kind, fields in SPECS.items()}
REQUIRED['process'].remove('baseline')
REQUIRED['coverage'].remove('gap')
for field in ('executed_on', 'result_source', 'execution_hash'):
    REQUIRED['query'].remove(field)
REQUIRED['incident'].remove('verification')
STATUSES = {kind: {'active', 'archived'} for kind in SPECS}
STATUSES.update(coverage={'covered', 'gap'}, query={'draft', 'executed', 'archived'},
                evaluation={'pass', 'fail'}, incident={'open', 'closed'})
# All semantic prerequisite fields feed provenance, impact and evaluation fingerprints.
REFS = {
    'process': {'baseline': {'process'}},
    'coverage': {'steps': {'process'}},
    'query': {'assets': {'data'}, 'result_source': {'source'}},
    'requirement': {'process': {'process'}, 'claims': {'claim'}},
    'decision': {'requirements': {'requirement'}},
    'component': {'decisions': {'decision'}, 'process': {'process'}},
    'evaluation': {'targets': {'requirement', 'component'}, 'result_source': {'source'}},
    'incident': {'affected': {'requirement', 'component'}, 'verification': {'evaluation'}},
}
CONCERNS = {'scope', 'execution', 'tools/data', 'state', 'context', 'recovery', 'evaluation', 'operations'}
