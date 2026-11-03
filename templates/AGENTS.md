# Agent instructions

<!-- Template. Replace each <placeholder>, then delete this line. -->

Read first: `README.md`, `docs/architecture/README.md`, `docs/stack/README.md`, the ADRs in `docs/decisions/`, and `.agents/rules/regenerative.md`.

The rules in `.agents/rules/regenerative.md` are part of these instructions and apply to every task. This file adds the project's settings and its own rules. It may add to those rules and may not relax them.

## Project settings

The shared rules refer to these by name.

| Setting | Value |
| -- | -- |
| Components folder | `<components>`, such as `internal/` or `src/` |
| Model folder | `<model>`, the folder that holds the domain model |
| Contracts and tests ADR | `docs/decisions/<contracts and tests ADR>` |
| Structure ADR | `docs/decisions/<structure ADR>` |
| Behavior judgment ADR | `docs/decisions/<behavior judgment ADR>` |
| Further behavior rules | `<ADRs the behavior judge also reads>`, or none |
| Testing stack doc | `docs/stack/testing.md` |
| Issue sizing examples | `docs/reference/issue-sizing.md` |
| Repository context guide | `docs/stack/repowise.md` |
| Check command | `just check` |
| Mutation command | `just mutate <component>` |
| Mutation cadence | `nightly` or `local` |

## Project rules

<!-- Rules that belong to this project alone. Add folders to the docs table, extra checks, or limits on what an agent may touch. Delete this line. -->

## Content rules

<!-- Project-specific: what must never enter the repo, such as client names, credentials, or personal data. Delete this line. -->
