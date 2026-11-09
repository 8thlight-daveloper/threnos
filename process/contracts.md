# Contracts

A contract says what one component must do, in a form that can judge any implementation of it. Writing and reviewing contracts is the main design work of a regenerative project. Thin contracts let a rebuild drift without failing a test.

## Four parts

| Part | Is | Language-specific? |
| -- | -- | -- |
| Description | `contract.md`: the behavior in plain words | No |
| Fixtures | Plain data: inputs and expected outputs, with a manifest of cases | No |
| Contract tests | Code that feeds each fixture to the component and compares | Yes, but thin |
| Interface binding | The interface and its data types, in the implementation language | Yes |

A change of language rewrites the tests' setup and the binding. The description and the fixtures stay.

## The description

[templates/contract/contract.md](../templates/contract/contract.md) is the skeleton. Its sections:

- **Interface.** The call, each argument, the result, and what the result depends on. Say what happens with an absent or empty argument.
- **Rules.** The behavior, one bold-labelled paragraph per rule. Define each term the first time. Use tables for case analysis.
- **Decisions to know.** Each choice the contract makes that a reasonable reader could have made differently, marked `cheap` or `hard` to reverse. A person reads the hard ones.
- **Open questions.** Choices not made yet. "None" is a fine answer.
- **Properties.** What holds for every input: pure, no memory, deterministic, declared data access, and any domain property.
- **Not covered.** Inputs the contract does not give a meaning to, and why, such as "the validator rejects these first".
- **Wrong implementations tried.** A table of plausible wrong implementations and the fixture cases that catch each one.

### Keep contracts free of history

A contract holds rules, fixtures, and the table of wrong implementations. It holds no counts, scores, dates, or account of how it was checked. Those go stale with every edit. Put them in the issue.

## Fixtures

- **Written by hand.** A tool may produce a first draft, but a person checks every value, and the committed file is the authority.
- **Each cites its source:** an example in the docs, a reference page, or an ADR, so a reviewer can check it against something trusted.
- **Traps are written out on purpose.** Values a loose reader accepts and a strict one rejects, such as `yes`, `no`, `on`, `0123`, bare dates, `~`, duplicate keys, and absent versus empty.
- **Every case expects something.** A case with an empty list of expected problems passes for an implementation that reports nothing. Keep a test that every case expects an output or at least one problem.
- **A manifest** (`cases.json` or similar) names each case, its inputs, its expected result, and its source.
- **Shared test code**, such as a function that turns fixture data into domain values, lives in one protected place beside the contracts.

## Drafting

1. **An agent drafts all four parts.** Nobody starts from a blank page. The run that drafts a contract does not build the component.
2. **The draft lists wrong implementations.** For each component, a few plausible wrong builds: ignoring a condition, breaking tie order, mutating an input, keeping state between calls. The drafter shows the tests fail each one, and adds fixtures where one slips through. The wrong builds are scratch work and are not committed.
3. **A person reads it** and gives feedback.

## Hardening

For a component with a rich input, such as a file format, the draft is hardened before anyone approves it. The [contract-hardening skill](../skills/contract-hardening/SKILL.md) is the procedure:

1. A fresh agent builds from the contract alone, then writes a hundred or more broken variants. Each variant that passes is a gap.
2. The real build, then the mutation tool. Each survivor is a gap or a proven equivalence.
3. A second independent build from the contract alone. It keeps a list of every place it had to guess.
4. Both builds run on ten thousand or more inputs. Each group of differences is an ambiguity, settled by a sentence and a fixture.

On onboard-kit's file decoder this found about 20 gaps from broken variants, 6 from the mutation tool, and about 12 from the second build and the differential run. It cost about ten agent runs. Use it where the input is large and fiddly. A small component needs only the first two steps.

## Approval

A person approves a contract once, after hardening, so the approval covers what will bind regeneration. The shared rules do not let a project relax this. onboard-kit later let builds start before approval, with the hard decisions listed, and relied on hardening and mutation to find gaps. That variant is not part of Threnos. Adopting it is a change to the shared rules.

## Growing a contract

A contract can grow in increments, such as answer checks, then structure checks, then checks across sections. Each increment is reviewed on its own. The existing component is run against the new tests first, and a different agent from the test author patches it.

## Transitional contracts

Some outputs are temporary, such as a document format the product plans to replace. Mark their contracts transitional, keep them thin, and make sure nothing lasting keys on their output.

## When the builder finds a problem

The builder reads the contract and does not edit it. If it finds a conflict, a gap, or a mistake, it stops and reports it. A person authorizes any contract change, one change at a time.
