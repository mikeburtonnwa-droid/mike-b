"""Independent G3 revision-2 novice/skill integration probes; synthetic temporary projects."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CLI = ROOT / 'scripts/aa.py'
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
from support import ready_project, record, edge, CRITERION

events, checks, observations = [], [], []
original_names = ['product.md', 'product-checks.py', 'product-evidence.json']
original_hashes = {name: hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in original_names}
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')


def run(args, cwd):
    p = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)
    result = dict(command=args, cwd=str(cwd), exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr)
    events.append(result)
    return result


def value(result):
    return json.loads(result['stdout'] or result['stderr'])


def check(name, passed, details):
    checks.append(dict(name=name, passed=bool(passed), details=details, last_command=len(events)))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads((OUT / 'candidate-r2.json').read_text())
check('candidate_before', all(sha(ROOT / p) == h for p, h in manifest.items()), {'entries': len(manifest)})
skill_names = ['agent-architect', 'process-discovery', 'evidence-curation', 'data-discovery', 'architecture-delivery', 'operations-review']
broken = []
for name in skill_names:
    p = ROOT / 'skills' / name / 'SKILL.md'
    body = p.read_text()
    assert body.startswith('---\nname: ' + name + '\ndescription: ')
    for link in re.findall(r'\]\(([^)]+)\)', body):
        if not link.startswith(('https:', 'http:')) and not (p.parent / link.split('#')[0]).exists():
            broken.append({'skill': name, 'link': link})
check('skill_frontmatter_and_local_links', not broken, {'skills': skill_names, 'broken': broken})

with tempfile.TemporaryDirectory(prefix='aa-g3-product-') as temporary:
    base = Path(temporary)
    cwd = base / 'unrelated working directory'
    cwd.mkdir()
    project = base / 'private project'

    def cli(*args, target=None):
        return run([sys.executable, str(CLI), '--project', str(target or project), *args], cwd)

    def file(name, data):
        (cwd / name).write_text(json.dumps(data), encoding='utf-8')
        return name

    def revision(target=None):
        return str(value(cli('show', target=target))['revision'])

    def put(data, name='records.json', target=None):
        return cli('put', file(name, data), '--expect-revision', revision(target), target=target)

    def capture(rid, content, kind='document', target=None):
        name = rid + '.txt'
        (cwd / name).write_text(content)
        return cli('source', '--id', rid, '--title', rid, '--file', name, '--kind', kind, '--locator', 'synthetic review ' + rid,
                   '--captured-on', '2026-09-09', '--environment', 'test', '--expect-revision', revision(target), target=target)

    result = cli('schema')
    schema = value(result)
    check('schema_before_initialization', result['exit_code'] == 0 and not project.exists()
          and 'acceptance' in schema['requirement']['required'], {'types': sorted(schema), 'project_created': project.exists()})
    result = cli('init', '--title', 'First interview', '--scope', 'unknown', '--owner', 'unknown')
    check('intake_unknowns_save', result['exit_code'] == 0, {'revision': value(result)['revision']})
    capture('FIRST', 'Synthetic first interview: customer hands request to an unknown team owner. Exception paths unknown.\n', 'interview')
    evidence = [{'source': 'FIRST', 'locator': 'line 1'}]
    nodes = []
    for rid, kind, actor, edges in [('PSTART', 'start', 'customer', [edge('PWORK', kind='handoff', receiver='unknown', payload='request')]),
                                    ('PWORK', 'activity', 'unknown', [edge('PEND', receiver='unknown')]),
                                    ('PEND', 'end', 'unknown', [])]:
        nodes.append(record(rid, 'process', title=rid, view='current', kind=kind, actor=actor, system='request desk',
                            boundary='intake', inputs=['request'], outputs=['request disposition'], variant='standard', edges=edges, evidence=evidence))
    nodes += [record('OWNER', 'issue', status='open', critical=True, owner='unknown', next_action='Identify accountable owner', evidence=evidence),
              record('EXCEPTIONS', 'coverage', status='gap', dimension='exception', value='rejected requests', critical=True,
                     steps=['PWORK'], owner='unknown', gap='Need a rejected request example'),
              record('ACCOUNT', 'claim', status='reported', assertion='Owner and rejected-request paths are unknown',
                     applicability='provisional intake', evidence=evidence)]
    result = put(nodes)
    check('provisional_map_can_be_saved', result['exit_code'] == 0, {'revision': value(result).get('revision')})
    checkpoint = dict(current_task='Clarify ownership and exceptions', completed=['First interview captured'],
                      unresolved=['Owner unknown', 'Rejected-request path unknown'], next_action='Ask for owner and one rejected request',
                      relevant_ids=['OWNER', 'EXCEPTIONS', 'PWORK'], stage='discovery')
    result = cli('checkpoint', file('checkpoint.json', checkpoint), '--expect-revision', revision())
    check('checkpoint_saves_pending_discovery', result['exit_code'] == 0, {'revision': value(result)['revision']})
    result = cli('check', 'process', '--view', 'current')
    check('provisional_check_explains_gaps', result['exit_code'] == 1 and any('unknown actor' in e for e in value(result)['errors'])
          and any('Need a rejected request example' in e for e in value(result)['errors']), value(result))
    result = cli('render', '--view', 'current', '--as-of', '2026-09-09')
    check('provisional_render_contains_map_gaps_and_resume', result['exit_code'] == 0
          and all(x in result['stdout'] for x in ['flowchart TD', 'Need a rejected request example', 'reported / unknown',
                                                'Ask for owner and one rejected request', 'local-simulation']),
          {'characters': len(result['stdout']), 'exit_code': result['exit_code']})
    result = cli('audit')
    check('cold_resume_audit', result['exit_code'] == 0, {'status': value(result)['status']})
    result = cli('context', '--as-of', '2026-09-09')
    check('cold_resume_recovers_checkpoint', value(result)['checkpoint'] == checkpoint, value(result)['checkpoint'])
    capture('CLARIFICATION', 'Synthetic clarification: Alice owns the project. Scope is standard requests only.\n', 'interview')
    clarification_note = record('BRIEF', 'note', title='Confirmed owner and scope', owner='Alice', next_action='Map standard requests',
                                description='Project scope is standard requests only', evidence=[dict(source='CLARIFICATION', locator='line 1')])
    result = put(clarification_note)
    assert result['exit_code'] == 0
    result = cli('show')
    observations.append(dict(name='clarified_metadata_after_supported_note', command_index=len(events),
                             canonical_owner=value(result)['owner'], canonical_scope=value(result)['scope'],
                             note_owner=value(result)['records']['BRIEF']['owner'],
                             note_scope=value(result)['records']['BRIEF']['description'],
                             project_record_supported='project' in schema))
    invalid_project = record('META', 'project', owner='Alice', scope='standard requests only')
    result = put(invalid_project, 'project-metadata.json')
    observations.append(dict(name='project_metadata_record_attempt', command_index=len(events), exit_code=result['exit_code'], output=value(result)))
    brief = dict(title='Standard requests', scope='Standard requests only', owner='Alice', rationale='Captured stakeholder clarification',
                 evidence=[dict(source='CLARIFICATION', locator='line 1')])
    before_brief = (project/'HEAD').read_text().strip()
    for name, bad in [('empty_evidence', dict(brief, evidence=[])),
                      ('missing_source', dict(brief, evidence=[dict(source='ABSENT', locator='line 1')]))]:
        result = cli('brief', file(name + '.json', bad), '--expect-revision', revision())
        check('brief_rejects_' + name, result['exit_code'] == 2 and (project/'HEAD').read_text().strip() == before_brief, value(result))
    old_revision = revision()
    result = cli('brief', file('brief.json', brief), '--expect-revision', old_revision)
    check('brief_clarification_saved', result['exit_code'] == 0, {'status': value(result)['status']})
    result = cli('brief', 'brief.json', '--expect-revision', old_revision)
    check('brief_rejects_stale_revision', result['exit_code'] == 2 and 'reread and reconcile' in value(result)['message'], value(result))
    checkpoint = dict(checkpoint, unresolved=['Rejected-request path unknown'], next_action='Ask Alice for a rejected request',
                      completed=['First interview captured', 'Project owner and scope clarified'])
    result = cli('checkpoint', file('clarified-checkpoint.json', checkpoint), '--expect-revision', revision())
    assert result['exit_code'] == 0
    result = cli('context', 'vocabulary-not-present', '--as-of', '2026-09-09')
    resumed = value(result)
    old_state = json.loads((project/'history'/f'{before_brief}.json').read_text())['state']
    check('clarified_brief_cold_resume_and_history', resumed['brief']['owner'] == 'Alice'
          and resumed['brief']['scope'] == 'Standard requests only' and resumed['checkpoint'] == checkpoint
          and 'CLARIFICATION' in {r['id'] for r in resumed['records']} and old_state['owner'] == old_state['scope'] == 'unknown',
          {'brief': resumed['brief'], 'checkpoint': resumed['checkpoint'], 'old_owner': old_state['owner'], 'old_scope': old_state['scope']})
    result = cli('check', 'release')
    check('release_argument_error_is_actionable', result['exit_code'] == 2 and '--environment and --handoff' in value(result)['message'], value(result))

    complete_path = base / 'complete synthetic project'
    complete = ready_project(complete_path, evaluation=False)
    # Cross-owner handoff exposes a payload that is absent from node inputs/outputs.
    start = complete.read()['records']['P1']
    result = put(start | dict(actor='customer', boundary='external', edges=[edge('P2', kind='handoff', payload='handoff-package-Z37')]), target=complete_path)
    assert result['exit_code'] == 0
    result = put(record('COV_CUSTOMER', 'coverage', status='covered', dimension='stakeholder', value='customer', critical=True,
                        steps=['P1'], owner='customer', evidence=[dict(source='S1', locator='line 1')]), target=complete_path)
    assert result['exit_code'] == 0
    for view in ['current', 'proposed']:
        result = cli('check', 'process', '--view', view, target=complete_path)
        check('complete_process_' + view, result['exit_code'] == 0, value(result))
    result = cli('render', '--view', 'current', '--as-of', '2026-09-09', target=complete_path)
    observations.append(dict(name='render_handoff_metadata', command_index=len(events),
                             payload_shown='handoff-package-Z37' in result['stdout'],
                             owner_shown='operations' in result['stdout'], exit_code=result['exit_code']))
    check('render_includes_handoff_payload_and_receiver', 'handoff-package-Z37' in result['stdout'] and 'Payload | Receiver' in result['stdout'], {'payload_shown': 'handoff-package-Z37' in result['stdout']})
    result = cli('check', 'architecture', target=complete_path)
    check('architecture_handoff_check', result['exit_code'] == 0, value(result))

    def evaluate_run(rid, actual):
        fingerprint = value(cli('fingerprint', 'REQ', 'COMP', target=complete_path))
        expected = {'decisions': 1}
        result = run([sys.executable, '-c', 'import json; print(json.dumps({"decisions": ' + str(actual) + '}))'], cwd)
        wrapper = dict(environment='test', run_on='2026-09-09', command=' '.join(result['command']), exit_code=result['exit_code'],
                       criterion=CRITERION, target_hashes=fingerprint['target_hashes'], brief_hash=fingerprint['brief_hash'], expected=expected, observed=json.loads(result['stdout']))
        capture('RESULT_' + rid, json.dumps(wrapper), 'query-result', complete_path)
        result = cli('evaluate', file(rid + '.json', dict(id=rid, title=rid, description='Executed synthetic review check',
                     targets=['REQ', 'COMP'], result_source='RESULT_' + rid, valid_until='2026-10-09', criterion=CRITERION)),
                     '--expect-revision', revision(complete_path), target=complete_path)
        observation = dict(name='evaluate_response_' + rid, command_index=len(events), exit_code=result['exit_code'],
                           response_status=value(result)['status'], evaluation=value(result).get('evaluation'), outcome=value(result).get('outcome'))
        saved = value(cli('show', target=complete_path))['records'][rid]
        observation['record_status'] = saved['status']
        check('evaluation_receipt_matches_' + rid, observation['evaluation'] == rid and observation['outcome'] == saved['status'], observation)
        observations.append(observation)
        return saved

    failed = evaluate_run('EVFAIL', 2)
    check('failed_run_is_preserved_as_fail', failed['status'] == 'fail', {'status': failed['status']})
    result = cli('check', 'release', '--handoff', 'HANDOFF', '--environment', 'test', '--as-of', '2026-09-09', target=complete_path)
    check('failed_evaluation_blocks_release', result['exit_code'] == 1 and any('no passing applicable' in e for e in value(result)['errors']),
          {'status': value(result)['status'], 'errors': value(result)['errors']})
    passed = evaluate_run('EVPASS', 1)
    check('passing_run_is_preserved_as_pass', passed['status'] == 'pass', {'status': passed['status']})
    result = cli('release', 'REL1', '--handoff', 'HANDOFF', '--environment', 'test', '--authority', 'Synthetic local review',
                 '--as-of', '2026-09-09', '--expect-revision', revision(complete_path), target=complete_path)
    check('release_is_explicit_local_simulation', result['exit_code'] == 0 and value(result)['deployment_mode'] == 'local-simulation',
          {'status': value(result)['status'], 'deployment_mode': value(result)['deployment_mode']})
    result = cli('activate', 'REL1', '--environment', 'test', '--reason', 'Synthetic local review', '--as-of', '2026-09-09',
                 '--expect-revision', revision(complete_path), target=complete_path)
    check('activation_is_explicit_local_simulation', result['exit_code'] == 0 and value(result)['deployment_mode'] == 'local-simulation',
          {'status': value(result)['status'], 'deployment_mode': value(result)['deployment_mode']})
    brief_branch = base/'brief change branch'
    shutil.copytree(complete_path, brief_branch)
    before_release = value(cli('show', target=brief_branch))['releases']['REL1']
    capture('NEW_BRIEF', 'Synthetic clarification: Alice owns a narrower standard-request scope.', 'interview', brief_branch)
    updated = dict(title='Narrower project', scope='Standard requests only', owner='Alice', rationale='Captured narrowed scope',
                   evidence=[dict(source='NEW_BRIEF', locator='line 1')])
    result = cli('brief', file('new-brief.json', updated), '--expect-revision', revision(brief_branch), target=brief_branch)
    assert result['exit_code'] == 0
    result = cli('context', 'EVPASS', '--as-of', '2026-09-09', target=brief_branch)
    check('brief_change_warns_old_evaluation', any('project brief changed' in w for w in value(result)['warnings']), {'warnings': value(result)['warnings']})
    result = cli('activate', 'REL1', '--environment', 'test', '--reason', 'Must reject brief drift', '--as-of', '2026-09-09',
                 '--expect-revision', revision(brief_branch), target=brief_branch)
    check('brief_change_blocks_old_release', result['exit_code'] == 2 and 'changed project brief' in value(result)['message'], value(result))
    rebind = dict(id='REBOUND', title='Rebound', description='Old result cannot change brief', targets=['REQ','COMP'],
                  result_source='RESULT_EVPASS', valid_until='2026-10-09', criterion=CRITERION)
    result = cli('evaluate', file('rebind.json', rebind), '--expect-revision', revision(brief_branch), target=brief_branch)
    check('brief_change_rejects_old_result_rebinding', result['exit_code'] == 2, value(result))
    result = cli('show', target=brief_branch)
    check('old_release_preserved_after_brief_change', value(result)['releases']['REL1'] == before_release, {'snapshot_unchanged': value(result)['releases']['REL1'] == before_release})
    component = value(cli('show', target=complete_path))['records']['COMP']
    result = put(component | dict(artifact='changed synthetic implementation'), target=complete_path)
    assert result['exit_code'] == 0
    result = cli('activate', 'REL1', '--environment', 'test', '--reason', 'Must reject drift', '--as-of', '2026-09-09',
                 '--expect-revision', revision(complete_path), target=complete_path)
    check('changed_implementation_blocks_activation', result['exit_code'] == 2 and 'changed COMP' in value(result)['message'], value(result))
    result = cli('close-incident', 'MISSING', '--evaluation', 'EVPASS', '--as-of', '2026-09-09',
                 '--expect-revision', revision(complete_path), target=complete_path)
    check('incident_error_names_required_inputs', result['exit_code'] == 2 and 'open incident and evaluation' in value(result)['message'], value(result))

    query_path = base/'query protocol project'
    query_project = ready_project(query_path, evaluation=False)
    capture('SCHEMA', 'create table requests(id integer primary key);', 'schema', query_path)
    asset = record('TABLE', 'data', environment='test', schema='main', table='requests', grain='one request', keys=['id'], refresh='fixture',
                   evidence=[dict(source='SCHEMA', locator='DDL')])
    query = record('QUERY1', 'query', status='draft', environment='test', sql='select id from requests order by id', assets=['TABLE'], parameters={},
                   join_assumptions='No joins', limitations='Synthetic SQLite fixture')
    result = put([asset, query], 'query-records.json', target=query_path)
    assert result['exit_code'] == 0
    fingerprint = value(cli('query-fingerprint', 'QUERY1', target=query_path))
    code = "import sqlite3,json,sys; db=sqlite3.connect(':memory:'); db.executescript('create table requests(id integer primary key); insert into requests values(1),(2);'); print(json.dumps(db.execute(sys.argv[1]).fetchall()))"
    actual = run([sys.executable, '-c', code, query['sql']], cwd)
    result_wrapper = dict(environment='test', run_on='2026-09-09', command=' '.join(actual['command']), exit_code=actual['exit_code'],
                          query_fingerprint=fingerprint, rows=json.loads(actual['stdout']))
    capture('QUERY_ROWS', json.dumps(result_wrapper), 'query-result', query_path)
    result = cli('bind-query', 'QUERY1', '--result', 'QUERY_ROWS', '--expect-revision', revision(query_path), target=query_path)
    check('query_protocol_binds_actual_sqlite_output', result['exit_code'] == 0 and result_wrapper['rows'] == [[1],[2]], {'rows': result_wrapper['rows'], 'status': value(result)['status']})
    executed = value(cli('show', target=query_path))['records']['QUERY1']
    result = put(dict(executed, sql='select id from requests where id=1'), 'changed-query.json', target=query_path)
    check('executed_query_edit_rejected', result['exit_code'] == 2, value(result))
    result = put(dict(query, id='QUERY2', sql='select id from requests where id=1'), 'second-query.json', target=query_path)
    assert result['exit_code'] == 0
    result = cli('bind-query', 'QUERY2', '--result', 'QUERY_ROWS', '--expect-revision', revision(query_path), target=query_path)
    check('old_rows_cannot_bind_changed_query', result['exit_code'] == 2, value(result))
    result = put(dict(asset, grain='changed grain assumption'), 'changed-asset.json', target=query_path)
    assert result['exit_code'] == 0
    result = cli('context', 'QUERY1', '--as-of', '2026-09-09', target=query_path)
    check('query_drift_visible_on_resume', any('query dependencies changed' in w for w in value(result)['warnings']), {'warnings': value(result)['warnings']})

check('original_artifacts_preserved', all(sha(OUT/name) == value for name,value in original_hashes.items()), original_hashes)
check('candidate_after', all(sha(ROOT / p) == h for p, h in manifest.items()), {'entries': len(manifest)})
(OUT / 'product-evidence-r2.json').write_text(json.dumps(dict(checks=checks, observations=observations, commands=events), indent=2) + '\n')
for c in checks:
    print(('PASS ' if c['passed'] else 'FAIL ') + c['name'] + ': ' + json.dumps(c['details'], sort_keys=True))
for o in observations:
    print('OBSERVATION ' + json.dumps(o, sort_keys=True))
print(json.dumps(dict(checks=len(checks), failed=sum(not c['passed'] for c in checks), commands=len(events), observations=len(observations)), sort_keys=True))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
