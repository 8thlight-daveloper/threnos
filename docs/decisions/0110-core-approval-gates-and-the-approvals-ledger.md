---
category: regenerative-process
status: accepted
approval: person
builds-on: ['0030', '0040', '0060', '0080']
partly-supersedes: ['0080']
note: Replaces the paragraph in 0080 that keeps the core gates fixed. The settings, the user layer, and the merge rule in 0080 stay.
---

# 0110. Core approval gates and the approvals ledger

Builds on [0030](0030-contracts-and-tests.md), [0040](0040-behavior-judgment.md),
[0060](0060-acceptance-scenarios-as-data-or-code.md), and [0080](0080-approval-gates-are-settings.md). It replaces the
part of 0080 that keeps the core gates fixed.

## Context

[0080](0080-approval-gates-are-settings.md) made the principles gate a setting and left the gates on contracts,
acceptance scenarios, `architecture.yaml`, and the domain model with a person. Some projects want to run with no person
in the loop until a person reviews a running build, and read the text only if the build looks wrong.

Two things stand in the way. The rules in [0030](0030-contracts-and-tests.md) and
[0060](0060-acceptance-scenarios-as-data-or-code.md) rest on an independent check: the one who approves the tests that
judge a build is not the one who wrote the build. A setting that lets any agent approve would remove that check without
a trace. And the protected files have no common place to record an approval. A contract has a `Status:` header,
`architecture.yaml` and the model have none, and a protected file is protected by convention, so a change after its
approval goes unseen.

## Decision

**Each core gate is a setting.** `[approvals]` in `.threnos/config.toml` gains `contracts`, `acceptance`,
`architecture`, `model`, and `build`, beside `principles`. Each is a list of `person`, `agent`, or both, and the default
is `["person"]`. The rules of [0080](0080-approval-gates-are-settings.md) apply: the user layer may replace a list for
that person's own work, an empty list is an error, and the project's list decides what merges.

**Approvals are recorded in a ledger.** `.threnos/approvals.yaml` is committed. One entry covers one protected unit:

| Gate           | Unit                                                          |
| -------------- | ------------------------------------------------------------- |
| `contracts`    | One component's folder under `contracts_root`                 |
| `acceptance`   | The `acceptance/` folder                                      |
| `architecture` | `architecture.yaml`                                           |
| `model`        | The model folder                                              |
| `build`        | A commit that a person ran and looked at, with its short note |

An entry holds the gate, the unit, a content hash, the approver, the author, a date, and an optional note. The hash is
SHA-256 over the unit's relative paths and file contents in sorted order. A new entry replaces the old one for its unit,
and Git holds the history. The principles file keeps its own front matter from
[0090](0090-product-principles-live-in-a-file.md).

**The checker holds each unit to its entry.** It fails when:

- a unit has no entry;
- the unit's hash differs from its entry, so the unit changed after it was approved;
- the approver's kind is not in the project's list for the gate;
- the independence rule below is broken.

The check runs only when `.threnos/approvals.yaml` exists. A project that has not adopted the ledger keeps the
convention it has today, and adopting it is a file and a first set of entries.

**An agent approval needs an independent agent.** The approver and the author are each `{kind, ...}`. A person has
`kind: person` and a name. An agent has `kind: agent`, a `harness`, and a `session` identifier that the harness exposes.
When the approver is an agent, its `(harness, session)` must differ from the author's. A person approver always passes.
`independence` under `[approvals]` is `session` by default. A project may set `harness` to require different harnesses.
The rule applies to every gate with an author.

**A running-build review is a gate.** A person starts the program built from a commit, uses it against the acceptance
scenarios and the product principles, and records a `build` entry with the commit. The entry replaces "a person read the
text" for a project that runs hands-off. The checker needs the entry's commit to be well formed and the approver to be
in the list. It does not check that the commit is the one under review.

**Sync warns when a list makes a gate empty of people.** A list of `["agent"]` alone warns, as in 0080. A `build` list
with `agent` warns that no person reviews anything.

**The escalation rules stay.** [0040](0040-behavior-judgment.md) still sends a new privacy, security, ownership,
destructive, stored-format, or hash-compatibility consequence to a person, whatever the settings say. A setting changes
who approves a routine change, not what an agent may decide alone.

## Consequences

- A project can run hands-off by listing `agent` on the gates it chooses, and a person reviews a running build.
- Every approval says who gave it and from which session. A person can read the ledger in a pull request.
- A protected unit that changes after its approval fails the check until a new entry covers it, which makes "protected"
  mechanical.
- The independence rule is self-reported. A harness and a session identifier are written by the approving agent, and CI
  cannot verify that the session is real or that it did not resume the author's context. The fields are an audit trail
  and a speed bump. They make a careless self-approval fail the check and leave evidence. The mutation tool and the
  second independent build of [0030](0030-contracts-and-tests.md) still test a contract on its merits.
- The flake gains `nix run .#approve`, which computes the hash and writes the entry, so no one hashes by hand. It checks
  the entry against the settings before it writes, and warns when the project's own list would reject it.
- The ledger needs an entry per component for contracts, so a project with many components has many entries.

## Alternatives considered

- **Front matter in each protected file.** Contracts could take it. `architecture.yaml`, the model, and scenarios
  written as code have no natural place, so the projects would have several mechanisms.
- **Commit trailers.** They record who approved a commit, not which unit, and they cannot bind an approval to the
  content that was approved.
- **Keep the core gates fixed.** It keeps the independent check without a trace, and it blocks a project that wants no
  person in the loop.
- **Let any agent approve.** It removes the independent check with no evidence that it was removed.
- **Require a person for `build` always.** It keeps one human gate in every project, but it blocks a project that
  chooses full automation and says so.
