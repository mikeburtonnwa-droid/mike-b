"""Independent G4 reproduction, persistence and acceptance probes; disposable projects only."""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from agent_architect.core import Project, Invalid, impact, context
from agent_architect import workflow as w
from agent_architect.schema import CONCERNS

checks, commands = [], []
def check(name, condition, evidence=None):
    checks.append(dict(name=name, passed=bool(condition), evidence=evidence))
    print(('PASS ' if condition else 'FAIL ') + name + (': ' + json.dumps(evidence) if evidence is not None else ''))
    (HERE / 'architecture-probe-checks.json').write_text(json.dumps(checks, indent=2) + '\n')
    assert condition, name

def command(argv, cwd=ROOT):
    proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    commands.append(dict(argv=[str(x) for x in argv], cwd=str(cwd), stdout=proc.stdout,
                         stderr=proc.stderr, exit_code=proc.returncode))
    (HERE / 'architecture-probe-commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    return proc

def reject(p, name, fn):
    before = p.head()
    try:
        fn()
    except Invalid as exc:
        check(name, p.head() == before, str(exc))
    else:
        check(name, False, 'unexpected success')

with tempfile.TemporaryDirectory(prefix='g4-architecture-') as temp:
    base = Path(temp)
    out = base / 'rehearsal with spaces'
    proc = command([sys.executable, str(ROOT / 'examples/order-triage/rehearse.py'), '--output', str(out)], base)
    check('reproduce rehearsal from separate directory', proc.returncode == 0 and proc.stderr == '', proc.returncode)
    report = json.loads(proc.stdout)
    declared = json.loads((out / 'checks.json').read_text())
    events = json.loads((out / 'events.json').read_text())
    check('all 37 predefined rehearsal assertions', len(declared) == 37 and all(c['passed'] for c in declared), report)
    for name in ['checks.json', 'events.json', 'report.json', 'current-map.md', 'proposed-map.md', 'resume-context.json', 'change-impact.json']:
        shutil.copyfile(out / name, HERE / ('architecture-reproduced-' + name))
    shutil.make_archive(str(HERE / 'architecture-reproduced-projects'), 'zip', out)
    p = Project(out / 'ready-project')
    s = p.read()
    date = report['as_of']
    check('ready and changed histories independently audit', p.audit()['status'] == Project(out / 'project').audit()['status'] == 'pass', {'ready_revision': s['revision'], 'changed_revision': Project(out / 'project').read()['revision']})
    check('all ten stakeholder sources preserve input bytes', all((p.path / s['records'][f'S{i:02}']['blob']).read_bytes() == path.read_bytes() for i, path in enumerate(sorted((ROOT / 'examples/order-triage/inputs').glob('*.md')), 1)))
    for view in ['current', 'proposed']:
        result = w.process_check(s, view)
        steps = [r for r in s['records'].values() if r['type'] == 'process' and r['view'] == view]
        check(view + ' map has complete declared structure and six steps', result['status'] == 'pass' and len(steps) == 6, {'kinds': [r['kind'] for r in steps], 'actors': sorted({r['actor'] for r in steps})})
    check('proposed steps explicitly trace current baselines', all(s['records'][r['baseline'][0]]['view'] == 'current' for r in s['records'].values() if r['type'] == 'process' and r['view'] == 'proposed'))
    reqs = [r for r in s['records'].values() if r['type'] == 'requirement' and r['critical']]
    check('three distinct critical criteria trace deterministic component', len(reqs) == 3 and len({r['acceptance'] for r in reqs}) == 3 and set(s['records']['DEC_CODE']['requirements']) == {r['id'] for r in reqs} and s['records']['COMP_ROUTER']['method'] == 'code' and s['records']['COMP_ROUTER']['decisions'] == ['DEC_CODE'], {r['id']: r['acceptance'] for r in reqs})
    concerns = [r for r in s['records'].values() if r['type'] == 'concern']
    check('eight concerns supported and architecture checks pass', {r['category'] for r in concerns} == CONCERNS and all(r['evidence'] and r['rationale'] for r in concerns) and w.architecture_check(s)['status'] == 'pass', sorted(CONCERNS))
    handoff = s['records']['HANDOFF']
    check('handoff states limited authorization and real deployment work', handoff['environment'] == 'fixture' and 'simulation only' in handoff['authorization'] and bool(handoff['remaining_steps']), handoff)
    executions = {e['action'].removeprefix('execute '): e for e in events if 'argv' in e}
    naive = json.loads(executions['Q_NAIVE']['stdout'])
    correct = json.loads(executions['Q_ROUTES']['stdout'])
    keys = lambda rows: {(r['tenant'], r['request_id']) for r in rows}
    check('actual bad join has duplicates and cross-tenant enrichment', len(naive['rows']) == 13 and len(keys(naive['rows'])) == 4 and sum(r['tenant'] != r['customer_tenant'] for r in naive['rows']) == 6, {'rows': len(naive['rows']), 'keys': len(keys(naive['rows'])), 'cross_tenant': sum(r['tenant'] != r['customer_tenant'] for r in naive['rows'])})
    expected_routes = [['north', 'R1', 'fulfillment'], ['north', 'R2', 'finance-review'], ['north', 'R3', 'service-desk'], ['south', 'R4', 'fulfillment']]
    check('actual corrected rows satisfy independent fixture oracle', len(correct['rows']) == len(keys(correct['rows'])) == 4 and all(r['tenant'] == r['customer_tenant'] for r in correct['rows']) and sorted([[r['tenant'],r['request_id'],r['route']] for r in correct['rows']]) == expected_routes)
    check('failure exits preserved separately from successful execution', {executions[k]['returncode'] for k in ['EV_NAIVE', 'EV_OUTAGE', 'EV_FAILED_RECOVERY']} == {1} and {executions[k]['returncode'] for k in ['EV_CARDINALITY', 'EV_ISOLATION', 'EV_ROUTING', 'EV_RECOVERED']} == {0} and all(e['stderr'] == '' for e in executions.values()))
    evals = [r for r in s['records'].values() if r['type'] == 'evaluation']
    runs = [json.loads((p.path / s['records'][r['result_source']]['blob']).read_text()) for r in evals]
    check('seven executions have unique canonical IDs and aware UTC dates', len(runs) == 7 and len({r['run_id'] for r in runs}) == 7 and all(str(uuid.UUID(r['run_id'])) == r['run_id'] and datetime.fromisoformat(r['run_at']).astimezone(timezone.utc).date().isoformat() == r['run_on'] for r in runs))
    check('failed recovery remains retained and fresh recovery closes', s['records']['EV_FAILED_RECOVERY']['status'] == 'fail' and s['records']['INC_FEED']['status'] == 'closed' and s['records']['INC_FEED']['verification'] == 'EV_RECOVERED', {k:s['records'][k]['status'] for k in ['EV_NAIVE','EV_FAILED_RECOVERY','EV_RECOVERED','INC_FEED']})
    release = copy.deepcopy(s['releases']['REL1'])
    key, envelope = p.head()
    release_states = []
    while True:
        if 'REL1' in envelope['state']['releases']:
            release_states.append(envelope['state']['releases']['REL1'])
        if envelope['parent'] is None:
            break
        envelope = p.envelope(envelope['parent'])
    check('complete REL1 snapshot immutable throughout later history', all(r == release for r in release_states), {'later_commits': len(release_states), 'snapshot_hash': release['snapshot_hash']})
    check('ready release passes while changed data invalidates readiness', w.readiness(s,date,'fixture','HANDOFF')['status'] == 'pass' and w.readiness(Project(out/'project').read(),date,'fixture','HANDOFF')['status'] == 'fail')
    changed = Project(out/'project')
    reject(changed, 'rollback on changed dependency is atomic rejection', lambda: w.activate(changed,'REL1',date,'fixture','independent stale rollback',changed.read()['revision'],'architecture',rollback=True))
    check('change impact includes executed query and component', {'Q_ROUTES','COMP_ROUTER'} <= set(impact(changed.read(),'D_APPROVALS')['affected']))

    # Independently execute a second fault/recovery sequence against the audited handoff.
    def execute_eval(rid, fault):
        state = p.read()
        binding = dict(target_hashes=w.fingerprints(state['records'], ['REQ_ROUTING','COMP_ROUTER']), brief_hash=w.brief_hash(state))
        binding_path = base / (rid + '-binding.json')
        binding_path.write_text(json.dumps(binding))
        run = command([sys.executable,str(ROOT/'examples/order-triage/execute.py'),'--sql','routes.sql','--binding',str(binding_path),'--criterion','routing','--fault',fault],base)
        p.source('RESULT_'+rid,rid,run.stdout.encode(),'query-result','independent actual SQLite execution',date,'fixture',p.read()['revision'],'architecture')
        result=w.evaluate(p,dict(id=rid,title=rid,description='Independent second lifecycle probe',targets=['REQ_ROUTING','COMP_ROUTER'],result_source='RESULT_'+rid,valid_until=s['records']['EV_RECOVERED']['valid_until'],criterion=s['records']['REQ_ROUTING']['acceptance']),p.read()['revision'],'architecture')
        return run, result
    fail_run,fail_receipt=execute_eval('EV_ARCH_FAULT','drop-approvals')
    check('new failure overrides the older passing handoff evidence', fail_run.returncode == 1 and fail_receipt['outcome']=='fail' and w.readiness(p.read(),date,'fixture','HANDOFF')['status']=='fail')
    inc=copy.deepcopy(s['records']['INC_FEED'])
    inc.update(id='INC_ARCH',status='open',release='REL2',diagnosis='Independently removed all approval rows',action='Restore original fixture and rerun same routing criterion')
    for field in ['verification','closed_on']:
        inc.pop(field,None)
    p.put([inc],p.read()['revision'],'architecture')
    reject(p,'older passing evaluation cannot close after latest failure',lambda:w.close_incident(p,'INC_ARCH','EV_RECOVERED',date,p.read()['revision'],'architecture'))
    reject(p,'latest failed evaluation cannot close incident',lambda:w.close_incident(p,'INC_ARCH','EV_ARCH_FAULT',date,p.read()['revision'],'architecture'))
    reject(p,'failed state cannot create release',lambda:w.create_release(p,'REL_ARCH_BAD','HANDOFF',date,'fixture',handoff['authorization'],p.read()['revision'],'architecture'))
    replay=(p.path/s['records']['RESULT_EV_RECOVERED']['blob']).read_bytes()
    p.source('ARCH_ALIAS','Alias of unchanged earlier result',replay,'query-result','alias',date,'fixture',p.read()['revision'],'architecture')
    reject(p,'unchanged old result source alias cannot be promoted',lambda:w.evaluate(p,dict(id='EV_ARCH_REPLAY',title='Replay',description='Negative unchanged source replay',targets=['REQ_ROUTING','COMP_ROUTER'],result_source='ARCH_ALIAS',valid_until=s['records']['EV_RECOVERED']['valid_until'],criterion=s['records']['REQ_ROUTING']['acceptance']),p.read()['revision'],'architecture'))
    check('incident still open after all rejected transitions',p.read()['records']['INC_ARCH']['status']=='open')
    pass_run,pass_receipt=execute_eval('EV_ARCH_RECOVERED','none')
    w.close_incident(p,'INC_ARCH','EV_ARCH_RECOVERED',date,p.read()['revision'],'architecture')
    check('fresh actual recovery closes and restores readiness',pass_run.returncode==0 and pass_receipt['outcome']=='pass' and p.read()['records']['INC_ARCH']['verification']=='EV_ARCH_RECOVERED' and w.readiness(p.read(),date,'fixture','HANDOFF')['status']=='pass')
    check('second lifecycle preserves REL1 and REL2',p.read()['releases']==s['releases'])
    reject(p,'release identifier cannot be replaced through record put',lambda:p.put([dict(id='REL1',type='note',title='collision',description='negative ID replacement',status='active')],p.read()['revision'],'architecture'))
    check('second lifecycle retains clean full audit',p.audit()['status']=='pass',p.audit())
    shutil.make_archive(str(HERE/'architecture-second-lifecycle'),'zip',p.path)

    # Restore frozen fresh-context artifacts into disposable directories; never use live originals.
    for label, expected_revision in [('start',4),('resume',40)]:
        dest=base/('novice-'+label)
        with zipfile.ZipFile(HERE/('novice-'+label+'-project.zip')) as archive:
            assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in archive.namelist())
            archive.extractall(dest)
        novice=Project(dest)
        ns=novice.read()
        check(label+' archived project audit and revision',novice.audit()['status']=='pass' and ns['revision']==expected_revision,novice.audit())
        check(label+' preserves exact first source and no activated release',(dest/ns['records']['S01']['blob']).read_bytes()==(ROOT/'examples/order-triage/inputs/01-frontline.md').read_bytes() and ns['active_release'] is None and not ns['releases'])
        if label=='start':
            claims=[r for r in ns['records'].values() if r['type']=='claim']
            check('single interview remains reported and incomplete',len(claims)==7 and all(r['status']=='reported' for r in claims) and ns['owner']=='unknown' and ns['checkpoint']['stage']=='discovery' and w.process_check(ns,'current')['status']=='fail')
        else:
            result={'process':w.process_check(ns,'current'),'architecture':w.architecture_check(ns),'release':w.readiness(ns,'2026-09-09','synthetic-training','H01')}
            (HERE/'architecture-novice-resume-checks.json').write_text(json.dumps(result,indent=2)+'\n')
            check('cold resume is a bounded design checkpoint with explicit failing gates',len(ns['records'])==95 and ns['checkpoint']['stage']=='design' and all(r['status']=='fail' for r in result.values()) and not any(r['type'] in ['component','evaluation'] for r in ns['records'].values()),{k:v['status'] for k,v in result.items()})
            check('cold resume reconciles hearsay and separates three requirements/eight deferred concerns',ns['records']['C08']['status']=='superseded' and ns['records']['DEC01']['requirements']==['REQ01','REQ02','REQ03'] and len([r for r in ns['records'].values() if r['type']=='concern' and r['disposition']=='deferred'])==8)
            check('cold resume preserves old query versions and current fresh bindings',{k:r['status'] for k,r in ns['records'].items() if r['type']=='query'}==dict(Q01='archived',Q02='archived',Q03='archived',Q04='executed',Q05='executed'))
            check('cold resume source data and routing observations agree with oracle',len(json.loads((dest/ns['records']['S17']['blob']).read_text())['rows'])==4)

print(json.dumps({'checks':len(checks),'passed':sum(c['passed'] for c in checks),'failed':[c['name'] for c in checks if not c['passed']],'captured_subprocesses':len(commands)},indent=2))
