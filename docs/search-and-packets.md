# From a search brief to an application packet

Use this runbook after an initial career conversation; do not wait for a perfect résumé. Discovery can test the direction while intake continues. The local CLI manages supplied state and packets. Live research, writing, visual rendering, scheduling and outgoing actions require a capable agent, a manual step or a separately implemented adapter. See [adapter boundaries](adapters.md).

## 1. Build a search brief around capabilities

**Owner:** orchestrator and role researcher. **Prompt:** [role researcher](../prompts/role-researcher.md).

Start with three questions: “Which capabilities do you want to use more?”, “What work environment helps you do good work?”, and “Which constraints would make a role unworkable?” Use the answers to create a small initial brief, then refine it through actual results.

| Search dimension | Practical decision |
| --- | --- |
| Capabilities | What the evidence shows the candidate can do, including leadership and adjacent transferable work |
| Role families | Primary and adjacent functions worth exploring; scope and level rather than title alone |
| Titles | Common synonyms, alternate titles and industry language for those functions |
| Environment | Team size, decision rights, resources, manager relationship, pace and desired culture signals |
| Location and attendance | Eligible geography, remote restrictions, commute, office days, travel and relocation |
| Pay | Currency, base versus total compensation, period, workable range and tradeoffs |
| Hard filters | Genuine non-negotiables, with a reason and the evidence needed to pass |
| Preferences | Desirable conditions that can be weighed against other strengths |
| Exclusions | Employers, industries, job patterns or activities the candidate explicitly wants omitted |
| Unknowns | Decisions that remain open and the next question that would resolve them |

Make tradeoffs visible. For example, a candidate might accept more office attendance for a better scope or accept a narrower title for stronger development. Do not silently convert a preference into a hard filter. An unknown requirement is a question, not an automatic pass or failure. Confirm any change to a hard filter with the candidate.

## 2. Set up a repeatable search

Create a small query set combining role families, synonyms, capabilities and geography. For example, `("program operations" OR "operational excellence") AND remote` is a query pattern, not evidence that a particular role exists. Include official employer career pages and reputable ATS sources. Aggregators and community leads can expand discovery, but they are leads until checked.

If browsing is unavailable, produce the query plan and official source list for a person to run. Do not invent employers, requisitions or current openings. Label any demonstration role fictional. Save new real leads only from observed sources supplied by the user or reached through an authorized browser/search capability.

Record why a result was kept or excluded. Search quality means useful matches and explainable tradeoffs, not a large count of roles. Periodically review examples with the candidate and adjust the brief; do not repeatedly show an explicit exclusion.

## 3. Resolve identity and current evidence

Use employer plus requisition ID as the role identity. If no requisition ID is available, use the canonical official posting URL. Title alone is insufficient: the same title can describe different teams, locations and requisitions.

Record the discovery URL and official employer/ATS URL separately. Preserve posting date and its source/precision, first-seen time and each verification observation. An old posting may still be open; there is no automatic posting-age cutoff. A recent aggregator listing may already be closed.

Use `active`, `closed` or `unknown` according to what the official source supports. Retain the evidence and checked time. Login walls, blocked access, broken redirects, ambiguous pages and failed requests mean unknown. A search snippet, successful HTTP response or visible button alone does not establish that applications are accepted. Explain conflicting observations instead of resolving them by guesswork.

A repost under a new requisition becomes a new role record related to the earlier one. Preserve the earlier application and packet history. If an existing requisition changes, update its revision and reassess affected fit, packet content and approvals. Do not carry an old approval forward without checking the changed inputs.

## 4. Present a short, decision-ready role card

For each useful role, present the official link and requisition, then a concise fit assessment. Connect strengths to candidate evidence. Separate capability gaps, missing information and preferences that are less ideal. Show hard-filter results and the source behind them.

Location includes eligibility and attendance, not only the advertised city. Pay includes its source, currency, period, base/total basis and applicable geography. Clearly label employer-posted pay, recruiter reports, estimates and unknowns. Do not present an estimate as a disclosed range or infer that a range applies to every location.

End with a small decision: select for tailoring, investigate one question, defer, or exclude. Keep a role with an unknown detail available for investigation when it may still be useful. Selection is a human decision and is separate from submitting an application.

## 5. Tailor after selection

**Owner:** tailoring writer. **Prompt:** [tailoring writer](../prompts/tailoring-writer.md).

Use the selected requisition, current assessment, confirmed evidence and approved style guide. Change emphasis and ordering to fit the role while preserving the truth of the claims. Track input versions and connect tailored statements to evidence IDs. Ask one targeted question if a missing fact changes the application; continue other useful drafting in parallel.

A cover letter is optional. Draft one when the candidate requests it, the application requires it, or it helps explain relevant motivation or a transition. Confirm whether it is worth the effort. Do not create extra work merely to fill a packet folder.

## 6. Assemble and inspect the packet

**Owner:** writer, then independent QA. **Prompt:** [QA reviewer](../prompts/qa-reviewer.md).

A review packet should include:

- Official source, employer, title and requisition identity.
- Location, work arrangement, attendance and travel requirements.
- Pay details with source, basis, geography and unknowns.
- Evidence-based fit, gaps, hard-filter findings and open questions.
- Observed posting status, verified-as-of time, source evidence and limitations.
- Versioned tailored résumé, optional proposed letter and claim map.
- Editable sources, input versions, factual QA results and visual QA status.
- The exact next action, its owner and the approval or fact still needed.

Check facts, attribution, chronology, requirements, links and grammar. Inspect rendered exports page by page and check extracted text when producing DOCX/PDF materials. A Markdown packet can be reviewed as source without claiming exported-document visual QA. Keep generated exports alongside their editable inputs and preserve earlier versions.

The packet should tell the candidate what to do next, such as “Review résumé version 3 and confirm the project scope.” It should not bury that ask beneath a long agent transcript. Use the [agent work-order contract](agent-loop.md) to return findings and update dependent state.

## 7. Recheck at intention to apply

When the candidate decides to apply, revisit the exact official posting and record a verification tied to that intention. Prior discovery evidence is not enough. The CLI's verification reuse limits are action gates; expiry means recheck, not closed. Verification is an observation at a time and never guarantees continued availability.

Check again immediately before any separately authorized submission. This starter kit does not submit. If a future adapter is added, it must obtain the required authorization, bind it to the exact materials/destination and confirm the outcome. A role that closes after tailoring stops application prompts for that requisition; keep the work and history for a candidate decision about related opportunities. An unknown result pauses the affected action for verification.

## 8. Record outcomes and follow up without pressure

**Owner:** follow-up coordinator. **Prompt:** [follow-up coordinator](../prompts/follow-up-coordinator.md).

Keep job status, packet readiness, consent and application status distinct. A tailored résumé is not a submitted application. Record an application only from a confirmed result or the candidate's explicit report, retaining its time and reference. An uncertain submission must be reconciled before retrying.

Ask whether the candidate wants reminders and record scope, cadence, timezone and channel. Deduplicate, honor snooze/stop and cancel reminders when completed, deselected or no longer applicable. No scheduler is included in v0.1; a local next-action list is not a scheduled notification. End the session with a clear owner and next action, then loop new evidence and preferences back into the bank and search brief.
