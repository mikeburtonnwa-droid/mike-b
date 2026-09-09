"""Process, architecture and consequential local-simulation transitions.

Checks expose structural gaps. They cannot establish stakeholder completeness,
evidence truth, or permission in an external runtime.
"""
import copy
import hashlib
import html
import json
import re
import uuid
from datetime import datetime, timezone
from .core import Invalid, closure, day, dependencies, digest, freshness, identifier, text
from .schema import CONCERNS, REFS


def run_time(value):
    text(value, 'run_at')
    try:
        result = datetime.fromisoformat(value[:-1]+'+00:00' if value.endswith('Z') else value)
    except ValueError as exc:
        raise Invalid('run_at must be an ISO timestamp with timezone') from exc
    if result.tzinfo is None:
        raise Invalid('run_at requires a timezone')
    return result.astimezone(timezone.utc)


def latest_runs(candidates):
    if not candidates:
        return []
    latest = max(run_time(r['run_at']) for r in candidates)
    return [r for r in candidates if run_time(r['run_at']) == latest]


def refs(record, field):
    value = record.get(field, [])
    return [value] if isinstance(value, str) else value


def validate_workflow_record(r):
    kind, rid = r['type'], r['id']
    for field in REFS.get(kind, {}):
        for ref in refs(r, field):
            identifier(ref)
    for field in ('inputs', 'outputs', 'keys', 'tools', 'alternatives', 'prerequisites', 'remaining_steps'):
        for item in r.get(field, []):
            text(item, f'{rid}.{field}')
    for field in ('executed_on', 'run_on', 'valid_until', 'opened_on'):
        if field in r:
            day(r[field])
    if kind == 'process':
        if r['view'] not in {'current', 'proposed'} or r['kind'] not in {'start', 'activity', 'decision', 'end'}:
            raise Invalid(f'{rid}: invalid process view/kind')
        for edge in r['edges']:
            if not isinstance(edge, dict) or set(edge) != {'to', 'condition', 'kind', 'payload', 'receiver'}:
                raise Invalid(f'{rid}: edge requires to, condition, kind, payload, receiver')
            identifier(edge['to'])
            for field in ('condition', 'payload', 'receiver'):
                text(edge[field], f'{rid}.edge.{field}')
            text(edge['kind'], f'{rid}.edge.kind')
            if edge['kind'] not in {'normal', 'exception', 'handoff'}:
                raise Invalid(f'{rid}: invalid edge kind')
    if kind == 'coverage':
        if r['dimension'] not in {'stakeholder', 'variant', 'exception'}:
            raise Invalid(f'{rid}: invalid coverage dimension')
        if r['status'] == 'gap':
            text(r.get('gap'), f'{rid}.gap')
        elif not r.get('evidence') or not r['steps']:
            raise Invalid(f'{rid}: covered dimension requires evidence and process steps')
    if kind == 'data' and not r['keys']:
        raise Invalid(f'{rid}: name keys, or explicitly use unknown pending discovery')
    if kind == 'query':
        execution_fields = ('result_source', 'executed_on', 'execution_hash')
        if any(f in r for f in execution_fields) and not all(f in r for f in execution_fields):
            raise Invalid(f'{rid}: execution metadata must be complete')
        if not r['assets']:
            raise Invalid(f'{rid}: query requires source assets')
        if r['status'] == 'executed' and not all(r.get(f) for f in ('result_source', 'executed_on', 'execution_hash')):
            raise Invalid(f'{rid}: executed query requires bound execution date, result source and hash')
        if r['status'] == 'draft' and any(f in r for f in ('result_source', 'executed_on', 'execution_hash')):
            raise Invalid(f'{rid}: draft query cannot claim execution evidence')
        if 'execution_hash' in r and not re.fullmatch(r'[a-f0-9]{64}', r['execution_hash']):
            raise Invalid(f'{rid}: invalid query execution fingerprint')
    if kind == 'requirement' and (not r['process'] or not r['claims']):
        raise Invalid(f'{rid}: requirement requires process and claim traceability')
    if kind == 'decision' and (not r['requirements'] or len(r['alternatives']) < 2):
        raise Invalid(f'{rid}: decision requires requirements and at least two alternatives')
    if kind == 'component':
        if r['method'] not in {'code', 'model', 'human', 'hybrid'}:
            raise Invalid(f'{rid}: invalid execution method')
        if not r['decisions'] or not r['process'] or not r['inputs'] or not r['outputs']:
            raise Invalid(f'{rid}: component requires decisions, process, inputs and outputs')
    if kind == 'concern':
        if r['category'] not in CONCERNS or r['disposition'] not in {'implemented', 'platform-provided', 'deferred', 'not-applicable'}:
            raise Invalid(f'{rid}: invalid architecture concern/disposition')
        if r['disposition'] in {'implemented', 'platform-provided'} and not r.get('evidence'):
            raise Invalid(f'{rid}: implementation/platform disposition requires evidence')
    if kind == 'evaluation':
        try:
            if str(uuid.UUID(r['run_id'])) != r['run_id']:
                raise ValueError('Noncanonical UUID')
        except ValueError as exc:
            raise Invalid(f'{rid}: run_id must be a UUID generated for the executed case') from exc
        if run_time(r['run_at']).date() != day(r['run_on']):
            raise Invalid(f'{rid}: UTC execution timestamp date differs from run_on')
        if not re.fullmatch(r'[a-f0-9]{64}', r['result_hash']):
            raise Invalid(f'{rid}: invalid result hash')
        if not r['targets'] or not r['hashes'] or day(r['valid_until']) < day(r['run_on']):
            raise Invalid(f'{rid}: invalid evaluation targets, hashes or dates')
        for key, value in r['hashes'].items():
            identifier(key)
            if not isinstance(value, str) or not re.fullmatch(r'[a-f0-9]{64}', value):
                raise Invalid(f'{rid}: invalid dependency fingerprint')
        if not re.fullmatch(r'[a-f0-9]{64}', r['brief_hash']) or r['recorded_revision'] < 1:
            raise Invalid(f'{rid}: invalid brief fingerprint or recorded revision')
    if kind == 'incident':
        identifier(r['release'])
        if not r['affected']:
            raise Invalid(f'{rid}: incident needs affected requirements/components')
        if r['status'] == 'closed' and not r.get('verification'):
            raise Invalid(f'{rid}: closed incident needs verification')


def validate_workflow_state(state):
    records = state['records']
    for r in records.values():
        rid, kind = r['id'], r['type']
        for field, allowed in REFS.get(kind, {}).items():
            for ref in refs(r, field):
                if ref not in records or records[ref]['type'] not in allowed:
                    raise Invalid(f'{rid}.{field}: {ref} must reference {sorted(allowed)}')
        if kind == 'process':
            for edge in r['edges']:
                dest = records.get(edge['to'], {})
                if dest.get('type') != 'process' or dest['view'] != r['view']:
                    raise Invalid(f'{rid}: edge must reference process in same view')
            if any(records[x]['view'] != 'current' for x in r.get('baseline', [])):
                raise Invalid(f'{rid}: baseline must reference current-state steps')
        if kind == 'query':
            if any(records[x]['environment'] != r['environment'] for x in r['assets']):
                raise Invalid(f'{rid}: query/asset environments differ')
            if r.get('result_source') and records[r['result_source']]['environment'] != r['environment']:
                raise Invalid(f'{rid}: query/result environments differ')
            if r.get('result_source') and (records[r['result_source']]['kind'] != 'query-result' or day(r['executed_on']) > day(records[r['result_source']]['captured_on'])):
                raise Invalid(f'{rid}: query requires result source captured no earlier than execution')
        if kind == 'incident':
            release = state.get('releases', {}).get(r['release'])
            if not release or release['environment'] != r['environment']:
                raise Invalid(f'{rid}: incident needs an existing release in its environment')
            if any(x not in release['snapshot']['records'] for x in r['affected']):
                raise Invalid(f'{rid}: affected element absent from pinned release')
    categories = [r['category'] for r in records.values() if r['type'] == 'concern' and r['status'] == 'active']
    if len(categories) != len(set(categories)):
        raise Invalid('Only one active disposition per architecture concern')
    evals = [r for r in records.values() if r['type'] == 'evaluation']
    for field in ('run_id', 'result_hash'):
        if len({r[field] for r in evals}) != len(evals):
            raise Invalid('Evaluation runs cannot be re-imported through duplicate identity/content')
    for key, release in state.get('releases', {}).items():
        identifier(key)
        if key != release.get('id') or digest(release['snapshot']) != release['snapshot_hash']:
            raise Invalid('Release snapshot integrity failure')
    active = state.get('active_release')
    if active and active not in state.get('releases', {}):
        raise Invalid('Active simulation points to missing release')


def active(state, kind):
    return [r for r in state['records'].values() if r['type'] == kind and r['status'] not in {'archived', 'superseded'}]


def unknown(value):
    return str(value).strip().lower() in {'unknown', 'tbd', '?', 'unresolved'}


def process_check(state, view='current'):
    if view not in {'current', 'proposed'}:
        raise Invalid('View must be current or proposed')
    nodes = {r['id']: r for r in active(state, 'process') if r['view'] == view}
    errors = []
    starts = {k for k, r in nodes.items() if r['kind'] == 'start'}
    ends = {k for k, r in nodes.items() if r['kind'] == 'end'}
    if not starts or not ends:
        errors.append(f'{view}: map requires start and end nodes')
    graph = {k: {e['to'] for e in r['edges']} for k, r in nodes.items()}
    for rid, r in nodes.items():
        if any(unknown(r[f]) for f in ('actor', 'system', 'boundary', 'variant')):
            errors.append(f'{rid}: unknown actor/system/boundary/variant')
        if not r['inputs'] or not r['outputs'] or any(unknown(x) for x in r['inputs'] + r['outputs']):
            errors.append(f'{rid}: unresolved inputs/outputs')
        if r['kind'] != 'end' and not r['edges']:
            errors.append(f'{rid}: nonterminal dead end')
        if r['kind'] == 'end' and r['edges']:
            errors.append(f'{rid}: end node has outgoing paths')
        if r['kind'] == 'decision' and (len(r['edges']) < 2 or len({e['condition'] for e in r['edges']}) != len(r['edges'])):
            errors.append(f'{rid}: decision needs distinct labeled alternatives')
        if view == 'current' and not any(state['records'][x]['type'] == 'source' for x in closure(state['records'], [rid])):
            errors.append(f'{rid}: current step lacks source evidence')
        if view == 'proposed' and not r.get('baseline'):
            errors.append(f'{rid}: proposed step lacks current-state baseline')
        for e in r['edges']:
            if e['to'] not in nodes:
                errors.append(f'{rid}: path to inactive step {e["to"]}')
                continue
            dest = nodes[e['to']]
            if unknown(e['condition']) or unknown(e['payload']) or unknown(e['receiver']):
                errors.append(f'{rid}->{e["to"]}: unresolved edge metadata')
            crossing = (r['actor'], r['system'], r['boundary']) != (dest['actor'], dest['system'], dest['boundary'])
            if crossing and (e['kind'] not in {'handoff', 'exception'} or e['receiver'] != dest['actor'] or e['payload'].strip().lower() == 'none'):
                errors.append(f'{rid}->{e["to"]}: boundary/owner change requires payload and receiving actor')
    def reachable(roots, edges):
        found, todo = set(), list(roots)
        while todo:
            node = todo.pop()
            if node not in found:
                found.add(node)
                todo.extend(edges.get(node, set()) - found)
        return found
    for rid in sorted(set(nodes) - reachable(starts, graph)):
        errors.append(f'{rid}: unreachable from a start')
    reverse = {k: {x for x, dest in graph.items() if k in dest} for k in nodes}
    for rid in sorted(set(nodes) - reachable(ends, reverse)):
        errors.append(f'{rid}: no route to an end')
    if view == 'current':
        cover = active(state, 'coverage')
        for dim in ('stakeholder', 'variant', 'exception'):
            if not any(r['dimension'] == dim for r in cover):
                errors.append(f'coverage: no declared {dim} dimension')
        for r in cover:
            if r['status'] == 'gap':
                errors.append(f'{r["id"]}: coverage gap: {r["gap"]}')
            if r['status'] == 'covered' and any(x not in nodes for x in r['steps']):
                errors.append(f'{r["id"]}: covered steps must be active current-state steps')
        for dim, values in [('stakeholder', {r['actor'] for r in nodes.values()}), ('variant', {r['variant'] for r in nodes.values()})]:
            for value in sorted(values - {'none', 'unknown'}):
                covered = [c for c in cover if c['dimension'] == dim and c['value'] == value and c['status'] == 'covered'
                           and any(x in nodes and nodes[x]['actor' if dim == 'stakeholder' else 'variant'] == value for x in c['steps'])]
                if not covered:
                    errors.append(f'coverage: {dim} {value} lacks matching current-step evidence')
        for rid, r in nodes.items():
            for e in r['edges']:
                if e['kind'] == 'exception' and not any(c['dimension'] == 'exception' and c['value'] == e['condition']
                    and c['status'] == 'covered' and rid in c['steps'] for c in cover):
                    errors.append(f'coverage: exception {rid}->{e["to"]} ({e["condition"]}) lacks evidence')
    return dict(status='pass' if not errors else 'fail', view=view, errors=errors,
                limit='Checks declared structure and coverage, not completeness of the real process.')


def architecture_check(state):
    errors = []
    requirements, decisions, components = (active(state, kind) for kind in ('requirement', 'decision', 'component'))
    if not requirements or not components:
        errors.append('Architecture requires requirements and components')
    for req in requirements:
        choices = {r['id'] for r in decisions if req['id'] in r['requirements']}
        if not choices or not any(choices.intersection(c['decisions']) for c in components):
            errors.append(f'{req["id"]}: no decision-to-component trace')
        if any(state['records'][x]['view'] != 'current' for x in req['process']):
            errors.append(f'{req["id"]}: requirements must trace current-state steps')
    for c in components:
        if any(state['records'][x]['view'] != 'proposed' for x in c['process']):
            errors.append(f'{c["id"]}: components must trace proposed steps')
        if any(unknown(c[f]) for f in ('artifact', 'state', 'failure')):
            errors.append(f'{c["id"]}: unresolved implementation/state/failure behavior')
    concerns = active(state, 'concern')
    for missing in sorted(CONCERNS - {r['category'] for r in concerns}):
        errors.append(f'concern: missing {missing} disposition')
    for r in concerns:
        if r['critical'] and r['disposition'] == 'deferred':
            errors.append(f'{r["id"]}: critical concern deferred')
    return dict(status='pass' if not errors else 'fail', errors=errors)


def fingerprints(records, roots):
    return {rid: digest(records[rid]) for rid in sorted(closure(records, roots))}


def brief_hash(state):
    return digest({k: state.get(k) for k in ('title', 'scope', 'owner', 'brief_evidence', 'brief_rationale')})


def query_fingerprint(state, rid):
    r = state['records'].get(rid, {})
    if r.get('type') != 'query':
        raise Invalid('Query fingerprint requires a query record')
    definition = {k:v for k,v in r.items() if k not in {'status','executed_on','result_source','execution_hash'}}
    return dict(query=rid, definition_hash=digest(definition),
                dependencies=fingerprints(state['records'], dependencies(definition)))


def bind_query(project, rid, result_id, expected, actor='local-user'):
    identifier(rid)
    identifier(result_id)
    def update(state):
        q, source = state['records'].get(rid, {}), state['records'].get(result_id, {})
        if q.get('type') != 'query' or q['status'] != 'draft' or source.get('type') != 'source' or source['kind'] != 'query-result':
            raise Invalid('Query binding requires a draft query and captured query-result source')
        result = json.loads((project.path/source['blob']).read_text())
        fields = {'environment','run_on','command','exit_code','query_fingerprint','rows'}
        if not isinstance(result, dict) or set(result) != fields or type(result['exit_code']) is not int or result['exit_code'] != 0 or not isinstance(result['rows'], list):
            raise Invalid('Query result requires environment, run_on, command, successful integer exit_code, query_fingerprint, rows list')
        text(result['command'], 'query execution command')
        if result['environment'] != q['environment'] or result['query_fingerprint'] != query_fingerprint(state, rid):
            raise Invalid('Query result environment or executed definition/dependencies differ')
        q.update(status='executed', executed_on=result['run_on'], result_source=result_id,
                 execution_hash=digest(result['query_fingerprint']))
    return project.mutate('bind executed query ' + rid, update, expected, actor)


def applicable(state, evaluation, as_of, environment):
    day(as_of)
    reasons = []
    if evaluation['status'] != 'pass':
        reasons.append('result failed')
    if evaluation['environment'] != environment:
        reasons.append('environment differs')
    if evaluation['brief_hash'] != brief_hash(state):
        reasons.append('project brief changed')
    if not day(evaluation['run_on']) <= day(as_of) <= day(evaluation['valid_until']):
        reasons.append('future-dated or expired evaluation')
    roots = evaluation['targets'] + [evaluation['result_source']]
    if fingerprints(state['records'], roots) != evaluation['hashes']:
        reasons.append('evaluated dependencies changed')
    relevant = closure(state['records'], roots) | {e['source'] for e in state.get('brief_evidence', [])}
    if any(state['records'][x]['type'] == 'source' and day(state['records'][x]['captured_on']) > day(as_of) for x in relevant):
        reasons.append('evidence captured after as-of date')
    return reasons


def evaluate(project, data, expected, actor='local-user'):
    fields = {'id', 'title', 'description', 'targets', 'result_source', 'valid_until', 'criterion'}
    if not isinstance(data, dict) or set(data) != fields:
        raise Invalid(f'Evaluation input requires exactly {sorted(fields)}')
    identifier(data['id'])
    identifier(data['result_source'])
    def update(state):
        if data['id'] in state['records'] or data['id'] in state['releases']:
            raise Invalid('Evaluation ID already exists; append a new run')
        source = state['records'].get(data['result_source'], {})
        if source.get('type') != 'source' or source['kind'] != 'query-result':
            raise Invalid('Evaluation requires a captured query-result source')
        result = json.loads((project.path / source['blob']).read_text())
        required = {'environment', 'run_on', 'expected', 'observed', 'command', 'exit_code', 'criterion', 'target_hashes', 'brief_hash', 'run_id', 'run_at'}
        if not isinstance(result, dict) or set(result) != required or type(result['exit_code']) is not int:
            raise Invalid('Result source requires environment, run_on, expected, observed, command, integer exit_code, criterion, target_hashes, brief_hash, run_id, run_at')
        text(result['command'], 'executed command or human observation procedure')
        if result['environment'] != source['environment'] or day(result['run_on']) > day(source['captured_on']):
            raise Invalid('Result environment/capture date mismatch')
        r = dict(data, type='evaluation', status='pass' if result['exit_code'] == 0 and digest(result['expected']) == digest(result['observed']) else 'fail',
                 environment=result['environment'], run_on=result['run_on'], hashes={}, brief_hash=brief_hash(state), recorded_revision=state['revision']+1,
                 run_id=result['run_id'], run_at=result['run_at'], result_hash=source['content_hash'])
        if not isinstance(r['targets'], list) or not r['targets']:
            raise Invalid('Evaluation targets must be a nonempty ID list')
        for rid in r['targets']:
            identifier(rid)
        if result['criterion'] != data['criterion'] or result['target_hashes'] != fingerprints(state['records'], r['targets']) or result['brief_hash'] != brief_hash(state):
            raise Invalid('Captured result criterion/dependency hashes do not match the evaluated targets')
        if any(ev['run_id'] == r['run_id'] or ev['result_hash'] == r['result_hash'] for ev in active(state,'evaluation')):
            raise Invalid('Execution evidence already evaluated; reuse its existing evaluation ID, not a new run order')
        r['hashes'] = fingerprints(state['records'], r['targets'] + [r['result_source']])
        state['records'][r['id']] = r
    receipt = project.mutate('evaluate ' + data['id'], update, expected, actor)
    # Read the exact committed envelope, not a later competing writer's HEAD.
    saved = project.envelope(receipt['commit'])['state']['records'][data['id']]
    return receipt | dict(evaluation=data['id'], outcome=saved['status'])


def readiness(state, as_of, environment, handoff_id):
    day(as_of)
    errors = []
    if any(unknown(state[f]) for f in ('title','scope','owner')):
        errors.append('Project brief title/scope/owner unresolved')
    for view in ('current', 'proposed'):
        errors.extend(process_check(state, view)['errors'])
    errors.extend(architecture_check(state)['errors'])
    records = state['records']
    handoff = records.get(handoff_id, {})
    if handoff.get('type') != 'handoff' or handoff.get('status') != 'active' or handoff.get('environment') != environment:
        errors.append('Active handoff in release environment required')
    elif any(unknown(handoff[f]) for f in ('runtime', 'artifact', 'owner', 'authorization')):
        errors.append('Handoff runtime/artifact/owner/authorization unresolved')
    critical = [r for r in active(state, 'requirement') if r['critical']]
    if not critical:
        errors.append('At least one critical acceptance requirement required')
    for r in active(state, 'issue'):
        if r['critical'] and r['status'] == 'open':
            errors.append(f'{r["id"]}: unresolved critical issue')
    for r in active(state, 'incident'):
        if r['status'] == 'open' and r['environment'] == environment:
            errors.append(f'{r["id"]}: open incident in release environment')
    # Pin all consequential design/process/data records, plus selected evaluations.
    roots = {r['id'] for r in records.values() if r['type'] in {'process', 'coverage', 'data', 'query', 'requirement', 'decision', 'component', 'concern'}
             and r['status'] not in {'archived', 'superseded'}}
    if handoff:
        roots.add(handoff_id)
    roots.update(e['source'] for e in state.get('brief_evidence', []))
    evaluations = []
    for req in critical:
        candidates = [r for r in active(state, 'evaluation') if req['id'] in r['targets'] and r['criterion'] == req['acceptance']
                      and r['environment'] == environment and r['brief_hash'] == brief_hash(state)
                      and fingerprints(records, r['targets']+[r['result_source']]) == r['hashes']]
        needed_components = {c['id'] for c in active(state, 'component')
                             if any(req['id'] in records[d]['requirements'] for d in c['decisions'])}
        candidates = [r for r in candidates if needed_components <= set(r['targets'])]
        latest = latest_runs(candidates)
        selected = max(latest,key=lambda r:r['recorded_revision']) if latest else None
        if not selected or any(applicable(state, r, as_of, environment) for r in latest):
            errors.append(f'{req["id"]}: no passing applicable evaluation of criterion and implementing components')
        else:
            evaluations.append(selected['id'])
            roots.add(selected['id'])
    pinned = closure(records, roots)
    for rid in sorted(pinned):
        r = records[rid]
        if r['status'] == 'archived':
            errors.append(f'{rid}: archived prerequisite')
        if r['type'] == 'claim' and (r['status'] != 'verified' or freshness(r, as_of) != 'current'):
            errors.append(f'{rid}: critical knowledge {r["status"]}, freshness={freshness(r, as_of)}')
        if r['type'] == 'source' and day(r['captured_on']) > day(as_of):
            errors.append(f'{rid}: future captured source')
        if r['type'] == 'data' and (any(unknown(r[f]) for f in ('grain', 'refresh', 'schema', 'table')) or any(unknown(x) for x in r['keys'])):
            errors.append(f'{rid}: data schema/table/grain/keys/refresh unknown')
        if r['type'] == 'data' and not any(records[x]['type'] == 'source' for x in closure(records, [rid])):
            errors.append(f'{rid}: data asset lacks captured provenance')
        if r['type'] == 'query' and (r['status'] != 'executed' or day(r['executed_on']) > day(as_of)):
            errors.append(f'{rid}: query not executed as of release')
        elif r['type'] == 'query' and digest(query_fingerprint(state, rid)) != r['execution_hash']:
            errors.append(f'{rid}: executed query dependencies changed')
    return dict(status='pass' if not errors else 'fail', errors=errors, evaluations=sorted(evaluations),
                critical_hashes={rid: digest(records[rid]) for rid in sorted(pinned)},
                deployment_mode='local-simulation', as_of=as_of, environment=environment,
                limit='Structural and captured evaluation evidence; no infrastructure deployment or proof of evidence truth.')


def create_release(project, rid, handoff, as_of, environment, authority, expected, actor='local-user'):
    identifier(rid)
    text(authority, 'release authority')
    def update(state):
        if rid in state['releases'] or rid in state['records']:
            raise Invalid('Release ID already exists')
        check = readiness(state, as_of, environment, handoff)
        if check['status'] != 'pass':
            raise Invalid('Release blocked: ' + '; '.join(check['errors']))
        # Snapshot only what is checked; excludes unrelated incidents/history containers.
        snapshot = {k: copy.deepcopy(v) for k, v in state.items() if k not in {'releases', 'active_release', 'activations', 'records', 'checkpoint'}}
        snapshot['records'] = {k: copy.deepcopy(state['records'][k]) for k in check['critical_hashes']}
        state['releases'][rid] = dict(id=rid, handoff=handoff, created_on=as_of, environment=environment, authority=authority,
                                     snapshot=snapshot, snapshot_hash=digest(snapshot), brief_hash=brief_hash(state), critical_hashes=check['critical_hashes'])
    return project.mutate('create local-simulation release ' + rid, update, expected, actor) | {'deployment_mode': 'local-simulation'}


def drift(state, rid):
    release = state['releases'].get(rid)
    if not release:
        raise Invalid('Unknown release')
    return dict(release=rid, changed=[key for key, value in release['critical_hashes'].items()
                                      if key not in state['records'] or digest(state['records'][key]) != value],
                brief_changed=brief_hash(state) != release['brief_hash'],
                consequential_added=sorted(r['id'] for r in state['records'].values() if r['id'] not in release['critical_hashes']
                    and r['type'] in {'process','coverage','data','query','requirement','decision','component','concern'} and r['status'] not in {'archived','superseded'}),
                unpinned=sorted(set(state['records']) - set(release['critical_hashes'])), deployment_mode='local-simulation')


def activate(project, rid, as_of, environment, reason, expected, actor='local-user', rollback=False):
    text(reason, 'activation/rollback reason')
    def update(state):
        release = state['releases'].get(rid)
        if not release or release['environment'] != environment or day(as_of) < day(release['created_on']):
            raise Invalid('Release/environment/date mismatch')
        project.check_sources(release['snapshot'])
        check = readiness(release['snapshot'], as_of, environment, release['handoff'])
        change = drift(state, rid)
        changed = change['changed'] + change['consequential_added'] + (['project brief'] if change['brief_changed'] else [])
        # Current critical gaps and incidents also invalidate an otherwise intact snapshot.
        live = readiness(state, as_of, environment, release['handoff'])
        if check['errors'] or changed or live['errors']:
            raise Invalid('Activation blocked: ' + '; '.join(check['errors'] + live['errors'] + ['changed ' + x for x in changed]))
        if rollback and not any(a['release'] == rid for a in state.get('activations', [])):
            raise Invalid('Rollback requires a previously activated simulation')
        previous = state['active_release']
        state['active_release'] = rid
        state.setdefault('activations', []).append(dict(release=rid, previous=previous, as_of=as_of, environment=environment,
                                                      action='rollback' if rollback else 'activate', reason=reason, actor=actor,
                                                      deployment_mode='local-simulation'))
    return project.mutate(('rollback' if rollback else 'activate') + ' local-simulation ' + rid, update, expected, actor) | {'deployment_mode': 'local-simulation'}


def close_incident(project, rid, evaluation_id, as_of, expected, actor='local-user'):
    def update(state):
        r, evaluation = state['records'].get(rid, {}), state['records'].get(evaluation_id, {})
        if r.get('type') != 'incident' or r['status'] != 'open' or evaluation.get('type') != 'evaluation':
            raise Invalid('Closure requires an open incident and evaluation')
        if applicable(state, evaluation, as_of, r['environment']) or day(evaluation['run_on']) < day(r['opened_on']):
            raise Invalid('Incident verification failed, expired, changed, premature or environment-mismatched')
        if not set(r['affected']) <= set(evaluation['targets']) or r['recovery_criterion'] != evaluation['criterion']:
            raise Invalid('Verification does not cover affected elements and recovery criterion')
        comparable = [ev for ev in active(state, 'evaluation') if ev['criterion'] == r['recovery_criterion'] and ev['environment'] == r['environment']
                      and set(r['affected']) <= set(ev['targets']) and ev['brief_hash'] == brief_hash(state)
                      and fingerprints(state['records'], ev['targets']+[ev['result_source']]) == ev['hashes']]
        latest = latest_runs(comparable)
        if evaluation_id not in {ev['id'] for ev in latest} or any(applicable(state,ev,as_of,r['environment']) for ev in latest):
            raise Invalid('Use the latest matching recovery evaluation; an earlier pass cannot hide a later result')
        if any(unknown(r[f]) for f in ('diagnosis', 'action', 'authority', 'follow_up')):
            raise Invalid('Incident requires diagnosis, action, authority and follow-up')
        r.update(status='closed', verification=evaluation_id)
    return project.mutate('close incident ' + rid, update, expected, actor)


def render(state, as_of, view='current'):
    """Deterministic, disposable Markdown view, never canonical evidence."""
    day(as_of)
    def safe(value):
        return html.escape(str(value), quote=True).replace('|', '&#124;').replace('\n', ' ')
    nodes = [r for r in active(state, 'process') if r['view'] == view]
    out = [f'# {safe(state["title"])} — {view} state', '',
           f'Derived from revision {state["revision"]}; as of {as_of}. Deployment mode: **local-simulation**.', '',
           '```mermaid', 'flowchart TD']
    for r in sorted(nodes, key=lambda r: r['id']):
        label = safe(f'{r["id"]}: {r["title"]} / {r["actor"]}')
        out.append(f'  {r["id"]}["{label}"]')
    for r in sorted(nodes, key=lambda r: r['id']):
        for e in r['edges']:
            out.append(f'  {r["id"]} -->|"{safe(e["kind"] + ": " + e["condition"])}"| {e["to"]}')
    out += ['```', '', '| ID / variant | Actor / system / boundary | Inputs → outputs | Evidence / prerequisites |',
            '| --- | --- | --- | --- |']
    for r in nodes:
        out.append('| ' + ' | '.join(safe(x) for x in [r['id']+' / '+r['variant'], f'{r["actor"]} / {r["system"]} / {r["boundary"]}',
                  ', '.join(r['inputs'])+' → '+', '.join(r['outputs']), ', '.join(sorted(dependencies(r)))]) + ' |')
    out += ['', '## Gaps and coverage', ''] + ['- ' + safe(x) for x in process_check(state, view)['errors']]
    out += ['', '## Handoffs and paths', '', '| From → to | Kind / condition | Payload | Receiver |', '| --- | --- | --- | --- |']
    for r in nodes:
        for e in r['edges']:
            out.append('| ' + ' | '.join(safe(x) for x in [r['id']+' → '+e['to'],e['kind']+' / '+e['condition'],e['payload'],e['receiver']]) + ' |')
    out += ['', '## Declared coverage', '', '| Dimension / value | Status | Steps | Source locators / gap |', '| --- | --- | --- | --- |']
    for r in active(state, 'coverage'):
        evidence = '; '.join(e['source']+' '+e['locator'] for e in r.get('evidence', []))
        out.append('| ' + ' | '.join(safe(x) for x in [r['dimension']+' / '+r['value'],r['status'],', '.join(r['steps']),evidence+' '+r.get('gap','')]) + ' |')
    out += ['', '## Knowledge', '', '| Claim | Status / freshness | Sources and locators |', '| --- | --- | --- |']
    for r in active(state, 'claim'):
        out.append(f'| {safe(r["id"] + ": " + r["assertion"])} | {r["status"]} / {freshness(r, as_of)} | ' + safe('; '.join(e['source']+' '+e['locator'] for e in r['evidence'])) + ' |')
    out += ['', '## Resume', '', safe(json.dumps(state.get('checkpoint', {}), ensure_ascii=False)), '',
            'Structural checks cannot prove that every stakeholder or real exception has been discovered.', '']
    return '\n'.join(out)
