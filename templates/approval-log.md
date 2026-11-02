# Private approval and outgoing-action log

Use one entry per actual decision; agents cannot approve on the candidate’s behalf. A draft or silence is not approval. Simulation entries must be labeled fictional.

| Field | Value |
| --- | --- |
| Approval ID / decision time with timezone | [ ] |
| Human decision maker | [ ] |
| Decision | [approved / declined / needs changes] |
| Scope | [facts+positioning / role selection / exact materials / outgoing action] |
| Input versions and fingerprints | [ ] |
| Exact artifact names and content hashes | [ ] |
| Action and destination / recipient | [ ] |
| Authorized actor / adapter | [ ] |
| Time window, one-time limits and other restrictions | [ ] |
| Open questions / blocked requirements | [ ] |
| User’s decision evidence | [minimal private reference, no secret] |

For any later outgoing attempt, record attempt ID, intent-specific posting recheck, authorization reference, time, result, receipt, and whether outcome is uncertain. On timeout, check current application/receipt state before retrying. A new file, destination, role requirement or substantive fact needs renewed review. Never treat local `--commit` as external permission.
