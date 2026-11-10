# Principles

Each rule in the other files follows from one of these. When a rule seems wrong for a case, come back here and ask which
principle it serves.

## The contract outlives the code

A component is defined by its contract: a plain description, fixtures, tests, and an interface. The code is one way to
satisfy it. If a choice is left open in the contract, the next rebuild may make it differently, and nothing will notice.
So an ambiguity in a contract is a defect, even when today's code happens to behave well.

## Things change at different speeds

| Rate    | What lives there                   | What a change takes                             |
| ------- | ---------------------------------- | ----------------------------------------------- |
| Slowest | Decisions, stored file formats     | A new ADR. Saved data exists in the wild        |
| Slow    | The domain model                   | An ADR, because it is the file format in memory |
| Medium  | Contracts and acceptance scenarios | A person approves                               |
| Fast    | Component code                     | Rebuilt freely inside its folder                |
| Fastest | Content, configuration             | Normal authoring and review                     |

A dependency points from a faster thing to a slower thing, never the other way. A slow thing that depends on a fast
thing breaks whenever the fast thing changes.

## Functional core, imperative shell

Every component except the drivers and the entry point is a pure function over immutable values.

- It never alters an argument. It returns a new value.
- It reads nothing but its arguments. No clock, no randomness, no environment. The caller passes the time in.
- It holds no state between calls.
- It does no input or output.
- An expected failure is a returned value. A crash means a bug.

Pure components expose their behavior through explicit inputs and outputs. Their contracts can specify that behavior
without recreating the operating environment or tracing shared state. This also limits the context an agent needs to
regenerate a component. The contract, relevant decisions, declared dependency interfaces, and shared domain types supply
the behavior it must preserve.

The shell, meaning the drivers and the entry point, reads files, asks the person, holds the current value, and writes
results. It holds no rules about the domain.

## Tests judge a rebuild only if someone else wrote them

The agent that builds or patches a component does not write or edit that component's contract tests, fixtures, or
acceptance scenarios. If one agent writes both, a shared misunderstanding passes every test, because the tests were
written to fit the code.

## Check whether the contract detects wrong behavior

Two checks show whether a contract can tell right from wrong, and both are run by something other than the builder:

- A **mutation tool** makes small changes to the built code. A change that no test notices is a gap in the contract.
- A **second independent build** from the contract alone, run on thousands of inputs beside the first, shows where two
  careful readers disagree. Each difference is an ambiguity.

## Trust but verify

A report is data until you have checked it, whether an agent, a tool, or your own earlier summary wrote it. Re-run the
tests you are told passed. A claim that a change is equivalent, a bug is fixed, or a survivor is harmless needs evidence
you produced yourself. Of the first four survivors an agent called harmless on onboard-kit, three crashed the component
when someone actually ran an input that reached them.

## Deterministic tests, not evals

Contract and acceptance tests are ordinary deterministic tests. "Eval" is reserved for checks a model judges. If the
product runs no model, its checks have none either.

## Settings live in settings files

A value that a tool or an agent reads as a setting goes in a file that a check can validate, and in one place. Program
shape is in `architecture.yaml`. How a project takes Threnos is in `.threnos/config.toml`. `AGENTS.md` holds pointers to
documents that a person chooses, and no value a tool needs. A setting that follows from another is derived, not written
twice. A table in prose cannot be checked, so it drifts.

## Rules without ceremony

Keep process work proportional to its contribution to rebuildability. Defer what has no work yet. A failing test does
not force a regeneration. A small component skips the expensive hardening steps. When a rule costs more than the risk it
covers, say so and change the rule in the ADR that holds it.
