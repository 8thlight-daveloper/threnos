# Go mutation adapter

The Go implementation of the mutation recipes in [task recipes](../../../process/task-recipes.md). It runs [gomu](https://github.com/sivchari/gomu) through a small wrapper, `gomurun`, and summarizes the result for CI.

It was generalized from onboard-kit's `tools/mutation/`. The wrapper's folders are now flags, and the scripts read the component and contract folders from the environment. The unit tests pass on Go 1.26. The scripts were run against made-up logs and a throwaway Git repository. The generalized wrapper has not run gomu itself, because this repository has no Go project and the unit tests do not call gomu.

## Use it

1. Copy this folder to `tools/mutation/` in the project.
2. Add `import "tools/mutation/mutation.just"` to the project's justfile.
3. Set the variables at the top of `mutation.just` to the project's components folder, contracts folder, accepted folder, and gomu version. The defaults are `internal`, `contracts`, `tools/mutation/accepted`, and `v0.3.0`.
4. Put `go`, `jq`, `just`, and `git` in the dev shell. `gomurun` runs gomu under `nice`.
5. Edit `SHARED_PATHS` in `plan.sh`, or set it in the environment, to the paths whose change should mutate every component. The default covers the domain model, the Go module files, the mutation tooling, the justfile, the dev shell, and the mutation workflow.

## Files

| File | Recipe | Does |
| -- | -- | -- |
| `mutation.just` | all four | Defines the recipes and their folder variables |
| `gomurun/` | `mutate` | Runs gomu on one component against its contract package, then prints survivors and the score |
| `plan.sh` | `mutate-plan` | Prints the components that changed since a revision as a JSON array |
| `summarize.sh` | `mutate-summary` | Reads a run's log, prints Markdown, and writes `result.json` |
| `report.sh` | `mutate-report` | Combines every `result.json` into one Markdown report with a time chart |
| `bar.sh` | none | Draws the time bar that the summary and the report use |
| `seedfloors.sh` | none | Writes a score floor for each component from a set of results |

## What `gomurun` does

It mutates `<components>/<component>` over an overlay, so no source file changes. It runs the contract package's tests against each mutant, with `-count=1` and `-failfast`, one mutant at a time unless you pass `--workers`. Survivors that a person accepted in `<accepted>/<component>.txt` are counted as accepted and left off the list.

| Flag | Does |
| -- | -- |
| `--workers <n>` | Tests this many mutants at once |
| `--timeout <s>` | Seconds one mutant's tests may take |
| `--short` | Runs the tests with `-short`. A mutant that only a skipped test kills shows as a survivor |
| `--cached` | Reuses results for source files whose text, contract suite, and gomu version are unchanged |
| `--components`, `--contracts`, `--accepted` | The folders, set by the recipe variables |
| `--gomu-version` | Part of the cache key, set by the recipe variable |

## The log format

`mutate-summary` reads the last line of the `mutate` log:

```text
The mutation score is 0.975000 (39 passed, 1 failed, 2 accepted, 3 not viable, 0 timed out, 0 errors, total is 45)
```

A different mutation tool must print that line, or the project replaces `summarize.sh`. A log without it gives a `result.json` with `null` counts.

## Exit codes and floors

`gomurun` exits 0 when the run finishes, even with survivors. It exits 1 when gomu fails and 2 on a usage mistake.

Floors are optional. `seedfloors.sh <results-dir> <margin>` writes `floor/<component>.txt` beside the scripts, set a margin below each score. `report.sh` shows each score against its floor and marks a component `BELOW`. A floor does not fail a build by default. `report.sh` lists each component below its floor on stderr and exits 0. Set `FAIL_BELOW_FLOOR=1` in the environment and it exits 1 instead.

## What stays the project's

The gomu version, the worker count the workflow passes, `THRESHOLD_MINUTES`, the floors, and the accepted lists. The wrapper limits Go to two parallel jobs through `GOFLAGS=-p=2` unless the environment already sets `-p`.
