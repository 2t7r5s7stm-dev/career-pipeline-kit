# Copyright 2026 James E. Dunn
# SPDX-License-Identifier: Apache-2.0
"""Run from the project root: python3 -m career_pipeline --help."""
import argparse
import json
import shutil
import sys
from pathlib import Path
from .core import (ROOT, PipelineError, acknowledge_reminder, due_reminders, ensure_valid,
                   facts_fingerprint, get_role, iso, load, next_actions, packet_fingerprint,
                   role_fingerprint, save, stamp, submission_fingerprint, submission_gate, transition, validate,
                   verify_packet_files, write_packet)


def output(value):
    print(json.dumps(value, indent=2, ensure_ascii=False))


def parser():
    p = argparse.ArgumentParser(description="Local career operations; no APIs, scheduling, uploads or submissions.")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("profile", help="Guarded LinkedIn field job bridge; run profile --help.")
    init = sub.add_parser("init", help="Initialize a new private workspace (never overwrites).")
    init.add_argument("workspace")
    init.add_argument("--example", action="store_true", help="Copy unmistakably fictional data.")
    for name in ("validate", "next-actions", "reminders", "inspect"):
        command = sub.add_parser(name)
        command.add_argument("workspace")
        command.add_argument("--now", help="ISO 8601 time with zone; useful for deterministic examples.")
    t = sub.add_parser("transition", help="Apply a structured local event; default is a non-mutating preview.")
    t.add_argument("workspace");t.add_argument("role_id");t.add_argument("--event-file", required=True)
    t.add_argument("--now");t.add_argument("--commit", action="store_true", help="Persist reviewed local state; does not authorize external action.")
    packet = sub.add_parser("packet", help="Render editable Markdown and an evidence manifest from approved claims.")
    packet.add_argument("workspace");packet.add_argument("role_id");packet.add_argument("--out", required=True)
    packet.add_argument("--now");packet.add_argument("--dry-run", action="store_true")
    verify = sub.add_parser("verify-packet", help="Check hashes after generation; edits need renewed review.")
    verify.add_argument("directory")
    ack = sub.add_parser("ack-reminder", help="Acknowledge a local reminder cycle; never claims delivery.")
    ack.add_argument("workspace");ack.add_argument("reminder_id");ack.add_argument("--key", required=True);ack.add_argument("--now")
    ack.add_argument("--commit", action="store_true")
    demo = sub.add_parser("demo", help="Simulate the full fictional walkthrough locally.")
    demo.add_argument("--out", required=True)
    return p


def initialize(path, example=False):
    path = Path(path)
    if path.exists():
        raise PipelineError("Workspace already exists; choose a new directory.")
    path.mkdir(parents=True)
    source = ROOT / ("examples/fictional/workspace.json" if example else "templates/workspace.blank.json")
    shutil.copyfile(source, path / "workspace.json")
    (path / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")
    return {"workspace_created": str(path), "fictional": example, "external_actions": "none", "next": "Open prompts/start.md with your agent; keep the workspace private."}


def demo_run(out):
    destination = Path(out)
    if destination.exists():
        raise PipelineError("Demo destination already exists; choose a fresh directory.")
    destination.mkdir(parents=True)
    workspace = destination / "workspace"
    initialize(workspace, True)
    state = load(workspace)
    now = "2026-11-02T12:00:00Z"
    role_id = "role-001"
    events = []
    def apply(event):
        nonlocal state
        before = state
        preview = transition(before, role_id, event, now)
        assert before == state  # transition is pure; nothing is sent.
        state = preview
        events.append(event)
    apply({"type":"approve","approval_id":"SIM-FACTS","kind":"facts","actor":"human","fingerprint":facts_fingerprint(state),"note":"SIMULATED fictional candidate fact and positioning approval."})
    role = get_role(state, role_id)
    apply({"type":"approve","approval_id":"SIM-ROLE","kind":"role_selection","actor":"human","fingerprint":role_fingerprint(state,role),"note":"SIMULATED fictional role selection."})
    apply({"type":"prepare_packet","sections":state["base_resume"]["sections"],"cover_letter":{"requested":True,"evidence_ids":["E-001","E-002"]}})
    role = get_role(state, role_id)
    fp = role["packet"]["fingerprint"]
    apply({"type":"qa_pass","fingerprint":fp,"reviewer":"Fictional independent reviewer","checks":["Approved claim IDs only; E-004 invented metric excluded.","Leadership scope preserved; editable Markdown text inspected.","Rendered Word/PDF visual QA remains required if those exports are created."]})
    apply({"type":"approve","approval_id":"SIM-MATERIALS","kind":"materials","actor":"human","fingerprint":fp,"note":"SIMULATED approval of the exact fictional materials."})
    apply({"type":"intend_apply","intent_id":"INTENT-SIM-001"})
    apply({"type":"verify","verification_id":"VERIFY-SIM-001","outcome":"active","source_type":"employer","url":role["canonical_url"],"evidence":"SIMULATED official page explicitly states the matching requisition is accepting applications; apply form available. Not browsed; reserved example domain.","purpose":"intention"})
    save(workspace,state)
    manifest=write_packet(state,role_id,destination/"packet-v1",now)
    (destination/"events.json").write_text(json.dumps(events,indent=2)+"\n")
    (destination/"next-actions.json").write_text(json.dumps(next_actions(state,now),indent=2)+"\n")
    reminders=due_reminders(state,now)
    (destination/"reminders-proposed.json").write_text(json.dumps(reminders,indent=2)+"\n")
    closed=transition(state,role_id,{"type":"verify","verification_id":"VERIFY-SIM-CLOSED","outcome":"closed","source_type":"employer","url":role["canonical_url"],"evidence":"SIMULATED official posting states applications are closed.","purpose":"intention"},"2026-11-02T12:01:00Z")
    (destination/"closed-after-tailoring.json").write_text(json.dumps(closed,indent=2)+"\n")
    (destination/"closed-next-actions.json").write_text(json.dumps(next_actions(closed,"2026-11-02T12:01:00Z"),indent=2)+"\n")
    report={"fictional_simulation":True,"network_calls":0,"scheduled_reminders":0,"applications_sent":0,"state_validation":validate(state,now),"packet_hash_check":verify_packet_files(destination/"packet-v1"),"manifest":manifest,"reminders_proposed":len(reminders),"closed_role_preserves_packet":closed['roles'][0]['packet'] is not None,"submission_gate":submission_gate(state,get_role(state,role_id),now)}
    (destination/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    return report


def main(argv=None):
    effective = sys.argv[1:] if argv is None else argv
    if effective and effective[0] == "profile":
        from .profile_cli import main as profile_main
        return profile_main(effective[1:])
    args=parser().parse_args(effective)
    try:
        if args.command=="init":
            output(initialize(args.workspace,args.example));return 0
        if args.command=="demo":
            output(demo_run(args.out));return 0
        if args.command=="verify-packet":
            errors=verify_packet_files(args.directory);output({"errors":errors});return 1 if errors else 0
        state=load(args.workspace)
        now=args.now
        if args.command=="validate":
            errors=validate(state,now);output({"valid":not errors,"errors":errors});return 1 if errors else 0
        ensure_valid(state,now)
        if args.command=="next-actions":output(next_actions(state,now))
        elif args.command=="reminders":output(due_reminders(state,now))
        elif args.command=="inspect":
            output({"facts_fingerprint":facts_fingerprint(state),"roles":[{"id":r['id'],"role_selection_fingerprint":role_fingerprint(state,r),"packet_fingerprint":r['packet']['fingerprint'] if r['packet'] else None,"packet_is_current":r['packet']['fingerprint']==packet_fingerprint(state,r) if r['packet'] else False,"submission_fingerprint":submission_fingerprint(state,r),"submission_gate":submission_gate(state,r,now)} for r in state['roles']]})
        elif args.command=="transition":
            event=json.loads(Path(args.event_file).read_text())
            result=transition(state,args.role_id,event,now)
            if args.commit:save(args.workspace,result)
            output({"mode":"committed_local_state" if args.commit else "dry_run_no_changes", "state":result,"external_actions":"none"})
        elif args.command=="packet":output(write_packet(state,args.role_id,args.out,now,args.dry_run))
        elif args.command=="ack-reminder":
            result=acknowledge_reminder(state,args.reminder_id,args.key,now)
            if args.commit:save(args.workspace,result)
            output({"mode":"committed_local_state" if args.commit else "dry_run_no_changes","delivery":"not_sent","state":result})
        return 0
    except (PipelineError,OSError,json.JSONDecodeError,KeyError,TypeError) as exc:
        print("Error: "+str(exc),file=sys.stderr);return 2


if __name__=="__main__":
    sys.exit(main())
