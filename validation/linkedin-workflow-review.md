# LinkedIn addition — local review

Prepared 2026-11-04 against the published v0.1.0 base, on `linkedin-profile-workflow`. This addition has not been pushed, published, added to a release or uploaded to Library. Existing public release artifacts remain unchanged.

## Reviewable experience

The optional “update my LinkedIn” path reuses the person's evidence bank, search brief, style and prior decisions. It reads permitted current text or snapshots, compares positioning choices, and returns accurate copy plus grounded visual recommendations in a private packet. Both start guides route to it; no completed résumé, account connection, organized folder or JSON work is required from the person.

The workflow keeps factual confirmation, public clearance, exact-copy approval, edit permission and actual publication distinct. Résumé approval does not clear employer metrics/internal systems for a public profile. The fictional packet demonstrates partial/manual status without implying that all sections were published, and quiet-update wording does not announce a search.

- [Consultative runbook](../docs/linkedin-profile.md)
- [Editor prompt](../prompts/linkedin-editor.md)
- [Audit](../templates/linkedin-profile-audit.md) and [review packet](../templates/linkedin-update-packet.md)
- [Fictional worked packet](../examples/fictional/linkedin-update.md)

## Implemented execution interface

The [execution guide](../docs/linkedin-execution.md) documents the actual local code:

- `career_pipeline/profiles.py`: separate scoped plan/approval/capability/attempt state machine.
- `career_pipeline/profile_cli.py`: private initialization, validation/inspection, local events, default previews, durable locked dispatch and reconciliation.
- `schemas/linkedin-execution.schema.json`, a blank template and fictional plan.
- `tests/test_profiles.py`: 35 new regression tests.

Automatic job scope is headline, About and the body of one stable existing experience entry. Skills, titles, dates, credentials, media and settings remain manual-only. The CLI emits jobs; a host agent must perform actual permitted tools. Its bundled reference host reads and writes **only fictional local JSON**. No live LinkedIn connector/API/browser driver is implemented or tested, and no real profile was accessed or changed.

A field needs current recorded facts/public/material decisions plus a separate one-time actor/session-scoped edit permission. Fingerprints invalidate changed exact plans. The optional `--workspace` gate checks career-source versions/full content and confirmed evidence; omitting it requires independent manual-source review and cannot detect changed external files. The journal cannot authenticate human decisions, prove fact/public-disclosure truth or override host permissions.

Committed dispatch locks/reloads/checks/persists before emitting one executable write. A host re-reads before saving and records completion evidence plus readback. Any possibly executed/unknown write blocks another attempt for that field; matching content alone cannot settle it or establish authorship. A UI without atomic conditional writes retains concurrent-edit risk. Directory synchronization was exercised on the local macOS filesystem; Windows and networked storage durability were not tested.

## Verification

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 tools/check_project.py
git diff --check
python3 -m career_pipeline demo --out <fresh-private-demo-directory>
python3 -m career_pipeline profile demo --out <fresh-private-profile-demo-directory>
```

**80 tests pass**: 45 existing tests and 35 profile-engine/CLI tests. The offline source/link/privacy/JSON check has zero findings; see [current preflight](publication-check.json). Whitespace checks pass. Both complete fictional demos pass. The profile demo performs one local fixture write, verifies that headline/version, leaves About not attempted, and makes zero live calls. [Retained result](linkedin-execution-demo.json).

The local review ZIP is tested for integrity, exact committed source inventory/content, excluded runtime/cache/private paths and clean extraction. Tests/preflight also run from that extraction. These checks verify the reviewed local implementation and package; they are not live LinkedIn or empirical cross-provider usability tests. Common-pattern privacy scanning is not a guarantee about future contributions.

## Independent review

A separate read-only reviewer inspected implementation and human/agent entrypoints and ran **17 independent engine/CLI probes**, then the full 80-test suite. It found and confirmed fixes for:

- Unknown saves previously becoming terminal from a readback: they now remain uncertain until definitive completion evidence, with fresh verification after saved settlement.
- Host-job deadlines missing shorter material/public approval expiries and capability observation age.
- Future/malformed imported approval timestamps.
- A late contradictory result on an older attempt allowing a newer write: all unresolved attempts now block dispatch for that field, including across revised plans.
- Directory rename persistence: the journal synchronizes both file and directory before executable output.

The reviewer confirmed one-time dispatch, concurrent-process exclusion, byte-identical previews, account/session scope, stale-source invalidation, manual fallback, partial field state and conservative reconciliation. No substantive finding remains open.

Scripted experience review confirms that the human can start from pasted partial material without code and the agent reuses evidence instead of restarting intake. A novice study or live provider comparison remains undone. The reviewer also corrected availability-sounding copy and added a per-field publication ledger in the earlier document review.

## Responsibilities that remain with the person/agent/host

Actual evidence truth, meaningful metrics, public disclosure, genuine decisions, identity, current tool permissions, stable live field identity, account access, platform field limits, unavoidable live side effects, service-side idempotency, visual/accessibility QA and actual execution/receipts require real observation and review. Local records are trusted declarations in a cooperative workflow, not tamper-resistant authorization. A copied job cannot be prevented from misuse outside the journal by this tool.

Unknown receipt reconciliation and definitive operation settlement need actual host evidence. Sticky wrong-scope or contradictory-operation conflicts require manual investigation; there is no automatic clearing or retry path. Private checkpoints must retain history across sessions, not fork active executors. No telemetry, scheduler, delivery channel, new credentials or external connections were added.

All example material is fictional. No private career facts, real snapshots, contact details, recordings or positioning materials were copied. Authored guides/templates/examples keep CC BY 4.0; Python and schemas keep Apache 2.0, under the existing [file-based scope](../LICENSE.md), attribution James E. Dunn.

Relevant instructions checked: repository `AGENTS.md`, both start guides, existing evidence/style/consent workflows and the writing-style skill. The style reference service was unavailable; edits follow the kit voice and requested approach without claiming a retrieved personal style match. No media or document-export skill was needed.

The next decision is James's review of this local addition before any push/publication or separately scoped live adapter work.
