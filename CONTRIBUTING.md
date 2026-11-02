# Contributing to Career Pipeline Kit

This is a v0.1 early release, open to feedback. Useful contributions include clearer first-run instructions, accessibility improvements, better fictional examples, focused local bug reports and small process refinements. A change should reduce burden without weakening factual review, consent or privacy.

## Keep public feedback safe

GitHub issues and pull requests are public. Do not include real résumés, contact information, career evidence, private feedback, full prompts or conversations, workspace/checkpoint files, identifying job URLs, employer-confidential material, credentials or tokens. Reproduce the issue with fictional names, reserved `.invalid` URLs and the smallest necessary data. Remove private information from screenshots and logs before deciding whether they are needed at all.

Use the bug-report or feedback template. Describe what you expected, what happened and which guide or command was involved. Include only non-sensitive environment details, such as the operating system and Python version. A provider name does not establish which capabilities were available; describe the relevant observed capability without sharing private session content.

One person's result is useful feedback, not proof that a change causes better hiring outcomes. Keep claims proportional to the evidence. Please do not use public issues for personal résumé review or upload a candidate workspace.

## Propose a small change

Explain the problem, the intended behavior and how you checked it. Keep unrelated cleanup separate. Preserve the human and agent entry points, editable sources and provider-neutral workflow. New integrations must state their actual capabilities, privacy boundaries and failure behavior; do not describe prompts as an implemented autonomous service.

Changes to code should include meaningful regression coverage where behavior changes. For guide-only edits, check that a new user can follow the instructions and that local links resolve. Tests and checks run from the project root:

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_project.py
```

Use a fresh private destination for a fictional walkthrough:

```sh
python3 -m career_pipeline demo --out .private/contribution-demo
```

Do not commit `.private/`, candidate data, generated personal packets, credentials or unrelated files. Review the entire diff and any new files before submitting. A clean automated scan is a preflight, not a guarantee that content is safe to publish.

## License scope

Follow the file scopes in [LICENSE.md](LICENSE.md): code uses [Apache 2.0](LICENSE-CODE.txt), while authored guides and templates use [CC BY 4.0](LICENSE-CONTENT.txt). Preserve applicable attribution and notices. Contribute only material you have permission to license under the applicable scope; explain any third-party material and its terms rather than copying private or incompatible content.
