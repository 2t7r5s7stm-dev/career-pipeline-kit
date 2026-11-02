# A portable agent loop

Use this operating contract with the agent you already prefer. An agent role is a responsibility; it does not require a separate product, subscription, or concurrent worker. One person and one agent can move through the same roles in sequence.

The local v0.1 CLI provides workspace and state utilities described in the [README](../README.md). It does not call a model, browse, run in the background, send reminders, share files, or submit applications. Prompts describe work an agent can do after the user starts a session. Adapters must be added and authorized before any external capability exists.

## Start with a small agreement

The orchestrator opens with three questions, using answers already in the workspace:

1. What would make this session useful: capture career evidence, build the base résumé, refine the search, review roles, or finish a packet?
2. Which decisions are already settled, and what should stay open for now?
3. What time or energy limit should shape today's work?

Then propose one small deliverable and begin. Ask for missing facts only when they affect the next decision. Continue independent work while waiting. For example, research role requirements while a candidate checks a metric, but do not place the unconfirmed metric in a final résumé.

Discovery may begin while intake continues. The evidence bank remains broad across the career; a résumé is a selective view of that evidence. A lack of polished prose is not a reason to delay learning which roles are worth pursuing.

## Route work by responsibility

| Role | Work it owns | Output and acceptance check |
| --- | --- | --- |
| Orchestrator | Choose the next useful job, preserve versions, route questions and reconcile results | A scoped work order; no duplicate task or contradictory state; one clear next decision |
| Intake researcher | Elicit career evidence, sources, dates, scope and attribution | Traceable evidence with unknowns flagged; no invented facts or credentials |
| Career editor | Select relevant evidence and develop positioning, base résumé and style guide | Editable drafts tied to confirmed evidence; leadership and team outcomes attributed accurately |
| Role researcher | Discover leads, resolve role identity, assess fit and check official sources | Official source and requisition identity when available; observed status, evidence and verification time |
| Tailoring writer | Adapt approved positioning and evidence to a selected role | Versioned résumé and optional cover letter with a claim map; unresolved claims excluded or visibly held for review |
| Independent QA reviewer | Challenge facts, fit, chronology, attribution, formatting and workflow state | Specific pass/fail findings against the work order; corrections checked before readiness is claimed |
| Follow-up coordinator | Identify a small next action, reconcile candidate choices and manage authorized reminders | Deduplicated, snoozable actions; no false scheduling or submission claims |

Independence in QA can mean a separate agent or a fresh review pass that reads the source evidence and job posting before reading the writer's rationale. It is not proof of correctness. The candidate still approves the final facts and positioning.

## Give each job an explicit contract

Do not hand off “make it better.” Include stable file identifiers and versions, the allowed scope, the intended output, and the checks that establish completion. A portable work order can look like this:

```json
{
  "work_id": "work-014",
  "assigned_role": "tailoring_writer",
  "objective": "Draft a role-specific resume for candidate review",
  "inputs": [
    {"file": "evidence.json", "version": 4},
    {"file": "base-resume.md", "version": 2},
    {"file": "style-guide.md", "version": 1},
    {"file": "role-assessment.json", "version": 3}
  ],
  "allowed_actions": ["read approved inputs", "write a new local draft"],
  "excluded_actions": ["upload", "message anyone", "submit an application"],
  "expected_outputs": ["resume-v003.md", "claim-map-v003.json"],
  "acceptance_checks": [
    "Every candidate claim has a confirmed evidence reference",
    "Role identity matches the selected requisition",
    "Leadership and team contributions are attributed accurately",
    "Unknown requirements are recorded without inventing experience"
  ],
  "unknowns": ["Whether a cover letter is useful or requested"],
  "next_human_decision": "Review positioning and approve or revise the draft"
}
```

This example illustrates an operating contract; it is not a promise that the CLI executes or validates arbitrary work orders. Use the actual state fields and schema files supplied by the kit when creating machine-readable state.

## Return a result, not just prose

Every worker returns:

- Work ID and exact input versions read.
- Paths and versions of editable outputs, plus any derived exports.
- Acceptance checks with evidence for pass, fail or not checked.
- New evidence and its source, separately from interpretations.
- Unknowns, assumptions and any blocked action with the reason.
- Changes proposed to state, and the next candidate decision.

The orchestrator checks that input versions are still current before accepting the result. If an evidence correction, search change or new posting revision affects the work, mark the result for review and rerun only the affected steps. Do not silently overwrite a newer draft or treat a superseded approval as current.

## Keep approvals specific

Use an approval log that identifies the subject, version, decision, approver and time. Approval of one subject does not imply approval of the next:

1. Confirm candidate facts, metrics, education and attribution.
2. Approve positioning and the style guide.
3. Select a particular employer and requisition for tailoring.
4. Approve the final version of material for its stated external destination.
5. Authorize the submission action, when supported and permitted in the execution environment.

Drafting, packet readiness, consent, posting status and application history remain separate. A ready packet is not a submitted application. An earlier decision to apply is not evidence that the posting is still active. A pending or uncertain action must be reconciled before retrying it.

## Close the loop with the candidate

Present the useful result first, then one concrete ask. For example: “The résumé draft is ready for review. Please confirm whether you led the rollout, delivered it hands-on, or shared delivery with the team.” Offer a reasonable option to defer or remove a role.

Use new information to update the evidence bank, search brief or style guide before producing dependent versions. Keep the original evidence and change history. Reuse confirmed evidence across applications without copying old role-specific claims into a new context unchecked.

When the candidate intends to apply, check the official employer or ATS posting again and record what was observable and when. A blocked, login-only or inconclusive page means unknown. If a role closes after tailoring, preserve the work, stop application prompts for that requisition and ask whether to archive it or explore a related requisition. A new or reposted requisition gets its own identity and history.

## A useful session ending

End each session with a compact handoff: what changed, current versions, unresolved facts, candidate decisions, exact next action, and any reminder request still awaiting consent. Save enough context that another preferred agent can continue without the conversation history. Never claim a reminder is scheduled or an external action happened without a confirming result from the relevant adapter.
