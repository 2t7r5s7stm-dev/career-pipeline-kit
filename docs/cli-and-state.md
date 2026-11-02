# CLI and state contract

Use the [friendly entrypoint](../README.md) first. The CLI is an optional local assistant tool. Python 3.9+, standard library only; run from the project root. All commands act on local files, never a job site. `--now` accepts an ISO timestamp with timezone for reproducible demonstrations; use actual observation times in real work, never backdate approval or fabricate page checks.

## Files and versioning

`workspace.json` follows [workspace.schema.json](../schemas/workspace.schema.json). `validate` enforces the bundled schema’s types, required fields, enums, numeric bounds and additional-property rules, plus semantic checks. This hand-written validator implements only the subset used by this schema, not general JSON Schema. Schema consumers may also use a full Draft 2020-12 validator.

Profile, evidence, baseline, style and search have independent positive integer versions. Roles have a revision, identity, source metadata, assessment, decision, job observations, packet and application record. Bump relevant versions after changes and preserve a private checkpoint before editing. Full input content also enters fingerprints, so a missed version bump cannot keep an old material approval current. `prepare_packet` keeps the previous structured packet in `packet_history`; separately keep all prior output folders and full workspace checkpoints for historical inputs. The CLI does not automatically archive every edited JSON record.

Stale packets are valid historical state but are not ready to render, approve or use. Preparing a new packet repairs them; re-run QA and approval. Changed search/role inputs require role-selection review. No title-only dedupe exists. URL normalization removes common tracking parameters and fragments; it does not prove two different URLs are the same job. No-ID possible duplicates need human review.

`job_status` is active/closed/unknown. Blocked, login and conflict details are preserved in observation evidence under unknown. The latest timestamped observation wins; a prior active page cannot override a later unknown/closed check. Future observations are invalid. Posting age never filters a role. The configured action-evidence windows are explicit: intention check within 24 hours of the current intention, pre-submission check within 5 minutes in the submission execution. These windows are extra controls, not a substitute for checking at each event. No guarantee of continued availability follows.

Application status is a small local record (`not_applied`, `applied`, `submitted_unconfirmed`, `withdrawn`, `rejected`, `interview`, `offer`). `applied` means a human reported it, not independent confirmation by this tool. Store the actual receipt/reference in history. A timeout should be recorded `submitted_unconfirmed`; investigate before retrying. This release has no attempt executor, receipt verifier or submission adapter. More detailed in-progress/screening workflow belongs to a reviewed adapter.

## Commands

```sh
python3 -m career_pipeline init .private/avery --example
python3 -m career_pipeline inspect .private/avery
python3 -m career_pipeline transition .private/avery role-001 --event-file .private/event.json
# Review the dry-run state before opting into a local write:
python3 -m career_pipeline transition .private/avery role-001 --event-file .private/event.json --commit
python3 -m career_pipeline packet .private/avery role-001 --out .private/packets/role-001-v1 --dry-run
python3 -m career_pipeline packet .private/avery role-001 --out .private/packets/role-001-v1
python3 -m career_pipeline verify-packet .private/packets/role-001-v1
```

`init`, `packet` and `demo` refuse an existing destination. `transition` and `ack-reminder` default to dry-run; the state is copied in memory and not saved. `packet --dry-run` calculates hashes without creating files. `next-actions`, `inspect`, `validate` and `reminders` are read-only. `--commit` is only a local persistence choice, never external consent.

The optional letter is a deterministic skeleton using selected claims; an agent writer can propose more natural role-specific prose for review. The renderer selects exact approved claim text from the bank; an AI must first propose and get approval for any new wording in the bank. It does not generate paraphrases or verify the truth of a candidate statement. Unconfirmed/estimated claims cannot enter a current packet. Numeric text in confirmed claims needs explicit confirmed metric metadata (unit, baseline, period, attribution and source fields); a human must assess whether those fields are meaningful and truthful. Textual numbers, causality and credentials still require factual review.

## Event objects

Save one JSON object as an event file. `inspect` supplies current fingerprints. These examples show field shapes; the person must actually make the decision. Use unique approval/verification IDs. Never copy fictional approval language into a real workspace.

| `type` | Other required fields | Meaning |
| --- | --- | --- |
| `approve` | `approval_id`, `kind`, `actor: "human"`, `fingerprint`, `note`; optional `decision: "approved"` or `"declined"` | `kind` is facts, role_selection, materials, submission. Facts use `_profile` as role argument and cover positioning plus evidence; role selection needs resolved hard filters to approve. QA is required before materials. |
| `prepare_packet` | `sections: [{heading, evidence_ids}]`; optional `cover_letter: {requested, evidence_ids}` | Requires current fact approval; creates a new draft and binds inputs. Omitting the letter keeps it optional. |
| `qa_pass` | `fingerprint`, `reviewer`, `checks: [strings]` | Record actual independent factual checks of the exact current packet. This declaration cannot prove independence or visual inspection. |
| `intend_apply` | `intent_id` | Record the person’s actual intention; creates a new verification scope. |
| `verify` | `verification_id`, `outcome`, `source_type`, `url`, `evidence`, `purpose` | Outcome active/closed/unknown; purpose discovery/intention/submission. Active/closed must reference matching canonical employer/ATS URL. Actual page inspection is a browser/manual responsibility. |
| `record_application` | `actor: "human"`, `status`, `external_reference` | Record a human-reported result; never submits. Include real receipt or confirmation note. |
| `snooze_reminder` | `reminder_id`, `until` | Suppress until a future timestamp. |
| `stop_reminder` / `complete_reminder` | `reminder_id` | Disable the reminder. Mark completion explicitly; CLI cannot infer that a task is finished. |

```json
{
  "type": "prepare_packet",
  "sections": [{"heading": "Selected experience", "evidence_ids": ["E-001"]}],
  "cover_letter": {"requested": false, "evidence_ids": []}
}
```

For approvals, use the exact hash from `inspect`. Submission consent needs current intention verification and approved materials. Its fingerprint binds the current intent, role identity, canonical destination and exact packet; a new intent invalidates that local consent. The `submission_gate` always reports no adapter in v0.1; it never initiates an application. Destination/action/time restrictions beyond these local fields must be recorded using the [approval log](../templates/approval-log.md) and enforced by any future adapter.

## Reminder planning

The person must opt in to purpose/cadence/timezone/channel. The example is fictional opt-in, not permission for a real person. `reminders` lists due proposals; it does not schedule or send. `ack-reminder WORKSPACE ID --key HASH --commit` records that the user reviewed a local cycle, advances due time by the agreed cadence, and prevents duplicate acknowledgement. It never asserts delivery.

Snoozed, stopped, declined-role, closed-role and applied-role reminders are suppressed. Retained application history also suppresses application nudges after a clerical status reset; reconcile uncertain outcomes before proceeding. Explicitly complete a packet-review reminder when its task is finished. Quiet hours, delivery receipts, pending-job cancellation and channel retries are adapter/manual responsibilities. A read-only listing can return the same pending proposal repeatedly until acknowledged; a delivery adapter must use the stable key transactionally before any send. [Reminder agreement](../templates/reminder-agreement.md).

## Packet contents

`resume.md` and optional `cover-letter.md` are editable drafts. `review.md` and `structured-input.json` are private review material, not application attachments. The source contains only selected claims but may still contain private evidence notes. `manifest.json` hashes every generated content file. If any file changes, hash verification fails; update the evidence/selection, generate a new version, review, and obtain renewed approval. Do not edit a manifest to make a changed artifact appear approved. Passing hash checks verifies integrity, not truth or consent.

No Word/PDF is generated in v0.1. If an assistant exports those later, preserve source, check text extraction and inspect every page for clipping, layout, spelling, contact fields and accessibility before external sharing.

## Optional improvement records

`improvements` is an optional array in the same workspace; earlier states without it remain valid. An agent records observed/proposed/approved/trial/retained/reverted changes, provenance, baseline, one bounded change, expected benefit, evaluation/stop/rollback plan, outcome limitations, rationale and before/after profile versions. It does not apply changes automatically. Use [the private log](../templates/improvement-log.md), [runbook](continuous-improvement.md) and [fictional record](../examples/fictional/improvement-record.json).

`validate` checks record shape, unique IDs, at most one active trial, specific approval metadata for sensitive domains, required trial/rollback fields, completed results/checkpoints and nondecreasing historical versions. `preserves_safeguards` must be true. These are checks of declared records, not proof that an approval is human, a capability is available or a trial happened. The agent/person must enforce actual behavior, truth and consent. No optimizer, telemetry, sanitized-export executor or new external connection is implemented.

Completed records remain valid history after later profile edits. Restore prior content in a new version when reverting; retain unrelated preferences and approval records. Do not rewrite past approval history. A tiny batch or callback is tentative feedback, not a causal interview-rate result or authority to alter ranking permanently.
