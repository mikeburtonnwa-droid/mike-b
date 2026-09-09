"""G3 r3 integrity probes: preserved integration plus execution identity/replay."""
import hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
gate = ROOT / 'development/gates/G3'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r2_preserved = {name: sha(gate / name) for name in ('candidate-r2.json','integrity-r2.md','integrity-probes-r2.py','integrity-probe-output-r2.txt')}
# Retain the previous independent integration scenarios; only select the new frozen
# candidate. The current synthetic helper supplies fresh run_id/run_at per run.
integration_source = (gate / 'integrity-probes-r2.py').read_text().replace('candidate-r2.json','candidate-r3.json')
exec(compile(integration_source, str(gate / 'integrity-probes-r2.py'), 'exec'))

import uuid
from datetime import datetime, timezone
from support import release, incident

def source_run(p, source_id, at, passed=True, criterion=CRITERION, overrides=None):
    instant = w.run_time(at)
    state = p.read()
    value = dict(environment='test', run_on=instant.date().isoformat(), run_at=at,
                 run_id=str(uuid.uuid4()), command='Synthetic controlled execution event',
                 exit_code=0, criterion=criterion, target_hashes=w.fingerprints(state['records'],['REQ','COMP']),
                 brief_hash=w.brief_hash(state), expected={'success':True}, observed={'success':passed})
    value.update(overrides or {})
    raw = json.dumps(value, sort_keys=True).encode()
    capture(p, source_id, raw, 'query-result', date=max(DATE, value['run_on']))
    return raw

def import_run(p, source_id, evaluation_id, criterion=CRITERION):
    return w.evaluate(p,dict(id=evaluation_id,title=evaluation_id,description='Independent synthetic execution probe',
          targets=['REQ','COMP'],result_source=source_id,valid_until='2026-10-09',criterion=criterion),revision(p))

with tempfile.TemporaryDirectory() as td:
    p = ready_project(Path(td)/'replay', evaluation=False)
    source_run(p,'OLDER',DATE+'T08:00:00+00:00')
    raw = source_run(p,'PASS_SOURCE',DATE+'T10:00:00+00:00')
    assert import_run(p,'PASS_SOURCE','FIRST_PASS')['outcome'] == 'pass'
    assert check(p)['status'] == 'pass'
    source_run(p,'FAIL_SOURCE',DATE+'T11:00:00+00:00',False)
    assert import_run(p,'FAIL_SOURCE','LATEST_FAILURE')['outcome'] == 'fail'
    assert check(p)['status'] == 'fail'
    reject_unchanged(p,lambda:import_run(p,'PASS_SOURCE','SAME_SOURCE_REPLAY'),'Same source replay')
    capture(p,'EXACT_ALIAS',raw,'query-result')
    alias = p.read()['records']['EXACT_ALIAS']
    assert (p.path/alias['blob']).read_bytes() == raw
    reject_unchanged(p,lambda:import_run(p,'EXACT_ALIAS','ALIAS_REPLAY'),'Exact content alias replay')
    capture(p,'REFORMATTED',json.dumps(json.loads(raw),indent=4).encode(),'query-result')
    reject_unchanged(p,lambda:import_run(p,'REFORMATTED','FORMAT_REPLAY'),'Reformatted identity replay')
    assert check(p)['status'] == 'fail'
    print('same_source_exact_alias_and_reformatted_identity_replays_rejected',True)
    import_run(p,'OLDER','BACKFILLED_OLDER_PASS')
    assert check(p)['status'] == 'fail'
    print('older_run_import_order_cannot_promote_evidence',True)
    source_run(p,'TIED_PASS',DATE+'T06:00:00-05:00')
    import_run(p,'TIED_PASS','TIED_PASS_EVAL')
    assert check(p)['status'] == 'fail'
    print('timezone_equivalent_pass_failure_tie_remains_blocked',True)
    source_run(p,'NEW_PASS',DATE+'T12:00:00+00:00')
    import_run(p,'NEW_PASS','GENUINE_LATER_PASS')
    assert check(p)['evaluations'] == ['GENUINE_LATER_PASS']
    print('strictly_later_fresh_identity_pass_restores_readiness',True)
    for i,delta in enumerate([{'run_id':uuid.uuid4().hex},{'run_at':DATE+'T12:00:00'},
                             {'run_at':DATE+'T23:30:00-02:00','run_on':DATE}]):
        source_run(p,'MALFORMED_'+str(i),DATE+'T12:30:00+00:00',overrides=delta)
        reject_unchanged(p,lambda i=i:import_run(p,'MALFORMED_'+str(i),'MALFORMED_EV_'+str(i)),'Invalid identity/time')
    print('canonical_uuid_timezone_and_utc_date_enforced',True)
    release(p)
    p.put(incident(p)|dict(diagnosis='Fixture failure',action='Restore fixture',follow_up='Retest'),revision(p))
    recovery = source_run(p,'RECOVERY_PASS_SOURCE',DATE+'T13:00:00+00:00',criterion='Service recovered')
    import_run(p,'RECOVERY_PASS_SOURCE','RECOVERY_PASS','Service recovered')
    source_run(p,'RECOVERY_FAIL_SOURCE',DATE+'T14:00:00+00:00',False,'Service recovered')
    import_run(p,'RECOVERY_FAIL_SOURCE','RECOVERY_FAILURE','Service recovered')
    capture(p,'RECOVERY_ALIAS',recovery,'query-result')
    reject_unchanged(p,lambda:import_run(p,'RECOVERY_ALIAS','RECOVERY_REPLAY','Service recovered'),'Recovery alias replay')
    reject_unchanged(p,lambda:w.close_incident(p,'INC1','RECOVERY_PASS',DATE,revision(p)),'Old recovery pass')
    assert p.read()['records']['INC1']['status'] == 'open'
    source_run(p,'RECOVERY_NEW_SOURCE',DATE+'T15:00:00+00:00',criterion='Service recovered')
    import_run(p,'RECOVERY_NEW_SOURCE','RECOVERY_NEW','Service recovered')
    w.close_incident(p,'INC1','RECOVERY_NEW',DATE,revision(p))
    assert p.read()['records']['INC1']['status'] == 'closed'
    assert p.audit()['status'] == 'pass'
    print('incident_replay_blocked_and_fresh_later_recovery_closes',True)

assert all(sha(gate/name)==value for name,value in r2_preserved.items())
assert manifest == runpy.run_path(str(ROOT/'scripts/record_development.py'))['manifest']()
print('r2_artifacts_preserved_and_r3_candidate_unchanged',True)
