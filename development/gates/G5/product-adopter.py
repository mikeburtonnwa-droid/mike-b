"""Independent G5 adopter checks; persistent command/result journal and private copies."""
import atexit
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
import shutil,subprocess,sys,tempfile

ROOT=Path(__file__).resolve().parents[3]
GATE=Path(__file__).resolve().parent
COMMIT='a0e93349b556709290068ef9aa8d3288de9122af'
DATE=datetime.now(timezone.utc).date().isoformat()
JOURNAL=GATE/'product-adopter-commands.jsonl'
STREAM=JOURNAL.open('x',encoding='utf-8')
checks=[];commands=[];completed=False
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1')
env.pop('PYTHONPATH',None)

def write(event):
    STREAM.write(json.dumps(event,ensure_ascii=False)+'\n');STREAM.flush()

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run(argv,cwd,custom_env=None):
    argv=[str(x) for x in argv]
    entry=dict(index=len(commands)+1,argv=argv,cwd=str(cwd),started_at=datetime.now(timezone.utc).isoformat())
    write(dict(entry,state='started'))
    try:
        p=subprocess.run(argv,cwd=cwd,env=custom_env or env,capture_output=True,text=True)
        entry.update(stdout=p.stdout,stderr=p.stderr,exit_code=p.returncode,state='completed')
    except BaseException as error:
        entry.update(stdout='',stderr=repr(error),exit_code=None,state='interrupted')
        raise
    finally:
        entry['finished_at']=datetime.now(timezone.utc).isoformat()
        commands.append(entry);write(entry)
    return entry

def value(event):return json.loads(event['stdout'] or event['stderr'])

def check(name,passed,details):
    item=dict(name=name,passed=bool(passed),details=details,command_index=len(commands))
    checks.append(item);write(dict(kind='assertion',**item))
    print(('PASS ' if passed else 'FAIL ')+name+': '+json.dumps(details,sort_keys=True),flush=True)
    if not passed:raise AssertionError(name)

@atexit.register
def finish():
    summary=dict(completed=completed,checks=len(checks),failed=[x['name'] for x in checks if not x['passed']],commands=len(commands),assertions=checks)
    with (GATE/'product-adopter-summary.json').open('x',encoding='utf-8') as p:p.write(json.dumps(summary,indent=2)+'\n')
    STREAM.close()

manifest=json.loads((GATE/'candidate.json').read_text())
check('candidate_before',all(sha(ROOT/k)==v for k,v in manifest.items()),dict(entries=len(manifest),candidate_sha256=sha(GATE/'candidate.json')))
with tempfile.TemporaryDirectory(prefix='aa-g5-product-') as temp:
    base=Path(temp);clone=base/'adopter clone';cwd=base/'unrelated working directory';cwd.mkdir()
    r=run(['git','clone','--no-local','--quiet',ROOT,clone],cwd)
    check('independent_git_clone',r['exit_code']==0,dict(exit_code=r['exit_code'],stderr=r['stderr']))
    r=run(['git','checkout','--detach',COMMIT],clone)
    check('frozen_source_checked_out',r['exit_code']==0,dict(exit_code=r['exit_code'],stderr=r['stderr']))
    r=run(['git','rev-parse','HEAD'],clone)
    check('source_commit_identity',r['stdout'].strip()==COMMIT,dict(commit=r['stdout'].strip()))
    check('clone_matches_every_product_hash',all(sha(clone/k)==v for k,v in manifest.items()),dict(entries=len(manifest)))
    venv=base/'empty venv'
    r=run([sys.executable,'-S','-m','venv','--without-pip',venv],cwd)
    check('empty_virtual_environment',r['exit_code']==0,dict(exit_code=r['exit_code']))
    python=venv/'bin/python3';isolated=dict(env,PATH=str(venv/'bin')+os.pathsep+env.get('PATH',''))
    r=run([python,'-c','import importlib.util,json,sys; print(json.dumps({"prefix":sys.prefix,"base_prefix":sys.base_prefix,"pip_available":importlib.util.find_spec("pip") is not None}))'],cwd,isolated)
    v=value(r);check('nested_python_is_isolated',v['prefix']!=v['base_prefix'] and not v['pip_available'],v)
    r=run([python,'-S',clone/'scripts/aa.py','--version'],cwd,isolated)
    check('version_without_project_or_site_packages',r['exit_code']==0 and r['stdout']=='agent-architect 0.1.0\n',dict(stdout=r['stdout'],stderr=r['stderr']))
    r=run([python,'-S','scripts/check_library.py'],clone,isolated)
    check('documented_library_check',r['exit_code']==0 and value(r)['status']=='pass',value(r))
    r=run([python,'-S','-m','unittest','discover','-s','tests','-v'],clone,isolated)
    check('documented_complete_regression',r['exit_code']==0 and 'Ran 86 tests' in r['stderr'],dict(exit_code=r['exit_code'],result_tail=r['stderr'].splitlines()[-5:]))

    project=base/'private invoice discovery'
    def cli(*args,target=project):return run([python,'-S',clone/'scripts/aa.py','--project',target,*args],cwd,isolated)
    def rev(target=project):return str(value(cli('show',target=target))['revision'])
    def save_file(name,data):
        path=cwd/name;path.write_text(json.dumps(data),encoding='utf-8');return path
    def capture(rid,text):
        path=cwd/(rid+'.txt');path.write_text(text,encoding='utf-8')
        return cli('source','--id',rid,'--title',rid,'--file',path,'--kind','interview','--locator','Synthetic adopter probe, line 1','--environment','practice','--captured-on',DATE,'--expect-revision',rev())
    r=cli('init','--title','Synthetic invoice discovery','--scope','unknown','--owner','unknown')
    check('adapted_project_starts_with_unknowns',r['exit_code']==0,value(r))
    r=capture('FIRST','Synthetic interview: the intake clerk receives an invoice and sends it for review; the overall owner and exception route are unknown.\n')
    check('adapted_input_captured',r['exit_code']==0,value(r))
    records=[dict(id='ACCOUNT',type='claim',title='Invoice intake account',description='Synthetic interview, not observed process',status='reported',assertion='The clerk sends received invoices for review.',applicability='Routine invoice intake',evidence=[dict(source='FIRST',locator='line 1')]),
             dict(id='OWNER',type='issue',title='Unknown owner and exceptions',description='First interview is incomplete',status='open',owner='unknown',critical=True,next_action='Ask the receiving reviewer for a routine and an exception example',evidence=[dict(source='FIRST',locator='line 1')])]
    r=cli('put',save_file('records.json',records),'--expect-revision',rev())
    check('guide_managed_record_inputs_save',r['exit_code']==0,value(r))
    checkpoint=dict(current_task='Clarify invoice ownership and exceptions',completed=['Captured first invoice interview'],unresolved=['Overall owner unknown','Exception route unknown'],next_action='Ask the receiving reviewer for a routine and an exception example',relevant_ids=['ACCOUNT','OWNER','FIRST'],stage='discovery')
    r=cli('checkpoint',save_file('checkpoint.json',checkpoint),'--expect-revision',rev())
    check('adapted_checkpoint_saves',r['exit_code']==0,value(r))
    r=cli('context','not-present-word','--as-of',DATE)
    check('saved_handoff_resumes_without_chat',r['exit_code']==0 and value(r)['checkpoint']==checkpoint and value(r)['brief']['owner']=='unknown',dict(checkpoint=value(r)['checkpoint'],brief=value(r)['brief']))
    r=cli('render','--view','current','--as-of',DATE)
    check('incomplete_map_and_next_action_are_explicit',r['exit_code']==0 and 'map requires start and end nodes' in r['stdout'] and 'Next action: **'+checkpoint['next_action']+'**' in r['stdout'] and 'No local simulation is activated.' in r['stdout'],dict(characters=len(r['stdout'])))
    backup=base/'restored private project';shutil.copytree(project,backup)
    r=cli('audit',target=backup)
    check('whole_project_backup_is_portable',r['exit_code']==0 and value(r)['commits']==4,value(r))
    r=cli('context','ACCOUNT','--as-of',DATE,target=backup)
    ctx=value(r)
    check('relocated_context_keeps_source_and_uncertainty',{'ACCOUNT','FIRST'}<={x['id'] for x in ctx['records']} and any('reported, freshness=unknown' in w for w in ctx['warnings']) and ctx['checkpoint']==checkpoint,dict(warnings=ctx['warnings'],record_ids=[x['id'] for x in ctx['records']]))
    original_head=(project/'HEAD').read_text().strip()
    r=capture('CLARIFY','Synthetic clarification: Invoice Operations owns receipt through recorded review outcome; shipment and payment are outside this discovery.\n')
    check('clarification_input_captured',r['exit_code']==0,value(r))
    brief=dict(title='Invoice review boundary',scope='Receipt through recorded review outcome',owner='Invoice Operations',rationale='Captured clarification',evidence=[dict(source='CLARIFY',locator='line 1')])
    r=cli('brief',save_file('brief.json',brief),'--expect-revision',rev())
    check('adaptation_updates_authoritative_brief',r['exit_code']==0,value(r))
    r=cli('context','scope','--as-of',DATE);current=value(r)
    previous=json.loads((project/'history'/(original_head+'.json')).read_text())['state']
    check('clarified_context_preserves_prior_boundary',current['brief']['owner']=='Invoice Operations' and previous['owner']=='unknown' and 'CLARIFY' in {x['id'] for x in current['records']},dict(current_owner=current['brief']['owner'],historical_owner=previous['owner']))
    before=(project/'HEAD').read_bytes()
    r=cli('checkpoint',cwd/'checkpoint.json','--expect-revision','4')
    check('stale_resume_edit_is_actionable_and_atomic',r['exit_code']==2 and 'reread and reconcile' in value(r)['message'] and (project/'HEAD').read_bytes()==before,value(r))
    r=cli('audit');check('adapted_project_audits',r['exit_code']==0,value(r))

    exercise=base/'retained practice exercise'
    r=run([python,'-S',clone/'examples/order-triage/rehearse.py','--output',exercise],cwd,isolated)
    report=value(r)
    check('documented_example_works_in_isolated_clone',r['exit_code']==0 and report['checks']==37 and report['failed']==[] and report['naive_rows']==13 and report['corrected_rows']==4,report)
    expected_outputs=['ready-project','project','current-map.md','proposed-map.md','report.json','checks.json','events.json','resume-context.json','change-impact.json']
    check('documented_outputs_exist',all((exercise/p).exists() for p in expected_outputs),dict(outputs=expected_outputs))
    hashes={p.relative_to(exercise).as_posix():sha(p) for p in exercise.rglob('*') if p.is_file()}
    r=run([python,'-S',clone/'examples/order-triage/rehearse.py','--output',exercise],cwd,isolated)
    after={p.relative_to(exercise).as_posix():sha(p) for p in exercise.rglob('*') if p.is_file()}
    check('g4_error_finding_resolved_without_overwrite',r['exit_code']==2 and r['stderr']=='Cannot run rehearsal: Output must be a new directory; previous evidence is never overwritten\n' and not r['stdout'] and hashes==after,dict(exit_code=r['exit_code'],stderr=r['stderr'],unchanged_files=len(hashes)))
    ready=exercise/'ready-project'
    r=cli('audit',target=ready);check('documented_ready_project_audits',r['exit_code']==0,value(r))
    r=cli('context','routing','--as-of',DATE,target=ready);ctx=value(r)
    check('documented_ready_project_resumes',r['exit_code']==0 and ctx['active_release']=='REL2' and bool(ctx['checkpoint'].get('next_action')),dict(active_release=ctx['active_release'],checkpoint=ctx['checkpoint']))
    r=cli('render','--view','proposed','--as-of',DATE,target=ready)
    check('recovered_proposed_map_disclaims_deployment',r['exit_code']==0 and 'Active local simulation: **REL2**.' in r['stdout'] and 'No infrastructure deployment is recorded here.' in r['stdout'] and 'Payload | Receiver' in r['stdout'],dict(characters=len(r['stdout'])))
    r=run(['git','status','--porcelain'],clone,isolated)
    check('adopter_checks_leave_clone_clean',r['exit_code']==0 and r['stdout']=='',dict(stdout=r['stdout'],stderr=r['stderr']))
check('candidate_after',all(sha(ROOT/k)==v for k,v in manifest.items()),dict(entries=len(manifest),candidate_sha256=sha(GATE/'candidate.json')))
completed=True
print(json.dumps(dict(completed=completed,checks=len(checks),commands=len(commands),failed=[]),sort_keys=True),flush=True)
