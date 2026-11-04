# LinkedIn workflow addition — local review

Prepared 2026-11-04 against the published v0.1.0 base. This addition is local on `linkedin-profile-workflow`; it has not been pushed, published, added to a release or uploaded to Library. Existing public release artifacts are unchanged.

## What changed

An optional consultant-style “update my LinkedIn” path now reuses the current career evidence, search brief and style guide. It reviews only supplied/permitted profile material, explains current capability limits, compares positioning choices, and prepares accurate copy plus optional visual recommendations. There is no connection requirement or new account access.

New materials:

- [LinkedIn runbook](../docs/linkedin-profile.md)
- [Editor prompt](../prompts/linkedin-editor.md)
- [Profile audit](../templates/linkedin-profile-audit.md)
- [Update packet](../templates/linkedin-update-packet.md)
- [Fictional worked example](../examples/fictional/linkedin-update.md)

Both start guides, README, the agent contract/loop, existing editor/QA/follow-up prompts, style/approval templates and privacy/CLI documentation route to this path. The workflow separates fact confirmation, public clearance, exact-copy approval, action permission and publication evidence, including partial updates per field. All new authored Markdown uses the existing CC BY 4.0 scope. Code and schema remain unchanged under Apache 2.0.

## Verification

Commands run from the project root:

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_project.py

git diff --check
```

The full existing suite passes: **45 tests**. The current offline source/link/privacy/JSON preflight passes with zero findings; see [the current preflight](publication-check.json). Whitespace checks pass. A local review ZIP is checked for integrity, excluded private/runtime/cache paths, source file inventory, and consistency with the reviewed branch. It is a review artifact, not a published release.

The addition is a guide/prompt/template workflow, so no new implementation-mirroring unit tests were added. Existing lifecycle, reminder, consent, state and packaging tests still pass. The checker's common-pattern scan is not a guarantee that future candidate material is safe to share.

## Independent scripted acceptance review

This review uses only the supplied fictional example and kit files. It is not a live LinkedIn session, an empirical novice study or a provider comparison.

| Scenario | Accepted behavior in the reviewed materials |
| --- | --- |
| Returning person asks for LinkedIn help | Reuse evidence/search/style versions; ask only missing material decisions; no repeated intake or completed résumé prerequisite |
| Only headline/About text is supplied | Draft those; mark experience, skills, visuals and live settings not reviewed; no connector or export requirement |
| Employer-first versus project-first choice | Compare relevance, evidence, public permission and preferences; no single prescribed order or invented independent project |
| Recruiter/audience language | Use supported capability terms, distinguish target labels from held titles, and make no ranking/callback promise |
| Résumé claim is factual but not publicly cleared | Keep employer metrics, internal systems, client/contact details out until destination-specific clearance; omit or approve a truthful generalization |
| Person wants a quiet update | Avoid inferred availability language, job-search signals, notification or visibility changes; example About describes work rather than announcing a search |
| One field is approved and manually pasted | Record that field's exact version and manual report only; other fields remain pending/not attempted; no invented live readback |
| Unseen visual or device layout | Mark not assessed; offer a later optional review rather than inventing critique, traits, assets or rights |
| A permitted later save has an uncertain result | Inspect current state before retrying; never mark confirmed publication from drafting approval or a timeout |

The reviewer identified two refinements that were incorporated: remove availability-sounding copy from the quiet-update example, and add a per-field publication ledger. The example also holds a broader skill label out pending specific confirmation rather than treating a search-brief label as sufficient public evidence.

## Limits and next review

There is no LinkedIn reader/editor/API, no new CLI command or profile-state schema, no automatic public-clearance enforcement and no live modification capability in this addition. Markdown profile records are agent/person maintained; factual truth, actual consent, public disclosure and any later live action require human/environment review. Do not add unsupported LinkedIn fields to the strict workspace JSON.

No real profile, screenshot, career evidence, contact detail or private positioning example was copied into the kit. The worked packet is fictional. No LinkedIn page was accessed, no profile/settings changed, and no reminder scheduled. Current platform field limits, controls, appearance, mobile previews and publication status were not live-verified; the guide calls for checking the actual interface only if a later chosen update requires it.

Relevant instructions checked: repository `AGENTS.md`, both start guides, the existing evidence/style/consent workflows and the writing-style skill. The style reference service was unavailable; edits follow the existing kit's voice and the requested approach without claiming a retrieved personal style match. No media/document-export skill was needed because this addition produces no image, Word or PDF.

James can review the wording and example locally before authorizing any push or publication. The published v0.1.0 version and its licenses remain intact.
