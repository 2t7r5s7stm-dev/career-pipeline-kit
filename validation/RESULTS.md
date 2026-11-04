# Validation results · published v0.1.0 baseline

For the v0.1.1 LinkedIn addition and current 80-test suite, see [the separate review record](linkedin-workflow-review.md) and [retained test output](tests-v0.1.1.txt). The checks below describe the v0.1.0 baseline.

Validated locally using Python 3.9.6. All candidate, employer, credential, posting, approval and observation data used is fictional. The fictional validation run performs no live research or model calls and creates no real schedule, notification, upload or application. This describes the demonstration, separately from delivery/publication of the reusable kit.

## Automated checks

Run from the project root:

```sh
python3 -m unittest discover -s tests -v
python3 -m career_pipeline demo --out validation/fictional-walkthrough
python3 -m career_pipeline validate validation/fictional-walkthrough/workspace --now 2026-11-02T12:00:00Z
python3 -m career_pipeline verify-packet validation/fictional-walkthrough/packet-v1
python3 tools/check_project.py
```

The retained walkthrough already exists; to rerun the demo choose a fresh destination such as `.private/review-run`. Commands refuse to overwrite earlier output.

The v0.1.0 baseline suite: **45 unique tests pass** across five test modules. [Retained test output](tests.txt). Tests include safe dry-run and default CLI nonmutation, profile approval without roles, stale packet repair/history, unsupported and numeric-substring metrics, changed facts/role inputs, intent-scoped consent, separate pre-submission window, latest unknown overriding active, aggregator rejection, closed-after-tailoring behavior, new requisition history, duplicate identity, optional cover letters, reminder opt-out/dedupe/snooze/stop/completion/decline, absent adapters, output hash integrity, selected-only evidence export, untrusted text rendering, privacy markers and ZIP runtime exclusion.

[Walkthrough report](fictional-walkthrough/report.json): valid state, hashes match, zero network calls, zero scheduled reminders and zero applications sent. [Review packet](fictional-walkthrough/packet-v1/review.md), [résumé](fictional-walkthrough/packet-v1/resume.md) and [optional letter](fictional-walkthrough/packet-v1/cover-letter.md) were read as editable text. Unsupported E-004 is absent from résumé, letter and selected-evidence snapshot. A later closed observation retains the packet and stops the application path. These checks do not prove Word/PDF appearance; those formats were not created.

[Publication preflight](publication-check.json) checks every included text/JSON source and retained output for broken local Markdown links, invalid JSON, common credential/email/home-path leaks and license scope/text/notice presence. Packaging rechecks the source, inspects ZIP contents, tests integrity and excludes runtime/cache directories. It does not upload anything and does not guarantee that future content is public-safe.

## Focused independent release review

A separate reviewer inspected implementation and both start guides against their claims. They found one advisory failure: after a submitted-unconfirmed record was reset to not-applied, the submission gate retained the history block but next actions and reminder planning could still nudge an application. The release now checks retained application history in both places. Two regression tests reproduce and prevent the failure. The affected tests and full suite pass. No new features were added.

The reviewer confirmed stale-intent verification, material-change fingerprints, intent-bound consent, absent sending adapters, private workspace exclusion and the novice/agent resource-first flow. Actual user identity, live observations and external-action controls remain manual/adapter responsibilities.

## Adaptive capability and improvement review

Nine tests cover optional/backward-compatible improvement records, retained/reverted state, specific approval metadata for a sensitive proposal, one active trial, declared safeguard preservation, bounded baseline/evaluation/stop/rollback, completed outcome/rationale/checkpoints including whitespace rejection, historical nondecreasing versions, and unique IDs. The local CLI validates declared records; it does not operate an optimizer or prove a human decision occurred.

Five review invariants are explicit:

1. Current environment capability evidence is an agent/manual responsibility. The kit never promotes availability from a provider name or a different session; the orientation separates direct/manual/optional/unknown help.
2. Sensitive changes cannot enter approved/trial/completed states without recorded specific approval metadata. Actual human identity, scope and behavior remain manual responsibilities; prior task consent does not grant new process consent.
3. Trial records require baseline, one change, evaluation/stop condition and rollback. At most one is active. Keep/revert records preserve versions and rationale; actual checkpoint content and preservation of unrelated preferences/approvals require operator review.
4. A single callback or rejection is tentative feedback. No automated ranking or causal-interview-rate inference is implemented. Outcome interpretation remains manual.
5. Sanitized reusable proposals are manual-only. The runbook excludes personal claims, contacts, private feedback, identifying URLs/tokens and approval records; sanitization never authorizes upload/publication. No telemetry or automatic upstream path exists.

A separate reviewer checked these additions and found one required-text whitespace gap, which was corrected and covered by regression subtests. The commute example aligns with its fictional structured record. Capability revalidation and process trials do not restart intake or ask the human to administer JSON. No live recurring task or third-party connection was added.

## Experience review

[Scripted experience acceptance](../docs/experience-acceptance.md) records a review of a novice reading only the human guide and an agent starting with messy partial materials. It verifies the guide supplies a way to begin without code and the script reuses existing answers, preserves uncertainty and returns few decisions. An empirical novice usability study and tests across named providers have not been conducted.

## Controls that remain agent/manual/adapter responsibilities

Actual fact/source truth, meaningful metric interpretation, credential confirmation, ownership nuance, scope of material access, confidential-data judgment, interview pacing, contradictions and search strategy are human/agent work. The local validator catches selected structural/invariant errors, not semantic truth.

Live discovery, official webpage inspection, requirements interpretation, salary/attendance verification and malicious-instruction judgment require a capable agent/browser or person. The CLI records declared evidence; it cannot prove a page was visited or the observation is true.

Actual user identity/consent, destination/recipient/actor/time restrictions, screening answers, export accessibility and visual QA, scheduled runtime, quiet hours, transactional delivery dedupe, receipts, uncertain-submission reconciliation and external-action authorization are manual/adapter duties. No outgoing adapter exists; the submission gate always reports that limitation. Local `--commit` never sends anything.

Full historical workspace checkpoints are saved by the agent/operator before edits. CLI preserves prior structured packets and refuses existing output directories; it does not archive every JSON edit. Reminder proposals are not scheduled notifications. No real-world continued availability is guaranteed.

Public v0.1 early release is authorized. The license split is Apache 2.0 for code and specified implementation files, and CC BY 4.0 for authored guides/templates and fictional content, with attribution to James E. Dunn. The public repository starts with clean history and a reviewed source file set. Live automation still needs separately implemented/reviewed adapters and authorization.

## v0.1.1 LinkedIn addition

The reviewed LinkedIn addition adds consultative profile review and a scoped execution bridge, with manual fallback and a fictional local-file host. The full suite now passes **80 tests**, including 35 new profile regression tests. A separate reviewer ran 17 independent probes and the full suite; identified issues were fixed and no substantive finding remains open. See the [focused review](linkedin-workflow-review.md) for implementation boundaries, exact checks, source-gate limitations and host responsibilities, plus the [retained fictional demo](linkedin-execution-demo.json). The v0.1.1 release preserves the earlier v0.1.0 artifacts and does not claim a tested live LinkedIn adapter.
