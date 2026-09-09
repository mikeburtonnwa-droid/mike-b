"""Independent G2 reliability probes; all projects/councils are disposable."""
import hashlib
import importlib.util
import json
import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from agent_architect import core

spec = importlib.util.spec_from_file_location("review_council", ROOT / "scripts/check_council.py")
council = importlib.util.module_from_spec(spec)
spec.loader.exec_module(council)
results = []


def record(name, expected, observed, passed):
    results.append(dict(probe=name, expected=expected, observed=observed, passed=passed))


def note(rid):
    return dict(id=rid, type="note", title=rid, description="Synthetic review note",
                status="active", owner="reviewer", next_action="Check", depends_on=[])


def project(path):
    p = core.Project(path)
    p.init("Review", "Synthetic", "reviewer")
    return p


def writer(path, start, queue, rid):
    start.wait()
    try:
        value = core.Project(path).put(note(rid), 1)
        queue.put(("saved", value["revision"]))
    except core.Invalid as exc:
        queue.put(("rejected", str(exc)))


def interrupted_writer(path, ready):
    original = core.atomic
    def stop_before_head(target, data):
        if target.name == "HEAD":
            ready.set()
            import time
            time.sleep(30)
        return original(target, data)
    with patch.object(core, "atomic", side_effect=stop_before_head):
        core.Project(path).put(note("Interrupted"), 1)


def make_council(root, variant):
    gate_name = "G2" if variant == "missing_previous" else "G1"
    folder = root / "development/gates" / gate_name
    folder.mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "scripts").mkdir()
    (root / "development/PLAN.md").write_text("Synthetic frozen plan\n")
    (root / "docs/CONTRACT.md").write_text("Synthetic candidate A\n")
    shutil.copyfile(ROOT / "scripts/record_development.py", root / "scripts/record_development.py")
    import runpy
    manifest = runpy.run_path(str(root / "scripts/record_development.py"))["manifest"]
    candidate_a = folder / "candidate-a.json"
    candidate_a.write_text(json.dumps(manifest(), sort_keys=True))
    candidate_a_hash = council.sha(candidate_a)
    events, reviews = [], []
    for role in ("one", "two", "three"):
        body = "Verdict: APPROVE\nCandidate: " + candidate_a_hash + "\nSynthetic test report.\n"
        if variant == "contradictory_verdict" and role == "one":
            body = "Verdict: DENY\nBlocker: missing implementation.\nExample of a future report:\nVerdict: APPROVE\n"
        report = folder / (role + ".md")
        report.write_text(body)
        events.extend([
            dict(sender="orchestrator", recipient=role, kind="dispatch",
                 message="Review candidate-a.json SHA-256 " + candidate_a_hash),
            dict(sender=role, recipient="orchestrator", kind="response", message=body),
        ])
        reviews.append(dict(role=role, report=report.name, verdict="APPROVE", hash=council.sha(report)))
    candidate = candidate_a
    if variant == "candidate_substitution":
        (root / "docs/CONTRACT.md").write_text("Synthetic candidate B: unreviewed scope change\n")
        candidate = folder / "candidate-b.json"
        candidate.write_text(json.dumps(manifest(), sort_keys=True))
    decision = dict(gate=gate_name, verdict="PASS", candidate=candidate.name,
                    candidate_hash=council.sha(candidate), reviews=reviews, previous_gates=[])
    (folder / "decision.json").write_text(json.dumps(decision))
    final = dict(sender="orchestrator", recipient="council", kind="decision", message=json.dumps(decision))
    events = [final] + events if variant == "early_decision" else events + [final]
    lines = []
    for index, event in enumerate(events):
        if variant != "missing_time":
            event["time"] = "2026-09-09T12:00:00+00:00"
        event["sequence"] = index + 1
        event["previous_hash"] = hashlib.sha256(lines[-1].encode()).hexdigest() if lines else None
        lines.append(json.dumps(event))
    (folder / "transcript.jsonl").write_text("\n".join(lines) + "\n")
    return gate_name


with tempfile.TemporaryDirectory(prefix="aa-g2-architecture-") as name:
    base = Path(name)
    p = project(base / "competing")
    ctx = multiprocessing.get_context("fork")
    start, queue = ctx.Event(), ctx.Queue()
    workers = [ctx.Process(target=writer, args=(p.path, start, queue, "N" + str(i))) for i in range(6)]
    for worker in workers:
        worker.start()
    start.set()
    outcomes = [queue.get(timeout=10) for _ in workers]
    for worker in workers:
        worker.join(10)
    saved = sum(x[0] == "saved" for x in outcomes)
    observed = dict(saved=saved, rejected=6-saved, revision=p.read()["revision"], commits=p.audit()["commits"])
    record("competing_writers", "one saved, five rejected, revision/commits 2", observed,
           observed == dict(saved=1, rejected=5, revision=2, commits=2))

    p = project(base / "killed")
    before = p.head()[0]
    ready = ctx.Event()
    child = ctx.Process(target=interrupted_writer, args=(p.path, ready))
    child.start()
    if not ready.wait(10):
        child.terminate()
        child.join(5)
        raise RuntimeError("Writer did not reach pre-HEAD checkpoint")
    child.terminate()
    child.join(5)
    unchanged = p.head()[0] == before and "Interrupted" not in p.read()["records"]
    p.put(note("Recovered"), 1)
    observed = dict(pre_head_unchanged=unchanged, recovery_revision=p.read()["revision"], commits=p.audit()["commits"])
    record("killed_pre_head_writer", "no partial commit; lock recovers", observed,
           observed == dict(pre_head_unchanged=True, recovery_revision=2, commits=2))

    p = project(base / "post_head")
    before = p.head()[0]
    original_replace, original_fsync = core.os.replace, core.os.fsync
    replaced = [False]
    def replacing(src, dst):
        value = original_replace(src, dst)
        if Path(dst).name == "HEAD":
            replaced[0] = True
        return value
    def syncing(fd):
        if replaced[0]:
            raise OSError("injected post-HEAD directory fsync failure")
        return original_fsync(fd)
    error = None
    with patch.object(core.os, "replace", side_effect=replacing), patch.object(core.os, "fsync", side_effect=syncing):
        try:
            p.put(note("Published"), 1)
        except OSError as exc:
            error = str(exc)
    observed = dict(error=error, head_changed=p.head()[0] != before,
                    revision=p.read()["revision"], record_present="Published" in p.read()["records"])
    record("post_head_fsync_failure", "failure must not be presented as an unapplied mutation", observed,
           error is None or not observed["head_changed"])

    p = project(base / "history")
    initial = p.head()[0]
    p.put(note("N1"), 1)
    old_path = p.path / "history" / (initial + ".json")
    old = json.loads(old_path.read_text())
    old["actor"] = "tampered historical actor"
    old_path.write_text(json.dumps(old))
    before = p.head()[0]
    rejected = []
    for operation in (p.audit, lambda: p.put(note("N2"), 2)):
        try:
            operation()
            rejected.append(False)
        except core.Invalid:
            rejected.append(True)
    record("historical_tampering", "audit and mutation reject; HEAD unchanged",
           dict(rejected=rejected, head_unchanged=p.head()[0] == before),
           all(rejected) and p.head()[0] == before)

    p = project(base / "malformed")
    incoming = base / "bad.json"
    incoming.write_text("[null]")
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/aa.py"), "--project", str(p.path),
                           "put", str(incoming), "--expect-revision", "1"], capture_output=True, text=True)
    try:
        structured = json.loads(proc.stderr).get("status") == "error"
    except ValueError:
        structured = False
    observed = dict(exit=proc.returncode, structured_error=structured,
                    traceback="Traceback" in proc.stderr, revision=p.read()["revision"])
    record("malformed_cli_record", "exit 2 with JSON error and unchanged revision 1", observed,
           observed == dict(exit=2, structured_error=True, traceback=False, revision=1))

    for variant in ("valid", "candidate_substitution", "contradictory_verdict",
                    "early_decision", "missing_time", "missing_previous"):
        gate_root = base / ("council_" + variant)
        gate = make_council(gate_root, variant)
        try:
            outcome = council.check_gate(gate_root, gate, current=True)["status"]
        except (ValueError, OSError, KeyError, TypeError) as exc:
            outcome = "rejected: " + str(exc)
        should_pass = variant == "valid"
        record("council_" + variant, "pass" if should_pass else "reject", outcome,
               (outcome == "pass") == should_pass)

for result in results:
    print(json.dumps(result, sort_keys=True))
print(json.dumps(dict(total=len(results), passed=sum(x["passed"] for x in results),
                      failed=sum(not x["passed"] for x in results)), sort_keys=True))
raise SystemExit(1 if any(not x["passed"] for x in results) else 0)

