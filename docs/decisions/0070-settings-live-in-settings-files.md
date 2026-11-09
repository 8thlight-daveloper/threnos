---
category: regenerative-process
status: accepted
approval: person
builds-on: ['0020', '0050']
note: Applies to the project settings the shared rules and skills read.
---

# 0070. Settings live in settings files

Builds on [0020](0020-structure-and-regenerative-components.md) and [0050](0050-records-and-checked-files.md).

## Context

The shared rules and skills read a project's settings: where its components live, how mutation runs, which guide to
follow. The first template kept them in a Markdown table in `AGENTS.md`. Two of its rows repeated values that
`architecture.yaml` already holds, so they could drift. A tool cannot validate a table in prose, and an agent has to
parse it by reading. Records already follow the same lesson: a table that a check could verify belongs in a checked
file, as [0050](0050-records-and-checked-files.md) says.

## Decision

**A setting lives in a settings file, in one place.** A value that a tool or an agent reads as a setting goes in a file
with a schema that a check can validate. Prose holds what a person chooses and explains.

- `architecture.yaml` holds the shape of the program: the components folder, the model, the contracts folder, the
  dependency rules, and how acceptance scenarios are written.
- `.agents/threnos.toml` holds how a project takes Threnos: which rules and skills are on, and the settings the rules
  and skills read, such as `repository_context` and `mutation_cadence`. Sync validates each value.
- `AGENTS.md` holds pointers to documents that a person picks, such as the product principles record and the testing
  stack doc. A pointer names a file. It carries no value that a tool needs.

**A value has one home.** A setting that a settings file already holds is not repeated in `AGENTS.md`. A setting that
follows from another is derived from it, not written twice.

**A fixed name is not a setting.** The five task recipes have fixed names in `process/task-recipes.md`, so no setting
names them.

## Consequences

- A tool validates every setting before an agent reads it, and a mistyped value fails sync and the flake check.
- A project has no copy of a value to keep in step. Changing a setting touches one file.
- The "Project settings" table in `AGENTS.md` is replaced by a table of document pointers.
- A rule that names a setting says where it lives, so an agent reads the file and does not guess.

## Alternatives considered

- **Keep a settings table in `AGENTS.md`.** One place for a person to read. A tool cannot validate it and it drifts from
  the files that hold the same values.
- **Put everything in `threnos.toml`.** One file, but program shape such as components belongs next to the dependency
  rules and the checks that read them.
