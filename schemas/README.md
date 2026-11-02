# Portable state

[workspace.schema.json](workspace.schema.json) is the machine-readable contract used by the local CLI. It uses JSON Schema Draft 2020-12 and a deliberately small keyword subset supported by the bundled validator. Semantic rules and actual human/source review remain necessary; a valid schema is not proof that a fact is true or an action is authorized.

[workspace.blank.json](../templates/workspace.blank.json) is a valid empty starting point. [The fictional workspace](../examples/fictional/workspace.json) shows filled fields. [CLI and state guide](../docs/cli-and-state.md) explains versioning, approval fingerprints, observation limits and event shapes.

The capability and handoff JSON templates are portable agent/manual contracts, not runtime state files and not validated by the CLI. An adapter should version its own extensions and validators rather than silently adding unsupported fields to this strict workspace schema.

Optional `improvements` entries share the current workspace and profile version references. The CLI validates bounded record fields and declared approval/safeguard requirements; an agent/person operates the trial and makes keep/revert decisions. [Improvement runbook](../docs/continuous-improvement.md).
