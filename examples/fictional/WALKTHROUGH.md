# Fictional end-to-end walkthrough

Every name, organization, certificate, job, pay amount, approval and page observation in this example is invented. Reserved `.invalid` domains do not point to real applications. This is a simulation of the workflow, not a discovered job or candidate recommendation.

Avery Example wants an operations or enablement role. The evidence bank includes team leadership and supported service-lead work. E-001 describes a four-person handoff redesign; no reliable numeric time saving exists. E-004 deliberately suggests an unsupported 40% reduction and is unresolved. The résumé must exclude it. The baseline retains a fictional education claim and the broader bank stays intact.

The search brief separates relocation and commission-only constraints from collaborative-culture and remote-work preferences. The fictional employer posting is old, but posting age does not exclude it. The matching employer+EX-101 requisition identifies the role. Pay is explicitly fictional, base/year and scoped to one fictional region; attendance details remain a question.

Run from the project root:

```sh
python3 -m career_pipeline demo --out .private/demo-run
```

The demo starts from [workspace.json](workspace.json), simulates fact and role approval, selects E-001/E-002/E-003, prepares an optional cover letter, records independent QA and material approval, records apply intent and a simulated official check. It renders editable files and their hashes. The application status stays `not_applied`. Proposed reminders say `not_sent`; no schedule exists.

The output `events.json` shows exact local transitions. `workspace/workspace.json` is the checkpoint. `packet-v1/` contains private review and source metadata plus the résumé and optional letter. `report.json` states zero network calls, scheduled reminders and applications sent. `closed-after-tailoring.json` demonstrates a later official closed observation without deleting the packet. `closed-next-actions.json` stops the application path.

For the retained reviewable output created during validation, see [validation walkthrough](../../validation/fictional-walkthrough/report.json) and [review packet](../../validation/fictional-walkthrough/packet-v1/review.md). These are public fictional artifacts only. Real workspace data must stay private.

Try rechecking the intended-apply state at a later time:

```sh
python3 -m career_pipeline next-actions .private/demo-run/workspace --now 2026-11-04T12:00:00Z
```

It asks for a new official check; the old “active” observation cannot authorize current action. A new requisition should get a new linked record. Declining this role does not create an employer-wide exclusion. A submission timeout would be uncertain history requiring investigation; v0.1 cannot submit or retry anything.
