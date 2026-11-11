# Review and approval

The process moves human attention from code to the artifacts that define correctness. A person reads contracts,
scenarios, and decisions. Reading regenerated code stays optional.

## Who changes what

| Artifact                              | Who writes it                      | Who approves it                                |
| ------------------------------------- | ---------------------------------- | ---------------------------------------------- |
| ADRs                                  | Anyone, often an agent drafting    | A person                                       |
| Domain model                          | Anyone, by ADR                     | A person                                       |
| `architecture.yaml`                   | Anyone                             | A person                                       |
| Contracts and fixtures                | A contract author, not the builder | A person                                       |
| Acceptance scenarios and their format | Not the builder of what they judge | A person                                       |
| The accepted survivor list            | A person only                      | A person                                       |
| Principles documents                  | A person, or an agent proposing    | A person, or an agent if the project allows it |
| Component code                        | A builder agent                    | Passes its contract and the scenarios          |
| Unit tests inside a component         | The builder                        | Disposable with the component                  |

An agent may draft any protected artifact when asked to. It may not approve it, and it may not change one as a side
effect of other work. When a build or rebuild finds that a protected artifact is wrong, it stops and reports.

## Who may approve, and where it is recorded

Each gate is a setting. `[approvals]` in `.threnos/config.toml` lists who may approve it: `person`, `agent`, or both.
The default is `person`. The gates are `principles`, `contracts`, `acceptance`, `architecture`, `model`, and `build`.
[ADR 0080](../docs/decisions/0080-approval-gates-are-settings.md) and
[ADR 0110](../docs/decisions/0110-core-approval-gates-and-the-approvals-ledger.md) give the reasons.

A project that adopts the ledger, `.threnos/approvals.yaml`, records one approval for each protected unit. An entry
holds the gate, the unit, a hash of its content, who approved, who wrote it, and a date. `nix run .#approve` writes it.
The records check fails when a unit has no entry, when a unit changed after its approval, or when the approver's kind is
not in the gate's list.

An agent approves only if its harness and session differ from the author's, so the one who judges a build is not the one
who wrote it. `independence` under `[approvals]` can require different harnesses. A person may approve what an agent
wrote. The identifiers are written by the approving agent and cannot be verified, so they leave a trail and stop a
careless self-approval. They do not prove independence. The mutation tool and the second independent build still test a
contract on its merits.

A person can work hands-off by replacing a list in `.threnos/local.toml`. The project's list still decides what merges,
so CI fails an agent approval that the project does not allow until a person approves the unit again.

## Reviewing a running build

A project that lets agents approve contracts and scenarios keeps one human step: a person starts the built program from
a commit, uses it against the acceptance scenarios and the product principles, and records the result with
`nix run .#approve -- build --approver person:<name>`. The entry names the commit. It replaces reading the text of every
contract. The person reads the text when the build looks wrong. A project that lists `agent` under `build` has no human
step, and sync warns about it.

## Reviewing a rebuild

The review passes when:

- Every contract test and acceptance scenario passes.
- No test, fixture, or scenario changed without approval.
- The change touched only the component's folder.
- The mutation report lists every survivor as a gap or a proven equivalence.

The reviewer reads the contract, the test results, the survivor report, and any test change. Reading regenerated code is
optional.

## What CI enforces

- The folder scope of a rebuild.
- Approval on changes to contracts, acceptance, `architecture.yaml`, and the domain model, through the approvals ledger,
  or through code owners in a project that has not adopted it.
- The dependency check and the architecture tests.
- The full test suite.
- The docs checks: format, links, and prose rules.

Run the same check before every commit, through a git hook, so a green local run means a green CI run. Never skip a
failing check, and never edit a tool's configuration to make one pass without asking a person.

## Keep the review queue short

Contracts can be drafted in parallel, because they do not depend on each other's code. Approvals are one person reading.
Keep at most three contract changes waiting for review at once, and start new work only as fast as reviews finish.
