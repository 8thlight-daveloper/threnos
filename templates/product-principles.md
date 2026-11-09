---
category: behavior
status: proposed
approval: unrecorded
affects: []
builds-on: []
---

# <NNNN>. Product principles

<!-- Goes to docs/decisions/. The behavior judge skill reads it. A person writes and approves it before the first survivor review. The delegated authority is in the behavior judge skill. -->

## Context

<Who the product serves, and what the work costs them today. Name the questions that keep coming up and that the code alone cannot answer.>

## Decision

The goal is <who the product serves, and what it saves them>.

Each principle has a short label so a decision can cite it. Write four to eight. Each says what to prefer and what it does not permit, and is about the people using the product.

### P1. <Prepare what the operator reliably knows>

<What to prefer. What this does not permit.>

### P2. <Respect ownership and deliberate choices>

<A default is a suggestion, not an answer. Only a person's explicit acceptance makes it one.>

### P3. <Make the next useful action clear>

<A diagnostic should help a person understand the problem, not merely contain some text.>

### P4. <Preserve work and keep changes local>

<Do not discard data or rewrite unrelated data as a side effect of another action. Prefer explicit, recoverable changes. When two options serve the person equally well, prefer fewer side effects.>

### P5. <Match protection to the threat you have>

<Name the threats this stage faces. Keep cheap protection against them. Record each deferral in an ADR so it can return. An agent does not defer a protection without a person's approval.>

### P6. <Ask for information precise enough for the decision>

<Prefer an observed event or a clearly labeled proxy to another question. Close enough is not permission to guess, silently accept a default, hide ambiguity, or relax safety or authorization.>

These principles are not points in a score. Privacy, correctness, ownership, and explicit commitments constrain convenience. Within those constraints, reduce avoidable work and uncertainty, then prefer a smaller and more reversible change.

## Consequences

- <Which kinds of decisions the judge may now settle without asking, and which it still escalates.>

## Alternatives considered

- **<Option>.** <What it would cost, and why not.>
