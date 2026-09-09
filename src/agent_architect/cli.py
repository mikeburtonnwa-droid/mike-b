"""Agent-facing CLI. A guide skill translates user intent into these commands."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path
from .core import Invalid, Project, context, impact
from . import workflow
from . import __version__


def load(path):
    return json.loads(Path(path).read_text())


def main(argv=None):
    parser = argparse.ArgumentParser(description='Agent Architect local project tools (Python 3.10+, macOS/Linux).')
    parser.add_argument('--version', action='version', version='agent-architect ' + __version__)
    parser.add_argument('--project', required=True, help='Adopter project directory, separate from the public library')
    parser.add_argument('--actor', default='local-user')
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init', help='Create a project; never overwrite an existing one')
    for field in ('title', 'scope', 'owner'):
        init.add_argument('--' + field, required=True)
    source = sub.add_parser('source', help='Capture original material and its provenance')
    for field in ('id', 'title', 'file', 'kind', 'locator', 'environment'):
        source.add_argument('--' + field, required=True)
    source.add_argument('--captured-on', default=date.today().isoformat())
    source.add_argument('--effective-on')
    put = sub.add_parser('put', help='Validate and atomically save one JSON record or a batch')
    put.add_argument('file')
    checkpoint = sub.add_parser('checkpoint', help='Save progress for a new session')
    checkpoint.add_argument('file')
    brief = sub.add_parser('brief', help='Revise the current brief with captured clarification and rationale')
    brief.add_argument('file')
    supersede = sub.add_parser('supersede', help='Explicitly replace a claim while retaining its history')
    supersede.add_argument('old')
    supersede.add_argument('new')
    supersede.add_argument('--reason', required=True)
    for p in (source, put, checkpoint, supersede, brief):
        p.add_argument('--expect-revision', type=int, required=True)
    ctx = sub.add_parser('context', help='Retrieve relevant evidence with conflicts/freshness visible')
    ctx.add_argument('query', nargs='?', default='')
    ctx.add_argument('--as-of', default=date.today().isoformat())
    imp = sub.add_parser('impact', help='Find transitive dependents of a record')
    imp.add_argument('id')
    sub.add_parser('show', help='Read canonical current records')
    sub.add_parser('audit', help='Check committed history and captured source hashes')
    sub.add_parser('schema', help='Describe record fields, required inputs and statuses')
    fingerprint = sub.add_parser('fingerprint', help='Capture target dependency hashes before executing an evaluation')
    fingerprint.add_argument('ids', nargs='+')
    query_fingerprint = sub.add_parser('query-fingerprint', help='Capture query definition and asset fingerprints before execution')
    query_fingerprint.add_argument('id')
    bind = sub.add_parser('bind-query', help='Bind captured execution results to a matching draft query')
    bind.add_argument('id')
    bind.add_argument('--result', required=True)
    check = sub.add_parser('check', help='Report structural process, architecture or release blockers')
    check.add_argument('area', choices=['process', 'architecture', 'release'])
    check.add_argument('--view', choices=['current', 'proposed'], default='current')
    check.add_argument('--handoff')
    check.add_argument('--environment')
    view = sub.add_parser('render', help='Print a disposable Markdown process/evidence/resume view')
    view.add_argument('--view', choices=['current', 'proposed'], default='current')
    evaluation = sub.add_parser('evaluate', help='Bind captured result JSON to evaluated dependency hashes')
    evaluation.add_argument('file')
    release = sub.add_parser('release', help='Pin a checked local-simulation release')
    release.add_argument('id')
    release.add_argument('--handoff', required=True)
    release.add_argument('--authority', required=True)
    activation = sub.add_parser('activate', help='Record local-simulation activation; does not deploy')
    activation.add_argument('id')
    activation.add_argument('--reason', required=True)
    activation.add_argument('--rollback', action='store_true')
    for p in (release, activation):
        p.add_argument('--environment', required=True)
    changes = sub.add_parser('drift', help='Compare current records with a pinned simulation release')
    changes.add_argument('id')
    close = sub.add_parser('close-incident', help='Close only with successful applicable recovery evidence')
    close.add_argument('id')
    close.add_argument('--evaluation', required=True)
    for p in (check, view, release, activation, close):
        p.add_argument('--as-of', default=date.today().isoformat())
    for p in (evaluation, release, activation, close, bind):
        p.add_argument('--expect-revision', type=int, required=True)
    args = parser.parse_args(argv)
    project = Project(args.project)
    try:
        if args.command == 'init':
            result = project.init(args.title, args.scope, args.owner, args.actor)
        elif args.command == 'source':
            result = project.source(args.id, args.title, Path(args.file).read_bytes(), args.kind,
                                    args.locator, args.captured_on, args.environment,
                                    args.expect_revision, args.actor, args.effective_on)
        elif args.command in ('put', 'checkpoint', 'brief'):
            result = getattr(project, args.command)(load(args.file), args.expect_revision, args.actor)
        elif args.command == 'supersede':
            result = project.supersede(args.old, args.new, args.reason, args.expect_revision, args.actor)
        elif args.command == 'context':
            result = context(project.read(), args.query, args.as_of)
        elif args.command == 'impact':
            result = impact(project.read(), args.id)
        elif args.command == 'audit':
            result = project.audit()
        elif args.command == 'schema':
            from .core import BASE, SPECS, REQUIRED, STATUSES
            result = {kind: dict(fields={f: t.__name__ for f, t in (BASE | spec).items()},
                                 required=['id', 'type', 'title', 'description', 'status'] + REQUIRED[kind],
                                 statuses=sorted(STATUSES[kind])) for kind, spec in SPECS.items()}
        elif args.command == 'fingerprint':
            state = project.read()
            result = dict(target_hashes=workflow.fingerprints(state['records'], args.ids), brief_hash=workflow.brief_hash(state))
        elif args.command == 'query-fingerprint':
            result = workflow.query_fingerprint(project.read(), args.id)
        elif args.command == 'bind-query':
            result = workflow.bind_query(project, args.id, args.result, args.expect_revision, args.actor)
        elif args.command == 'check':
            state = project.read()
            if args.area == 'process':
                result = workflow.process_check(state, args.view)
            elif args.area == 'architecture':
                result = workflow.architecture_check(state)
            else:
                if not args.environment or not args.handoff:
                    raise Invalid('Release check requires --environment and --handoff')
                result = workflow.readiness(state, args.as_of, args.environment, args.handoff)
        elif args.command == 'render':
            print(workflow.render(project.read(), args.as_of, args.view))
            return 0
        elif args.command == 'evaluate':
            result = workflow.evaluate(project, load(args.file), args.expect_revision, args.actor)
        elif args.command == 'release':
            result = workflow.create_release(project, args.id, args.handoff, args.as_of, args.environment,
                                             args.authority, args.expect_revision, args.actor)
        elif args.command == 'activate':
            result = workflow.activate(project, args.id, args.as_of, args.environment, args.reason,
                                       args.expect_revision, args.actor, args.rollback)
        elif args.command == 'drift':
            result = workflow.drift(project.read(), args.id)
        elif args.command == 'close-incident':
            result = workflow.close_incident(project, args.id, args.evaluation, args.as_of, args.expect_revision, args.actor)
        else:
            result = project.read()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1 if result.get('status') == 'fail' else 0
    except (Invalid, OSError, ValueError) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
