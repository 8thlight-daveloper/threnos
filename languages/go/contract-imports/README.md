# Go contract imports check

Checks that the Go code in `contract-tests/` imports only what its role allows. It enforces the import rules of
[ADR 0150](../../../docs/decisions/0150-contracts-hold-data-and-contract-tests-hold-the-code.md). The language-neutral
rule is that the suite and the harness import no implementation, and that a wiring test is the only code that imports a
component.

## How it works

`check.py` runs `go list -e -json -test ./contract-tests/...`, which resolves imports exactly and includes test files.
It reads each package's `Imports`, `TestImports`, and `XTestImports`. A package's role is its first folder under
`contract-tests/`.

| Role      | May import                                                                                             |
| --------- | ------------------------------------------------------------------------------------------------------ |
| `runner`  | The standard library, the model, `contract-tests/harness`, and the libraries in `contracts.may_import` |
| `harness` | The same as `runner`                                                                                   |
| `wiring`  | The standard library, its own component, and its own runner. Nothing else                              |

An import of any other package in the project's module is a violation. So is a third-party package that is not listed.
An entry in `contracts.may_import` is an import path and allows the packages below it. A folder directly under
`contract-tests/` that is not `runner/`, `wiring/`, or `harness/` may import the standard library only. The check prints
the package folder and the import, and exits 1.

```yaml
contract_tests_root: contract-tests
contracts:
  may_import: [github.com/example/diff]
```

A component that imports the contract tests is a different violation. The
[dependency check](../dependency-check/README.md) reports it as an edge to the rest of the repo.

## Use it

1. Copy this folder to `tools/contract-imports/` in the project.
1. Put `go` and Python with PyYAML in the dev shell. The Threnos dev shell has PyYAML.
1. Run it from the `check` recipe: `python3 tools/contract-imports/check.py`.

## Limits

It reads imports, not what a suite does with them, so it cannot tell that a wiring package calls the suite. The stub run
at the start of a build shows that. Build constraints apply as `go list` applies them, so a file excluded for the
current platform is not checked. A project with no `contract-tests/` folder passes.
