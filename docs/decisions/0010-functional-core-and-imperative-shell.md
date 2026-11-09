---
category: regenerative-process
status: accepted
approval: unrecorded
note: Generalized from onboard-kit 0015, which is accepted there.
---

# 0010. Functional core and imperative shell

## Context

Components are built to be deleted and regenerated from a contract. Whoever regenerates one, a person or an agent, needs only that component's folder, its contract, and the dependency rules. For that to work, everything a component can do must be visible at its boundary. A component that reads a hidden clock, keeps state between calls, or reaches into a shared object has behavior the contract cannot state and the tests cannot judge.

## Decision

The program is a functional core inside an imperative shell. This is a rule, not a preference.

### The core

Every component except the drivers and the entry point.

- **Values are immutable.** No function alters an argument. A function that needs a different value returns a new one.
- **Functions are pure.** The same inputs give the same output. A function reads nothing but its arguments.
- **No hidden state.** No module-level mutable state, and no state held between calls. State a function needs is passed in, and changed state is returned.
- **No clock, no randomness, no environment.** The caller passes the time in.
- **No input or output.** The core never reads or writes files, the network, or the terminal, and never runs commands.
- **Expected failures are values.** A problem is a returned result. A crash means a bug.

### The shell

The drivers and the entry point. It reads and writes files, reads the clock and the environment, asks the person, shows results, holds the current value, and replaces it with the value the core returns. It writes stored files and documents only after a confirmed action or an explicit command. It holds no rules about the domain. A decision that depends on the content of a value belongs in the core.

### Testing boundaries

Pure components expose their behavior through explicit inputs and outputs.
Their contracts specify that behavior without recreating the operating
environment or tracing shared state. This limits the context an agent needs
to regenerate a component.

Keep effects at explicit boundaries so acceptance scenarios can supply inputs
and observe results through the program's public interface. Control relevant
files, time, randomness, and external-service responses to make scenarios
reproducible. Component contracts check individual responsibilities; acceptance
scenarios check their wiring and promised user-visible behavior. The scenarios
continue to judge the program after an implementation is regenerated.

### Sharing

A returned value may share unchanged parts with its input. Nothing is mutated, so sharing is safe. Where a language cannot guard against mutation, a test enforces the rule, as below.

### Enforcement

- Every contract test snapshots its inputs deeply before the call and compares afterward.
- Every contract test runs each call twice and compares the results byte for byte.
- After any call, every field outside the component's declared set equals the input.
- The dependency check bans the filesystem, network, process, terminal, clock, randomness, and environment categories in core components. The stack docs list the libraries.
- A lint forbids module-level variables that can change.

## Consequences

- A contract can specify a whole component, so a component can be deleted and regenerated against it.
- An agent changing a component reads its folder, its contract, and the dependency rules, and nothing else.
- Pure component tests need no external environment setup and can run in parallel without shared mutable state. Whole-program acceptance tests also exercise the shell and need control over relevant environmental inputs.
- Copies cost memory and time. Revisit if values grow large enough for that to show.

## Alternatives considered

- **A mutable core with discipline.** Cheaper to write. It brings back undo logic and tests that cannot fork, and nothing stops a rebuilt component from reaching through a shared reference.
- **Objects that hold their own state.** Once the value carries all the state, the object adds a name and no behavior, and its hidden state sits outside any contract.
- **A library of immutable data structures.** Real immutability, at the cost of a dependency. Revisit if copying shows up as a cost.
