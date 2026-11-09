---
category: regenerative-process
status: accepted
approval: unrecorded
builds-on: ['0020', '0030']
note: Generalized from onboard-kit 0620, which a person approved there.
---

# 0050. Keep decisions as records and current state in checked files

Builds on [0020](0020-structure-and-regenerative-components.md) and [0030](0030-contracts-and-tests.md).

## Context

A regenerative build starts from contracts and the decisions behind them. A person or an agent has to be able to ask which decisions affect one component, and trust the answer. Three things get in the way:

- **A table in a record goes stale.** Nothing fails when prose drifts from the code, because a table in prose cannot be checked.
- **Status is free text.** Spellings of "accepted" multiply, and some add the state of the build, such as "implementation pending". That state goes stale, and a program cannot read any of it.
- **Decisions are hard to find from a component or a category.** Contracts cite records in several styles, and method decisions, product decisions, and a project's operations share one list.

## Decision

**A record and a checked file have different jobs.** A decision record is a dated statement of what was chosen and why. It changes only by its status, and a later record supersedes it. Current state lives in files that a check reads: `architecture.yaml`, the contracts, the reference docs, and the stack files. A record never holds a table or a list that a check could verify. It states the decision and links to the file that carries the result.

**Every record starts with front matter.** The schema is in [decision record front matter](../../templates/decision-record-front-matter.md).

**Records have five categories.**

| Category | What it decides | Owner |
| -- | -- | -- |
| `regenerative-process` | The method of building from contracts | Threnos only. Not copied into projects, and a project does not reuse the category |
| `architecture` | The shape of the product and its code | The project |
| `behavior` | What the product does or refuses, whatever it looks like | The project |
| `ux` | How a person meets it: screens, flows, messages, and the command surface | The project |
| `operations` | How the project runs: CI, releases, tooling, and one-time exceptions | The project |

A project may add categories. It does not reuse `regenerative-process` for its own decisions. The shared rules carry what an agent needs from the method ADRs, so a project record does not restate them.

**`affects` links a decision to components.** A `behavior` or `ux` record names the components it changes, as ids in `architecture.yaml`. It is `[]` only while the component it describes is not built. An `architecture` record may name them. A process record names none. No record says `all`.

**A record holds no implementation state.** "Implemented" and "pending" are facts about the code, and a check of the code says them better. A record also holds no counts or scores.

**The record check runs with the project's other checks.** It fails on a missing or unknown field, on a component id that does not exist, on a replacement that is not listed on both records, on `affects` in a process record, and on a contract that cites a product record missing from that record's `affects`. It reports without failing a listed component whose contract does not cite the record, because contracts keep no history.

## Consequences

- A new record is harder to write by a little. It needs a category and an `affects` list. The check says what is missing.
- A person can list the Threnos method decisions with one category query, and can list the decisions that touch one component.
- A table that a record used to hold moves to `architecture.yaml` or a reference doc, and the record links to it.

## Alternatives considered

- **Free-text status and prose cross-references.** Cheapest to write. It drifts, and no tool can tell which records a component depends on.
- **One list for all decisions.** Simple to browse. Method decisions then mix with product decisions, and a project cannot tell which ones it inherits.
