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
- Approval on changes to contracts, acceptance, `architecture.yaml`, and the domain model, for example through code
  owners.
- The dependency check and the architecture tests.
- The full test suite.
- The docs checks: format, links, and prose rules.

Run the same check before every commit, through a git hook, so a green local run means a green CI run. Never skip a
failing check, and never edit a tool's configuration to make one pass without asking a person.

## Keep the review queue short

Contracts can be drafted in parallel, because they do not depend on each other's code. Approvals are one person reading.
Keep at most three contract changes waiting for review at once, and start new work only as fast as reviews finish.
