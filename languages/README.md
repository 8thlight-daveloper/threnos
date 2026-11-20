# Language mappings

The process names no language. A project maps each neutral term to its language once, in `docs/stack/code-layout.md`,
and a change of language replaces that file and leaves the ADRs in place.

[go.md](go.md) is the mapping onboard-kit used, worked out in practice. The table below is a set of candidates for other
languages. None of them has been tried with this process. Verify each before relying on it.

## What each language needs

| Need                                                         | Why                                                                                     |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| A unit of isolation for a component                          | A rebuild deletes one folder. The language must keep other code from reaching inside it |
| A way for the suite to call a component's operations         | The suite declares them where the language can, and calls them by name where it cannot  |
| A way to hand one implementation to the suite from one place | The wiring                                                                              |
| An import graph a tool can extract                           | The dependency check                                                                    |
| A way to snapshot and compare values deeply                  | The inputs-unchanged and determinism properties                                         |
| A mutation tool that can run another module's tests          | Contract tests live outside the component                                               |

## Candidates

| Neutral term      | TypeScript                                                          | Python                                                     | Rust                                                        | Java or Kotlin                              |
| ----------------- | ------------------------------------------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------- |
| Component         | A folder with an `index.ts`, in one package or a workspace package  | A package under `src/<project>/<noun>/<role>/`             | A module, or a crate in a workspace                         | A package, or a Gradle or Maven module      |
| Operations        | An exported `interface` in the suite                                | None needed. The suite calls them by name                  | A trait in the suite's crate                                | An interface in the suite's module          |
| Wiring            | One test file that passes the implementation's factory to the suite | One test that passes the built implementation to the suite | One integration test that constructs it and calls the suite | One test class or a `ServiceLoader` binding |
| Import isolation  | dependency-cruiser, or ESLint boundary rules                        | import-linter                                              | Crate boundaries and `pub(crate)`                           | ArchUnit                                    |
| Deep snapshot     | `structuredClone` and a deep-equal                                  | `copy.deepcopy` and `==` on dataclasses                    | `Clone` and `PartialEq`                                     | Records, or a serializer to compare bytes   |
| Immutability help | `readonly`, `Readonly<T>`                                           | Frozen dataclasses                                         | The default                                                 | Records, immutable collections              |
| Mutation tool     | Stryker                                                             | mutmut, cosmic-ray                                         | cargo-mutants                                               | PIT                                         |

## A language without interfaces: a Python sketch

This is a paper sketch, not tried. It checks that the roles and rules of
[ADR 0150](../docs/decisions/0150-contracts-hold-data-and-contract-tests-hold-the-code.md) need no change where a
language has no way to declare an interface.

```text
contracts/specifications/<noun>/<role>/contract.md
contracts/fixtures/<noun>/<role>/cases.json
contract-tests/
  harness/loader.py                         turns fixture data into model values
  runner/<noun>/<role>/suite.py             run(impl): loads the cases, calls impl.<operation>(**arguments), compares
  wiring/<noun>/<role>/test_contract.py     def test_contract(): suite.run(build_component())
src/<project>/<noun>/<role>/                the component
```

- **Operations.** There is no declaration. The suite calls each operation by name. It starts with a check that every
  operation the contract names exists on the implementation and can be called, so a missing operation fails before the
  first case runs. A `typing.Protocol` in the suite is optional documentation.
- **Mismatches.** They fail at the first call, not at compile time. Swapped arguments of one type still need a fixture
  that tells them apart, and keyword arguments help.
- **Rules.** The suite and the harness import the model and the harness. The wiring imports its own component and its
  own suite. `import-linter` can state both. No rule needs a different wording.
- **Tools.** Mutation runs the wiring test with mutmut. Fixtures and the specification are the same files as in Go, so a
  move from Go to Python replaces `contract-tests/` only.

## Fixtures stay data

Whatever the language, fixtures are plain data, such as JSON or YAML, in `contracts/fixtures/`. A small piece of shared
test code in `contract-tests/harness/` turns them into domain values. A change of language rewrites that piece, the
suite, and the wiring, not the fixtures.

## The dump adapter

The contract-hardening skill's differential run needs a small program per build. Its protocol is in the
[dump format](../skills/contract-hardening/references/dump-format.md), and a Go version is in the skill's
`scripts/adapters/go/`. Write one per language from the format.
