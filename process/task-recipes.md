# Task recipes

CI and agents call a project through named recipes in its `justfile`. The process fixes each recipe's name, arguments, and output. The project writes what the recipe does. That keeps the CI workflows free of any language, layout, or mutation tool.

Run every recipe from the repository root, inside the project's dev shell. A recipe never prompts, never reads a secret, and prints its result on standard output and its diagnostics on standard error.

## The recipes

| Recipe | Arguments | Does | Prints |
| -- | -- | -- | -- |
| `check` | none | Runs every check: format, lint, tests, and acceptance scenarios | Human-readable progress. Exits nonzero on any failure |
| `mutate` | `<component> [flags]` | Mutation-tests one component against its contract. Accepts `--workers <n>` | The mutation tool's log. Exits nonzero only when the run did not finish |
| `mutate-plan` | `<base>` | Chooses the components to mutate | One line of JSON: an array of component names, such as `["plan/encoder"]`, or `[]` for none |
| `mutate-summary` | `<component> <log> <seconds>` | Summarizes one mutation run from its log | Markdown. Also writes `result.json` in the working directory |
| `mutate-report` | `<results-dir>` | Combines every `result.json` under the directory into one report | Markdown. Exits nonzero when it finds no results |

## What each recipe must do

**`check`.** It is what a person runs before a commit and what CI runs on every pull request. A check that is not in `check` does not gate a merge.

**`mutate`.** It never leaves a change in the working tree, so it can run beside `check`. Survivors and a low score are reported, not failures. A floor belongs to `mutate-report`. A survivor in the component's accepted list is skipped, as the [mutation testing](mutation-testing.md) process describes.

**`mutate-plan`.** `<base>` is a Git revision, or empty. The plan must return every component when `<base>` is empty or does not exist. It must also return every component when anything shared changed since `<base>`: the domain model, the dependency files, the mutation tooling, the justfile, and the mutation workflow. Otherwise it returns the components whose own folder or contract changed.

**`mutate-summary`.** It reads the log that `mutate` printed. It writes `result.json` with these fields. A field is `null` when the log does not hold it, for example when a run did not finish.

| Field | Holds |
| -- | -- |
| `component` | The component's name, as a string |
| `seconds` | Wall-clock run time, as a number |
| `score` | The mutation score, as a number or `null` |
| `killed`, `survivors`, `accepted`, `notViable`, `timedOut`, `errors`, `total` | Mutant counts, as numbers or `null` |

**`mutate-report`.** It reads those `result.json` files. It may add whatever a project tracks, such as floors and a time threshold, and a project may fail it when a component falls below its floor. The workflow passes `THRESHOLD_MINUTES` in the environment, and a recipe may use it.

## What the process leaves to the project

The language, the mutation tool, the layout that maps a folder to a component, the log format that `mutate` and `mutate-summary` share, and any floors or thresholds. A language mapping can hold a working implementation. The Go mapping's is in [languages/go/mutation/](../languages/go/mutation/README.md).

A project that renames a recipe also changes every workflow that calls it. Keep the names.

## Workflows

[templates/workflows/](../templates/workflows/) holds the two GitHub Actions workflows that call these recipes: `check.yml` on every pull request and push, and `mutate.yml` on demand or on a schedule. Neither contains project logic.
