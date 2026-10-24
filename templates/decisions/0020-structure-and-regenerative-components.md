# 0020. Structure and regenerative components

Status: proposed

Builds on [0010](0010-functional-core-and-imperative-shell.md). The contract and test rules are in [0030](0030-contracts-and-tests.md).

## Context

We want to rebuild any component from scratch when it proves inadequate, and to limit the debt a rebuild can add, even when a smaller model does the work. That needs boundaries that outlive any implementation, tests that define correct behavior independently of the code, and rules that keep a rebuild inside its own folder.

## Decision

### One program, components as modules

- One program, built from `<entry point folder>`. Logic lives in components. The entry point is thin glue.
- Each component is one module, and a component is the unit of rebuild.
- The domain model, in `<model>`, holds the types several components pass to each other. It is never deleted and rebuilt. Changing it needs an ADR.

### Choosing component boundaries

Group behavior that changes for the same business reason, following the
[Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html).
Keep source dependencies directed toward domain policy, following
[Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).
Adapters translate external representations into the values policy needs.

For each component, record its responsibility, likely reasons for change,
interface, invariants, and dependencies. Keep one invariant together. Choose a
boundary that lets its implementation be regenerated without reading a
neighbor's internals or changing a neighbor's contract. Helpers can stay inside
a component when they share its responsibility. Record the project's concrete
boundaries and change examples in `docs/architecture/components.md`.

### Permanent and disposable

| Permanent, changed deliberately | Disposable, rebuilt freely |
| -- | -- |
| The domain model | Each component's folder |
| `contracts/` | Unit tests inside a component's folder |
| `acceptance/` | |
| `architecture.yaml` | |
| `docs/decisions/` | |

### Layout

| Folder | Holds | Changes |
| -- | -- | -- |
| `<components>/<noun>/<role>/` | One component each | Rebuilt freely |
| `<model>/` | The shared types | By ADR only |
| `contracts/<noun>/<role>/` | The interface, fixtures, contract tests, and a wiring test | A person approves |
| `acceptance/` | Scenarios as data, fixtures, and a replaceable runner | A person approves |
| `<entry point folder>/` | The thin entry point | Rebuilt with what it wires |

The interface lives in the contract folder, so deleting a component does not delete its specification. A wiring test is the only place a contract touches its implementation, through one constructor call. Contract folders may import only the model and shared test code.

The file names for the current language are in `docs/stack/code-layout.md`.

### Dependency rules

Each component has a position in a dependency order, and may depend only on components at earlier positions. Two components at the same position may not depend on each other. The order lives in `architecture.yaml`, and `docs/architecture/components.md` shows it.

### Rules as data

`architecture.yaml` holds the components, the order, the naming rule, and the library categories core components may not use. It names no language. An extractor reads the code and emits a graph of imports. A checker compares the graph with the rules. File system checks cover the folder layout, the naming, and that every component has a contract folder. The extractor and the category-to-library map are in `docs/stack/dependency-check.md`.

### Rate of change

| Rate | What lives there | What a change takes |
| -- | -- | -- |
| Slowest | ADRs, stored file formats | A new ADR |
| Slow | The domain model | An ADR |
| Medium | Contracts and acceptance scenarios | A person approves |
| Fast | Component code | Rebuilt freely inside its folder |
| Fastest | Content and configuration | Normal authoring, reviewed by a person |

A dependency points from a faster thing to a slower thing, never the other way. The one exception is a contract's wiring test.

Pace layers describe stability and change approval. Dependency positions describe
which components may import which others. Several components at different
positions can share a pace layer. Policy may consume changing configuration as
input while remaining independent of its loader.

### Side effects and data access

Each component's contract declares its side effects, and what it does with a value it was given: reads fields, returns a copy that differs only in declared fields, or creates a value. A property test checks the declaration. The current table is in `docs/architecture/components.md`.

## Consequences

- A rebuild sees one folder, one interface, and one fixture suite, so the debt it can add is bounded by the folder.
- The domain model is the shared dependency. A mistake there ripples, so it stays small and changes only by ADR.
- There is more structure up front than a single tree of code.

## Alternatives considered

- **Separate programs per component.** Hard isolation, at the cost of version skew, inter-process protocols, and distribution. Revisit for a component where isolation is a security feature.
- **Separate build modules per component.** The compiler enforces the graph. Costs workspace plumbing and version bumps for releases we do not need.
- **No permanent contracts folder.** A rebuild would delete its own specification, and the tests that judge it would live in the folder being rebuilt.
