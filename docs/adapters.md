# Connect an agent or adapter

The shared files are the interface. Start with the [README](../README.md), the project instructions and a prompt from `prompts/`. Use your preferred assistant—Copilot, Claude, GPT, DeepSeek, Gemini, or another tool—with the same evidence, search brief, state and approval log. Availability of file access, browsing, background work and scheduling varies by product, plan and configuration. Do not assume the same prompt gives every agent the same capabilities.

## What v0.1 does

The local reference implementation uses the Python standard library. It can perform the workspace, validation, next-action and review-packet tasks documented in the README. Run it locally with fictional example inputs before creating a private candidate workspace.

| Capability | Local v0.1 | What a future adapter must supply |
| --- | --- | --- |
| Initialize a private workspace and read structured files | Included | Optional storage integration with explicit access scope |
| Validate supported state and identify next actions | Included | Any extra schema and rule validation for new fields |
| Assemble a local review packet from supplied inputs | Included | Optional document rendering; preserve editable source |
| Interpret career evidence or write a tailored résumé | Agent-guided through prompts | Model execution, context selection, claim provenance and output review |
| Discover or verify live roles | Not automatic | Browser/search access, official-source evidence, timestamps and failure states |
| Send a reminder later | Not included | Opted-in scheduler plus authorized delivery channel |
| Upload or externally share materials | Not included | Destination-specific consent, data minimization and confirmed delivery result |
| Submit an application | Not included | Explicit action authorization, fresh posting check and reliable outcome reconciliation |

The CLI does not become an autonomous service when placed on a schedule. A scheduler can invoke local commands, but research, model work, external delivery and submission still need their own supported adapters and controls.

## Declare capabilities before assigning work

Each adapter should publish a small capability record: its name and version, supported actions, input/output schema versions, network destinations, credential storage method, known limits, whether it can run unattended, and how it reports errors or uncertain outcomes. Never place credentials, tokens or session cookies in prompts, state, example files or logs.

An orchestrator must ask “can this environment actually do this?” before promising a result. If no browser exists, return “verification required” with the official link for the user to open. If no scheduler exists, list a reminder suggestion as unscheduled. If a tool lacks permission, report the blocked capability and continue unrelated work. Do not simulate success or route around a denied action.

At first use, translate this capability record into the short “Here is what we can do here” orientation in the agent-start guide. Each available claim needs current observed evidence, scope and a timestamp. A feature in this kit, an agent brand or a successful run elsewhere cannot establish availability here. Distinguish direct execution, help with a manual step, optional setup, and unknowns. Offer only the smallest relevant setup improvement; starting does not require it.

A new chat/provider reads the private checkpoint and capability manifest, then revalidates its environment. Carry forward confirmed career facts; do not ask the entire intake again. Reassess when tools or access change. [Improvement runbook](continuous-improvement.md).

## A minimal adapter result contract

An adapter result needs an operation ID, action, target, input versions, time, result status, evidence and retry guidance. Use distinct outcomes for confirmed success, confirmed failure, blocked or unavailable capability, and uncertain execution. Record only the minimum evidence needed to support the result.

Read-only posting checks additionally record the canonical URL, employer and requisition identity, observed status, checked time, source evidence and any limitations. An HTTP success code, search-result snippet or working application button alone is not sufficient evidence that the role is accepting applications. Verification describes an observation at a time; it never guarantees continued availability.

For outgoing actions, separate preparation from execution. A draft payload should be reviewable before the action is authorized. Bind authorization to the exact materials and destination. If execution times out after the request is sent, check whether it happened before retrying. Use an idempotency key or equivalent duplicate prevention when the service supports it.

## Reminder consent and delivery

A next-action list is useful without notifications. Ask whether the candidate wants reminders before enabling any external scheduling. Record:

- Opt-in decision and the actions covered, such as reviewing one selected packet.
- Cadence or one-time due time, IANA timezone, delivery channel and quiet-time preference.
- A deduplication key based on candidate workspace, role identity and action type.
- Last delivery, next eligible delivery, snooze-until value and stop state.
- Scheduler identity and the confirmed schedule ID, if scheduling succeeded.

Use a small, agreed cadence. A missed response is not permission to increase frequency. Suppress duplicates across agents and overlapping runs. Snoozing changes the next eligible time without creating a second reminder. Completion, withdrawal of consent, deselection of the role, a closed posting or a stop request must cancel the relevant pending reminder. An unknown posting should prompt verification only within the agreed reminder scope; it must not generate repeated pressure to apply.

When a user says “remind me,” ask only for missing scheduling details that the environment cannot safely infer. A scheduler adapter should validate the timezone and preserve the user's intended local time across daylight-saving changes. If no scheduler is connected, say plainly: “This is listed as a next action; no reminder has been scheduled.”

## Document and visual adapters

Keep the Markdown or structured résumé source with every exported DOCX or PDF. A renderer should record source version, export version and render time. Check spelling, facts, dates, links and claim attribution, then visually inspect every exported page for clipping, orphaned headings, unreadable density, broken symbols and unexpected page breaks. Extract text from the final export as an additional check of reading order and missing content. Do not mark visual QA complete if no rendered artifact was inspected.

## Implement incrementally

Start with manual agent sessions and user-opened official postings. Add one read-only capability at a time and test its failure behavior before unattended use. Separate adapters from the portable files so a colleague can change providers without rewriting their evidence bank or application history. No adapter should send telemetry or candidate data to an unlisted destination.
