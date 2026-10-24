# 0040. Behavior judgment

Status: proposed

Builds on [0030](0030-contracts-and-tests.md).

## Context

Mutation survivors and contract reviews expose choices about product behavior. Asking a person to settle each one slows work, but letting an agent follow the current code makes an implementation accident into a requirement. We need explicit product principles and a bounded way for an agent to apply them.

The behavior judge is a development workflow. It adds no model call or runtime dependency to the shipped program. Its decisions become deterministic tests.

## Product principles

<!-- Write the project's goal in one sentence, then four to eight principles. Each one says what to prefer and what it does not permit, and is about the people using the product. Examples of shapes that worked: -->

The goal is <who the product serves, and what it saves them>.

### P1. <Prepare what the operator reliably knows>

<What to prefer. What this does not permit.>

### P2. <Respect ownership and deliberate choices>

<A default is a suggestion, not an answer; only a person's explicit acceptance makes it one.>

### P3. <Make the next useful action clear>

<A diagnostic should help a person understand the problem, not merely contain some text.>

### P4. <Preserve work and keep changes local>

<Do not discard data or rewrite unrelated data as a side effect of another action. Prefer explicit, recoverable changes. When two options serve the person equally well, prefer fewer side effects.>

## Decision

Use the behavior judge skill for open product-behavior questions. The principles live here; the skill carries the procedure. Neither an implementation nor a mutation score is product authority.

These principles are not points in a score. Privacy, correctness, ownership, and explicit commitments constrain convenience. Within those constraints, reduce avoidable work and uncertainty, then prefer a smaller and more reversible change. A general principle does not silently supersede a specific accepted decision or resolve a contract conflict.

### Delegated product judgment

An agent may choose a new behavior without another product discussion when:

- It stays within the person's assigned task.
- These principles clearly favor one option without an unresolved tradeoff.
- It is local and practically reversible, with no new privacy, security, ownership, destructive, stored-format, or hash-compatibility consequences.
- It does not contradict an accepted decision, contract, or explicit direction.
- It has an observable acceptance criterion and a valid independent test oracle.

This authority selects a product direction. It does not grant permission to edit protected artifacts, approve tests, or weaken a requirement.

### Escalation

Ask the person when principles conflict, required facts are missing, a valid test cannot be established, the consequences exceed the delegation, or an existing commitment must change. Include a concrete example, a recommendation, alternatives, and the effect on the people using the product.

Do not escalate arithmetic or library claims as product choices. Investigate them as engineering questions.

### Evidence and approval

Record the decision, its governing principles, assumptions, observable scenario, independent expected result, and a wrong behavior the proposed test rejects. Separate these states: decided, test planned, test verified, implemented.

The human approval and independent authorship rules in 0030 remain unchanged. A skill does not approve itself, expand its own authority, or mark a judgment as human approval.

## Consequences

The judge can settle bounded behavior choices and present routine decisions in batches. It must not merely repeat the current code, or find a principle that sounds like an excuse for each survivor. Evaluate it on concrete outcomes and escalation behavior before expanding its authority.
