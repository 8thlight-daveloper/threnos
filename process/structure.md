# Structure

How a regenerative project is laid out, in terms that name no language. [languages/](../languages/README.md) maps each
term to folders and files.

## One program, components as modules

- One program. Its logic lives in components, and the entry point is thin glue that wires them.
- A **component** is one module, package, or crate: the smallest unit the language isolates well. It is the unit of
  rebuild. A rebuild deletes its folder and regenerates it.
- The **domain model** holds the types that several components pass to each other. It is not a component. It is never
  deleted and rebuilt, and changing it takes an ADR.
- **Drivers** are the shell: the commands, the terminal interface, anything that reads or writes outside the program.

Separate binaries or services per component give harder isolation, at the cost of protocols, versioning, and
distribution. Start with one program. Revisit for a component whose isolation is a security feature.

## Choosing boundaries

[Choosing component boundaries](decomposition.md) gives guidance and a worked example. Group behavior by its reason to
change, keep domain policy independent of external mechanisms, and check whether each implementation can be regenerated
without changing neighboring contracts. Dependency positions and pace layers describe different aspects of the design.

## Folders by role

| Folder                              | Holds                                                                                      | Changes                        |
| ----------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------ |
| Components, grouped `<noun>/<role>` | One component each, such as `section/selector`                                             | Rebuilt freely                 |
| Domain model                        | The shared types                                                                           | By ADR only                    |
| `contracts/`                        | Specifications and fixtures, one path per component, mirroring the component folders       | A person approves              |
| `contract-tests/`                   | The language-bound suite and wiring for each contract, and a shared harness                | A person approves              |
| `acceptance/`                       | Scenarios as data, their fixtures, and a replaceable runner                                | A person approves              |
| Entry point                         | Wiring only                                                                                | Rebuilt with whatever it wires |
| `docs/`                             | Decisions, reference, architecture, stack. See [docs and decisions](docs-and-decisions.md) | Each at its own pace           |

## Naming

Name a unit for what it acts on and what it does: the noun, then the role. A name that needs "and" is two units. In
docs, write plain spaced words, such as "section selector". In code, the parent folder carries the noun and the module
carries the role. Spell words out or use a common short form such as `config`. Do not coin abbreviations.

## The contract

A component's contract is four mirrored paths, and it outlives the component.
[ADR 0150](../docs/decisions/0150-contracts-hold-data-and-contract-tests-hold-the-code.md) gives the reasons.

| Path                            | Holds                                                                         | Language-bound |
| ------------------------------- | ----------------------------------------------------------------------------- | -------------- |
| `contracts/specifications/<c>/` | `contract.md`, the behavior in plain words                                    | No             |
| `contracts/fixtures/<c>/`       | The cases, as data                                                            | No             |
| `contract-tests/runner/<c>/`    | The suite: loads the cases, calls the component's operations, and judges them | Yes            |
| `contract-tests/wiring/<c>/`    | The connection from the suite to one implementation                           | Yes            |

`<c>` is `<noun>/<role>`. `contract-tests/harness/` holds test code that suites share, such as turning fixture data into
model values.

- `contracts/` holds Markdown and data, so a change of language replaces `contract-tests/` and leaves `contracts/`
  alone.
- The **suite** declares the operations it calls, where the language has a way to declare them. The drafter writes it
  with the wiring, and the builder does neither. The component does not import the suite, so deleting the component
  deletes nothing that a rebuild needs.
- The **wiring** is the only code that imports a component, through one constructor call. A rebuild that changes the
  entry point fails there. It keeps the call that runs the suite in the protected tree, where a rebuild cannot drop it.
- The suite and the harness import only the domain model and the harness. A type that several contracts need must
  therefore live in the domain model.

[contracts.md](contracts.md) covers what goes in one.

## Dependency order

Each component has a position, and may depend only on components at earlier positions. Two components at the same
position may not depend on each other. If one needs the other, they belong at different positions.

```text
0  model                         nothing from the project
1  section/hasher                model
1  condition/evaluator           model
2  section/selector              condition/evaluator, model
3  question/finder               section/selector, condition/evaluator, model
...
n  entry point                   wires everything
```

The list lives in one data file, [`architecture.yaml`](../templates/architecture.yaml), not in code.

## Rules as data

The dependency rules are checked by tests whose rules are data, so a change of language replaces an adapter and not the
rules.

- **`architecture.yaml`** lists the components, the dependency order, the naming rule, and the categories of library
  that core components may not use: filesystem, network, process, terminal, clock, randomness, environment. It names no
  language. It is protected like a contract.
- **An extractor** reads the source and emits a plain graph: each component and what it imports. It is the only
  language-specific part, along with the map from each banned category to that language's libraries.
- **A checker** compares the graph with the rules, and reports each violation with the import that proves it. It also
  checks that `acceptance/` imports only what `acceptance.may_import` lists, never the project's own implementation, and
  that the contract tests import only what their role allows.
- **File system checks** need no parser: the folder layout, the naming, that every specification has fixtures, a suite,
  and a wiring path and the reverse, that `acceptance/` holds only its three folders, and that the docs' tables match
  `architecture.yaml`.

Start with the language's own tooling for the extractor, because it resolves imports exactly.

## Side effects and data access

Every component declares two things in its contract, and the architecture docs keep the current table.

- **Side effects:** what it does outside its arguments. For a core component the answer is "none".
- **Data access:** what it does with a value it was given. It **reads** fields, or **returns a changed copy** that
  differs only in the fields it declares, or **creates** a value from inputs of another kind.

## How the functional core is enforced

Each check runs on every contract test, so a rebuild cannot slip past it.

| Rule                           | Check                                                                               |
| ------------------------------ | ----------------------------------------------------------------------------------- |
| Inputs unchanged               | Snapshot every input deeply before the call and compare after                       |
| Deterministic                  | Run every call twice and compare the results byte for byte                          |
| No memory                      | Run cases forward and in reverse on one instance. The results match                 |
| Declared data access           | After any call, every field outside the declared set equals the input               |
| No input or output in the core | The dependency check bans the filesystem, network, process, and terminal categories |
| No shared mutable state        | A lint forbids module-level variables that can change                               |

A returned value may share unchanged parts with its input. Nothing is ever mutated, so sharing is safe. Where a language
cannot guard against mutation, these tests are the guard.
