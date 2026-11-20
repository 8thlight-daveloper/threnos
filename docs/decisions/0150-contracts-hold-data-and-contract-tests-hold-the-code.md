---
category: regenerative-process
status: accepted
approval: person
builds-on: ['0020', '0030', '0060', '0110']
partly-supersedes: ['0020', '0030']
note: Replaces where the parts of a contract live, in the Layout of 0020 and the table of 0030. The rest of both stays. languages/README.md holds a paper sketch of a language without interfaces, not yet tried.
---

# 0150. Contracts hold data and contract tests hold the code

Builds on [0020](0020-structure-and-regenerative-components.md), [0030](0030-contracts-and-tests.md),
[0060](0060-acceptance-scenarios-as-data-or-code.md), and [0110](0110-core-approval-gates-and-the-approvals-ledger.md).

## Context

A contract has four parts: a description, fixtures, contract tests, and an interface binding. Two are language-neutral
and two are written in the implementation language. Today all four share one folder per component. That has three costs.

- A language change edits files inside `contracts/`, next to files that should not change.
- A folder named for the specification holds code, including the one file that imports an implementation.
- An agent that builds a component meets code and data in the folder it was told to read. It reads the language-bound
  files, which are most of the folder, when it needed the description.

Acceptance already draws the line. Its scenarios and fixtures are data, and its runner is the only language-specific
part. Contracts have no equivalent split.

## Decision

### The method fixes roles and folders, and a language mapping fixes files

This record names the roles, the folders, and the rules. It does not name a file, an interface type, or how the suite
receives an implementation. The mapping for each language says that, in `docs/stack/code-layout.md`.

### Folders, mirrored by component

| Folder                          | Holds                                                                       | Language-bound |
| ------------------------------- | --------------------------------------------------------------------------- | -------------- |
| `contracts/specifications/<c>/` | `contract.md`, the behavior in plain words                                  | No             |
| `contracts/fixtures/<c>/`       | Cases as data, each citing its source                                       | No             |
| `contract-tests/runner/<c>/`    | The suite: loads the fixtures, calls the component's operations, and judges | Yes            |
| `contract-tests/wiring/<c>/`    | The connection from the suite to one implementation                         | Yes            |
| `contract-tests/harness/`       | Test code shared by suites, such as turning fixture data into model values  | Yes            |

`<c>` is `<noun>/<role>`, as for components. Each component with a specification has a path in `specifications/`,
`fixtures/`, `runner/`, and `wiring/`, and a path with no counterpart is an error. `harness/` is shared and not
mirrored.

`acceptance/` keeps its name and holds `scenarios/`, `fixtures/`, and `runner/`. Its `testdata/` becomes `fixtures/`, so
the two trees use the same word.

### Rules

- `contracts/` holds no source. `specifications/` holds Markdown only, and `fixtures/` holds data only.
- The suite imports no implementation. It imports the shared model and the harness.
- The wiring is the only code that imports a component. It imports its own component and its own suite, nothing else.
- No component imports anything under `contract-tests/`.
- The drafter writes the suite and the wiring. The builder of a component writes neither and never edits them, as
  [0030](0030-contracts-and-tests.md) says of any test that judges its own build.

### The interface is declared where the suite is

A contract names its operations, their arguments, and their results in the description, in neutral terms. Where the
language has a way to declare them, the drafter declares them in the suite, beside the code that calls them. There is no
interface file or folder of its own. The builder reads the description and the suite's declaration, and a mismatch fails
when the suite runs. The component does not import the declaration, so deleting the component deletes nothing that a
rebuild needs. A language with no such declaration needs no file, and the suite calls the operations by name.

### One approval unit

A component's contract is one unit in the `contracts` gate of
[0110](0110-core-approval-gates-and-the-approvals-ledger.md). It covers the four mirrored paths, hashed together, so one
approval binds the description, the cases, the suite, and the wiring. `architecture.yaml` gains a root for the tests
beside `contracts_root`.

### Checks

- **Layout**, from the file system and in no language: the mirrored paths exist and match, nothing sits outside the
  folders above, `specifications/` holds only Markdown, and `fixtures/` holds only data. The check allows a named set of
  data formats and treats everything else as source, so it names no language.
- **Imports**, one adapter per language as for [0100](0100-dependency-rules-are-checked-from-architecture-yaml.md): the
  suite and harness import the model and the harness, the wiring imports its component and its suite, and no component
  imports `contract-tests/`.

### What a builder reads

To build a component, read its `specifications/<c>/contract.md` and the operation declaration in its suite. Run the
suite. Open the suite and the fixtures only to debug a failure. This record does not stop an agent from reading more.
The shared rules say what to read.

### Fixtures are as much data as the cases allow

A case that is an input and an expected output belongs in `fixtures/`. A rule that needs a sequence of calls, computed
values, or a property over many inputs may live in the suite as code. A contract moves rules from the suite to the
fixtures when the fixture format can say them, and the suite shrinks as it does.

## Consequences

- A language change replaces `contract-tests/` and leaves `contracts/` and `acceptance/` as they are.
- `contracts/` is Markdown and data, so a person reviews the specification without reading code, and an agent building a
  component has a clean folder to read.
- A component's contract spans four folders. Adding a component adds four paths, and the layout check reports a missing
  one.
- The wiring stays in the protected tree, so a rebuild cannot drop the call that runs the suite. That keeps one
  implementation import under `contract-tests/`, in a folder of its own with its own rule.
- The ledger unit and the layout and import checks change, and each language mapping states its files. Existing projects
  migrate their contracts and rename `testdata/` in acceptance.
- The interface is no longer a protected file of its own. The suite holds it, and the description holds the neutral
  form.

## Alternatives considered

- **Keep code in `contracts/`.** Nothing moves. The folder still mixes data with code, and a language change still edits
  it. Revisit if the four-folder cost proves higher than the mixing cost.
- **Contracts as data only, with no suite code.** A generic runner would load every case. It cannot yet say a rule that
  needs a sequence of calls or a value computed in the test. The last section keeps the direction and makes it
  incremental. Revisit when a project's fixture format covers its rules.
- **Wiring in the component's folder.** The contract folders hold no implementation import. A rebuild could drop the
  call that runs the suite, and the guard would be an import check and a stub run. Revisit if those prove enough.
- **The builder writes the interface.** The suite is written and approved before the build, so it would depend on the
  builder's output, and the builder would shape its own judge.
- **One `tests/` parent for contract tests, acceptance, and unit tests.** It puts the disposable unit tests beside the
  protected ones, and it hides who may change what.
- **Rename `acceptance/` to `acceptance-tests/`.** It buys naming parity at the cost of the gate name, the settings key,
  and every check that names the folder.

## Open questions

- Mutation tooling points at one contract package today. How it runs when the suite and the wiring are in different
  places.
- Each mapping must show that the roles fit. Go is the worked one. A paper sketch of one language without interfaces is
  still owed, to show that the roles and rules need no change.
- The name and shape of the setting for the tests root in `architecture.yaml`.
