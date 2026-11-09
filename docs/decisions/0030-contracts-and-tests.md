---
category: regenerative-process
status: accepted
approval: unrecorded
builds-on: ['0010', '0020']
note: Generalized from onboard-kit 0025, which is accepted there.
---

# 0030. Contracts and tests

Builds on [0010](0010-functional-core-and-imperative-shell.md) and
[0020](0020-structure-and-regenerative-components.md).

## Context

A component can be deleted and rebuilt only if something permanent says what correct means, and that something does not
depend on the component's code. This record says what those tests are, who writes them, how we know they are strong
enough, and how a rebuild is run and reviewed.

## Decision

### Two kinds of tests

| Kind            | Level                                                         | Lives in                   | Judges                            |
| --------------- | ------------------------------------------------------------- | -------------------------- | --------------------------------- |
| Contract test   | One component boundary: fixture in, expected out              | `contracts/<noun>/<role>/` | A component and any rebuild of it |
| Acceptance test | The whole program: files and input in, observable results out | `acceptance/`              | The assembled system              |

"Eval" is reserved for checks a model judges. These are ordinary deterministic tests.

Rules for both:

- **Behavior only.** Assert on outputs, never on internals.
- **Independent authorship.** The agent that builds or patches a component does not write or edit its contract tests,
  fixtures, or acceptance scenarios. A person approves every change to them.
- **Properties as well as goldens.** Two runs produce identical bytes. Inputs are unchanged.
- **Parallel by default.** Per-test temporary folders, an injected clock, no shared mutable state, and sorted output
  wherever iteration order could leak. Golden regeneration is an explicit command, never a side effect of a test.

### Acceptance tests are language-neutral

Scenarios are data under `acceptance/scenarios/`. A replaceable runner drives the built program. Tests never import the
implementation. The scenario format is protected. See `docs/reference/acceptance-scenarios.md`.

### Where contract tests run

A contract's tests run once the component's folder exists, so a contract can merge ahead of its component without
turning the build red.

### Fixtures

Contract fixtures are plain data, written by hand. A tool may draft them, but a person checks every value. Values a
loose reader accepts and a strict one rejects are written out on purpose. Each case names its source.

### Writing contracts

A contract has four parts: a plain description, fixtures, contract tests, and the interface binding.

- **An agent drafts, a person approves.** A separate agent run writes the first version of every part, so nobody starts
  from a blank page. A person reads all of it and gives feedback before anything is built against it. The run that
  drafts a contract does not build the component.
- **Fixtures cite their source.**
- **The builder reads the contract and does not edit it.** It reports a conflict, a gap, or a mistake, and stops.
- **A contract must tell right from wrong.** One agent writes the spec and the tests together, so a shared
  misunderstanding could pass review. Two checks guard against it. Both are workflow steps, not optional requests.
  - Drafting: the drafter lists plausible wrong implementations and shows the tests fail each one. The lists are scratch
    work and are not committed.
  - Building: the builder runs the tests against a stub first, and every test that exercises the output must fail. A
    test of a property, such as determinism, can pass against a stub that returns nothing. After the tests pass,
    mutation testing reports surviving mutants as contract gaps. The tool generates the mutants, not the agent, so the
    agent does not grade itself. The project's mutation cadence says whether the builder runs the tool or reads the
    latest CI result.
  - Hardening, for a component with a rich input: a second independent build and a differential run. Where two builds
    differ, the contract is ambiguous. See the `contract-hardening` skill.

### Rebuilding a component

1. Open a branch. Delete the component's folder.
1. Regenerate it from its contract, its architecture doc, and the dependency rules.
1. Run contract tests and acceptance tests.
1. CI checks that the change touches only that folder.

Any change to the contracts, the acceptance tests, `architecture.yaml`, or the domain model is a separate change with
human approval. A rebuild that needs a contract change stops and asks.

### When to regenerate

- A failing contract test does not trigger regeneration. Patch a local defect in place.
- Regenerate when the design is inadequate, when the domain model under it changes, or when patches have piled up.
- A mutation survivor is a gap in the contract. The fix goes to the contract's tests or fixtures, approved by a person.
  The code changes only if the new tests fail against it.
- A contract change runs first against the existing component. Someone other than the author of the new tests patches
  it.
- After a large contract change, regenerate once from the contract alone. That checks the contract is enough: a second
  independent build must also pass, and where two builds differ, the contract is ambiguous.
- A person reviews every regeneration. Do not regenerate faster than that review keeps up.

### Accepted survivors

A survivor a person has checked and accepted goes in `tools/mutation/accepted/<component>.txt`, with a stable key and
the reason in terms of the contract. Only a person adds a line.

### Review

A person reviews a rebuild by reading the contract, the acceptance results, the survivor report, and any change to
tests, not the regenerated code. The review passes if every test passes and no test changed without approval. Reading
the code stays optional. CI enforces the folder scope, approval on protected paths, the dependency check and
architecture tests before every commit, and the full suite.

## Consequences

- The quality of the contracts decides the quality of the rebuilds. Writing and reviewing contracts is the main design
  work.
- Reviewers rely on test results. Independent authorship is what makes that safe, so the rule is not optional.

## Alternatives considered

- **One agent writes the contract and the component.** Fastest. A shared misunderstanding passes review, because the
  tests were written to fit the code.
