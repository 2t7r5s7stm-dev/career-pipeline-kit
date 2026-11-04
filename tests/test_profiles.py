# Copyright 2026 James E. Dunn
# SPDX-License-Identifier: Apache-2.0
"""Behavioral checks for a scoped local journal, not a live LinkedIn adapter."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from career_pipeline import profiles as p
from career_pipeline import profile_cli as cli

ROOT = Path(__file__).resolve().parents[1]
NOW = '2026-11-04T12:00:00Z'
ACTOR = 'fictional-agent'
CONTEXT = 'fictional-session'


def example():
    return json.loads((ROOT/'examples/fictional/linkedin-execution.json').read_text())


def approve(state, kind, key='headline', decision='approved', suffix='', expires=None):
    return p.event(state, {
        'type': 'approve', 'field_key': key, 'kind': kind, 'decision': decision,
        'fingerprint': p.field_fingerprint(state, key),
        'approval_id': kind+'-'+key+'-'+decision+suffix,
        'by': 'Fictional Avery', 'reference': 'Simulated exact-field decision for testing.',
        'actor_id': ACTOR if kind == 'edit' else None,
        'context_id': CONTEXT if kind == 'edit' else None,
        'expires_at': expires or ('2026-11-04T12:30:00Z' if kind == 'edit' else None),
    }, NOW)


def observed_capability(state):
    return p.event(state, {'type': 'capability', 'value': {
        'status': 'available', 'adapter_id': 'fictional-local-host',
        'actor_id': ACTOR, 'context_id': CONTEXT, 'profile_ref': state['profile_ref'],
        'fields': ['headline', 'about', 'skills', 'experience:entry-1:body'],
        'can_read': True, 'can_write': True, 'observed_at': NOW,
        'expires_at': '2026-11-04T13:00:00Z',
        'evidence': 'Fictional local host self-test only; no live LinkedIn access.',
    }}, NOW)


def approved_state(key='headline'):
    state = observed_capability(example())
    for kind in ('facts', 'public', 'material', 'edit'):
        state = approve(state, kind, key)
    return state


def receipt(job, value=None, outcome=None, **overrides):
    is_read = job['operation'] == 'read_field'
    result = {'type': 'observation' if is_read else 'write_result',
              'request_id': job['request_id'], 'profile_ref': job['profile_ref'],
              'field_key': job['field_key'], 'actor_id': job['actor_id'],
              'context_id': job['context_id'], 'observed_at': NOW,
              'outcome': outcome or ('observed' if is_read else 'saved'),
              'evidence': 'Simulated local-host observation for this exact request.'}
    if is_read:
        result.update(value=job['if_current_value'] if value is None else value, revision='1')
    result.update(overrides)
    return result


def prepared(state=None):
    state = state or approved_state()
    state, read_job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
    state = p.event(state, receipt(read_job), NOW)
    return p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)


def dispatched(state=None):
    state, job = prepared(state)
    return p.dispatch(state, job['request_id'], ACTOR, CONTEXT, NOW)


class ProfileEngineTests(unittest.TestCase):
    def test_missing_public_clearance_blocks_even_with_other_approvals(self):
        state = observed_capability(example())
        for kind in ('facts', 'material', 'edit'):
            state = approve(state, kind)
        unchanged, job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
        self.assertFalse(job['execute'])
        self.assertEqual(job['status'], 'review_required')
        self.assertTrue(any('public' in reason for reason in job['reasons']))
        self.assertEqual(unchanged['attempts'], [])

    def test_each_material_review_gate_is_required(self):
        for missing in ('facts', 'public', 'material'):
            with self.subTest(missing=missing):
                state = observed_capability(example())
                for kind in ('facts', 'public', 'material', 'edit'):
                    if kind != missing:
                        state = approve(state, kind)
                _, job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
                self.assertEqual(job['status'], 'review_required')
                self.assertFalse(job['execute'])

    def test_copy_approval_without_edit_permission_offers_manual_route(self):
        state = observed_capability(example())
        for kind in ('facts', 'public', 'material'):
            state = approve(state, kind)
        _, job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
        self.assertEqual(job['status'], 'manual_available')
        self.assertFalse(job['execute'])
        self.assertEqual(job['manual_copy']['publication'], 'not_verified')

    def test_capability_absence_and_wrong_scope_do_not_issue_jobs(self):
        for change in ({'status': 'unverified'}, {'status': 'unavailable'},
                       {'profile_ref': 'https://profiles.example.invalid/someone-else'},
                       {'actor_id': 'another-agent'}, {'context_id': 'another-session'},
                       {'can_write': False}, {'can_read': False}, {'fields': ['about']}):
            with self.subTest(change=change):
                state = approved_state()
                state['capability'].update(change)
                unchanged, job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
                self.assertEqual(job['status'], 'manual_available')
                self.assertFalse(job['execute'])
                self.assertEqual(unchanged['attempts'], [])

    def test_expired_capability_and_observation_age_are_checked(self):
        for change in ({'expires_at': '2026-11-04T11:59:59Z'},
                       {'observed_at': '2026-11-04T10:59:59Z'}):
            with self.subTest(change=change):
                state = approved_state();state['capability'].update(change)
                _, job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
                self.assertFalse(job['execute'])
                self.assertEqual(job['status'], 'manual_available')

    def test_future_capability_observation_is_invalid(self):
        state = approved_state()
        state['capability']['observed_at'] = '2026-11-04T12:01:00Z'
        self.assertTrue(p.errors(state, NOW))
        with self.assertRaises(p.ProfileError):
            p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)

    def test_imported_future_or_malformed_approval_time_is_invalid(self):
        for decision_time in ('2026-11-04T12:01:00Z', 'not-a-timestamp'):
            with self.subTest(decision_time=decision_time):
                state = approved_state()
                state['fields'][0]['approvals'][0]['at'] = decision_time
                self.assertTrue(p.errors(state, NOW))
                with self.assertRaises(p.ProfileError):
                    p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)

    def test_preflight_read_is_required_and_prepared_write_is_not_executable(self):
        state = approved_state()
        unchanged = copy.deepcopy(state)
        state, job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
        self.assertEqual(unchanged['attempts'], [])
        self.assertEqual(job['operation'], 'read_field')
        self.assertTrue(job['execute'])
        waiting, no_job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
        self.assertFalse(no_job['execute'])
        self.assertEqual(waiting, state)
        state = p.event(state, receipt(job), NOW)
        state, write = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
        self.assertEqual(write['operation'], 'replace_field')
        self.assertFalse(write['execute'])
        self.assertEqual(write['if_revision'], '1')

    def test_changed_current_value_stops_before_write(self):
        state, read_job = p.next_job(approved_state(), 'headline', ACTOR, CONTEXT, NOW)
        state = p.event(state, receipt(read_job, 'Edited elsewhere'), NOW)
        self.assertEqual(p.latest_attempt(state, 'headline')['status'], 'conflict')
        state, job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
        self.assertFalse(job['execute'])
        self.assertEqual(len(state['attempts']), 1)

    def test_desired_copy_already_present_does_not_claim_our_write(self):
        state, job = p.next_job(approved_state(), 'headline', ACTOR, CONTEXT, NOW)
        state = p.event(state, receipt(job, job['value']), NOW)
        self.assertEqual(p.latest_attempt(state, 'headline')['status'], 'already_present')
        _, again = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
        self.assertFalse(again['execute'])
        self.assertIsNone(p.confirmed_save_time(p.latest_attempt(state, 'headline')))

    def test_dispatch_consumes_one_time_permission(self):
        state, write = prepared()
        state, job = p.dispatch(state, write['request_id'], ACTOR, CONTEXT, NOW)
        self.assertTrue(job['execute'])
        self.assertEqual(p.latest_attempt(state, 'headline')['status'], 'write_dispatched')
        with self.assertRaises(p.ProfileError):
            p.dispatch(state, write['request_id'], ACTOR, CONTEXT, NOW)
        _, again = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
        self.assertFalse(again['execute'])

    def test_plan_copy_and_version_changes_invalidate_prepared_dispatch(self):
        for change in ('copy', 'version', 'source', 'profile'):
            with self.subTest(change=change):
                state, write = prepared()
                if change == 'copy':
                    state['fields'][0]['after'] += ' changed'
                elif change == 'version':
                    state['fields'][0]['version'] += 1
                elif change == 'source':
                    state['source_fingerprint'] = 'a'*64
                else:
                    state['profile_ref'] = 'https://profiles.example.invalid/another'
                with self.assertRaises(p.ProfileError):
                    p.dispatch(state, write['request_id'], ACTOR, CONTEXT, NOW)

    def test_revocation_of_each_approval_blocks_prepared_write(self):
        for kind in ('facts', 'public', 'material', 'edit'):
            with self.subTest(kind=kind):
                state, write = prepared()
                state = approve(state, kind, decision='revoked')
                with self.assertRaises(p.ProfileError):
                    p.dispatch(state, write['request_id'], ACTOR, CONTEXT, NOW)

    def test_earliest_approval_expiry_bounds_host_job(self):
        state = approved_state()
        state = approve(state, 'public', suffix='-short', expires='2026-11-04T12:01:00Z')
        state, write = prepared(state)
        state, job = p.dispatch(state, write['request_id'], ACTOR, CONTEXT, NOW)
        self.assertEqual(job['expires_at'], '2026-11-04T12:01:00Z')

    def test_stale_preflight_cannot_be_dispatched(self):
        state, write = prepared()
        with self.assertRaises(p.ProfileError):
            p.dispatch(state, write['request_id'], ACTOR, CONTEXT, '2026-11-04T12:05:01Z')

    def test_passed_workspace_detects_changed_source_without_version_bump(self):
        state = approved_state()
        workspace = json.loads((ROOT/'examples/fictional/workspace.json').read_text())
        self.assertEqual(p.workspace_gaps(state, workspace, p.stamp(NOW)), [])
        workspace['candidate']['display_name'] = 'Different fictional name'
        _, job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW, workspace)
        self.assertFalse(job['execute'])
        self.assertTrue(any('inputs changed' in reason for reason in job['reasons']))

    def test_success_requires_save_receipt_and_fresh_readback(self):
        state, write = dispatched()
        state = p.event(state, receipt(write), NOW)
        self.assertEqual(p.latest_attempt(state, 'headline')['status'], 'verify_required')
        state, read_job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
        self.assertEqual(read_job['operation'], 'read_field')
        state = p.event(state, receipt(read_job, write['value']), NOW)
        self.assertEqual(p.latest_attempt(state, 'headline')['status'], 'verified')
        self.assertEqual(p.inspect(state, NOW)['fields'][1]['attempt_status'], 'not_attempted')
        _, no_duplicate = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
        self.assertFalse(no_duplicate['execute'])

    def test_unknown_save_with_any_readback_stays_uncertain(self):
        for content in ('before', 'after', 'third'):
            with self.subTest(content=content):
                state, write = dispatched()
                state = p.event(state, receipt(write, outcome='unknown'), NOW)
                state, read_job = p.reconcile(state, 'headline', ACTOR, CONTEXT, NOW)
                value = write['if_current_value'] if content == 'before' else write['value'] if content == 'after' else 'Third value'
                state = p.event(state, receipt(read_job, value), NOW)
                self.assertEqual(p.latest_attempt(state, 'headline')['status'], 'uncertain')
                state['fields'][0]['after'] = 'A revised approved proposal'
                for kind in ('facts', 'public', 'material', 'edit'):
                    state = approve(state, kind, suffix='-revised')
                unchanged, no_write = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
                self.assertFalse(no_write['execute'])
                self.assertEqual(len(unchanged['attempts']), 1)

    def test_settlement_preserves_unknown_receipt_then_requires_new_read(self):
        state, write = dispatched()
        unknown = receipt(write, outcome='unknown')
        state = p.event(state, unknown, NOW)
        settlement = {'type': 'settlement', 'request_id': write['request_id'],
                      'profile_ref': write['profile_ref'], 'field_key': write['field_key'],
                      'actor_id': ACTOR, 'context_id': CONTEXT, 'observed_at': NOW,
                      'outcome': 'saved', 'evidence': 'Definitive fictional host operation-completion record.'}
        state = p.event(state, settlement, NOW)
        self.assertEqual(p.locate_request(state, write['request_id'])[1]['receipt'], unknown)
        self.assertEqual(p.latest_attempt(state, 'headline')['status'], 'verify_required')
        state, read_job = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
        state = p.event(state, receipt(read_job, write['value']), NOW)
        self.assertEqual(p.latest_attempt(state, 'headline')['status'], 'verified')

    def test_known_write_result_cannot_be_overridden_by_settlement(self):
        state, write = dispatched()
        state = p.event(state, receipt(write, outcome='not_saved'), NOW)
        with self.assertRaises(p.ProfileError):
            p.event(state, {'type': 'settlement', 'request_id': write['request_id'],
                            'outcome': 'saved', 'evidence': 'Not a valid override.'}, NOW)

    def test_late_conflicting_result_blocks_a_new_prepared_attempt(self):
        for outcome in ('unknown', 'saved'):
            with self.subTest(outcome=outcome):
                state, first_write = dispatched()
                first_attempt_id = first_write['attempt_id']
                state = p.event(state, {'type': 'settlement', 'request_id': first_write['request_id'],
                                       'profile_ref': first_write['profile_ref'], 'field_key': 'headline',
                                       'actor_id': ACTOR, 'context_id': CONTEXT, 'observed_at': NOW,
                                       'outcome': 'not_saved',
                                       'evidence': 'Definitive fictional host completion record; no save.'}, NOW)
                state['fields'][0]['after'] = 'A new fictional headline proposal'
                state['fields'][0]['version'] += 1
                for kind in ('facts', 'public', 'material', 'edit'):
                    state = approve(state, kind, suffix='-second')
                state, second_write = prepared(state)
                self.assertEqual(len(state['attempts']), 2)
                state = p.event(state, receipt(first_write, outcome=outcome), NOW)
                old_attempt = next(a for a in state['attempts'] if a['id'] == first_attempt_id)
                self.assertEqual(old_attempt['status'], 'uncertain')
                self.assertTrue(old_attempt['outcome_conflict'])
                with self.assertRaises(p.ProfileError):
                    p.dispatch(state, second_write['request_id'], ACTOR, CONTEXT, NOW)
                unchanged, next_instruction = p.next_job(state, 'headline', ACTOR, CONTEXT, NOW)
                self.assertFalse(next_instruction['execute'])
                self.assertEqual(len(unchanged['attempts']), 2)

    def test_reconciliation_keeps_original_target_and_values_after_plan_changes(self):
        state, write = dispatched()
        state['profile_ref'] = 'https://profiles.example.invalid/new-target'
        state['fields'][0]['after'] = 'Changed proposed text'
        state, read_job = p.reconcile(state, 'headline', ACTOR, CONTEXT, NOW)
        self.assertEqual(read_job['profile_ref'], write['profile_ref'])
        self.assertEqual(read_job['value'], write['value'])
        self.assertEqual(read_job['operation'], 'read_field')

    def test_wrong_scope_receipt_never_verifies_attempt(self):
        state, write = dispatched()
        state = p.event(state, receipt(write, profile_ref='https://profiles.example.invalid/wrong'), NOW)
        self.assertTrue(p.latest_attempt(state, 'headline')['scope_violation'])
        self.assertEqual(p.latest_attempt(state, 'headline')['status'], 'uncertain')
        state, read_job = p.reconcile(state, 'headline', ACTOR, CONTEXT, NOW)
        state = p.event(state, receipt(read_job, write['value']), NOW)
        self.assertEqual(p.latest_attempt(state, 'headline')['status'], 'uncertain')

    def test_result_replay_is_idempotent_but_conflicting_replay_rejected(self):
        state, write = dispatched()
        result = receipt(write)
        state = p.event(state, result, NOW)
        self.assertEqual(p.event(state, result, NOW), state)
        result['outcome'] = 'not_saved'
        with self.assertRaises(p.ProfileError):
            p.event(state, result, NOW)

    def test_undispatched_can_cancel_but_dispatched_requires_reconcile(self):
        state, write = prepared()
        state = p.event(state, {'type': 'cancel', 'field_key': 'headline', 'reference': 'Fictional user deferred.'}, NOW)
        with self.assertRaises(p.ProfileError):
            p.dispatch(state, write['request_id'], ACTOR, CONTEXT, NOW)
        state, write = dispatched()
        with self.assertRaises(p.ProfileError):
            p.event(state, {'type': 'cancel', 'field_key': 'headline', 'reference': 'Cannot erase possible write.'}, NOW)

    def test_skills_are_manual_even_when_host_claims_capability(self):
        state = example()
        skills = copy.deepcopy(state['fields'][0])
        skills.update(key='skills', before=['Operations'], after=['Onboarding process design'], approvals=[])
        state['fields'].append(skills)
        state = observed_capability(state)
        for kind in ('facts', 'public', 'material', 'edit'):
            state = approve(state, kind, 'skills')
        unchanged, job = p.next_job(state, 'skills', ACTOR, CONTEXT, NOW)
        self.assertEqual(job['status'], 'manual_available')
        self.assertFalse(job['execute'])
        self.assertEqual(unchanged['attempts'], [])

    def test_manual_completion_report_is_unverified_not_published(self):
        state = approved_state()
        state = p.event(state, {'type': 'manual_report', 'field_key': 'headline',
                               'by': 'Fictional Avery', 'reference': 'Reported manual copy-paste.'}, NOW)
        self.assertEqual(state['manual_reports'][0]['status'], 'reported_unverified')
        row = p.inspect(state, NOW)['fields'][0]
        self.assertTrue(row['manual_reported'])
        self.assertEqual(row['attempt_status'], 'not_attempted')

    def test_per_field_approval_does_not_authorize_another_field(self):
        state = approved_state()
        _, job = p.next_job(state, 'about', ACTOR, CONTEXT, NOW)
        self.assertEqual(job['status'], 'review_required')
        self.assertFalse(job['execute'])

    def test_unsupported_fields_duplicate_keys_and_missing_evidence_are_invalid(self):
        for change in ('unsupported', 'duplicate', 'no_evidence', 'bad_url', 'unknown_property'):
            with self.subTest(change=change):
                state = example()
                if change == 'unsupported':
                    state['fields'][0]['key'] = 'experience:entry-1:title'
                elif change == 'duplicate':
                    state['fields'].append(copy.deepcopy(state['fields'][0]))
                elif change == 'no_evidence':
                    state['fields'][0]['evidence_ids'] = []
                elif change == 'bad_url':
                    state['profile_ref'] = 'https://profiles.example.invalid/avery?token=example'
                else:
                    state['secret'] = 'No arbitrary extra state.'
                self.assertTrue(p.errors(state, NOW))


class ProfileCliTests(unittest.TestCase):
    def run_cli(self, *arguments):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        return subprocess.run([sys.executable, '-m', 'career_pipeline', 'profile', *map(str, arguments)],
                              cwd=ROOT, env=environment, capture_output=True, text=True)

    def test_init_is_private_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)/'profile'
            cli.initialize(directory, example=True, now=NOW)
            self.assertEqual((directory/'.gitignore').read_text(), '*\n!.gitignore\n')
            self.assertEqual(p.errors(cli.read(directory), NOW), [])
            with self.assertRaises(p.ProfileError):
                cli.initialize(directory, example=True, now=NOW)

    def test_preview_preserves_bytes_and_cannot_emit_executable_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)/'profile'
            cli.initialize(directory, example=True, now=NOW)
            state, write = prepared();cli.save(directory, state)
            before = (directory/'profile.json').read_bytes()
            result = self.run_cli('dispatch', directory, write['request_id'], '--actor', ACTOR,
                                  '--context', CONTEXT, '--now', NOW)
            self.assertEqual(result.returncode, 0, result.stderr)
            answer = json.loads(result.stdout)
            self.assertFalse(answer['execute'])
            self.assertFalse(answer['persisted'])
            self.assertFalse(answer['actual_host_action_performed'])
            self.assertEqual((directory/'profile.json').read_bytes(), before)

    def test_two_concurrent_dispatches_emit_only_one_executable_job(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)/'profile'
            cli.initialize(directory, example=True, now=NOW)
            state, write = prepared();cli.save(directory, state)
            command = [sys.executable, '-m', 'career_pipeline', 'profile', 'dispatch', str(directory),
                       write['request_id'], '--actor', ACTOR, '--context', CONTEXT, '--now', NOW, '--commit']
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
            runs = [subprocess.Popen(command, cwd=ROOT, env=environment, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True) for _ in range(2)]
            results = [run.communicate(timeout=15) for run in runs]
            executable = [json.loads(output)['execute'] for run, (output, _) in zip(runs, results) if run.returncode == 0]
            self.assertEqual(executable, [True])
            self.assertEqual(p.latest_attempt(cli.read(directory), 'headline')['status'], 'write_dispatched')
            replay = self.run_cli('dispatch', directory, write['request_id'], '--actor', ACTOR,
                                  '--context', CONTEXT, '--now', NOW, '--commit')
            self.assertNotEqual(replay.returncode, 0)
            self.assertEqual(replay.stdout, '')

    def test_existing_lock_blocks_dispatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)/'profile'
            cli.initialize(directory, example=True, now=NOW)
            state, write = prepared();cli.save(directory, state)
            before = (directory/'profile.json').read_bytes()
            with cli.locked(directory):
                result = self.run_cli('dispatch', directory, write['request_id'], '--actor', ACTOR,
                                      '--context', CONTEXT, '--now', NOW, '--commit')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')
            self.assertEqual((directory/'profile.json').read_bytes(), before)

    def test_fictional_reference_host_refuses_changed_current_value(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'fixture.json'
            state, write = dispatched()
            fixture = {'fictional': True, 'profile_ref': write['profile_ref'], 'revision': 2,
                       'fields': {'headline': 'Concurrent edit', 'about': 'Untouched'}}
            path.write_text(json.dumps(fixture))
            result = cli.fixture_host(write, path, NOW)
            self.assertEqual(result['outcome'], 'not_saved')
            self.assertEqual(json.loads(path.read_text()), fixture)

    def test_fictional_demo_changes_only_reviewed_field_and_has_no_live_calls(self):
        with tempfile.TemporaryDirectory() as temporary:
            report = cli.demo(Path(temporary)/'demo')
            self.assertEqual(report['state_errors'], [])
            self.assertEqual(report['headline'], 'verified')
            self.assertEqual(report['about'], 'not_attempted')
            self.assertEqual(report['local_fixture_writes'], 1)
            self.assertEqual(report['live_linkedin_calls'], 0)
            self.assertFalse(report['whole_profile_published'])
            fixture = json.loads((Path(temporary)/'demo/fictional-profile.json').read_text())
            self.assertEqual(fixture['fields']['about'], example()['fields'][1]['before'])


if __name__ == '__main__':
    unittest.main()
