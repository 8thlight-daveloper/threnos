# Templates

Starting files for a new project. Copy them, replace each `<placeholder>`, and change what does not fit. Once copied
they belong to the project, so they do not link back here. `nix run .#sync` seeds every file here where the project has
nothing at that path, and never overwrites one. Live files go to their paths: `AGENTS.md`, `CLAUDE.md`, `workflows/`,
`issues/`, the decision record schema, a short `docs/decisions/README.md`, the acceptance scenario format,
`repowise.md`, and `osv-scanner.md`. The two acceptance examples go to `acceptance/scenarios/` with a `.example` suffix,
so a runner ignores them until renamed. Skeletons with placeholders go to `docs/reference/templates/`: `adr.md`,
`product-principles.md`, `issue-sizing.md`, `contract/`, `stack-topic.md`, and `accepted-survivors.txt`. A project
copies each once per record, component, or stack topic, and agents read them there. Sync does not write the product
principles record or the issue sizing doc, because a person has to fill them in and a placeholder file could pass for a
real one.

## Seeds are written once

Sync records every path it seeds, or finds already in place, in `.agents/.threnos-seeded`, and does not seed that path
again. A project can delete a seed for good. To get one back, remove its line from `.agents/.threnos-seeded` and run
sync. The file is back if it is missing. To keep a seed out from the first sync, list its path under `skip` in a
`[seeds]` table in `.agents/threnos.toml`.

## Linting the seeds

The live seeds are formatted at a 120 column wrap and have no `<placeholder>` text, and a flake check holds them to
that. The skeletons in `docs/reference/templates/` keep placeholders, which a Markdown formatter, a prose linter, or a
link checker can reject. Exclude `docs/reference/templates/**` from those tools in the project, as Threnos does in its
own `.mdformat.toml`. A prose linter may also object to words in a seed, such as a tool's name in a heading. Add those
words to the project's vocabulary.

| File                                                               | Goes to                                       | Is                                                                                                                                                         |
| ------------------------------------------------------------------ | --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [AGENTS.md](AGENTS.md)                                             | Repo root                                     | The project's document pointers and rules. The shared rules are in [rules/regenerative.md](../rules/regenerative.md), copied read-only to `.agents/rules/` |
| [CLAUDE.md](CLAUDE.md)                                             | Repo root                                     | Two lines that import `AGENTS.md` and `.agents/rules/regenerative.md` for Claude Code                                                                      |
| [architecture.yaml](architecture.yaml)                             | Repo root                                     | The dependency rules, as data. Required. `nix flake init` seeds an empty one                                                                               |
| [decisions/](decisions/)                                           | `docs/decisions/`                             | The ADR skeleton, with front matter. The method ADRs are Threnos's own in [docs/decisions/](../docs/decisions/) and are not copied                         |
| [decision-record-front-matter.md](decision-record-front-matter.md) | `docs/reference/`                             | The front matter every decision record starts with, and the checks over it                                                                                 |
| [product-principles.md](product-principles.md)                     | `docs/decisions/<NNNN>-product-principles.md` | The project's product principles, which the behavior judge reads                                                                                           |
| [contract/](contract/)                                             | `contracts/<noun>/<role>/`                    | A contract description and a fixture manifest                                                                                                              |
| [acceptance/](acceptance/README.md)                                | `docs/reference/` and `acceptance/scenarios/` | The scenario format and two example scenarios                                                                                                              |
| [workflows/](workflows/)                                           | `.github/workflows/`                          | The `check` and `mutate` GitHub Actions workflows. They call only the [task recipes](../process/task-recipes.md)                                           |
| [issues/](issues/)                                                 | `.github/ISSUE_TEMPLATE/`                     | Decision, contract, build, and integration issues                                                                                                          |
| [accepted-survivors.txt](accepted-survivors.txt)                   | `tools/mutation/accepted/<component>.txt`     | The header of a component's accepted survivor list                                                                                                         |
| [repowise.md](repowise.md)                                         | `docs/stack/repowise.md`                      | Local open-source repository context, with model and embedding API calls disabled                                                                          |
| [osv-scanner.md](osv-scanner.md)                                   | `docs/stack/osv-scanner.md`                   | Dependency vulnerability scan from OSV, with an offline path for projects that cannot send their dependency list                                           |
| [issue-sizing.md](issue-sizing.md)                                 | `docs/reference/issue-sizing.md`              | The project's own examples for each issue size, which the `writing-issues` skill reads                                                                     |
| [stack-topic.md](stack-topic.md)                                   | `docs/stack/<topic>.md`                       | A stack topic with Current, Retired, and Considered tables                                                                                                 |

## Order

1. `.agents/rules/regenerative.md`, `AGENTS.md`, `CLAUDE.md`, and the skills.
1. The product principles record, from [product-principles.md](product-principles.md). Write it before the first
   survivor review, not after. Link the Threnos method ADRs from `AGENTS.md`.
1. `docs/stack/code-layout.md` from a [language mapping](../languages/README.md), then `docs/stack/repowise.md` from the
   setup guide. Initialize the local index and connect the project's agent as that guide describes.
1. `architecture.yaml` with the first components.
1. The scenario format, then the first scenario.
1. The domain model, then the first contract.
