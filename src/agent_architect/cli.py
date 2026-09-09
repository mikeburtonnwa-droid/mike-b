"""Agent-facing CLI. A guide skill translates user intent into these commands."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path
from .core import Invalid, Project, context, impact


def load(path):
    return json.loads(Path(path).read_text())


def main(argv=None):
    parser = argparse.ArgumentParser(description='Agent Architect local project tools (Python 3.10+, macOS/Linux).')
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
    supersede = sub.add_parser('supersede', help='Explicitly replace a claim while retaining its history')
    supersede.add_argument('old')
    supersede.add_argument('new')
    supersede.add_argument('--reason', required=True)
    for p in (source, put, checkpoint, supersede):
        p.add_argument('--expect-revision', type=int, required=True)
    ctx = sub.add_parser('context', help='Retrieve relevant evidence with conflicts/freshness visible')
    ctx.add_argument('query', nargs='?', default='')
    ctx.add_argument('--as-of', default=date.today().isoformat())
    imp = sub.add_parser('impact', help='Find transitive dependents of a record')
    imp.add_argument('id')
    sub.add_parser('show', help='Read canonical current records')
    sub.add_parser('audit', help='Check committed history and captured source hashes')
    args = parser.parse_args(argv)
    project = Project(args.project)
    try:
        if args.command == 'init':
            result = project.init(args.title, args.scope, args.owner, args.actor)
        elif args.command == 'source':
            result = project.source(args.id, args.title, Path(args.file).read_bytes(), args.kind,
                                    args.locator, args.captured_on, args.environment,
                                    args.expect_revision, args.actor, args.effective_on)
        elif args.command in ('put', 'checkpoint'):
            result = getattr(project, args.command)(load(args.file), args.expect_revision, args.actor)
        elif args.command == 'supersede':
            result = project.supersede(args.old, args.new, args.reason, args.expect_revision, args.actor)
        elif args.command == 'context':
            result = context(project.read(), args.query, args.as_of)
        elif args.command == 'impact':
            result = impact(project.read(), args.id)
        elif args.command == 'audit':
            result = project.audit()
        else:
            result = project.read()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (Invalid, OSError, ValueError) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
