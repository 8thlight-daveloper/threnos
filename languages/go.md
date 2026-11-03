# Go

The mapping onboard-kit used. Copy it to `docs/stack/code-layout.md` in a Go project.

## Mapping

| Neutral term | In Go |
| -- | -- |
| Component | One package under `internal/<noun>/<role>`. The directory carries the noun and the package carries the role |
| Domain model | `internal/model`. Go's `internal/` rule keeps it from being imported outside the module |
| Entry point | `binary/`, holding a thin `main` |
| Interface file | `api.go` in the contract package, holding the interface and its data types |
| Contract tests | `<role>_test.go` in the contract package |
| Wiring test | `wire_test.go`, the only file in a contract package that imports its implementation, through one constructor call |
| Fixtures | `testdata/` folders, which the Go tool ignores when it builds. A fixture shared by two contracts lives in `contracts/<noun>/testdata/` |
| Shared test code | `contracts/harness/`, for example a package that turns fixture JSON into model values, because the model has no JSON tags |

## Folders

```text
internal/
  model/                 permanent: shared types, imports nothing from the project
  <noun>/<role>/         one component per package
contracts/
  harness/               protected shared test code
  <noun>/<role>/
    api.go               the interface
    contract.md          the description
    <role>_test.go       contract tests
    wire_test.go         binds the tests to the implementation
    testdata/            fixtures and cases.json
acceptance/
  scenarios/             language-neutral scenario files
  testdata/
  runner/                replaceable Go runner
binary/                  thin main
tools/mutation/
  accepted/<noun>/<role>.txt
```

## Naming and calls

- Package names follow the linter: lowercase, no underscores or mixed caps.
- A call uses the package name, so the noun shows only in the import path: `editor.Submit(plan, id, value)`. If two roles ever clash, alias the import.

## Running a contract only once its component exists

The check lists packages with a rule: a package under `contracts/` is included only when the matching folder under `internal/` exists, or when it is under `contracts/harness/`.

```just
_go-packages:
    @go list ./... | while read -r package; do case "$package" in <module>/contracts/harness/*) echo "$package";; <module>/contracts/*) rel="${package#<module>/contracts/}"; if [ -d "internal/$rel" ]; then echo "$package"; fi;; *) echo "$package";; esac; done
```

## Tools

| Need | Used | Notes |
| -- | -- | -- |
| Test runner | `go test -race`, `t.Parallel()`, `t.TempDir()` | Run a build's tests with `-count=3` too, to catch hidden state |
| Mutation | gomu, through a small wrapper program | gomu builds mutants over an overlay and leaves non-compiling mutants out of the score. The wrapper points it at the contract package, runs one mutant at a time with `GOFLAGS=-p=2`, passes `-timeout` to `go test` so looping mutants die, and prints survivors with stable keys. See the [mutation adapter](go/mutation/README.md). |
| Not chosen for mutation | gremlins, go-mutesting, ooze | gremlins runs only the package's own tests. go-mutesting edits files in place and skipped struct, slice, and map assignments. ooze counts non-compiling mutants as killed |
| Dependency check | Rules in `architecture.yaml`. ArchUnitGo was being evaluated | `depguard` would duplicate the dependency table one package at a time |
| Banned in core | `os`, `io/fs`, `path/filepath`, `net`, `os/exec`, `syscall`, `math/rand`, `crypto/rand`, terminal packages, and clock calls in `time` | `time` also holds types the model needs, so an import ban alone is too coarse |
| Docs checks | mdformat, markdownlint-cli2, lychee offline, Vale | Run by `just check` with the tests |
| Dev shell | Nix flake with direnv, and `just` as the task runner | CI runs `nix develop --command just check` |

## Value printing

Go's `%#v` prints pointer addresses, so two equal results look different in a differential run. Use the reflection printer in the contract-hardening skill's `scripts/adapters/go/dump.go.tmpl`.
