"""Independent G3 transition probes built on the small synthetic structural fixture."""
import copy
import hashlib
import io
import json
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
from agent_architect import core, workflow as w, cli
from support import DATE, CRITERION, ready_project, release, revision, record, incident, run_result, capture

results = []
def observed(name, expected, value, passed):
    results.append(dict(probe=name, expected=expected, observed=value, passed=passed))
def reject(p, callback):
    before = p.head()[0]
    try:
        callback()
        return dict(rejected=False, head_unchanged=p.head()[0] == before)
    except core.Invalid as exc:
        return dict(rejected=True, head_unchanged=p.head()[0] == before, error=str(exc))
def probe_reject(name, p, callback):
    value = reject(p, callback)
    observed(name, "reject and leave HEAD unchanged", value, value["rejected"] and value["head_unchanged"])
def change(p, rid, **values):
    p.put(p.read()["records"][rid] | values, revision(p))

with tempfile.TemporaryDirectory(prefix="aa-g3-architecture-") as dirname:
    root = Path(dirname)
    counter = [0]
    def fresh():
        counter[0] += 1
        return ready_project(root / ("project-" + str(counter[0])))

    p = fresh()
    release(p)
    pinned = copy.deepcopy(p.read()["releases"]["REL1"])
    result = w.activate(p, "REL1", DATE, "test", "Synthetic activation", revision(p))
    p.put(record("N1", "note", owner="reviewer", next_action="Review"), revision(p))
    value = dict(mode=result["deployment_mode"], active=p.read()["active_release"],
                 snapshot_unchanged=p.read()["releases"]["REL1"] == pinned,
                 changed=w.drift(p.read(), "REL1")["changed"], audit=p.audit()["status"])
    observed("release_activation_and_note", "local simulation, immutable snapshot, no critical drift", value,
             value == dict(mode="local-simulation", active="REL1", snapshot_unchanged=True, changed=[], audit="pass"))
    change(p, "COMP", artifact="different synthetic implementation")
    probe_reject("changed_dependency_rollback", p,
                 lambda: w.activate(p, "REL1", DATE, "test", "Synthetic rollback", revision(p), rollback=True))
    observed("snapshot_after_component_change", "original release unchanged",
             p.read()["releases"]["REL1"] == pinned, p.read()["releases"]["REL1"] == pinned)

    for kind in ("put", "source", "evaluate"):
        p = fresh()
        release(p)
        if kind == "put":
            action = lambda: p.put(record("REL1", "note", owner="reviewer", next_action="Check"), revision(p))
        elif kind == "source":
            action = lambda: capture(p, "REL1", b"synthetic colliding source")
        else:
            action = lambda: w.evaluate(p, dict(id="REL1", title="Reused release ID", description="Synthetic collision",
                targets=["REQ", "COMP"], result_source="RESULT_EV1", valid_until="2026-10-09", criterion=CRITERION), revision(p))
        value = reject(p, action)
        value["id_in_records_and_releases"] = "REL1" in p.read()["records"] and "REL1" in p.read()["releases"]
        observed("release_id_collision_" + kind, "reject globally reused stable ID", value,
                 value["rejected"] and value["head_unchanged"])

    p = fresh()
    run_result(p, "LATER_FAIL", observed={"decisions":2}, run_on="2026-09-10")
    check = w.readiness(p.read(), "2026-09-10", "test", "HANDOFF")
    value = dict(readiness=check["status"], selected=check["evaluations"],
                 later_result=p.read()["records"]["LATER_FAIL"]["status"])
    observed("later_failed_critical_run", "fail readiness until a subsequent passing run resolves the failure", value,
             check["status"] == "fail")
    probe_reject("release_after_later_failed_run", p,
                 lambda: w.create_release(p, "NEW_RELEASE", "HANDOFF", "2026-09-10", "test", "Synthetic test", revision(p)))
    run_result(p, "RECOVERED_RUN", run_on="2026-09-11")
    check = w.readiness(p.read(), "2026-09-11", "test", "HANDOFF")
    observed("passing_run_after_failure", "new passing run restores readiness", dict(status=check["status"], selected=check["evaluations"]),
             check["status"] == "pass" and "RECOVERED_RUN" in check["evaluations"])

    p = fresh()
    release(p)
    run_result(p, "LATER_FAIL", observed={"decisions":2}, run_on="2026-09-10")
    probe_reject("activate_after_later_failed_run", p,
                 lambda: w.activate(p, "REL1", "2026-09-10", "test", "Synthetic test", revision(p)))

    p = fresh()
    release(p)
    p.put(incident(p) | dict(diagnosis="Synthetic defect", action="Restore service", follow_up="Check next run"), revision(p))
    result = dict(environment="test", run_on=DATE, command="Synthetic recovery observation", exit_code=0,
                  criterion="Service recovered", target_hashes=w.fingerprints(p.read()["records"], ["COMP"]),
                  expected={"healthy":True}, observed={"healthy":True})
    capture(p, "FUTURE_RESULT", json.dumps(result).encode(), kind="query-result", date="2026-09-10")
    w.evaluate(p, dict(id="FUTURE_RECOVERY", title="Synthetic recovery", description="Future captured evidence",
                      targets=["COMP"], result_source="FUTURE_RESULT", valid_until="2026-10-09",
                      criterion="Service recovered"), revision(p))
    probe_reject("incident_future_captured_evidence", p,
                 lambda: w.close_incident(p, "INC1", "FUTURE_RECOVERY", DATE, revision(p)))
    observed("incident_future_capture_status", "incident remains open",
             p.read()["records"]["INC1"]["status"], p.read()["records"]["INC1"]["status"] == "open")

    p = fresh()
    release(p)
    p.put(incident(p) | dict(diagnosis="Synthetic defect", action="Restore service", follow_up="Check next run"), revision(p))
    run_result(p, "RECOVERY", criterion="Service recovered", targets=["COMP"])
    w.close_incident(p, "INC1", "RECOVERY", DATE, revision(p))
    value = dict(status=p.read()["records"]["INC1"]["status"], audit=p.audit()["status"])
    observed("valid_incident_recovery", "close with applicable recovery evidence", value,
             value == dict(status="closed", audit="pass"))

    p = fresh()
    probe_reject("stale_release_revision", p,
                 lambda: w.create_release(p, "REL1", "HANDOFF", DATE, "test", "Synthetic test", revision(p)-1))
    before = p.head()[0]
    original_atomic = core.atomic
    def pre_head(path, data):
        if path.name == "HEAD":
            raise OSError("injected pre-HEAD failure")
        return original_atomic(path, data)
    failed = False
    with patch.object(core, "atomic", side_effect=pre_head):
        try:
            release(p)
        except OSError:
            failed = True
    value = dict(error=failed, unchanged=p.head()[0] == before, release_absent="REL1" not in p.read()["releases"], audit=p.audit()["status"])
    observed("pre_head_release_fault", "unapplied release failure preserves history", value,
             value == dict(error=True, unchanged=True, release_absent=True, audit="pass"))
    def post_head(path, data):
        original_atomic(path, data)
        if path.name == "HEAD":
            raise OSError("injected post-HEAD failure")
    with patch.object(core, "atomic", side_effect=post_head):
        response = release(p)
    value = dict(status=response["status"], mode=response["deployment_mode"],
                 present="REL1" in p.read()["releases"], commit_matches=response["commit"] == p.head()[0])
    observed("post_head_release_fault", "explicit visible local-simulation commit uncertainty", value,
             value == dict(status="committed-durability-uncertain", mode="local-simulation", present=True, commit_matches=True))

    for bad in (None, [], {"id":"BAD","type":[]}, {"id":"BAD"}):
        p = fresh()
        file = root / "malformed.json"
        file.write_text(json.dumps(bad))
        stdout, stderr = io.StringIO(), io.StringIO()
        before = p.head()[0]
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = cli.main(["--project", str(p.path), "evaluate", str(file), "--expect-revision", str(revision(p))])
        try:
            structured = json.loads(stderr.getvalue())["status"] == "error"
        except (ValueError, KeyError):
            structured = False
        value = dict(exit=code, json_error=structured, head_unchanged=p.head()[0] == before)
        observed("malformed_evaluation_" + str(len(results)), "exit 2 JSON error without mutation", value,
                 value == dict(exit=2, json_error=True, head_unchanged=True))

for row in results:
    print(json.dumps(row, sort_keys=True))
print(json.dumps(dict(total=len(results), passed=sum(x["passed"] for x in results), failed=sum(not x["passed"] for x in results)), sort_keys=True))
raise SystemExit(1 if any(not x["passed"] for x in results) else 0)

