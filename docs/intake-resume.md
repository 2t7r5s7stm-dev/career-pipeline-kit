# From a career conversation to a usable résumé

Start with the person, then build the source material. The goal is a confirmed career evidence bank, a useful base résumé and a tailoring/style guide that another preferred agent can continue using. The evidence bank is broader than any one résumé.

This is an agent-guided runbook. The local CLI stores and checks structured inputs and assembles supplied evidence; it does not interview a candidate, interpret documents or independently confirm a career claim. Follow the [README](../README.md) for the commands that actually run.

## 1. Agree on today's outcome

**Owner:** orchestrator. **Prompt:** [start a session](../prompts/start.md).

Begin with three small questions, reusing answers already provided:

1. “What would make this useful today: starting a résumé, improving one, changing direction, or preparing for a specific role?” This establishes the deliverable.
2. “What materials do you already have, and which are you comfortable using here?” This identifies usable sources and their privacy scope.
3. “How much time and energy do you want to spend now?” This determines the size of the next step.

Explain that “unknown,” “skip” and “later” are valid answers. Do not require every question to be answered before useful work begins. Offer a first deliverable such as a career outline and three strong evidence entries. Agree on which source files the agent may read or upload; choosing an agent is not permission to send it every private file.

## 2. Map the whole career, one chapter at a time

**Owner:** intake researcher. **Prompt:** [intake](../prompts/intake.md).

Ask for the broad timeline first: paid roles, earlier work, consulting, projects, volunteer work, community leadership and relevant learning. Older work may contain the clearest example of a capability. Keep it in the bank even when it will not appear on the current résumé.

For one chapter, ask a few focused questions: “What were you responsible for?”, “What needed to change?”, and “What did you contribute?” Then follow the answer toward collaborators, scale and results. Explain why a detail matters before requesting it. A team outcome can be strong evidence of leadership without suggesting the person performed every task themselves.

Reconcile timeline discrepancies neutrally: “These two sources show different start months. Which should we use, or should we leave the month unresolved?” Do not pressure the candidate to explain health, family circumstances or other private reasons for a gap. Ask only for the chronology needed to represent their experience accurately.

## 3. Turn stories into traceable evidence

Capture each useful story as a stable claim ID. The [workspace schema](../schemas/workspace.schema.json) includes claim text, kind, confirmation status and basis, source, confirmer and confirmation time. It also captures contribution scope and richer details:

- Organization, role and date range.
- Problem, contribution, collaborators and outcome.
- Uncertainty, confidentiality and possible relevance.
- Metrics with value, unit, baseline, period, attribution, source and confirmation.

Use `direct`, `team`, `shared` or `supported` scope according to the actual contribution. For a leader, describe the decisions, team direction, systems or accountability they owned, then attribute the resulting team outcome. Do not downgrade leadership merely because someone else delivered part of the work.

Ask “How do we know?” about material claims. A candidate's explicit confirmation can be the recorded basis; do not label it independently corroborated unless another source supports it. Mark estimates and unresolved claims honestly. Never turn “I think it was about…” into a precise confirmed metric. If no reliable number exists, use a specific qualitative outcome.

Confirm education and credentials exactly. Distinguish learning a skill, taking coursework, completing a course, earning a certificate and earning a degree or professional certification. Studying a topic does not establish a credential. Keep confidential source details private and agree on wording that can be shared.

The CLI's checks catch some structural and numeric inconsistencies; they cannot establish that a claim is true. In this reference implementation, numeric claim text also needs reviewed metric metadata. Keep nuanced interview notes in a separate private source file if they do not fit the strict schema; do not add unsupported fields to `workspace.json`.

## 4. Approve facts, then select résumé material

**Owner:** career editor, with candidate approval. **Prompt:** [career editor](../prompts/career-editor.md).

Review the most relevant claims in small batches. Ask for corrections to facts, ownership, dates and metrics before treating them as final-ready. Save the source and confirmation basis rather than overwriting uncertainty with stronger prose.

Build the base résumé from confirmed evidence. Select material that explains actual capabilities and the desired direction. Use a clear chronology and concrete outcomes. Preserve relevant earlier experience when it makes the case stronger; do not impose a silent age or year cutoff. The base résumé is a starting view of the bank, not the only allowed story of the career.

Keep a claim map connecting résumé statements to evidence IDs. If an editor rewrites a statement, review whether it changed the meaning or implied more ownership. The CLI assembles selected claim text; a model-written alternative requires its own factual review and updated source mapping.

## 5. Create the tailoring/style guide

Agree on a short guide that future writers can follow:

| Decision | Capture |
| --- | --- |
| Positioning | Capabilities to lead with; type and level of contribution; target reader |
| Voice | Plain or more formal language; first-person rules; appropriate confidence |
| Evidence | How to attribute leadership and team results; metric and source requirements |
| Terminology | Candidate's preferred terms; industry terms supported by experience; phrases to avoid |
| Format | Section order, regional spelling, date style, length preference and accessible layout |
| Tailoring | What may change by role, what needs confirmation and what must never be implied |

Offer two positioning options when that helps a real decision. Do not force the candidate to invent a personal brand before seeing a useful draft. Review the guide with them and version it alongside the résumé and evidence bank.

## 6. Hand off a usable baseline

**Owner:** independent QA reviewer. **Prompt:** [QA reviewer](../prompts/qa-reviewer.md).

Check dates, credentials, metrics, contribution attribution, grammar, consistency and every claim reference. Preserve the editable résumé source. If exporting a Word or PDF version, inspect every rendered page and check extracted text; record visual QA as not checked when no export has been rendered.

Return the evidence-bank version, base-résumé version, approved style-guide version, unresolved questions and one next action. Search setup can begin while other career chapters remain unfinished. Continue with [search and packets](search-and-packets.md), and use the [agent loop](agent-loop.md) whenever work moves between people or agents.
