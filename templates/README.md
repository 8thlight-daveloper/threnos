# Templates

Starting files for a new project. Copy them, replace each `<placeholder>`, and change what does not fit. Once copied
they belong to the project, so they do not link back here.

| File                                                               | Goes to                                       | Is                                                                                                                                                |
| ------------------------------------------------------------------ | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| [AGENTS.md](AGENTS.md)                                             | Repo root                                     | The project's settings and rules. The shared rules are in [rules/regenerative.md](../rules/regenerative.md), copied read-only to `.agents/rules/` |
| [CLAUDE.md](CLAUDE.md)                                             | Repo root                                     | Two lines that import `AGENTS.md` and `.agents/rules/regenerative.md` for Claude Code                                                             |
| [architecture.yaml](architecture.yaml)                             | Repo root                                     | The dependency rules, as data. Required. `nix flake init` seeds an empty one                                                                      |
| [decisions/](decisions/)                                           | `docs/decisions/`                             | The ADR skeleton, with front matter. The method ADRs are Threnos's own in [docs/decisions/](../docs/decisions/) and are not copied                |
| [decision-record-front-matter.md](decision-record-front-matter.md) | `docs/reference/`                             | The front matter every decision record starts with, and the checks over it                                                                        |
| [product-principles.md](product-principles.md)                     | `docs/decisions/`                             | The project's product principles, which the behavior judge reads                                                                                  |
| [contract/](contract/)                                             | `contracts/<noun>/<role>/`                    | A contract description and a fixture manifest                                                                                                     |
| [acceptance/](acceptance/README.md)                                | `docs/reference/` and `acceptance/scenarios/` | The scenario format and two example scenarios                                                                                                     |
| [workflows/](workflows/)                                           | `.github/workflows/`                          | The `check` and `mutate` GitHub Actions workflows. They call only the [task recipes](../process/task-recipes.md)                                  |
| [issues/](issues/)                                                 | `.github/ISSUE_TEMPLATE/`                     | Decision, contract, build, and integration issues                                                                                                 |
| [accepted-survivors.txt](accepted-survivors.txt)                   | `tools/mutation/accepted/<component>.txt`     | The header of a component's accepted survivor list                                                                                                |
| [repowise.md](repowise.md)                                         | `docs/stack/repowise.md`                      | Local open-source repository context, with model and embedding API calls disabled                                                                 |
| [osv-scanner.md](osv-scanner.md)                                   | `docs/stack/osv-scanner.md`                   | Dependency vulnerability scan from OSV, with an offline path for projects that cannot send their dependency list                                  |
| [issue-sizing.md](issue-sizing.md)                                 | `docs/reference/issue-sizing.md`              | The project's own examples for each issue size, which the `writing-issues` skill reads                                                            |
| [stack-topic.md](stack-topic.md)                                   | `docs/stack/<topic>.md`                       | A stack topic with Current, Retired, and Considered tables                                                                                        |

## Order

1. `.agents/rules/regenerative.md`, `AGENTS.md`, `CLAUDE.md`, and the skills.
1. The product principles record, from [product-principles.md](product-principles.md). Write it before the first
   survivor review, not after. Link the Threnos method ADRs from `AGENTS.md`.
1. `docs/stack/code-layout.md` from a [language mapping](../languages/README.md), then `docs/stack/repowise.md` from the
   setup guide. Initialize the local index and connect the project's agent as that guide describes.
1. `architecture.yaml` with the first components.
1. The scenario format, then the first scenario.
1. The domain model, then the first contract.
