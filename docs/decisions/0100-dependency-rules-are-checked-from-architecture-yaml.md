---
category: regenerative-process
status: proposed
approval: unrecorded
builds-on: ['0020', '0050']
note: Adds the libraries and naming.exceptions keys and the checks over them. The structure in 0020 is unchanged.
---

# 0100. Dependency rules are checked from architecture.yaml

Builds on [0020](0020-structure-and-regenerative-components.md) and [0050](0050-records-and-checked-files.md).

## Context

[0020](0020-structure-and-regenerative-components.md) puts the dependency order, the drivers, and the banned categories
in `architecture.yaml` and says a language adapter checks them. Until a checker exists, a rule in that file binds
nobody. A project that declared its components and then split a package found that a core component imported `os` only
by reading imports by hand. The file also named no way to say that a component keeps a flat name until it is decomposed,
or which third-party libraries belong to a banned category.

## Decision

**Each language ships a checker that reads `architecture.yaml` and the language's own import graph.** It reports each
violation with the import that proves it, and fails the project's `check` recipe. The Go checker is
[languages/go/dependency-check/](../../languages/go/dependency-check/README.md).

**The rules it enforces:**

- A component imports only components in its `depends_on`, and only at an earlier position.
- A package under `components_root` belongs to a component. The model is always an allowed import, the model imports no
  component, and a component imports nothing outside the components and the model.
- A core component, which is any component not listed under `drivers`, and the model import no library in a category
  listed under `banned_in_core`. Drivers are exempt from the ban and follow the other rules.
- The clock category bans functions that read the clock, not the `time` import.
- The entry point is outside `components_root` and is not checked. Test files are not checked.

**`libraries` maps a category to the third-party libraries in it.** The standard library part of each category is the
language's own and is built in. An entry covers the packages below it.

**A flat name fails unless the project lists it under `naming.exceptions`.** A listed name is an accepted exception
until the component is decomposed. The check fails when a listed name follows the rule or is not a component, and it
prints how many exceptions remain. A warning would be ignored, so the default is failure.

## Consequences

- A rule in `architecture.yaml` that a checker can read has a check behind it, and `just check` runs it.
- A project lists its terminal libraries once, in `architecture.yaml`, and the checker takes them from there.
- A component that cannot be decomposed yet is visible in a protected file, and the count shows how many remain.
- A language with no checker has the rules and no enforcement until one is written.

## Alternatives considered

- **ArchUnitGo.** A rules library in the target language, with its own rule syntax. The rules are already data here, and
  a second copy would drift.
- **`depguard` or a linter allowlist.** It checks one package at a time and would repeat the dependency table.
- **A warning for flat names.** It leaves the rule unenforced until someone reads the log.
- **List drivers and tooling packages separately.** A tooling package under `components_root` is moved out of it, so no
  new key is needed.
