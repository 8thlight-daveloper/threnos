# Agent instructions

<!-- Template. Replace each <placeholder>, then delete this line. -->

Read first: `README.md`, `docs/architecture/README.md`, `docs/stack/README.md`, the ADRs in `docs/decisions/`, and
`.agents/rules/regenerative.md`.

The rules in `.agents/rules/regenerative.md` are part of these instructions and apply to every task. This file adds the
project's document pointers and its own rules. It may add to those rules and may not relax them.

## Document pointers

The documents a person chooses. The shared rules and skills read them from here. Values that a tool reads live in
`architecture.yaml` and `.agents/threnos.toml`, not in this table.

| Document               | Path                                               |
| ---------------------- | -------------------------------------------------- |
| Product principles     | `docs/decisions/<product principles record>`       |
| Further behavior rules | `<records the behavior judge also reads>`, or none |
| Testing stack doc      | `docs/stack/testing.md`                            |
| Issue sizing examples  | `docs/reference/issue-sizing.md`, or none          |

## Project rules

<!-- Rules that belong to this project alone. Add folders to the docs table, extra checks, or limits on what an agent may touch. Delete this line. -->

## Content rules

<!-- Project-specific: what must never enter the repo, such as client names, credentials, or personal data. Delete this line. -->
