"""Independent G4 product review; copies of preserved synthetic evidence only."""
from pathlib import Path
import hashlib,json,os,re,shutil,sqlite3,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
CLI=ROOT/'scripts/aa.py'
commands=[];checks=[];observations=[]
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(argv,cwd=ROOT):
    r=subprocess.run([str(x) for x in argv],cwd=cwd,env=ENV,capture_output=True,text=True)
    event=dict(argv=[str(x) for x in argv],cwd=str(cwd),stdout=r.stdout,stderr=r.stderr,exit_code=r.returncode)
    commands.append(event);return event
def data(r):return json.loads(r['stdout'] or r['stderr'])
def check(name,passed,details):checks.append(dict(name=name,passed=bool(passed),details=details,command_index=len(commands)))
def files_hash(paths):return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}
manifest=json.loads((OUT/'candidate.json').read_text())
check('candidate_before',all(sha(ROOT/p)==h for p,h in manifest.items()),dict(entries=len(manifest),candidate_sha256=sha(OUT/'candidate.json')))
originals=[OUT/n for n in ['novice-start-project.zip','novice-resume-project.zip','rehearsal-projects-r4.zip','novice-start.md','novice-resume.md','novice-start-artifact.md','novice-resume-artifact.md','novice-start-commands.json','novice-resume-commands.json','experiment-acceptance.md','development-observations.md','current-map.png','proposed-map.png']]
original_hashes=files_hash(originals)
# These read commands preserve the exact reviewed text and original command-log bytes.
for paths in [
 ['development/PLAN.md','development/gates/G4/README.md','development/gates/G4/experiment-acceptance.md','development/gates/G4/development-observations.md'],
 ['development/gates/G4/novice-start-dispatch.txt','development/gates/G4/novice-start.md','development/gates/G4/novice-start-artifact.md'],
 ['development/gates/G4/novice-resume-dispatch.txt','development/gates/G4/novice-resume.md','development/gates/G4/novice-resume-artifact.md'],
 ['development/gates/G4/novice-start-commands.json','development/gates/G4/novice-resume-commands.json'],
 ['START.md','examples/order-triage/README.md','skills/agent-architect/SKILL.md','skills/process-discovery/SKILL.md','skills/evidence-curation/SKILL.md','skills/data-discovery/SKILL.md'],
 ['examples/order-triage/sample-current-map.md','examples/order-triage/sample-proposed-map.md','examples/order-triage/sample-report.json']]:
    assert run(['cat',*paths])['exit_code']==0
assert run(['sed','-n','185,210p','src/agent_architect/workflow.py'])['exit_code']==0
assert run(['sed','-n','510,610p','src/agent_architect/workflow.py'])['exit_code']==0
assert run(['cat',*sorted((ROOT/'examples/order-triage/inputs').glob('*'))])['exit_code']==0

start_log=json.loads((OUT/'novice-start-commands.json').read_text())
resume_log=json.loads((OUT/'novice-resume-commands.json').read_text())
for label,logs in [('start',start_log),('resume',resume_log)]:
    observations.append(dict(name=label+'_commands',entries=len(logs),nonzero=[dict(index=i+1,command=r['command'] if isinstance(r['command'],list) else r['command'].splitlines()[0],exit_code=r.get('exit_code'),stderr=r.get('stderr')) for i,r in enumerate(logs) if r.get('exit_code')!=0]))
    check(label+'_log_preserves_output_fields',all(all(k in r for k in ('command','stdout','stderr','exit_code')) for r in logs),dict(entries=len(logs)))

with tempfile.TemporaryDirectory(prefix='aa-g4-product-') as tmp:
    base=Path(tmp);cwd=base/'unrelated working directory';cwd.mkdir()
    def cli(project,*args):return run([sys.executable,CLI,'--project',project,*args],cwd)
    def extract(name,dest):
        with zipfile.ZipFile(OUT/name) as z:
            assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
            z.extractall(dest)
    first=base/'first session';resumed=base/'resumed session';rehearsal=base/'preserved rehearsal'
    extract('novice-start-project.zip',first);extract('novice-resume-project.zip',resumed);extract('rehearsal-projects-r4.zip',rehearsal)
    states={}
    for name,path,rev in [('first',first,4),('resumed',resumed,40)]:
        r=cli(path,'audit');check(name+'_archive_audits',r['exit_code']==0 and data(r)['commits']==rev,data(r))
        r=cli(path,'show');states[name]=data(r);check(name+'_revision_and_no_release',r['exit_code']==0 and data(r)['revision']==rev and not data(r)['releases'] and data(r)['active_release'] is None,dict(revision=data(r)['revision'],records=len(data(r)['records'])))
    f=states['first'];s=states['resumed'];fr=f['records'];sr=s['records']
    check('first_interview_source_only_and_exact',len([v for v in fr.values() if v['type']=='source'])==1 and (first/fr['S01']['blob']).read_bytes()==(ROOT/'examples/order-triage/inputs/01-frontline.md').read_bytes(),dict(source_ids=[k for k,v in fr.items() if v['type']=='source']))
    check('first_intake_preserves_unknowns_and_reported_claims',f['owner']=='unknown' and all(v['status']=='reported' for v in fr.values() if v['type']=='claim') and len(f['checkpoint']['unresolved'])>=4,dict(owner=f['owner'],claim_statuses={k:v['status'] for k,v in fr.items() if v['type']=='claim'},next_action=f['checkpoint']['next_action']))
    r=cli(first,'check','process','--view','current');check('first_process_fails_with_precise_gaps',r['exit_code']==1 and 'P03: unknown system' in data(r)['errors'] and any('urgent' in x.lower() for x in data(r)['errors']),data(r))
    r=cli(first,'render','--view','current','--as-of','2026-09-09');first_render=r['stdout']
    check('first_render_rework_is_readable',r['exit_code']==0 and 'No local simulation is activated.' in first_render and 'Current task: ' in first_render and 'Next action: **'+f['checkpoint']['next_action']+'**' in first_render and 'Covered means an attributed account' in first_render and '{&quot;current_task&quot;' not in first_render,dict(characters=len(first_render),activation_line=first_render.splitlines()[4]))
    r=cli(first,'context','not-present-lexical-term','--as-of','2026-09-09');check('first_context_recovers_checkpoint_without_chat',data(r)['checkpoint']==f['checkpoint'] and data(r)['brief']['owner']=='unknown',dict(brief=data(r)['brief'],next_action=data(r)['checkpoint']['next_action']))
    check('resume_preserves_first_history_and_source',all((resumed/p.relative_to(first)).read_bytes()==p.read_bytes() for p in (first/'history').glob('*.json')) and (resumed/sr['S01']['blob']).read_bytes()==(first/fr['S01']['blob']).read_bytes(),dict(first_commits=len(list((first/'history').glob('*.json')))))
    check('all_ten_sources_and_schema_are_exact',all((resumed/sr['S'+str(i).zfill(2)]['blob']).read_bytes()==p.read_bytes() for i,p in enumerate(sorted((ROOT/'examples/order-triage/inputs').glob('*.md')),1)) and (resumed/sr['S11']['blob']).read_bytes()==(ROOT/'examples/order-triage/inputs/setup.sql').read_bytes(),dict(interviews=10,schema='S11'))
    check('resume_authoritative_brief_has_policy_evidence',s['owner']=='Operations' and {v['source'] for v in s['brief_evidence']}=={'S03','S10'},dict(owner=s['owner'],scope=s['scope'],evidence=s['brief_evidence']))
    r=cli(resumed,'context','C08','--as-of','2026-09-09');ctx=data(r)
    check('resume_conflicting_hearsay_is_historical', 'C08' not in {v['id'] for v in ctx['records']} and 'C08' in {v['id'] for v in ctx['historical_dependencies']} and 'C20' in {v['id'] for v in ctx['records']} and sr['C08']['status']=='superseded',dict(active_ids=[v['id'] for v in ctx['records']],historical_ids=[v['id'] for v in ctx['historical_dependencies']],warnings=ctx['warnings']))
    hist=[json.loads(p.read_text())['state'] for p in (resumed/'history').glob('*.json')]
    check('resume_preserves_original_bilateral_conflict',any('C08' in h['records'] and h['records']['C08'].get('conflicts_with')==['C09'] and h['records']['C09'].get('conflicts_with')==['C08'] for h in hist),dict(history_entries=len(hist)))
    check('policy_stays_reported_and_queries_are_executed',all(sr[k]['status']=='reported' for k in ['C09','C10','C11','C20']) and {k for k,v in sr.items() if v['type']=='query' and v['status']=='executed'}=={'Q04','Q05'},dict(policy={k:sr[k]['status'] for k in ['C09','C10','C11','C20']},queries={k:v['status'] for k,v in sr.items() if v['type']=='query'}))
    check('composite_keys_and_event_grain_preserved',sr['D01']['keys']==['tenant','request_id'] and sr['D02']['keys']==['tenant','customer_id'] and sr['D03']['keys']==['tenant','request_id','decision_seq'] and sr['D04']['keys']==['tenant','request_id','event_seq'],{k:dict(keys=sr[k]['keys'],grain=sr[k]['grain']) for k in ['D01','D02','D03','D04']})
    r=cli(resumed,'context','C24','--as-of','2026-09-10');ctx=data(r)
    check('fixture_observation_becomes_stale_next_day',any(v['id']=='C24' and v['freshness']=='stale' for v in ctx['records']),dict(warnings=ctx['warnings']))
    r=cli(resumed,'context','Q04','--as-of','2026-09-09');ctx=data(r)
    check('current_query_context_has_bound_sources_without_drift',{'Q04','S11','S17','D01','D02','D03','D04'}<={v['id'] for v in ctx['records']} and not any('Q04: executed query dependencies changed' in w for w in ctx['warnings']),dict(ids=[v['id'] for v in ctx['records']],warnings=ctx['warnings']))
    r=cli(resumed,'check','process','--view','current');check('resume_preserves_receiver_coverage_gaps',r['exit_code']==1 and any('CV08' in x for x in data(r)['errors']) and any('CV09' in x for x in data(r)['errors']),data(r))
    r=cli(resumed,'check','architecture');check('resume_keeps_unimplemented_architecture_blocked',r['exit_code']==1 and len([x for x in data(r)['errors'] if 'critical concern deferred' in x])==8,data(r))
    r=cli(resumed,'check','release','--handoff','H01','--environment','synthetic-training','--as-of','2026-09-09');check('resume_does_not_claim_release_readiness',r['exit_code']==1,data(r))
    r=cli(resumed,'render','--view','current','--as-of','2026-09-09');check('resumed_render_has_next_action_and_real_activation_state',r['exit_code']==0 and 'No local simulation is activated.' in r['stdout'] and s['checkpoint']['next_action'] in r['stdout'] and 'Payload | Receiver' in r['stdout'],dict(characters=len(r['stdout']),next_action=s['checkpoint']['next_action']))
    check('readable_handoff_preserved_exactly',(resumed/'deliverables/discovery-to-design.md').read_bytes()==(OUT/'novice-resume-artifact.md').read_bytes() and all((resumed/'deliverables'/p).is_file() for p in ['start-here.md','current-state-resumed.md','resumed-context.json','final-checks.json']),dict(handoff_hash=sha(resumed/'deliverables/discovery-to-design.md')))
    # Independently execute the saved exploratory SQL against its captured schema.
    sql_probe=cwd/'rerun-saved-query.py'
    sql_probe.write_text('import json,sqlite3,sys\nfrom pathlib import Path\np=Path(sys.argv[1]);s=json.loads(Path(sys.argv[2]).read_text());r=s["records"];db=sqlite3.connect(":memory:");db.row_factory=sqlite3.Row;db.executescript((p/r["S11"]["blob"]).read_text());print(json.dumps({k:[dict(row) for row in db.execute(r[k]["sql"],r[k]["parameters"])] for k in ["Q01","Q04"]}))\n')
    state_path=cwd/'saved-state.json';state_path.write_text(json.dumps(s))
    r=run([sys.executable,sql_probe,resumed,state_path],cwd);rows=data(r)
    expected={('north','R1'):'fulfillment',('north','R2'):'finance-review',('north','R3'):'service-desk',('south','R4'):'fulfillment'}
    observations.append(dict(name='saved_query_rows',rows=rows))
    check('saved_queries_reproduce_13_and_4_rows',len(rows['Q01'])==13 and len(rows['Q04'])==4,dict(naive=len(rows['Q01']),corrected=len(rows['Q04']),columns=list(rows['Q04'][0])))
    # The rows' actual schema is retained for inspection; verify all route values.
    check('saved_query_routes_match_sponsor',sorted(v['disposition'] for v in rows['Q04'])==sorted(expected.values()) and all(v['tenant']==v['customer_tenant'] for v in rows['Q04']),dict(rows=rows['Q04']))
    for label,path in [('ready',rehearsal/'ready-project'),('changed',rehearsal/'project')]:
        r=cli(path,'audit');check(label+'_rehearsal_archive_audits',r['exit_code']==0,data(r))
        r=cli(path,'show');st=data(r)
        r=cli(path,'render','--view','current','--as-of','2026-09-09')
        check(label+'_rehearsal_render_labels_active_simulation',r['exit_code']==0 and 'Active local simulation: **REL2**.' in r['stdout'] and 'No infrastructure deployment is recorded here.' in r['stdout'],dict(activation=st['active_release'],characters=len(r['stdout'])))
        r=cli(path,'check','release','--handoff','HANDOFF','--environment','fixture','--as-of','2026-09-09')
        check(label+'_rehearsal_readiness_expected',r['exit_code']==(0 if label=='ready' else 1),dict(status=data(r)['status'],errors=data(r)['errors']))
    # Run the documented example from elsewhere, then prove it refuses overwrite.
    out=base/'new rehearsal with spaces'
    r=run([sys.executable,ROOT/'examples/order-triage/rehearse.py','--output',out],cwd)
    report=data(r);check('documented_example_runs_from_elsewhere',r['exit_code']==0 and report['failed']==[] and report['naive_rows']==13 and report['corrected_rows']==4,report)
    retained=json.loads((out/'checks.json').read_text());check('example_37_expectations_pass',len(retained)==37 and all(v['passed'] for v in retained),dict(expectations=len(retained)))
    observations.append(dict(name='new_rehearsal_details',checks=retained,events=json.loads((out/'events.json').read_text())))
    before=sha(out/'ready-project/HEAD');r=run([sys.executable,ROOT/'examples/order-triage/rehearse.py','--output',out],cwd)
    check('documented_example_refuses_existing_output',r['exit_code']!=0 and 'never overwritten' in r['stderr'] and sha(out/'ready-project/HEAD')==before,dict(exit_code=r['exit_code'],stderr=r['stderr']))
    empty=base/'new empty project';assert cli(empty,'init','--title','Review empty','--scope','unknown','--owner','unknown')['exit_code']==0
    r=cli(empty,'render','--view','current','--as-of','2026-09-09');check('missing_checkpoint_gets_focused_instruction',r['exit_code']==0 and 'No checkpoint saved. Capture the current task, unresolved questions and next action before handing off.' in r['stdout'],dict(render=r['stdout']))
    before=(resumed/'HEAD').read_bytes();r=cli(resumed,'context','C24','--as-of','bad-date');check('bad_date_is_structured_error_and_preserves_state',r['exit_code']==2 and 'Traceback' not in r['stderr'] and (resumed/'HEAD').read_bytes()==before,data(r))

r=run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_workflow.py','-q']);check('workflow_regression_suite',r['exit_code']==0,dict(stdout=r['stdout'],stderr=r['stderr']))
check('original_evidence_preserved',files_hash(originals)==original_hashes,original_hashes)
check('candidate_after',all(sha(ROOT/p)==h for p,h in manifest.items()),dict(entries=len(manifest),candidate_sha256=sha(OUT/'candidate.json')))
(OUT/'product-evidence.json').write_text(json.dumps(dict(checks=checks,observations=observations,commands=commands),indent=2)+'\n')
for c in checks:print(('PASS ' if c['passed'] else 'FAIL ')+c['name']+': '+json.dumps(c['details'],sort_keys=True))
print(json.dumps(dict(checks=len(checks),failed=[v['name'] for v in checks if not v['passed']],commands=len(commands)),sort_keys=True))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
