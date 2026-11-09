# Language mappings

The process names no language. A project maps each neutral term to its language once, in `docs/stack/code-layout.md`,
and a change of language replaces that file and leaves the ADRs in place.

[go.md](go.md) is the mapping onboard-kit used, worked out in practice. The table below is a set of candidates for other
languages. None of them has been tried with this process. Verify each before relying on it.

## What each language needs

| Need                                                                | Why                                                                                     |
| ------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| A unit of isolation for a component                                 | A rebuild deletes one folder. The language must keep other code from reaching inside it |
| An interface that lives outside the component                       | The contract folder holds it, so deleting the component keeps its specification         |
| A test that can bind an interface to an implementation in one place | The wiring test                                                                         |
| An import graph a tool can extract                                  | The dependency check                                                                    |
| A way to snapshot and compare values deeply                         | The inputs-unchanged and determinism properties                                         |
| A mutation tool that can run another module's tests                 | Contract tests live outside the component                                               |

## Candidates

| Neutral term      | TypeScript                                                                | Python                                                   | Rust                                    | Java or Kotlin                              |
| ----------------- | ------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------------------- | ------------------------------------------- |
| Component         | A folder with an `index.ts`, in one package or a workspace package        | A package under `src/<project>/<noun>/<role>/`           | A module, or a crate in a workspace     | A package, or a Gradle or Maven module      |
| Interface file    | An exported `interface` and its types in `contracts/<noun>/<role>/api.ts` | A `typing.Protocol` in `contracts/<noun>/<role>/api.py`  | A trait in a contracts crate            | An interface in a contracts module          |
| Wiring test       | One test file that imports the implementation's factory                   | One `conftest.py` fixture that builds the implementation | One integration test that constructs it | One test class or a `ServiceLoader` binding |
| Import isolation  | dependency-cruiser, or ESLint boundary rules                              | import-linter                                            | Crate boundaries and `pub(crate)`       | ArchUnit                                    |
| Deep snapshot     | `structuredClone` and a deep-equal                                        | `copy.deepcopy` and `==` on dataclasses                  | `Clone` and `PartialEq`                 | Records, or a serializer to compare bytes   |
| Immutability help | `readonly`, `Readonly<T>`                                                 | Frozen dataclasses                                       | The default                             | Records, immutable collections              |
| Mutation tool     | Stryker                                                                   | mutmut, cosmic-ray                                       | cargo-mutants                           | PIT                                         |

## Fixtures stay data

Whatever the language, fixtures are plain data, such as JSON or YAML, and a small piece of shared test code turns them
into domain values. A change of language rewrites that piece and the test setup, not the fixtures.

## The dump adapter

The contract-hardening skill's differential run needs a small program per build. Its protocol is in the
[dump format](../skills/contract-hardening/references/dump-format.md), and a Go version is in the skill's
`scripts/adapters/go/`. Write one per language from the format.
