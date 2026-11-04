# Copyright 2026 James E. Dunn
# SPDX-License-Identifier: Apache-2.0
"""Guarded JSON job bridge. It never logs in, browses, or calls a profile service."""
import copy
import json
import re
import uuid
from datetime import timedelta
from urllib.parse import urlsplit
from .core import PipelineError, ROOT, digest, iso, stamp, schema_errors, validate as validate_workspace

PROFILE_KEYS = ('candidate', 'evidence', 'base_resume', 'style_guide', 'search_brief')
TERMINAL = {'verified', 'already_present', 'blocked', 'conflict', 'not_saved'}
PRECHECK_SECONDS = 300
CAPABILITY_SECONDS = 3600


class ProfileError(PipelineError):
    pass


def source_fingerprint(workspace):
    return digest({k: workspace[k] for k in PROFILE_KEYS})


def field(state, key):
    item = next((f for f in state['fields'] if f['key'] == key), None)
    if item is None:
        raise ProfileError('Unknown profile field: ' + key)
    return item


def can_automate(key):
    return key in ('headline', 'about') or bool(re.fullmatch(r'experience:[A-Za-z0-9._-]+:body', key))


def field_fingerprint(state, key):
    f = field(state, key)
    return digest({'plan_id': state['plan_id'], 'profile_ref': state['profile_ref'],
                   'input_versions': state['input_versions'], 'source_fingerprint': state['source_fingerprint'],
                   'field': {k: v for k, v in f.items() if k != 'approvals'}})


def errors(state, now=None):
    schema = json.loads((ROOT/'schemas/linkedin-execution.schema.json').read_text())
    problems = schema_errors(state, schema, 'profile')
    if problems:
        return problems
    now_dt = stamp(now)
    if state['fields']:
        parsed = urlsplit(state['profile_ref'])
        valid_host = parsed.hostname and (parsed.hostname.endswith('.invalid') if state['fictional'] else parsed.hostname in ('www.linkedin.com', 'linkedin.com'))
        if parsed.scheme != 'https' or not valid_host or parsed.username or parsed.password or parsed.query or parsed.fragment:
            problems.append('Use one explicit canonical HTTPS profile reference; fictional examples use .invalid.')
    keys = [f['key'] for f in state['fields']]
    if len(keys) != len(set(keys)):
        problems.append('Profile field keys must be unique.')
    for f in state['fields']:
        if not can_automate(f['key']) and f['key'] != 'skills':
            problems.append('Unsupported field; titles, dates, media and settings are outside this bridge.')
        expected_type = list if f['key'] == 'skills' else str
        if not isinstance(f['before'], expected_type) or not isinstance(f['after'], expected_type):
            problems.append('Field values must be text; skills use a list for manual review only.')
        if f['after'] and not f['evidence_ids']:
            problems.append('Nonempty proposed copy needs evidence references.')
        if len({a['id'] for a in f['approvals']}) != len(f['approvals']):
            problems.append('Approval IDs must be unique within a field.')
        for a in f['approvals']:
            if not a['by'].strip() or not a['reference'].strip():
                problems.append('Approval records need an actual decision maker and private decision reference.')
            if a['kind'] == 'edit' and a['decision'] == 'approved' and (not a['actor_id'] or not a['context_id'] or not a['expires_at']):
                problems.append('Edit permission needs the exact actor, context and expiry.')
    if len({a['id'] for a in state['attempts']}) != len(state['attempts']):
        problems.append('Attempt IDs must be unique.')
    request_ids = []
    for attempt in state['attempts']:
        if attempt['field_key'] not in keys:
            problems.append('Retain attempted fields in the plan until their history is reconciled.')
        for request in attempt['requests']:
            request_ids.append(request['id'])
            if request['field_key'] != attempt['field_key'] or request['profile_ref'] != attempt['profile_ref'] or request['fingerprint'] != attempt['fingerprint']:
                problems.append('Request scope must match its stored attempt.')
            if request['before'] != attempt['before'] or request['after'] != attempt['after']:
                problems.append('Request values must match the original attempted version.')
    if len(request_ids) != len(set(request_ids)):
        problems.append('Request IDs must be unique.')
    cap = state['capability']
    if cap['status'] == 'available' and (not cap['evidence'].strip() or not cap['actor_id'] or not cap['context_id'] or not cap['profile_ref'] or not cap['observed_at'] or not cap['expires_at']):
        problems.append('Available capability requires current scoped observation evidence and expiry.')
    def check_dates(value, key=''):
        if isinstance(value, dict):
            for k, v in value.items():
                check_dates(v, k)
        elif isinstance(value, list):
            for v in value:
                check_dates(v, key)
        elif value and (key.endswith('_at') or key == 'at'):
            try:
                time = stamp(value)
                if key != 'expires_at' and time > now_dt:
                    problems.append('Future-dated observation or decision: ' + key)
            except PipelineError as exc:
                problems.append(key + ': ' + str(exc))
    check_dates(state)
    return problems


def ensure(state, now=None):
    problems = errors(state, now)
    if problems:
        raise ProfileError('\n'.join(problems))


def latest_approval(f, kind):
    return next((a for a in reversed(f['approvals']) if a['kind'] == kind), None)


def approval_gaps(state, key, kinds, now_dt, actor=None, context=None):
    f = field(state, key)
    fp = field_fingerprint(state, key)
    gaps = []
    for kind in kinds:
        a = latest_approval(f, kind)
        if not a or a['decision'] != 'approved' or a['fingerprint'] != fp:
            gaps.append('Current exact-field ' + kind + ' approval is required.')
        elif a['expires_at'] and stamp(a['expires_at']) < now_dt:
            gaps.append(kind + ' approval expired.')
        elif kind == 'edit' and (a['actor_id'] != actor or a['context_id'] != context):
            gaps.append('Edit permission does not cover this actor and session context.')
    return gaps


def workspace_gaps(state, workspace, now_dt):
    if workspace is None:
        return []
    problems = validate_workspace(workspace, iso(now_dt))
    if problems:
        return ['Referenced career workspace is invalid: ' + '; '.join(problems)]
    if state['input_versions'] != {k: workspace[k]['version'] for k in PROFILE_KEYS} or state['source_fingerprint'] != source_fingerprint(workspace):
        return ['Career inputs changed; refresh the plan and affected exact-field approvals.']
    claims = {c['id']: c for c in workspace['evidence']['claims']}
    return ['Missing/unconfirmed evidence: ' + cid for f in state['fields'] for cid in f['evidence_ids'] if cid not in claims or claims[cid]['status'] != 'confirmed']


def capability_gaps(state, profile_ref, key, actor, context, now_dt, write=False):
    c = state['capability']
    if c['status'] != 'available':
        return ['Capability is unavailable or unverified; use the manual route.']
    result = []
    if c['profile_ref'] != profile_ref or c['actor_id'] != actor or c['context_id'] != context:
        result.append('Capability evidence belongs to another profile, actor or session.')
    if key not in c['fields'] or not c['can_read'] or (write and not c['can_write']):
        result.append('This exact field/read/write operation is not supported by the observed host.')
    if not c['observed_at'] or not c['expires_at'] or not (stamp(c['observed_at']) <= now_dt <= stamp(c['expires_at'])) or now_dt - stamp(c['observed_at']) > timedelta(seconds=CAPABILITY_SECONDS):
        result.append('Capability observation expired or is not current.')
    return result


def effective_deadline(state, key, now_dt, include_approvals=True):
    c = state['capability']
    deadlines = [now_dt + timedelta(seconds=PRECHECK_SECONDS), stamp(c['expires_at']),
                 stamp(c['observed_at']) + timedelta(seconds=CAPABILITY_SECONDS)]
    if include_approvals:
        for kind in ('facts', 'public', 'material', 'edit'):
            a = latest_approval(field(state, key), kind)
            if a and a['expires_at']:
                deadlines.append(stamp(a['expires_at']))
    return min(deadlines)


def confirmed_save_time(attempt):
    if attempt.get('scope_violation') or attempt.get('outcome_conflict'):
        return None
    settlement = attempt.get('settlement')
    if settlement and settlement['outcome'] == 'saved':
        return stamp(settlement['observed_at'])
    for r in reversed(attempt['requests']):
        receipt = r['receipt']
        if r['operation'] == 'replace_field' and receipt and receipt['outcome'] == 'saved':
            return stamp(receipt['observed_at'])
    return None


def latest_attempt(state, key):
    return next((a for a in reversed(state['attempts']) if a['field_key'] == key), None)


def unresolved_attempts(state, key):
    return [a for a in state['attempts'] if a['field_key'] == key and a['status'] not in TERMINAL]


def _request(attempt, operation, purpose, actor, context, now_dt, expiry=None):
    r = {'id': str(uuid.uuid4()), 'operation': operation, 'purpose': purpose,
         'created_at': iso(now_dt), 'expires_at': iso(expiry or now_dt + timedelta(seconds=PRECHECK_SECONDS)),
         'actor_id': actor, 'context_id': context, 'profile_ref': attempt['profile_ref'],
         'field_key': attempt['field_key'], 'fingerprint': attempt['fingerprint'],
         'before': copy.deepcopy(attempt['before']), 'after': copy.deepcopy(attempt['after']),
         'status': 'prepared' if operation == 'replace_field' else 'pending', 'receipt': None}
    attempt['requests'].append(r)
    return r


def _job(attempt, request, execute):
    return {'status': attempt['status'], 'execute': execute, 'request_id': request['id'],
            'attempt_id': attempt['id'], 'operation': request['operation'], 'purpose': request['purpose'],
            'profile_ref': request['profile_ref'], 'field_key': request['field_key'],
            'field_fingerprint': request['fingerprint'], 'actor_id': request['actor_id'],
            'context_id': request['context_id'], 'expires_at': request['expires_at'],
            'if_current_value': request['before'], 'value': request['after'],
            'if_revision': (attempt.get('preflight') or {}).get('revision'),
            'idempotency_key': attempt['id'],
            'host_requirements': ['Use only the named account and stable field identity.',
                                  'Re-read immediately before save; stop if the current value changed.',
                                  'Honor expiry, actual human consent and all environment permission rules.',
                                  'Do not change other fields, media, visibility, notifications or settings.',
                                  'Record actual outcome; uncertain saves must be reconciled, never replayed.']}


def next_job(state, key, actor, context, now=None, workspace=None):
    ensure(state, now)
    result = copy.deepcopy(state)
    f = field(result, key)
    now_dt = stamp(now)
    pending = unresolved_attempts(result, key)
    a = pending[0] if pending else latest_attempt(result, key)
    fp = field_fingerprint(result, key)
    if a and a['status'] not in TERMINAL:
        if a['status'] == 'verify_required':
            return reconcile(result, key, actor, context, now)
        if a['status'] == 'ready' and a['fingerprint'] == fp:
            gaps = workspace_gaps(result, workspace, now_dt) + approval_gaps(result, key, ('facts', 'public', 'material', 'edit'), now_dt, actor, context)
            gaps += capability_gaps(result, result['profile_ref'], key, actor, context, now_dt, True)
            if gaps:
                return result, {'execute': False, 'status': 'review_required', 'reasons': gaps}
            r = _request(a, 'replace_field', 'apply', actor, context, now_dt, effective_deadline(result, key, now_dt))
            a['status'] = 'write_prepared'
            return result, _job(a, r, False)
        return result, {'execute': False, 'status': a['status'], 'next_action': 'Record the pending result, dispatch a prepared request, or explicitly reconcile. Never repeat a write.'}
    gaps = workspace_gaps(result, workspace, now_dt) + approval_gaps(result, key, ('facts', 'public', 'material'), now_dt)
    if gaps:
        return result, {'execute': False, 'status': 'review_required', 'reasons': gaps}
    if a and a['fingerprint'] == fp and a['status'] in ('verified', 'already_present'):
        return result, {'execute': False, 'status': a['status'], 'next_action': 'This version was read back; no duplicate write will be issued.'}
    edit = latest_approval(f, 'edit')
    gaps = approval_gaps(result, key, ('edit',), now_dt, actor, context)
    gaps += capability_gaps(result, result['profile_ref'], key, actor, context, now_dt, True)
    if not can_automate(key):
        gaps.append('This bridge automates text only; skills, media and settings use manual review.')
    if gaps:
        return result, {'execute': False, 'status': 'manual_available', 'reasons': gaps,
                        'manual_copy': {'field_key': key, 'value': f['after'], 'publication': 'not_verified'},
                        'next_action': 'The person may copy approved material manually; no edit or reminder was performed.'}
    if a and a['fingerprint'] == fp and a['permission_id'] == edit['id']:
        return result, {'execute': False, 'status': 'review_required', 'reasons': ['This one-time permission was consumed. Reconcile history and obtain a fresh specific decision.']}
    a = {'id': str(uuid.uuid4()), 'field_key': key, 'profile_ref': result['profile_ref'], 'fingerprint': fp,
         'permission_id': edit['id'], 'before': copy.deepcopy(f['before']), 'after': copy.deepcopy(f['after']),
         'created_at': iso(now_dt), 'status': 'read_pending', 'requests': [], 'preflight': None}
    result['attempts'].append(a)
    r = _request(a, 'read_field', 'preflight', actor, context, now_dt, effective_deadline(result, key, now_dt))
    return result, _job(a, r, True)


def dispatch(state, request_id, actor, context, now=None, workspace=None):
    ensure(state, now)
    result = copy.deepcopy(state)
    a, r = locate_request(result, request_id)
    now_dt = stamp(now)
    if a['status'] != 'write_prepared' or r['status'] != 'prepared' or r['operation'] != 'replace_field':
        raise ProfileError('Write is already dispatched, resolved or not prepared. Do not replay it.')
    if any(other['id'] != a['id'] for other in unresolved_attempts(result, a['field_key'])):
        raise ProfileError('Another attempt for this field is unresolved; reconcile it before any write.')
    if a['fingerprint'] != field_fingerprint(result, a['field_key']) or a['profile_ref'] != result['profile_ref']:
        raise ProfileError('Plan changed; this prepared write is no longer authorized.')
    gaps = workspace_gaps(result, workspace, now_dt) + approval_gaps(result, a['field_key'], ('facts', 'public', 'material', 'edit'), now_dt, actor, context)
    gaps += capability_gaps(result, a['profile_ref'], a['field_key'], actor, context, now_dt, True)
    edit = latest_approval(field(result, a['field_key']), 'edit')
    if not edit or edit['id'] != a['permission_id']:
        gaps.append('This request is not covered by the current one-time edit permission.')
    if r['actor_id'] != actor or r['context_id'] != context or stamp(r['expires_at']) < now_dt:
        gaps.append('Prepared request scope or expiry changed.')
    if not a['preflight'] or now_dt - stamp(a['preflight']['observed_at']) > timedelta(seconds=PRECHECK_SECONDS):
        gaps.append('Current-value observation is stale; no write can be dispatched.')
    if not can_automate(a['field_key']):
        gaps.append('Unsupported automatic field.')
    if gaps:
        raise ProfileError('\n'.join(gaps))
    expiry = min(effective_deadline(result, a['field_key'], now_dt), stamp(a['preflight']['observed_at']) + timedelta(seconds=PRECHECK_SECONDS), stamp(r['expires_at']))
    r['expires_at'] = iso(expiry)
    r['status'] = 'dispatched'
    a['status'] = 'write_dispatched'
    return result, _job(a, r, True)


def reconcile(state, key, actor, context, now=None):
    ensure(state, now)
    result = copy.deepcopy(state)
    a = next((a for a in unresolved_attempts(result, key) if a['status'] in ('write_dispatched', 'verify_required', 'uncertain')), None)
    if not a or a['status'] not in ('write_dispatched', 'verify_required', 'uncertain'):
        raise ProfileError('Reconciliation requires an actual dispatched or uncertain attempt; no write is repeated.')
    now_dt = stamp(now)
    gaps = capability_gaps(result, a['profile_ref'], key, actor, context, now_dt, False)
    if gaps:
        return result, {'execute': False, 'status': 'manual_verification_required', 'reasons': gaps}
    r = _request(a, 'read_field', 'verify' if a['status'] == 'verify_required' else 'reconcile', actor, context, now_dt, effective_deadline(result, key, now_dt, False))
    a['status'] = 'verify_pending'
    return result, _job(a, r, True)


def locate_request(state, request_id):
    for a in state['attempts']:
        for r in a['requests']:
            if r['id'] == request_id:
                return a, r
    raise ProfileError('Unknown request ID.')


def event(state, value, now=None):
    ensure(state, now)
    result = copy.deepcopy(state)
    now_dt = stamp(now)
    kind = value.get('type')
    if kind == 'capability':
        result['capability'] = copy.deepcopy(value['value'])
    elif kind == 'approve':
        f = field(result, value['field_key'])
        if value['kind'] not in ('facts', 'public', 'material', 'edit') or value['decision'] not in ('approved', 'declined', 'revoked'):
            raise ProfileError('Unknown approval kind or decision.')
        if value['fingerprint'] != field_fingerprint(result, f['key']):
            raise ProfileError('Approval must name the current exact-field fingerprint.')
        f['approvals'].append({'id': value['approval_id'], 'kind': value['kind'], 'decision': value['decision'],
                               'fingerprint': value['fingerprint'], 'by': value['by'], 'reference': value['reference'],
                               'at': iso(now_dt), 'actor_id': value.get('actor_id'), 'context_id': value.get('context_id'),
                               'expires_at': value.get('expires_at')})
    elif kind == 'cancel':
        a = latest_attempt(result, value['field_key'])
        if not a or a['status'] not in ('read_pending', 'ready', 'write_prepared'):
            raise ProfileError('Only an undispatched attempt can be cancelled; reconcile any possible write.')
        if not value.get('reference', '').strip():
            raise ProfileError('Cancellation needs a reason/reference.')
        a['status'] = 'blocked'
        a['cancel_reference'] = value['reference']
        for request in a['requests']:
            if request['status'] in ('pending', 'prepared'):
                request['status'] = 'cancelled'
    elif kind == 'manual_report':
        key = value['field_key']
        if approval_gaps(result, key, ('facts', 'public', 'material'), now_dt):
            raise ProfileError('Manual report needs the current reviewed/public-cleared material version.')
        if not value.get('by', '').strip() or not value.get('reference', '').strip():
            raise ProfileError('Manual report needs a person and completion reference.')
        result['manual_reports'].append({'field_key': key, 'fingerprint': field_fingerprint(result, key),
                                          'by': value['by'], 'reference': value['reference'], 'at': iso(now_dt),
                                          'status': 'reported_unverified'})
    elif kind == 'settlement':
        a, r = locate_request(result, value['request_id'])
        if r['operation'] != 'replace_field' or r['status'] not in ('dispatched', 'responded') or (r['receipt'] and r['receipt']['outcome'] != 'unknown'):
            raise ProfileError('Settlement is only for a genuinely unresolved dispatched write, not a result override.')
        if value['outcome'] not in ('saved', 'not_saved') or not value.get('evidence', '').strip():
            raise ProfileError('Settlement needs definitive host operation evidence, not merely a matching or old field value.')
        observed = stamp(value['observed_at'])
        if not stamp(r['created_at']) <= observed <= now_dt:
            raise ProfileError('Invalid settlement observation time.')
        if any(value.get(k) != r[k] for k in ('profile_ref', 'field_key')):
            raise ProfileError('Settlement target does not match the original attempt.')
        gaps = capability_gaps(result, a['profile_ref'], a['field_key'], value['actor_id'], value['context_id'], now_dt, False)
        if gaps:
            raise ProfileError('\n'.join(gaps))
        if a.get('settlement') is not None:
            if a['settlement'] == value:
                return result
            raise ProfileError('Conflicting settlement; preserve history and inspect manually.')
        a['settlement'] = copy.deepcopy(value)
        a['status'] = 'uncertain' if a.get('scope_violation') or a.get('outcome_conflict') else 'verify_required' if value['outcome'] == 'saved' else 'not_saved'
    elif kind in ('observation', 'write_result'):
        a, r = locate_request(result, value['request_id'])
        if r['receipt'] is not None:
            if r['receipt'] == value:
                return result
            raise ProfileError('Conflicting replay of an already recorded result.')
        observed = stamp(value['observed_at'])
        if not stamp(r['created_at']) <= observed <= now_dt:
            raise ProfileError('Result needs a real observation time after its request, not a future or backdated one.')
        if not value.get('evidence', '').strip():
            raise ProfileError('Result needs observed evidence or a precise failure/uncertainty note.')
        mismatch = any(value.get(k) != r[k] for k in ('profile_ref', 'field_key', 'actor_id', 'context_id'))
        if kind == 'write_result':
            if r['operation'] != 'replace_field' or r['status'] != 'dispatched':
                raise ProfileError('No dispatched write exists for this result.')
            if value['outcome'] not in ('saved', 'not_saved', 'unknown'):
                raise ProfileError('Unknown write outcome.')
            if a.get('settlement') and a['settlement']['outcome'] != value['outcome']:
                a['outcome_conflict'] = True
                a['status'] = 'uncertain'
            elif mismatch:
                a['scope_violation'] = True
                a['status'] = 'uncertain'
            elif any(q['operation'] == 'read_field' and q['purpose'] != 'preflight' and q['status'] == 'pending' for q in a['requests']):
                a['status'] = 'verify_pending'
            else:
                a['status'] = 'uncertain' if value['outcome'] == 'unknown' else 'verify_required' if value['outcome'] == 'saved' else 'not_saved'
        else:
            if r['operation'] != 'read_field' or r['status'] != 'pending':
                raise ProfileError('No pending read exists for this observation.')
            if value['outcome'] not in ('observed', 'blocked', 'unknown'):
                raise ProfileError('Unknown observation outcome.')
            if mismatch or value['outcome'] != 'observed':
                a['status'] = 'blocked' if r['purpose'] == 'preflight' else 'uncertain'
            elif value['value'] == a['after']:
                if r['purpose'] == 'preflight':
                    a['status'] = 'already_present'
                else:
                    saved_at = confirmed_save_time(a)
                    a['status'] = 'verified' if saved_at is not None and observed >= saved_at else 'uncertain'
            elif r['purpose'] == 'preflight' and value['value'] == a['before']:
                a['preflight'] = copy.deepcopy(value)
                a['status'] = 'ready'
            elif r['purpose'] == 'preflight':
                a['status'] = 'conflict'
            else:
                # Old content after a timeout does not prove a delayed write will not land.
                a['status'] = 'uncertain'
        r['receipt'] = copy.deepcopy(value)
        r['status'] = 'responded'
    else:
        raise ProfileError('Unsupported profile event.')
    ensure(result, now)
    return result


def inspect(state, now=None, workspace=None):
    ensure(state, now)
    now_dt = stamp(now)
    fields = []
    for f in state['fields']:
        a = latest_attempt(state, f['key'])
        fp = field_fingerprint(state, f['key'])
        fields.append({'key': f['key'], 'fingerprint': fp, 'automated_text_supported': can_automate(f['key']),
                       'approval_gaps': approval_gaps(state, f['key'], ('facts', 'public', 'material'), now_dt),
                       'attempt_status': a['status'] if a else 'not_attempted',
                       'write_attribution': 'No authorship/causation inferred from readback; inspect recorded host result.',
                       'attempt_matches_current_version': a['fingerprint'] == fp if a else None,
                       'unresolved_attempt_ids': [item['id'] for item in unresolved_attempts(state, f['key'])],
                       'unresolved_attempts': [{'id': item['id'], 'status': item['status']} for item in unresolved_attempts(state, f['key'])],
                       'manual_reported': any(m['field_key'] == f['key'] and m['fingerprint'] == fp for m in state['manual_reports'])})
    return {'profile_ref': state['profile_ref'], 'workspace_gaps': workspace_gaps(state, workspace, now_dt),
            'fields': fields, 'limits': 'Host performs actual tools and verifies real consent/account. No live LinkedIn adapter is bundled.'}
