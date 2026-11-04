# Release contents · v0.1.0

The published v0.1.0 base contains the reusable kit and fictional demonstration data only. The optional LinkedIn workflow in this local branch is prepared for review and is not yet published. It does not run scheduled work or submit applications.

| Path | Purpose |
| --- | --- |
| [START_HERE_HUMAN.md](START_HERE_HUMAN.md) | Approachable experience guide, what to bring, copyable orientation and short conversation examples |
| [START_HERE_AGENT.md](START_HERE_AGENT.md) | Human triage → resource triage, agent-owned roster and concise decisions |
| [README.md](README.md) | Quick start, workflow index, capability limits and optional CLI |
| [AGENTS.md](AGENTS.md) | Shared operating contract for the chosen assistant |
| `docs/` | Intake/résumé, search/packets, agent loops, adapters, CLI/state, privacy/publication and scripted experience acceptance |
| `prompts/` | Start, intake, editor, role research, tailoring, independent QA and follow-up prompts |
| `templates/` | Evidence bank, baseline, style/search, role roster/assessment, tailoring, packet, approval, reminders, QA, capabilities, handoff and blank state |
| [schemas/workspace.schema.json](schemas/workspace.schema.json) | Portable typed local state with additional semantic rules in core |
| `career_pipeline/` | Standard-library Python CLI, local lifecycle rules and scoped profile job bridge; no live external adapters |
| [examples/fictional/WALKTHROUGH.md](examples/fictional/WALKTHROUGH.md) | Fictional scenario and rerunnable commands |
| [docs/linkedin-profile.md](docs/linkedin-profile.md) | Pending local LinkedIn workflow: audit, copy-ready packet, optional editor prompt and fictional example |
| [docs/linkedin-execution.md](docs/linkedin-execution.md) | Optional scoped field-job protocol, separate private execution journal and fictional-file host demo; no live LinkedIn driver |
| [schemas/linkedin-execution.schema.json](schemas/linkedin-execution.schema.json) | Profile plan, per-field approval, capability, attempt, request and receipt structure; additional semantic rules in profiles.py |
| [docs/continuous-improvement.md](docs/continuous-improvement.md) | Bounded private improvement loop; local record checks, agent-operated trials and sanitized proposals |
| `tests/` | State, consent, source status, reminder, CLI, privacy and packaging tests |
| [tools/check_project.py](tools/check_project.py) | Offline local-link/common-leak scan and allowlisted local ZIP generation |
| [validation/RESULTS.md](validation/RESULTS.md) | Exact validation commands, results, limitations and retained walkthrough |
| [LICENSE.md](LICENSE.md) | File-based Apache 2.0 / CC BY 4.0 scope, attribution and official license texts |

The ZIP is created beside the project, not inside it. Its entry names begin `career-pipeline-kit/`; private runtime directories, credentials, caches and ZIPs are excluded. The release checker is a preflight, not proof that future edits contain no private material. Review the exact archive and Git changes before any public release.

Runtime requires Python 3.9+ with timezone data. No third-party packages, credentials or installation are needed. Run from this source directory. The CLI is optional; human/agent guides are the primary product.
