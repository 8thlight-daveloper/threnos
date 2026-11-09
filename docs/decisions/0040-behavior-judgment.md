---
category: regenerative-process
status: accepted
approval: unrecorded
builds-on: ['0030']
note: Accepted for experimental use, as in onboard-kit 0100. The product principles are not part of this record. Each project writes its own.
---

# 0040. Behavior judgment

Builds on [0030](0030-contracts-and-tests.md).

## Context

Mutation survivors and contract reviews expose choices about product behavior. Asking a person to settle each one slows
work, but letting an agent follow the current code makes an implementation accident into a requirement. We need explicit
product principles and a bounded way for an agent to apply them. The method is the same for every project. The
principles describe one product's people, so each project writes its own, starting from the Threnos template
`templates/product-principles.md`.

The behavior judge is a development workflow. It adds no model call or runtime dependency to the shipped program. Its
decisions become deterministic tests.

## Decision

Use the behavior judge skill for open product-behavior questions. The principles live in the project's own record. The
skill carries the procedure and the delegated authority below, which stay in step with this record. Neither an
implementation nor a mutation score is product authority.

These principles are not points in a score. Privacy, correctness, ownership, and explicit commitments constrain
convenience. Within those constraints, reduce avoidable work and uncertainty, then prefer a smaller and more reversible
change. A general principle does not silently supersede a specific accepted decision or resolve a contract conflict.

### Delegated product judgment

An agent may choose a new behavior without another product discussion when:

- It stays within the person's assigned task.
- These principles clearly favor one option without an unresolved tradeoff.
- It is local and practically reversible, with no new privacy, security, ownership, destructive, stored-format, or
  hash-compatibility consequences.
- It does not contradict an accepted decision, contract, or explicit direction.
- It has an observable acceptance criterion and a valid independent test oracle.

This authority selects a product direction. It does not grant permission to edit protected artifacts, approve tests, or
weaken a requirement. A recorded choice must distinguish product judgment from evidence and implementation.

### Escalation

Ask the person when principles conflict, required facts are missing, a valid test cannot be established, the
consequences exceed the delegation, or an existing commitment must change. Include a concrete example, a recommendation,
alternatives, and the effect on the people using the product.

Do not escalate arithmetic or library claims as product choices. Investigate them as engineering questions. Conversely,
a plausible test does not justify inventing a preferred behavior without product authority.

### Evidence and approval

Record the decision, its governing principles, assumptions, observable scenario, independent expected result, and a
wrong behavior the proposed test rejects. Use a component contract test or a whole-program acceptance scenario according
to the boundary being judged. Separate these states: decided, test planned, test verified, implemented.

The human approval and independent authorship rules in [0030](0030-contracts-and-tests.md) remain unchanged. A person
still approves protected contract and test changes, and still adds accepted-survivor entries after checking the
evidence. A skill does not approve itself, expand its own authority, or mark a trial judgment as human approval.
Contract conflicts are reported, not repaired without authorization.

## Consequences

The judge can settle bounded behavior choices and present routine decisions in batches. It must not merely repeat the
current code, or find a principle that sounds like an excuse for each survivor. Working review records stay in
`output/`. Decisions that contracts or acceptance tests depend on belong in ADRs. Evaluate the judge on concrete
outcomes and escalation behavior before expanding its authority. A passing skill-format check is not proof that its
product judgments are sound.
