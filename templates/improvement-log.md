# Private improvement log — maintained by the agent

Use one short record per observation or trial. Keep at most one active trial. The person should make a concise decision, not administer this log. This is a manual/agent operating record. If using the optional private workspace `improvements[]`, its fields are `id`, `classification`, `status`, `observed_at`, `feedback_source`, `friction`, `proposal`, `expected_benefit`, `affected_domains`, `preserves_safeguards`, `before_versions`, `after_versions`, `approval`, `trial` and `decision`. Use the bundled schema for their exact shapes. Local validation checks structure and bounded-state rules; evidence quality, actual approval, trial execution and external behavior remain agent/manual responsibilities.

- Improvement ID / observed at: [ ]
- Friction and provenance: [dated user feedback, batch/role IDs or tool result; minimal private reference]
- Observation versus interpretation: [ ]
- Classification: [personal preference / potentially reusable process fix]
- One proposed change and expected benefit: [ ]
- Domains affected: [goals / filters / cadence / privacy / external_behavior / approval_rules / format / record_quality / question_pacing; use existing profile/search/style version references for affected files]
- Approval needed and actual decision: [`approval`: decision, by, at, note; never inferred from silence]
- Before-checkpoint and existing input versions: [private reference; preserve rollback]
- Trial bound: [`trial`: baseline, one_change, measure, evaluation_boundary, stop_condition, rollback_checkpoint, rollback_action, result, limitations; one batch/session and no second active trial]
- Observable measure and baseline: [matches the friction, with source]
- Trial result and evidence: [or not yet observed]
- Limitations: [small sample, differing roles, missing evidence; no unsupported causal claim]
- Status: [observed / proposed / approved / trial / retained / reverted; use proposed while a trial is paused for a decision]
- Keep/revert decision and rationale: [`decision`: at, by, rationale, checkpoint]
- After-checkpoint and affected versions: [increment relevant profile/search/style version if changed]
- Next action / owner: [resume career work; no endless retrospective]

Guardrails: preserve goals unless the person approves a change; never weaken factual QA, consent or privacy. `preserves_safeguards` must be true and must reflect the actual proposed behavior. A single callback or rejection is tentative feedback, not a permanent ranking rule or evidence of causation.

Personal adaptations and underlying evidence stay private. A reusable proposal must exclude personal claims, contacts, private feedback, identifying URLs, tokens and approval records. Sanitization is not upload or publication authorization; sharing still needs a separate decision. There is no automatic telemetry or upstream publication.
