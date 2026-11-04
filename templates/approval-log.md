# Private approval and outgoing-action log

Use one entry per actual decision; agents cannot approve on the candidate’s behalf. A draft or silence is not approval. Simulation entries must be labeled fictional.

| Field | Value |
| --- | --- |
| Approval ID / decision time with timezone | [ ] |
| Human decision maker | [ ] |
| Decision | [approved / declined / needs changes] |
| Scope | [facts+positioning / role selection / public-profile clearance / exact materials / outgoing action] |
| Input versions and fingerprints | [ ] |
| Exact artifact names and content hashes | [ ] |
| Action and destination / recipient | [ ] |
| Authorized actor / adapter | [ ] |
| Time window, one-time limits and other restrictions | [ ] |
| Open questions / blocked requirements | [ ] |
| User’s decision evidence | [minimal private reference, no secret] |

For an application attempt, record attempt ID, intent-specific posting recheck, authorization reference, time, result, receipt, and whether outcome is uncertain. On timeout, check current application/receipt state before retrying. A new file, destination, role requirement or substantive fact needs renewed review. Never treat local `--commit` as external permission.

For LinkedIn, record public clearance separately from résumé/factual approval. Exact-copy approval identifies profile account, fields and version; profile edits, banner replacements or visibility/notification changes require separate explicit action permission. Before any authorized write, compare the current field with the saved source and pause for changed content. Preserve the before copy and read back the result. A manual user report is labeled as reported; an unverified save is not confirmed publication. The [profile packet](linkedin-update-packet.md) keeps these records private and distinct.
