# Copyright 2026 James E. Dunn
# SPDX-License-Identifier: Apache-2.0
"""Durable agent bridge CLI. Actual authorized host tools run outside this process."""
import argparse
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from . import profiles as p
from .core import ROOT, PipelineError, load as load_workspace


def read(directory):
    return json.loads((Path(directory)/'profile.json').read_text(encoding='utf-8'))


def save(directory, state):
    directory = Path(directory)
    target = directory/'profile.json'
    if target.is_symlink():
        raise p.ProfileError('Refusing a symlink for the execution journal.')
    fd, temporary = tempfile.mkstemp(prefix='.profile-', suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(state, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        # Persist the directory entry before a caller receives an executable job.
        # A failure stops output; inspect the journal rather than replay a write.
        directory_fd = os.open(str(directory), os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        Path(temporary).unlink(missing_ok=True)


@contextmanager
def locked(directory):
    lock = Path(directory)/'.profile.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise p.ProfileError('Another execution owns the journal lock. Do not bypass it; inspect any stale process and unresolved write first.')
    try:
        os.write(fd, str(os.getpid()).encode())
        yield
    finally:
        os.close(fd)
        lock.unlink()


def initialize(directory, source=None, example=False, now=None):
    destination = Path(directory)
    if destination.exists():
        raise p.ProfileError('Profile workspace already exists; never overwrite execution history.')
    path = Path(source) if source else ROOT/('examples/fictional/linkedin-execution.json' if example else 'templates/linkedin-execution.blank.json')
    state = json.loads(path.read_text(encoding='utf-8'))
    p.ensure(state, now)
    destination.mkdir(parents=True)
    (destination/'.gitignore').write_text('*\n!.gitignore\n', encoding='utf-8')
    save(destination, state)
    return {'created': str(destination), 'fictional': state['fictional'], 'external_actions': 'none'}


def parser():
    root = argparse.ArgumentParser(description='Scoped profile execution bridge; host tools perform any real action.')
    sub = root.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init');init.add_argument('directory')
    choice = init.add_mutually_exclusive_group();choice.add_argument('--example', action='store_true');choice.add_argument('--state')
    init.add_argument('--now')
    for name in ('validate', 'inspect', 'next', 'dispatch', 'reconcile', 'event'):
        cmd = sub.add_parser(name);cmd.add_argument('directory');cmd.add_argument('--now');cmd.add_argument('--workspace')
        if name in ('next', 'reconcile'):
            cmd.add_argument('field_key')
        if name == 'dispatch':
            cmd.add_argument('request_id')
        if name in ('next', 'dispatch', 'reconcile'):
            cmd.add_argument('--actor', required=True);cmd.add_argument('--context', required=True)
        if name == 'event':
            cmd.add_argument('--event-file', required=True)
        if name not in ('validate', 'inspect'):
            cmd.add_argument('--commit', action='store_true', help='Persist local state before emitting any executable host job; not proof of user permission.')
    demo = sub.add_parser('demo');demo.add_argument('--out', required=True)
    return root


def fixture_host(job, path, now):
    """Reference host for fictional local JSON only. No network or LinkedIn implementation."""
    fixture = json.loads(Path(path).read_text())
    if fixture.get('fictional') is not True or fixture['profile_ref'] != job['profile_ref']:
        raise p.ProfileError('The reference host only accepts its exact fictional local fixture.')
    if not job['execute']:
        raise p.ProfileError('Prepared or dry-run jobs cannot execute.')
    if p.stamp(now) > p.stamp(job['expires_at']):
        raise p.ProfileError('Job expired before the host operation.')
    key = job['field_key']
    result = {'request_id': job['request_id'], 'profile_ref': fixture['profile_ref'], 'field_key': key,
              'actor_id': job['actor_id'], 'context_id': job['context_id'], 'observed_at': now}
    if job['operation'] == 'read_field':
        return {**result, 'type': 'observation', 'outcome': 'observed', 'value': fixture['fields'][key],
                'revision': str(fixture['revision']), 'evidence': 'Observed fictional local JSON field; not LinkedIn.'}
    # This simulator has a conditional update. A real UI may not offer an atomic equivalent.
    if fixture['fields'][key] != job['if_current_value'] or str(fixture['revision']) != job['if_revision']:
        return {**result, 'type': 'write_result', 'outcome': 'not_saved', 'evidence': 'Fictional fixture changed; conditional write refused.'}
    fixture['fields'][key] = job['value'];fixture['revision'] += 1
    Path(path).write_text(json.dumps(fixture, indent=2)+'\n')
    return {**result, 'type': 'write_result', 'outcome': 'saved', 'evidence': 'Confirmed one fictional local JSON field save; not LinkedIn.'}


def demo(directory):
    destination = Path(directory)
    if destination.exists():
        raise p.ProfileError('Choose a fresh demo directory.')
    now = '2026-11-04T12:00:00Z'
    initialize(destination, example=True, now=now)
    state = read(destination)
    state = p.event(state, {'type': 'capability', 'value': {'status': 'available', 'adapter_id': 'fictional-local-file-host',
                      'actor_id': 'demo-agent', 'context_id': 'demo-local-session', 'profile_ref': state['profile_ref'],
                      'fields': ['headline'], 'can_read': True, 'can_write': True, 'observed_at': now,
                      'expires_at': '2026-11-04T13:00:00Z', 'evidence': 'Fictional file host read/write self-test only; no LinkedIn observation.'}}, now)
    key = 'headline'
    for kind in ('facts', 'public', 'material', 'edit'):
        state = p.event(state, {'type': 'approve', 'field_key': key, 'kind': kind, 'decision': 'approved',
                       'fingerprint': p.field_fingerprint(state, key), 'approval_id': 'SIM-'+kind, 'by': 'Fictional Avery',
                       'reference': 'SIMULATED exact-field '+kind+' decision; not real user consent.',
                       'actor_id': 'demo-agent' if kind == 'edit' else None,
                       'context_id': 'demo-local-session' if kind == 'edit' else None,
                       'expires_at': '2026-11-04T12:30:00Z' if kind == 'edit' else None}, now)
    fixture_path = destination/'fictional-profile.json'
    fixture_path.write_text(json.dumps({'fictional': True, 'profile_ref': state['profile_ref'], 'revision': 1,
                                       'fields': {f['key']: f['before'] for f in state['fields']}}, indent=2)+'\n')
    jobs = []
    for stage in ('preflight', 'prepare', 'dispatch', 'verify'):
        if stage == 'dispatch':
            state, job = p.dispatch(state, jobs[-1]['request_id'], 'demo-agent', 'demo-local-session', now)
        else:
            state, job = p.next_job(state, key, 'demo-agent', 'demo-local-session', now)
        save(destination, state)  # persist consumed dispatch BEFORE the reference host writes.
        jobs.append(job)
        if job.get('execute'):
            receipt = fixture_host(job, fixture_path, now)
            state = p.event(state, receipt, now)
            save(destination, state)
    summary = p.inspect(state, now)
    report = {'fictional_simulation': True, 'live_linkedin_calls': 0, 'local_fixture_writes': 1,
              'headline': summary['fields'][0]['attempt_status'], 'about': summary['fields'][1]['attempt_status'],
              'whole_profile_published': False, 'state_errors': p.errors(state, now),
              'manual_route_available': True, 'jobs': jobs}
    (destination/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == 'init':
            result = initialize(args.directory, args.state, args.example, args.now)
        elif args.command == 'demo':
            result = demo(args.out)
        elif args.command in ('validate', 'inspect'):
            state = read(args.directory)
            workspace = load_workspace(args.workspace) if args.workspace else None
            if args.command == 'validate':
                problems = p.errors(state, args.now)
                if workspace is not None and not problems:
                    problems += p.workspace_gaps(state, workspace, p.stamp(args.now))
                result = {'valid': not problems, 'errors': problems}
                print(json.dumps(result, indent=2));return 1 if problems else 0
            result = p.inspect(state, args.now, workspace)
        else:
            def operation():
                state = read(args.directory)
                workspace = load_workspace(args.workspace) if args.workspace else None
                if args.command == 'event':
                    event = json.loads(Path(args.event_file).read_text())
                    updated = p.event(state, event, args.now)
                    answer = {'status': 'local_event_recorded', 'event': event['type'], 'external_actions': 'none'}
                elif args.command == 'next':
                    updated, answer = p.next_job(state, args.field_key, args.actor, args.context, args.now, workspace)
                elif args.command == 'dispatch':
                    updated, answer = p.dispatch(state, args.request_id, args.actor, args.context, args.now, workspace)
                else:
                    updated, answer = p.reconcile(state, args.field_key, args.actor, args.context, args.now)
                p.ensure(updated, args.now)
                if args.commit:
                    save(args.directory, updated)
                else:
                    answer = {**answer, 'execute': False, 'dry_run': True}
                return {**answer, 'persisted': args.commit, 'actual_host_action_performed': False}
            if args.commit:
                with locked(args.directory):
                    result = operation()
            else:
                result = operation()
        print(json.dumps(result, indent=2, ensure_ascii=False));return 0
    except (PipelineError, OSError, ValueError, KeyError, TypeError) as exc:
        print('Error: '+str(exc), file=sys.stderr);return 2
