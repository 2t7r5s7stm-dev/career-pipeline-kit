# Improve the process without adding another job

The point is less friction and better decisions for this person, not endless optimization. The agent maintains this loop alongside the career work. Use it when the person asks **“What could work better here?”** or when a repeated problem materially affects progress. Do not run a retrospective after every role or turn every response into a new task.

The optional private workspace `improvements[]` record uses the supported states `observed`, `proposed`, `approved`, `trial`, `retained` and `reverted`. Local validation checks record shapes, one active trial, declared safeguard preservation, sensitive-domain approval fields, bounded trial/rollback details and completed-result/version references. It does not establish semantic truth, actual capability evidence or approval, run experiments, change preferences or execute external behavior. Observation, approval, trial execution, evidence judgment and sanitized export are agent/manual work. Keep the [improvement log](../templates/improvement-log.md) private and reuse existing profile, search and style versions rather than creating another tracking system.

## One small loop

1. **Observe with a source.** Name one friction: repeated questions, irrelevant or missed roles, stale records, unused packet work, failed handoffs or reminder fatigue. Cite a dated candidate comment, roster rows, batch summary or tool result. Separate an observation from an interpretation; do not manufacture feedback.
2. **Propose one change.** Explain the likely cause, the smallest change, expected benefit and what will remain uncertain. Classify it as a personal preference or a potentially reusable process fix. “Leave it as it is” is a valid choice.
3. **Check approval and preserve a rollback.** Approval is required before changing goals, filters, cadence, privacy or external behavior. Record the actual decision. Routine reversible organization within the agreed workflow does not need a new approval ceremony. No trial may weaken fact checks, consent or environment requirements. Save the before-checkpoint and affected versions.
4. **Trial within a bound.** Agree on one next batch, one session or another small limit and a sensible observable measure. Keep at most one active trial. The measure should match the friction: repeated questions per session, roles with attendance captured, roles requiring avoidable rework, or reminders the person found useful. Do not optimize application volume at the expense of fit or wellbeing.
5. **Compare and decide.** Record what happened, the evidence and important differences between the baseline and trial. Ask for a concise keep/revert decision where needed. A small sample is directional feedback, not proof of causation. A higher interview rate in a tiny sample does not prove the change caused it. A single callback or rejection remains tentative feedback; it must not become a permanent ranking rule or a causal conclusion.
6. **Checkpoint and stop.** Keep or revert, record rationale and prior/current versions, and clear the active trial. Restore the prior preference or process if reverted; preserve the record of what was tried. Continue career work. Revisit only if new friction or user feedback warrants it.

If evidence is insufficient, mark that limitation and stop the trial or return the record to `proposed` for a later decision; there is no separate `paused` state. Do not keep extending experiments indefinitely. A person can decline or stop any review.

## A concise response to “what could work better here?”

> One useful change: [proposal]. I noticed [friction, source and date]. It may help by [expected benefit]. This is [personal preference / reusable process idea]. [Approval needed, or within the existing agreement.] We could try it for [small bound], checking [observable measure], then keep or revert it. We can also leave things alone and continue with [current career task].

Do not present a catalogue of optimizations. Use the candidate's preferred pace and detail.

## Fictional example: commute information was missed

All names, counts and outcomes in this example are invented. A candidate has already confirmed a commute constraint. Two surfaced roles were ranked before their attendance was assessed, creating avoidable review of potentially unsuitable onsite roles. The agent traces the batch to source notes: attendance was not captured before ranking. This is a process omission, not evidence that the candidate should relax the constraint.

The proposed change is to capture actual attendance and its source before ranking. Confirmed conflicts fail the existing constraint; unknown attendance stays visible as **investigate**, rather than being silently treated as remote or excluded. Capturing a missing field implements the existing agreement. If the agent proposes a new filter—such as rejecting every role with unknown attendance—it must first record the candidate's approval and increment the search-brief version.

The [fictional structured log](../examples/fictional/improvement-record.json) records a two-role baseline, the capture rule, the before-checkpoint and a trial of the next two leads. The invented trial assesses attendance before ranking; one lead has known attendance and the other stays unknown and is held for clarification. No confirmed conflicting onsite role is presented as a fit; the unknown lead remains a question. The candidate chooses to keep the capture step. The agent records the result, limitations and current search/process versions, while preserving the old checkpoint for rollback. These counts describe handling of this batch; they do not establish better interview odds.

If the extra capture work were not useful, the agent would revert the process step while preserving the candidate's original commute constraint. A rollback cannot erase a user constraint or weaken verification and approval requirements.

## Fictional example: no scheduler

A session can edit local drafts but has no observed scheduler or notification channel. The capability orientation says so. Instead of claiming a reminder is scheduled, the agent saves a private checkpoint with one next action and offers a user-triggered return: “When you come back, say ‘pick up where we left off.’” A scheduler is optional setup only if the person wants future delivery; no account connection or recurring task is authorized by this example.

## Private adaptation and a portable restart

Store personal feedback, trials, roster evidence and checkpoint references only in the candidate's private workspace. Do not send them as telemetry or copy them into the public kit. A reusable fix can be written as a sanitized proposal with fictional examples. Exclude personal claims, contacts, private feedback, identifying URLs, tokens and approval records. Review the sanitized result before any separately authorized export. Sanitization itself does not authorize upload, publication or upstream submission.

A new chat/provider reads the checkpoint, current versions, open trial and capability manifest, then revalidates its actual access. It preserves the person's decisions but does not inherit a claim that old browsing, scheduling or file tools remain available. Reassess the changed capability without restarting intake. If a trial cannot continue safely, record why, return it to `proposed` while awaiting a decision, and offer a small manual next step.
