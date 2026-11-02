# Copyright 2026 James E. Dunn
# SPDX-License-Identifier: Apache-2.0
"""Standard-library state rules. No network, model, scheduler, or sending code."""
import copy
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

VERSION = "0.1"
ROOT = Path(__file__).resolve().parents[1]


class PipelineError(ValueError):
    pass


def stamp(value=None):
    if value is None:
        return datetime.now(timezone.utc)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise PipelineError("Use an ISO 8601 timestamp with a timezone.")
    if parsed.tzinfo is None:
        raise PipelineError("Timestamps must include a timezone.")
    return parsed.astimezone(timezone.utc)


def iso(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def canonical_url(value):
    if re.search(r"\s|[\x00-\x1f\x7f]", value):
        raise PipelineError("Source URLs must not contain whitespace or control characters.")
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise PipelineError("Invalid source URL: " + str(exc))
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise PipelineError("Source URLs must be HTTPS URLs without embedded credentials.")
    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in ("gclid", "fbclid")]
    return urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip("/") or "/", urlencode(query), ""))


def identity(role):
    employer = " ".join(role["employer"].lower().split())
    req = role.get("requisition_id")
    return employer + ("|req:" + str(req).strip().lower() if req else "|url:" + canonical_url(role["canonical_url"]))


def load(workspace):
    path = Path(workspace) / "workspace.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineError("Cannot read workspace.json: " + str(exc))


def save(workspace, state):
    target = Path(workspace) / "workspace.json"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(target)


def schema_errors(value, schema, path="state"):
    """Validate the subset used by the bundled schema; no third-party dependency."""
    errors = []
    expected = schema.get("type")
    matches = {"object": isinstance(value, dict), "array": isinstance(value, list),
               "string": isinstance(value, str), "integer": isinstance(value, int) and not isinstance(value, bool),
               "boolean": isinstance(value, bool), "null": value is None}
    types = expected if isinstance(expected, list) else [expected]
    if expected and not any(matches.get(t, False) for t in types):
        return [path + ": expected " + str(expected)]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(path + ": invalid value " + repr(value))
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(path + ": must not be empty")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(path + ": does not match required format")
    if isinstance(value, int) and "minimum" in schema and value < schema["minimum"]:
        errors.append(path + ": below minimum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(path + ": too few items")
        for i, item in enumerate(value):
            errors.extend(schema_errors(item, schema.get("items", {}), path + "[" + str(i) + "]"))
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(path + ": missing " + key)
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                errors.extend(schema_errors(item, properties[key], path + "." + key))
            elif schema.get("additionalProperties") is False:
                errors.append(path + ": unexpected field " + key)
    return errors


def version_inputs(state, role):
    versions = {key: state[key]["version"] for key in ("candidate", "evidence", "base_resume", "style_guide", "search_brief")}
    versions["role"] = role["revision"]
    return versions


def facts_fingerprint(state):
    return digest({"candidate": state["candidate"], "evidence": state["evidence"]})


def role_content(role):
    operational = {"job_status", "verifications", "intent", "packet", "packet_history", "application", "decision"}
    return {k: v for k, v in role.items() if k not in operational}


def role_fingerprint(state, role):
    return digest({"role": role_content(role), "search": state["search_brief"]})


def packet_fingerprint(state, role):
    packet = role.get("packet")
    return digest({"candidate": state["candidate"], "evidence": state["evidence"], "base_resume": state["base_resume"],
                   "style_guide": state["style_guide"], "search_brief": state["search_brief"], "role_content": role_content(role),
                   "packet": {k: v for k, v in (packet or {}).items() if k not in ("qa", "status", "fingerprint")}})


def submission_fingerprint(state, role):
    return digest({"action": "one_submission", "role_identity": identity(role), "destination": role["canonical_url"],
                   "packet_fingerprint": role["packet"]["fingerprint"] if role["packet"] else None, "intent": role["intent"]})


def approved(state, kind, fingerprint, role_id=None):
    matching = [a for a in state["approvals"] if a["kind"] == kind and a["fingerprint"] == fingerprint and a.get("role_id") == role_id]
    return bool(matching and matching[-1]["decision"] == "approved")


def current_verification(role):
    checks = role["verifications"]
    return max(enumerate(checks), key=lambda pair: (stamp(pair[1]["at"]), pair[0]))[1] if checks else None


def verification_ready(role, purpose, now, max_age_hours=24):
    """Posting age never filters roles. This age limit applies only to action evidence."""
    check = current_verification(role)
    intent = role.get("intent")
    if not check or not intent or check["outcome"] != "active":
        return False
    if check["source_type"] not in ("employer", "ats") or check["intent_id"] != intent["id"]:
        return False
    if check["purpose"] != purpose or stamp(check["at"]) < stamp(intent["at"]):
        return False
    elapsed = now - stamp(check["at"])
    # Pre-submission evidence must be observed in this execution, not reused hours later.
    window = timedelta(minutes=5) if purpose == "submission" else timedelta(hours=max_age_hours)
    return timedelta(0) <= elapsed <= window


def claim_map(state):
    return {claim["id"]: claim for claim in state["evidence"]["claims"]}


def selected_ids(packet):
    result = [claim for section in packet["sections"] for claim in section["evidence_ids"]]
    if packet["cover_letter"]["requested"]:
        result.extend(packet["cover_letter"]["evidence_ids"])
    return result


def validate(state, now=None):
    schema = json.loads((ROOT / "schemas" / "workspace.schema.json").read_text())
    errors = schema_errors(state, schema)
    if errors:
        return errors
    now = stamp(now)
    # Validate timestamp syntax before any sort/comparison can use it.
    def dates(value, key=""):
        if isinstance(value, dict):
            for k, v in value.items():
                dates(v, k)
        elif isinstance(value, list):
            for v in value:
                dates(v, key)
        elif value and (key.endswith("_at") or key in ("at", "snoozed_until")):
            try:
                parsed = stamp(value)
                if key not in ("next_due_at", "snoozed_until") and parsed > now:
                    errors.append("Future observation/approval timestamp: " + key)
            except PipelineError as exc:
                errors.append(key + ": " + str(exc))
    dates(state)
    if errors:
        return errors
    ids = set()
    claims = claim_map(state)
    if len(claims) != len(state["evidence"]["claims"]):
        errors.append("Evidence claim IDs must be unique.")
    for claim in claims.values():
        if claim["status"] == "confirmed":
            if claim["confirmation_basis"] == "none":
                errors.append("Confirmed claim " + claim["id"] + " needs a candidate/source confirmation basis.")
            if not claim["source"].strip() or not claim["confirmed_by"].strip() or not claim["confirmed_at"]:
                errors.append("Confirmed claim " + claim["id"] + " needs a source, confirmer, and timestamp.")
            for metric in claim["metrics"]:
                if not metric["confirmed"] or not metric["source"].strip() or metric["value"] not in claim["text"]:
                    errors.append("Unconfirmed or inconsistent metric in " + claim["id"])
            # Numeric claims require explicit reviewed metric metadata, including dates/credentials.
            numeric = re.findall(r"\d[\d,.]*%?", claim["text"])
            recorded = {token for m in claim["metrics"] if m["confirmed"] for token in re.findall(r"\d[\d,.]*%?", m["value"])}
            if any(n not in recorded for n in numeric):
                errors.append("Numeric text lacks confirmed metric metadata in " + claim["id"])
    for section in state["base_resume"]["sections"]:
        for cid in section["evidence_ids"]:
            if cid not in claims:
                errors.append("Base resume references missing claim " + cid)
    identity_keys = set()
    for role in state["roles"]:
        if role["id"] in ids:
            errors.append("Duplicate role ID " + role["id"])
        ids.add(role["id"])
        try:
            key = identity(role)
            if key != role["identity_key"]:
                errors.append("Identity key mismatch for " + role["id"])
            if key in identity_keys:
                errors.append("Duplicate employer/requisition or canonical source identity: " + key)
            identity_keys.add(key)
            canonical_url(role["canonical_url"])
            if role["pay"]["source_url"]:
                canonical_url(role["pay"]["source_url"])
            if role["posting_date"]:
                from datetime import date
                if role["posting_date_precision"] == "month":
                    datetime.strptime(role["posting_date"], "%Y-%m")
                elif role["posting_date_precision"] == "day":
                    date.fromisoformat(role["posting_date"])
                else:
                    errors.append("Posting date needs day/month precision and a source.")
                if not role["posting_date_source"].strip():
                    errors.append("Posting date needs a source.")
        except (PipelineError, ValueError) as exc:
            errors.append(str(exc))
        for related in role["related_role_ids"]:
            if related == role["id"] or related not in [r["id"] for r in state["roles"]]:
                errors.append("Invalid related role reference in " + role["id"])
        checks = role["verifications"]
        if len({v["id"] for v in checks}) != len(checks):
            errors.append("Verification IDs must be unique for " + role["id"])
        for check in checks:
            if check["outcome"] != "unknown" and check["source_type"] not in ("employer", "ats"):
                errors.append("Active/closed verification requires an official employer/ATS source.")
            if not check["evidence"].strip():
                errors.append("Verification needs observed evidence, not only a URL.")
            try:
                if check["outcome"] != "unknown" and canonical_url(check["url"]) != canonical_url(role["canonical_url"]):
                    errors.append("Action verification must refer to the canonical official posting for " + role["id"])
                canonical_url(check["url"])
            except PipelineError as exc:
                errors.append(str(exc))
        latest = current_verification(role)
        expected_status = latest["outcome"] if latest else "unknown"
        if role["job_status"] != expected_status:
            errors.append("Job status must reflect latest observation for " + role["id"])
        packet = role["packet"]
        if packet:
            if packet["fingerprint"] == packet_fingerprint(state, role):
                if packet["input_versions"] != version_inputs(state, role):
                    errors.append("Current packet has inconsistent input version references.")
                for cid in selected_ids(packet):
                    if cid not in claims or claims[cid]["status"] != "confirmed":
                        errors.append("Packet selects missing/unconfirmed claim " + cid)
            if packet["status"] in ("qa_passed", "approved") and packet["qa"]["fingerprint"] != packet["fingerprint"]:
                errors.append("QA does not match packet fingerprint for " + role["id"])
            if packet["status"] == "approved" and not approved(state, "materials", packet["fingerprint"], role["id"]):
                errors.append("Packet approval is missing for " + role["id"])
    if len({a["id"] for a in state["approvals"]}) != len(state["approvals"]):
        errors.append("Approval IDs must be unique.")
    for reminder in state["reminders"]:
        if reminder["role_id"] not in ids:
            errors.append("Reminder references missing role " + reminder["role_id"])
    if len({r["id"] for r in state["reminders"]}) != len(state["reminders"]):
        errors.append("Reminder IDs must be unique.")
    prefs = state["reminder_preferences"]
    if prefs["opted_in"]:
        if prefs["cadence_hours"] < 1 or not prefs["channel"].strip():
            errors.append("Opted-in reminders need cadence >= 1 hour and channel.")
        try:
            ZoneInfo(prefs["timezone"])
        except (ZoneInfoNotFoundError, ValueError):
            errors.append("Opted-in reminders need a valid IANA timezone.")
    improvements = state.get("improvements", [])
    if len({i["id"] for i in improvements}) != len(improvements):
        errors.append("Improvement IDs must be unique.")
    if sum(i["status"] == "trial" for i in improvements) > 1:
        errors.append("Only one improvement trial may be active at a time.")
    sensitive = {"goals", "filters", "cadence", "privacy", "external_behavior", "approval_rules"}
    for improvement in improvements:
        status = improvement["status"]
        active = status in ("approved", "trial", "retained", "reverted")
        if not improvement["feedback_source"].strip() or not improvement["friction"].strip():
            errors.append("Improvement observations need nonempty friction and provenance.")
        if status != "observed" and (not improvement["proposal"].strip() or not improvement["expected_benefit"].strip()):
            errors.append("Proposed improvements need one change and an expected benefit.")
        approval = improvement["approval"]
        if active and sensitive.intersection(improvement["affected_domains"]):
            if approval["decision"] != "approved" or not approval["by"].strip() or not approval["at"] or not approval["note"].strip():
                errors.append("Sensitive improvement changes need specific recorded human approval.")
        if status in ("trial", "retained", "reverted"):
            for field in ("baseline", "one_change", "measure", "evaluation_boundary", "stop_condition", "rollback_checkpoint", "rollback_action"):
                if not improvement["trial"][field].strip():
                    errors.append("Improvement trial needs " + field + ".")
        if status in ("retained", "reverted"):
            if improvement["after_versions"] is None or any(not (value or "").strip() for value in improvement["decision"].values()):
                errors.append("Retained/reverted improvements need resulting versions, dated rationale and checkpoint.")
            if not improvement["trial"]["result"].strip() or not improvement["trial"]["limitations"].strip():
                errors.append("Completed improvement review needs observed result and limitations.")
            if improvement["after_versions"] is not None and any(improvement["after_versions"][k] < value for k, value in improvement["before_versions"].items()):
                errors.append("Rollback restores content in a new version; do not decrement historical versions.")
    return errors


def ensure_valid(state, now=None):
    errors = validate(state, now)
    if errors:
        raise PipelineError("\n".join(errors))


def get_role(state, role_id):
    for role in state["roles"]:
        if role["id"] == role_id:
            return role
    raise PipelineError("Unknown role ID: " + role_id)


def transition(state, role_id, event, now=None):
    """Pure transition: returns a new state. Caller chooses whether to persist."""
    now_dt = stamp(now)
    ensure_valid(state, iso(now_dt))
    result = copy.deepcopy(state)
    kind = event.get("type")
    role = None if kind == "approve" and event.get("kind") == "facts" else get_role(result, role_id)
    at = iso(now_dt)
    if kind == "intend_apply":
        role["intent"] = {"id": event["intent_id"], "at": at}
        role["decision"] = "apply_intent"
    elif kind == "verify":
        if role["intent"] is None and event.get("purpose") != "discovery":
            raise PipelineError("Record intention before action-specific verification.")
        check = {"id": event["verification_id"], "at": at, "outcome": event["outcome"],
                 "source_type": event["source_type"], "url": event["url"], "evidence": event["evidence"],
                 "purpose": event["purpose"], "intent_id": role["intent"]["id"] if role["intent"] else None}
        role["verifications"].append(check)
        role["job_status"] = check["outcome"]
    elif kind == "prepare_packet":
        if not approved(result, "facts", facts_fingerprint(result)):
            raise PipelineError("Human fact approval for current candidate/evidence is required.")
        old = role["packet"]
        if old:
            role["packet_history"].append(copy.deepcopy(old))
        role["packet"] = {"version": old["version"] + 1 if old else 1, "created_at": at,
                          "input_versions": version_inputs(result, role), "sections": event["sections"],
                          "cover_letter": event.get("cover_letter", {"requested": False, "evidence_ids": []}),
                          "status": "draft", "qa": {"fingerprint": None, "reviewer": None, "findings": []}, "fingerprint": ""}
        role["packet"]["fingerprint"] = packet_fingerprint(result, role)
    elif kind == "qa_pass":
        packet = role.get("packet")
        if not packet:
            raise PipelineError("Prepare a packet before QA.")
        if packet["fingerprint"] != packet_fingerprint(result, role):
            raise PipelineError("Packet inputs changed; prepare a new version before QA.")
        if event.get("fingerprint") != packet["fingerprint"]:
            raise PipelineError("QA must name the current packet fingerprint.")
        if not event.get("reviewer") or not event.get("checks"):
            raise PipelineError("QA needs an independent reviewer and recorded checks.")
        packet["qa"] = {"fingerprint": packet["fingerprint"], "reviewer": event["reviewer"], "findings": event["checks"]}
        packet["status"] = "qa_passed"
    elif kind == "approve":
        approval_kind = event["kind"]
        if event.get("actor") != "human" or not event.get("note", "").strip():
            raise PipelineError("Approvals require a human decision and a recorded note.")
        if approval_kind == "facts":
            target = facts_fingerprint(result)
            target_role = None
        elif approval_kind == "role_selection":
            if event.get("decision", "approved") == "approved" and role["assessment"]["hard_filter_result"] != "pass":
                raise PipelineError("Resolve hard filters before selecting a role.")
            target = role_fingerprint(result, role)
            target_role = role_id
        elif approval_kind in ("materials", "submission"):
            if not role["packet"] or role["packet"]["status"] not in ("qa_passed", "approved"):
                raise PipelineError("Independent QA is required before material/submission approval.")
            target = role["packet"]["fingerprint"]
            if target != packet_fingerprint(result, role):
                raise PipelineError("Packet inputs changed; prepare a new version before approval.")
            target_role = role_id
            if approval_kind == "submission":
                if not approved(result, "materials", target, role_id):
                    raise PipelineError("Approve exact materials before submission consent.")
                if not verification_ready(role, "intention", now_dt):
                    raise PipelineError("Current intention verification is required before submission consent.")
                target = submission_fingerprint(result, role)
        else:
            raise PipelineError("Unknown approval kind.")
        if event.get("fingerprint") != target:
            raise PipelineError("Approval must name the current fingerprint.")
        result["approvals"].append({"id": event["approval_id"], "kind": approval_kind, "role_id": target_role,
                                    "fingerprint": target, "decision": event.get("decision", "approved"), "at": at,
                                    "actor": "human", "note": event["note"]})
        if approval_kind == "role_selection":
            role["decision"] = "shortlisted" if event.get("decision", "approved") == "approved" else "declined"
        if approval_kind == "materials":
            role["packet"]["status"] = "approved" if event.get("decision", "approved") == "approved" else "qa_passed"
    elif kind == "record_application":
        if not event.get("external_reference", "").strip() or event.get("actor") != "human":
            raise PipelineError("Record a human-reported application with an external reference or confirmation note.")
        role["application"]["status"] = event["status"]
        role["application"]["history"].append({"at": at, "status": event["status"], "external_reference": event["external_reference"], "source": "human_report"})
    elif kind == "snooze_reminder":
        reminder = next((r for r in result["reminders"] if r["id"] == event["reminder_id"] and r["role_id"] == role_id), None)
        if not reminder:
            raise PipelineError("Unknown reminder for this role.")
        if stamp(event["until"]) <= now_dt:
            raise PipelineError("Snooze must end in the future.")
        reminder["snoozed_until"] = event["until"]
    elif kind in ("stop_reminder", "complete_reminder"):
        reminder = next((r for r in result["reminders"] if r["id"] == event["reminder_id"] and r["role_id"] == role_id), None)
        if not reminder:
            raise PipelineError("Unknown reminder for this role.")
        reminder["enabled"] = False
    else:
        raise PipelineError("Unsupported event type: " + str(kind))
    result["audit"].append({"at": at, "role_id": role_id if role is not None else None, "event": kind, "mode": "fictional_simulation" if result["fictional"] else "local_record"})
    ensure_valid(result, at)
    return result


def packet_ready(state, role):
    packet = role["packet"]
    return bool(role["decision"] in ("shortlisted", "apply_intent") and packet and packet["fingerprint"] == packet_fingerprint(state, role)
                and packet["status"] == "approved" and approved(state, "facts", facts_fingerprint(state))
                and approved(state, "role_selection", role_fingerprint(state, role), role["id"])
                and approved(state, "materials", packet["fingerprint"], role["id"]))


def submission_gate(state, role, now=None):
    """Adapter checklist only. Passing never causes or promises a submission."""
    now_dt = stamp(now)
    reasons = []
    if not packet_ready(state, role):
        reasons.append("Current facts, role selection, QA and exact materials need approval.")
    if not verification_ready(role, "submission", now_dt):
        reasons.append("Recheck official posting immediately before any separately authorized submission (within 5 minutes).")
    packet = role["packet"]
    if not packet or not approved(state, "submission", submission_fingerprint(state, role), role["id"]):
        reasons.append("Explicit consent for this role and exact material fingerprint is required.")
    if role["application"]["status"] != "not_applied" or role["application"]["history"]:
        reasons.append("Application history requires human review before another submission.")
    # v0.1 has no sending implementation, even if someone edits capability declarations.
    reasons.append("No submission adapter exists in v0.1; apply manually or implement and review an adapter.")
    return reasons


def next_actions(state, now=None):
    now_dt = stamp(now)
    actions = []
    if not state["evidence"]["claims"]:
        actions.append({"role_id": None, "action": "Start intake: choose one recent contribution and its source."})
    elif not approved(state, "facts", facts_fingerprint(state)):
        actions.append({"role_id": None, "action": "Confirm current evidence and positioning; record human fact approval."})
    for role in state["roles"]:
        rid = role["id"]
        if role["application"]["status"] != "not_applied" or role["application"]["history"]:
            action = "Review application history and reconcile uncertain outcomes before another application or follow-up."
        elif role["decision"] == "declined":
            action = "Role declined by the person; retain history. This does not exclude the entire employer."
        elif role["job_status"] == "closed":
            action = "Role observed closed: retain packet/history; investigate only a distinct reopened or new requisition."
        elif role["assessment"]["hard_filter_result"] != "pass":
            action = "Resolve hard-filter gaps or exclude this role; continue independent discovery."
        elif not approved(state, "role_selection", role_fingerprint(state, role), rid):
            action = "Present fit, gaps and questions for human role selection."
        elif role["packet"] is None:
            action = "Request a tailored resume; ask whether a cover letter would help."
        elif role["packet"]["fingerprint"] != packet_fingerprint(state, role):
            action = "Packet inputs changed: prepare a new version, then repeat QA and exact-material approval."
        elif not packet_ready(state, role):
            action = "Complete packet QA and approve exact materials."
        elif role["intent"] is None:
            action = "Packet ready: ask whether the person intends to apply; nothing has been submitted."
        elif not verification_ready(role, "intention", now_dt):
            action = "Recheck official employer/ATS posting for this intention; blocked/login/unknown remains unknown."
        else:
            action = "Ready for manual application review; obtain submission consent and recheck immediately before any authorized submission."
        actions.append({"role_id": rid, "action": action})
    actions.append({"role_id": None, "action": "Model, browser, scheduler, delivery and submission adapters are absent; CLI performs local work only."})
    return actions


def due_reminders(state, now=None):
    now_dt = stamp(now)
    prefs = state["reminder_preferences"]
    if not prefs["opted_in"]:
        return []
    result = []
    for r in state["reminders"]:
        role = get_role(state, r["role_id"])
        if not r["enabled"] or role["decision"] == "declined" or role["job_status"] == "closed" or role["application"]["status"] != "not_applied" or role["application"]["history"]:
            continue
        due = stamp(r["next_due_at"])
        snooze = stamp(r["snoozed_until"]) if r["snoozed_until"] else None
        if now_dt < due or (snooze and now_dt < snooze):
            continue
        # A stable cycle key persists until the next due time is explicitly advanced.
        key = digest({"id": r["id"], "due": r["next_due_at"], "channel": prefs["channel"]})
        if key not in r["acknowledged_keys"]:
            result.append({"id": r["id"], "role_id": r["role_id"], "task": r["task"], "dedupe_key": key,
                           "channel": prefs["channel"], "timezone": prefs["timezone"], "delivery": "not_sent; no delivery adapter"})
    return result


def acknowledge_reminder(state, reminder_id, key, now=None):
    """Record a user-reviewed cycle. This does not assert external delivery."""
    result = copy.deepcopy(state)
    due = next((r for r in due_reminders(result, now) if r["id"] == reminder_id and r["dedupe_key"] == key), None)
    if not due:
        raise PipelineError("Reminder cycle is absent, snoozed, stopped, or already acknowledged.")
    r = next(r for r in result["reminders"] if r["id"] == reminder_id)
    r["acknowledged_keys"].append(key)
    r["next_due_at"] = iso(stamp(now) + timedelta(hours=result["reminder_preferences"]["cadence_hours"]))
    result["audit"].append({"at": iso(stamp(now)), "role_id": r["role_id"], "event": "reminder_acknowledged_locally", "mode": "local_record"})
    ensure_valid(result, now)
    return result


def safe_text(value):
    # Prevent source strings becoming markdown headings/links/HTML or terminal controls.
    value = re.sub(r"[\x00-\x1f\x7f]", " ", str(value))
    return re.sub(r"([\\`*_{}\[\]<>#!|])", r"\\\1", value)


def render_packet(state, role_id, now=None):
    now_dt = stamp(now)
    ensure_valid(state, iso(now_dt))
    role = get_role(state, role_id)
    packet = role["packet"]
    if not packet:
        raise PipelineError("Prepare structured packet inputs first.")
    if packet["fingerprint"] != packet_fingerprint(state, role):
        raise PipelineError("Packet inputs changed; prepare a new version before rendering.")
    claims = claim_map(state)
    candidate = state["candidate"]
    banner = "FICTIONAL DEMONSTRATION — NOT A LIVE JOB OR APPLICATION\n\n" if state["fictional"] else "PRIVATE DRAFT — REVIEW BEFORE EXTERNAL USE\n\n"
    resume = banner + "# " + safe_text(candidate["display_name"]) + "\n\n"
    resume += safe_text(candidate["positioning"]) + "\n\n"
    if candidate["contact_lines"]:
        resume += " · ".join(safe_text(c) for c in candidate["contact_lines"]) + "\n\n"
    for section in packet["sections"]:
        resume += "## " + safe_text(section["heading"]) + "\n\n"
        for cid in section["evidence_ids"]:
            resume += "- " + safe_text(claims[cid]["text"]) + "\n"
        resume += "\n"
    letter = None
    if packet["cover_letter"]["requested"]:
        letter = banner + "# Cover letter draft\n\nDear hiring team,\n\n"
        letter += "I am interested in the " + safe_text(role["title"]) + " role at " + safe_text(role["employer"]) + ".\n\n"
        letter += "My relevant experience includes:\n\n"
        letter += "\n".join("- " + safe_text(claims[cid]["text"]) for cid in packet["cover_letter"]["evidence_ids"])
        letter += "\n\nI would welcome the opportunity to discuss how this experience aligns with your team's needs.\n\nThank you for considering my application.\n\n" + safe_text(candidate["display_name"]) + "\n"
    check = current_verification(role)
    verified = (check["outcome"] + " observed " + check["at"] + "; " + check["evidence"]) if check else "unknown; no official observation recorded"
    lines = [banner, "# Role review packet", "", "- Employer: " + safe_text(role["employer"]),
             "- Role: " + safe_text(role["title"]), "- Requisition: " + safe_text(role["requisition_id"] or "not supplied"),
             "- Identity: " + safe_text(role["identity_key"]), "- Official source: " + safe_text(canonical_url(role["canonical_url"])),
             "- Location: " + safe_text(role["location"]), "- Work arrangement: " + safe_text(role["work_arrangement"]), "- Attendance: " + safe_text(role["attendance"]),
             "- Pay: " + safe_text(role["pay"]["text"]), "- Pay source: " + (safe_text(canonical_url(role["pay"]["source_url"])) if role["pay"]["source_url"] else "not supplied") + " (" + safe_text(role["pay"]["kind"]) + ")",
             "- Posting date: " + safe_text(role["posting_date"] or "not provided"), "- First seen: " + role["first_seen_at"],
             "- Verified as of: " + safe_text(verified), "- Job status: " + role["job_status"] + " (observation only; availability can change)",
             "- Intention verification current: " + str(verification_ready(role, "intention", now_dt)).lower(),
             "- Packet: v" + str(packet["version"]) + " / " + packet["status"], "- Packet fingerprint: " + packet["fingerprint"],
             "- Input versions: " + json.dumps(packet["input_versions"], sort_keys=True), "- Application status: " + role["application"]["status"], ""]
    for title, key in (("Fit", "fit"), ("Gaps", "gaps"), ("Open questions", "questions")):
        lines += ["## " + title, ""] + ["- " + safe_text(v) for v in role["assessment"][key]] + [""]
    action = next(a["action"] for a in next_actions(state, iso(now_dt)) if a["role_id"] == role_id)
    lines += ["## Exact next action", "", action, "", "## Evidence and review", "",
              "Editable sources are preserved. Claims below identify the approved evidence selected; the renderer does not paraphrase or invent facts.", ""]
    for cid in dict.fromkeys(selected_ids(packet)):
        c = claims[cid]
        lines.append("- " + cid + ": " + safe_text(c["source"]) + "; contribution scope: " + c["scope"])
    lines += ["", "QA: " + safe_text(json.dumps(packet["qa"], ensure_ascii=False)), "",
              "Before sharing: inspect all claims and exported pages, confirm audience and exact files, and record human approval. No application has been sent by this tool.", ""]
    return {"review.md": "\n".join(lines), "resume.md": resume, **({"cover-letter.md": letter} if letter else {})}


def write_packet(state, role_id, out, now=None, dry_run=False):
    files = render_packet(state, role_id, now)
    role = get_role(state, role_id)
    # The source snapshot contains selected claims only; never export the whole career bank.
    selected = list(dict.fromkeys(selected_ids(role["packet"])))
    files["structured-input.json"] = json.dumps({"privacy": "PRIVATE REVIEW SOURCE; share only exact approved resume/letter files", "candidate": state["candidate"], "selected_evidence": [c for c in state["evidence"]["claims"] if c["id"] in selected], "role_source": role_content(role), "packet": role["packet"]}, indent=2, ensure_ascii=False) + "\n"
    manifest = {"role_id": role_id, "packet_version": role["packet"]["version"], "packet_fingerprint": role["packet"]["fingerprint"],
                "generated_at": iso(stamp(now)), "application_status": role["application"]["status"],
                "files": {name: hashlib.sha256(content.encode()).hexdigest() for name, content in files.items()}}
    if dry_run:
        return manifest
    out = Path(out)
    if out.exists():
        raise PipelineError("Output directory already exists. Choose a new versioned destination to preserve editable sources.")
    out.mkdir(parents=True)
    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def verify_packet_files(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    errors = []
    for name, expected in manifest["files"].items():
        target = directory / name
        if Path(name).name != name:
            errors.append("Unsafe manifest filename.")
        elif not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            errors.append("Changed or missing file: " + name + "; regenerate and obtain new review/approval.")
    return errors
