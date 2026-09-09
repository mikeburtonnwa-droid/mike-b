"""Validated records and crash-safe, locally tamper-evident project history.

Each commit is one immutable envelope. Only the small HEAD pointer is replaced.
An interrupted pre-HEAD write leaves an unreachable object, never a half commit.
The local filesystem is trusted for access control; hashes do not authenticate users.
"""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path


class Invalid(ValueError):
    """An input or stored artifact violates the project contract."""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def day(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise Invalid(f'Expected YYYY-MM-DD, got {value!r}')
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise Invalid(str(exc)) from exc


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,79}', value):
        raise Invalid(f'Invalid stable ID: {value!r}')
    return value


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise Invalid(f'{label}: nonempty text required')


# Optional fields are still typed. Unknown fields fail rather than silently becoming typos.
BASE = {'id': str, 'type': str, 'title': str, 'description': str, 'status': str,
        'depends_on': list, 'evidence': list, 'tags': list}
SPECS = {
    'source': {'kind': str, 'locator': str, 'captured_on': str, 'effective_on': str,
               'environment': str, 'content_hash': str, 'blob': str},
    'claim': {'assertion': str, 'applicability': str, 'verified_on': str, 'review_due': str,
              'verification': str, 'conflicts_with': list, 'superseded_by': str,
              'supersedes': str, 'rationale': str},
    'note': {'owner': str, 'next_action': str},
    'issue': {'critical': bool, 'owner': str, 'next_action': str, 'resolution': str},
}
REQUIRED = {
    'source': ['kind', 'locator', 'captured_on', 'environment', 'content_hash', 'blob'],
    'claim': ['assertion', 'applicability'],
    'note': ['owner', 'next_action'],
    'issue': ['critical', 'owner', 'next_action'],
}
STATUSES = {'source': {'captured'},
            'claim': {'reported', 'inferred', 'verified', 'disputed', 'superseded'},
            'note': {'active', 'archived'}, 'issue': {'open', 'resolved'}}


def dependencies(record):
    """Knowledge prerequisites, excluding process control flow and symmetric conflicts."""
    return set(record.get('depends_on', [])) | {x['source'] for x in record.get('evidence', [])}


def closure(records, roots):
    pending, visited = list(roots), set()
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        if current not in records:
            raise Invalid(f'Missing reference: {current}')
        visited.add(current)
        pending.extend(dependencies(records[current]) - visited)
    return visited


def validate_record(record):
    if not isinstance(record, dict):
        raise Invalid('Each record must be an object')
    rid = identifier(record.get('id'))
    kind = record.get('type')
    if not isinstance(kind, str) or kind not in SPECS:
        raise Invalid(f'{rid}: unsupported type {kind!r}')
    spec = BASE | SPECS[kind]
    unknown = set(record) - set(spec)
    if unknown:
        raise Invalid(f'{rid}: unknown fields {sorted(unknown)}')
    for field in ['id', 'type', 'title', 'description', 'status', *REQUIRED[kind]]:
        if field not in record:
            raise Invalid(f'{rid}.{field}: required')
    for field, value in record.items():
        if type(value) is not spec[field]:
            raise Invalid(f'{rid}.{field}: expected {spec[field].__name__}')
        if spec[field] is str:
            text(value, f'{rid}.{field}')
    if record['status'] not in STATUSES[kind]:
        raise Invalid(f'{rid}: invalid status {record["status"]}')
    for field in ('depends_on', 'conflicts_with'):
        for ref in record.get(field, []):
            identifier(ref)
            if ref == rid:
                raise Invalid(f'{rid}: self-reference in {field}')
    for tag in record.get('tags', []):
        text(tag, f'{rid}.tags')
    for item in record.get('evidence', []):
        if not isinstance(item, dict) or set(item) != {'source', 'locator'}:
            raise Invalid(f'{rid}: evidence requires source and locator')
        identifier(item['source'])
        text(item['locator'], f'{rid}.evidence.locator')
    for field in ('captured_on', 'effective_on', 'verified_on', 'review_due'):
        if field in record:
            day(record[field])
    if kind == 'claim':
        if not record.get('evidence'):
            raise Invalid(f'{rid}: claims require attributable evidence, including inferences')
        if record['status'] == 'verified':
            for field in ('verified_on', 'review_due', 'verification'):
                text(record.get(field), f'{rid}.{field}')
        if 'verified_on' in record and 'review_due' in record and day(record['review_due']) < day(record['verified_on']):
            raise Invalid(f'{rid}: review_due precedes verification')
        if record['status'] == 'superseded' and not record.get('superseded_by'):
            raise Invalid(f'{rid}: superseded claim needs replacement')
    if kind == 'source':
        if record['kind'] not in {'interview', 'observation', 'document', 'schema', 'query-result', 'research'}:
            raise Invalid(f'{rid}: invalid source kind')
        if not re.fullmatch(r'[a-f0-9]{64}', record['content_hash']):
            raise Invalid(f'{rid}: invalid content hash')
        if record['blob'] != f'sources/{record["content_hash"]}.blob':
            raise Invalid(f'{rid}: invalid captured source path')
    if kind == 'issue' and record['status'] == 'resolved':
        text(record.get('resolution'), f'{rid}.resolution')
        if not record.get('evidence'):
            raise Invalid(f'{rid}: resolved issue needs evidence')


def validate_state(state):
    if state.get('schema_version') != 1:
        raise Invalid('Unsupported schema_version')
    if state.get('stage') not in {'intake', 'discovery', 'design', 'build', 'release', 'operate'}:
        raise Invalid('Invalid stage')
    records = state['records']
    for rid, record in records.items():
        validate_record(record)
        if rid != record['id']:
            raise Invalid('Record key differs from ID')
        for ref in dependencies(record):
            if ref not in records:
                raise Invalid(f'{rid}: missing dependency {ref}')
        for evidence in record.get('evidence', []):
            if records[evidence['source']]['type'] != 'source':
                raise Invalid(f'{rid}: evidence must reference a source')
        if record['type'] == 'claim':
            for ref in record.get('conflicts_with', []):
                if ref not in records or records[ref]['type'] != 'claim' or rid not in records[ref].get('conflicts_with', []):
                    raise Invalid(f'{rid}: conflict must be bilateral with a claim: {ref}')
            if record.get('conflicts_with') and record['status'] == 'verified':
                raise Invalid(f'{rid}: unresolved conflicts cannot be verified')
            for field, reverse in [('superseded_by', 'supersedes'), ('supersedes', 'superseded_by')]:
                if field in record:
                    ref = record[field]
                    if ref not in records or records[ref]['type'] != 'claim' or records[ref].get(reverse) != rid:
                        raise Invalid(f'{rid}: nonreciprocal supersession')
            if 'superseded_by' in record and record['status'] != 'superseded':
                raise Invalid(f'{rid}: replacement requires superseded status')
    # Iterative DFS allows large records without recursion depth surprises.
    for graph in ({k: dependencies(v) for k, v in records.items()},
                  {k: {v['superseded_by']} if v.get('superseded_by') else set() for k, v in records.items()}):
        done = set()
        for start in graph:
            stack, active = [(start, False)], set()
            while stack:
                node, closing = stack.pop()
                if closing:
                    active.remove(node)
                    done.add(node)
                elif node in active:
                    raise Invalid(f'Dependency/supersession cycle at {node}')
                elif node not in done:
                    active.add(node)
                    stack.append((node, True))
                    stack.extend((dep, False) for dep in graph[node])
    checkpoint = state.get('checkpoint', {})
    for rid in checkpoint.get('relevant_ids', []):
        if rid not in records:
            raise Invalid(f'Checkpoint references missing record {rid}')


def atomic(path, data):
    """Atomic replace with flush; parent must already exist on the same filesystem."""
    fd, name = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Project:
    def __init__(self, path):
        self.path = Path(path).expanduser().resolve()

    @contextmanager
    def locked(self):
        self.path.mkdir(parents=True, exist_ok=True)
        with (self.path / '.lock').open('a') as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise Invalid('Project is busy; retry after the current writer finishes') from exc
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def envelope(self, key):
        if not isinstance(key, str) or not re.fullmatch(r'[a-f0-9]{64}', key):
            raise Invalid('Invalid commit pointer')
        try:
            envelope = json.loads((self.path / 'history' / f'{key}.json').read_text())
        except (OSError, ValueError) as exc:
            raise Invalid(f'Missing or unreadable history object {key}') from exc
        if digest(envelope) != key or digest(envelope['state']) != envelope['after_hash']:
            raise Invalid(f'History integrity failure: {key}')
        return envelope

    def head(self):
        try:
            key = (self.path / 'HEAD').read_text().strip()
        except FileNotFoundError as exc:
            raise Invalid(f'No project at {self.path}; run init first') from exc
        return key, self.envelope(key)

    def read(self):
        state = self.head()[1]['state']
        validate_state(state)
        self.check_sources(state)
        return state

    def check_sources(self, state):
        for record in state['records'].values():
            if record['type'] == 'source':
                p = self.path / record['blob']
                if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != record['content_hash']:
                    raise Invalid(f'{record["id"]}: missing, replaced or tampered captured source')

    def audit(self):
        key, envelope = self.head()
        count, seen = 0, set()
        while True:
            if key in seen:
                raise Invalid('History cycle')
            seen.add(key)
            validate_state(envelope['state'])
            self.check_sources(envelope['state'])
            count += 1
            parent = envelope['parent']
            if parent is None:
                if envelope['state']['revision'] != 1 or envelope['before_hash'] is not None:
                    raise Invalid('Invalid initial revision')
                break
            previous = self.envelope(parent)
            if previous['after_hash'] != envelope['before_hash'] or previous['state']['revision'] + 1 != envelope['state']['revision']:
                raise Invalid('Broken revision chain')
            key, envelope = parent, previous
        return {'status': 'pass', 'commits': count, 'head': self.head()[0],
                'limit': 'Local hash consistency; does not authenticate authors or truth.'}

    def commit(self, state, parent, before_hash, actor, operation):
        text(actor, 'actor')
        validate_state(state)
        self.check_sources(state)
        envelope = dict(state=state, parent=parent, before_hash=before_hash,
                        after_hash=digest(state), actor=actor, operation=operation, time=now())
        key = digest(envelope)
        (self.path / 'history').mkdir(exist_ok=True)
        atomic(self.path / 'history' / f'{key}.json', canonical(envelope))
        try:
            atomic(self.path / 'HEAD', (key + '\n').encode())
        except OSError:
            # HEAD replacement is the commit point; a subsequent flush can fail.
            if (self.path / 'HEAD').exists() and (self.path / 'HEAD').read_text().strip() == key:
                return {'status': 'committed-durability-uncertain', 'revision': state['revision'],
                        'commit': key, 'warning': 'Commit is visible; durability flush failed. Inspect/audit and back up before continuing; do not blindly retry.'}
            raise
        return {'status': 'saved', 'revision': state['revision'], 'commit': key}

    def init(self, title, scope, owner, actor='local-user'):
        for label, value in [('title', title), ('scope', scope), ('owner', owner)]:
            text(value, label)
        with self.locked():
            if (self.path / 'HEAD').exists():
                raise Invalid('Project already exists; initialization never overwrites it')
            state = dict(schema_version=1, title=title, scope=scope, owner=owner,
                         id='project', stage='intake', created=now(), updated=now(), revision=1,
                         records={}, checkpoint={}, releases={}, active_release=None)
            return self.commit(state, None, None, actor, 'init')

    def mutate(self, operation, callback, expected, actor='local-user'):
        with self.locked():
            self.audit()
            key, envelope = self.head()
            state = copy.deepcopy(envelope['state'])
            if expected != state['revision']:
                raise Invalid(f'Stale revision: expected {expected}, current {state["revision"]}; reread and reconcile')
            callback(state)
            state['revision'] += 1
            state['updated'] = now()
            return self.commit(state, key, envelope['after_hash'], actor, operation)

    def put(self, incoming, expected, actor='local-user'):
        if not isinstance(incoming, list):
            incoming = [incoming]
        if not incoming:
            raise Invalid('No records supplied')
        for record in incoming:
            validate_record(record)
        ids = [r['id'] for r in incoming]
        if len(set(ids)) != len(ids):
            raise Invalid('Duplicate IDs in batch')
        def update(state):
            for record in incoming:
                validate_record(record)
                rid = record['id']
                old = state['records'].get(rid)
                if record['type'] == 'source' or (old and old['type'] == 'source'):
                    raise Invalid('Sources are immutable; use source to capture a new record')
                if old and old['type'] != record['type']:
                    raise Invalid(f'{rid}: cannot change record type')
                if record['type'] == 'claim':
                    if old and old.get('superseded_by'):
                        raise Invalid(f'{rid}: superseded history is immutable')
                    for field in ('supersedes', 'superseded_by'):
                        if record.get(field) != (old or {}).get(field):
                            raise Invalid('Use supersede to change replacement links')
                    if old and old['assertion'] != record['assertion']:
                        raise Invalid('Use a new claim and supersede; assertions cannot be rewritten')
                    if old and old['applicability'] != record['applicability']:
                        raise Invalid('Changed applicability requires a separate claim and verification')
                state['records'][rid] = copy.deepcopy(record)
        return self.mutate('put ' + ','.join(ids), update, expected, actor)

    def source(self, rid, title, content, kind, locator, captured_on, environment, expected, actor='local-user', effective_on=None):
        identifier(rid)
        if not isinstance(content, bytes) or not content:
            raise Invalid('Source content must be nonempty bytes')
        hashed = hashlib.sha256(content).hexdigest()
        record = dict(id=rid, type='source', title=title, description=title, status='captured',
                      kind=kind, locator=locator, captured_on=captured_on, environment=environment,
                      content_hash=hashed, blob=f'sources/{hashed}.blob')
        if effective_on:
            record['effective_on'] = effective_on
        validate_record(record)
        def update(state):
            if rid in state['records']:
                raise Invalid(f'ID already exists: {rid}')
            (self.path / 'sources').mkdir(exist_ok=True)
            p = self.path / record['blob']
            if p.exists():
                if p.is_symlink() or p.read_bytes() != content:
                    raise Invalid('Existing content object failed integrity check')
            else:
                atomic(p, content)
            state['records'][rid] = record
        return self.mutate('source ' + rid, update, expected, actor)

    def supersede(self, old_id, new_id, reason, expected, actor='local-user'):
        text(reason, 'supersession rationale')
        def update(state):
            records = state['records']
            if old_id == new_id or any(rid not in records or records[rid]['type'] != 'claim' for rid in (old_id, new_id)):
                raise Invalid('Supersession requires two different existing claims')
            old, new = records[old_id], records[new_id]
            if old['status'] == 'superseded' or new['status'] == 'superseded' or 'supersedes' in new:
                raise Invalid('Supersession endpoints already replaced or linked')
            if old['applicability'] != new['applicability']:
                raise Invalid('Different applicability: retain as variants, not supersession')
            old.update(status='superseded', superseded_by=new_id, rationale=reason)
            new.update(supersedes=old_id)
            # Replacement explicitly resolves only the conflict between these endpoints.
            old['conflicts_with'] = [x for x in old.get('conflicts_with', []) if x != new_id]
            new['conflicts_with'] = [x for x in new.get('conflicts_with', []) if x != old_id]
        return self.mutate(f'supersede {old_id} -> {new_id}', update, expected, actor)

    def checkpoint(self, value, expected, actor='local-user'):
        required = {'current_task', 'completed', 'unresolved', 'next_action', 'relevant_ids', 'stage'}
        if not isinstance(value, dict) or set(value) != required:
            raise Invalid(f'Checkpoint requires exactly {sorted(required)}')
        for field in ('current_task', 'next_action', 'stage'):
            text(value[field], field)
        for field in ('completed', 'unresolved', 'relevant_ids'):
            if not isinstance(value[field], list) or any(not isinstance(x, str) for x in value[field]):
                raise Invalid(f'{field}: text list required')
        def update(state):
            state['checkpoint'] = copy.deepcopy(value)
            state['stage'] = value['stage']
        return self.mutate('checkpoint', update, expected, actor)


def freshness(record, as_of):
    today = day(as_of)
    if record.get('verified_on') and day(record['verified_on']) > today:
        return 'future-dated'
    if not record.get('review_due'):
        return 'unknown'
    return 'stale' if day(record['review_due']) < today else 'current'


def context(state, query='', as_of=None):
    as_of = as_of or date.today().isoformat()
    day(as_of)
    records = state['records']
    words = query.casefold().split()
    roots = {rid for rid, r in records.items()
             if (not words and r.get('status') != 'superseded') or (words and
                 any(w in json.dumps(r, ensure_ascii=False).casefold() for w in words))}
    selected = closure(records, roots)
    # Dependencies, replacements and conflicts reach one common fixed point.
    while True:
        replacements = {records[rid]['superseded_by'] for rid in selected if records[rid].get('superseded_by')}
        conflicts = {ref for rid in selected for ref in records[rid].get('conflicts_with', [])}
        expanded = closure(records, selected | replacements | conflicts)
        if expanded == selected:
            break
        selected = expanded
    warnings, active, historical = [], [], []
    for rid in sorted(selected):
        r = copy.deepcopy(records[rid])
        if r['type'] == 'claim':
            r['freshness'] = freshness(r, as_of)
            if r['status'] == 'superseded':
                historical.append(r)
                warnings.append(f'{rid} superseded by {r["superseded_by"]}; dependent records may need revision')
                continue
            if r['status'] != 'verified' or r['freshness'] != 'current':
                warnings.append(f'{rid}: {r["status"]}, freshness={r["freshness"]}')
        active.append(r)
    return dict(project=state['title'], revision=state['revision'], as_of=as_of,
                stage=state['stage'], checkpoint=state['checkpoint'], query=query,
                records=active, historical_dependencies=historical, warnings=warnings,
                active_release=state['active_release'], deployment_mode='local-simulation')


def impact(state, rid):
    records = state['records']
    if rid not in records:
        raise Invalid(f'Unknown record: {rid}')
    affected, pending = set(), [rid]
    while pending:
        target = pending.pop()
        for key, value in records.items():
            if target in dependencies(value) and key not in affected and key != rid:
                affected.add(key)
                pending.append(key)
    return {'record': rid, 'affected': sorted(affected)}
