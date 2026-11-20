# Go

The mapping for the contract layout of
[ADR 0150](../docs/decisions/0150-contracts-hold-data-and-contract-tests-hold-the-code.md). Copy it to
`docs/stack/code-layout.md` in a Go project. The checks still accept the older layout, one folder per contract with
`api.go`, `contract.md`, the tests, and `testdata/` together, until a project moves.

## Mapping

| Neutral term     | In Go                                                                                                                                                     |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Component        | One package under `internal/<noun>/<role>`. The directory carries the noun and the package carries the role                                               |
| Domain model     | `internal/model`. Go's `internal/` rule keeps it from being imported outside the module                                                                   |
| Entry point      | `binary/`, holding a thin `main`                                                                                                                          |
| Specification    | `contract.md` in `contracts/specifications/<noun>/<role>/`                                                                                                |
| Fixtures         | `cases.json` and any files it names, in `contracts/fixtures/<noun>/<role>/`. The data formats the layout check accepts are in `architecture.yaml`         |
| Suite            | A package in `contract-tests/runner/<noun>/<role>/` with non-test files. One declares the interface and an exported `Run(t *testing.T, impl <Interface>)` |
| Contract tests   | The subtests that `Run` starts with `t.Run`, one per case, plus the property checks                                                                       |
| Wiring           | `wire_test.go` in `contract-tests/wiring/<noun>/<role>/`, the only file that imports the component, with one test that calls `Run`                        |
| Shared test code | `contract-tests/harness/`, for example a package that turns fixture JSON into model values, because the model has no JSON tags                            |

The suite is an ordinary package so that the wiring, which is another package, can call it. A package that holds a `Run`
function and imports `testing` is a normal Go pattern. The interface is declared in the suite by the drafter. The
component imports nothing from it, because a Go type satisfies an interface by its methods. The wiring test is where a
mismatch shows, as a compile error.

## Folders

```text
internal/
  model/                 permanent: shared types, imports nothing from the project
  <noun>/<role>/         one component per package
contracts/
  specifications/<noun>/<role>/contract.md
  fixtures/<noun>/<role>/cases.json
contract-tests/
  harness/               protected shared test code
  runner/<noun>/<role>/  the suite: the interface and Run
  wiring/<noun>/<role>/  wire_test.go
acceptance/
  scenarios/             language-neutral scenario files
  fixtures/
  runner/                replaceable Go runner
binary/                  thin main
tools/mutation/
  accepted/<noun>/<role>.txt
```

The wiring test is one function:

```go
func TestContract(t *testing.T) {
    runner.Run(t, role.New())
}
```

## Naming and calls

- Package names follow the linter: lowercase, no underscores or mixed caps.
- A call uses the package name, so the noun shows only in the import path: `editor.Submit(plan, id, value)`. If two
  roles ever clash, alias the import.

## Running a contract only once its component exists

The suite and the harness never import a component, so they build before it exists. A wiring package imports its
component, so the check lists it only when the matching folder under `internal/` exists.

```just
_go-packages:
    @go list ./... | while read -r package; do case "$package" in <module>/contract-tests/wiring/*) rel="${package#<module>/contract-tests/wiring/}"; if [ -d "internal/$rel" ]; then echo "$package"; fi;; *) echo "$package";; esac; done
```

## Tools

| Need                    | Used                                                                                                                                                   | Notes                                                                                                                                                                                                                                                                                                                                                     |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Test runner             | `go test -race`, `t.Parallel()`, `t.TempDir()`                                                                                                         | Run a build's tests with `-count=3` too, to catch hidden state                                                                                                                                                                                                                                                                                            |
| Mutation                | gomu, through a small wrapper program                                                                                                                  | gomu builds mutants over an overlay and leaves non-compiling mutants out of the score. The wrapper points it at the wiring package, which runs the suite, runs one mutant at a time with `GOFLAGS=-p=2`, passes `-timeout` to `go test` so looping mutants die, and prints survivors with stable keys. See the [mutation adapter](go/mutation/README.md). |
| Not chosen for mutation | gremlins, go-mutesting, ooze                                                                                                                           | gremlins runs only the package's own tests. go-mutesting edits files in place and skipped struct, slice, and map assignments. ooze counts non-compiling mutants as killed                                                                                                                                                                                 |
| Dependency check        | `go list` over `components_root`, checked against the rules in `architecture.yaml`, in [languages/go/dependency-check/](go/dependency-check/README.md) | `depguard` would duplicate the dependency table one package at a time                                                                                                                                                                                                                                                                                     |
| Acceptance imports      | `go list -test` over `acceptance/`, checked against `acceptance.may_import`, in [languages/go/acceptance-imports/](go/acceptance-imports/README.md)    | A scenario that imports a project package is a violation, in data or code form                                                                                                                                                                                                                                                                            |
| Contract imports        | `go list -test` over `contract-tests/`, checked against each package's role, in [languages/go/contract-imports/](go/contract-imports/README.md)        | A suite or harness that imports a component, or a wiring test that imports anything but its own component and suite, is a violation                                                                                                                                                                                                                       |
| Banned in core          | `os`, `io/fs`, `path/filepath`, `net`, `os/exec`, `syscall`, `math/rand`, `crypto/rand`, terminal packages, and clock calls in `time`                  | `time` also holds types the model needs, so an import ban alone is too coarse. The [dependency check](go/dependency-check/README.md) bans the clock functions                                                                                                                                                                                             |
| Docs checks             | mdformat, markdownlint-cli2, lychee offline, Vale                                                                                                      | Run by `just check` with the tests                                                                                                                                                                                                                                                                                                                        |
| Dev shell               | Nix flake with direnv, and `just` as the task runner                                                                                                   | CI runs `nix develop --command just check`                                                                                                                                                                                                                                                                                                                |

## Value printing

Go's `%#v` prints pointer addresses, so two equal results look different in a differential run. Use the reflection
printer in the contract-hardening skill's `scripts/adapters/go/dump.go.tmpl`.
