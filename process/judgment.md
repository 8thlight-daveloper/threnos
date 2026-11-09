# Principles and judges

Mutation survivors, contract reviews, and feature design keep raising small product questions. Should an empty list and
an absent list mean the same thing? Should removing an item also clear what refers to it? Asking a person each time
slows the work. Letting an agent follow the current code turns an accident into a requirement.

Write the principles down and give a skill bounded authority to apply them.

## A principles document

One document holds the project's principles for a kind of judgment. It is an ADR, so it changes slowly and deliberately.
Each principle has a short label, such as P4, so a decision can cite it.

A good principle:

- States what to prefer and what it does not permit. "Prefer explicit, recoverable changes" also needs "this does not
  impose one absent or empty rule on every component".
- Is about the people using the product, not about the code.
- Can be cited in a test plan. A principle that no test could ever reflect is a slogan.

Principles are not points in a score. Privacy, correctness, ownership, and explicit commitments constrain convenience. A
general principle never silently overrides a specific accepted decision.

[ADR 0040](../docs/decisions/0040-behavior-judgment.md) holds the authority rules.
[templates/product-principles.md](../templates/product-principles.md) is a starting record for the principles, which
each project writes itself.

## A judge applies them

The [behavior judge skill](../skills/behavior-judge/SKILL.md) reads the principles document and decides open behavior
questions. It may choose a behavior without another discussion only when:

- The choice is inside the assigned task.
- The principles clearly favor one option.
- The choice is local and reversible, with no new privacy, security, ownership, destructive, stored-format, or
  hash-compatibility consequence.
- It contradicts no accepted decision, contract, or explicit direction.
- It has an observable acceptance criterion and an independent test.

Otherwise it escalates with a concrete example, a recommendation, the alternatives, and the effect on the people using
the product.

Every judgment records the decision, the principles it rests on, its assumptions, an observable scenario, the expected
result, and a wrong behavior the test must reject. It keeps four states apart: decided, test planned, test verified,
implemented.

## A judge never edits its own standard

The judge reads the principles. It does not change them, expand its own authority, or mark its own judgment as a
person's approval. A person changes the principles document. The same holds for any skill that judges against a
document.

## More than one kind of principle

onboard-kit is adding a second principles document for its interface: how the program shows things, as opposed to what
it may do to data. It covers focus and emphasis, colour that never carries meaning alone, keys, and previews before
destructive actions. The [ux-designer skill](../skills/ux-designer/SKILL.md) is to propose changes to it and judge
screens against it, and a person approves changes.

Keep each rule in one home. A behavior rule ("side effects on other data are computed before commit") belongs in the
behavior principles. Its presentation ("show a dry run, confirm with a deliberate key") belongs in the interface
principles, which cite the behavior rule rather than repeat it. Screen specs link to the rules they apply.

## Decisions that came from this

Examples of the kind of question the principles settle, from onboard-kit's ADRs:

- **Defaults are suggestions.** A template default is never an answer until a person accepts it, following "respect
  deliberate choices". Code never fills one in silently.
- **Reject ambiguity.** Two definitions of the same thing are an error, not "first one wins", because choosing changes
  what the data means.
- **Equivalence is engineering, not product.** Whether a changed allocation size alters output is checked by running it,
  not decided by principle.
