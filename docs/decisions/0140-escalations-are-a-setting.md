---
category: regenerative-process
status: accepted
approval: person
builds-on: ['0040', '0080', '0110', '0120']
note: Makes the cases that go to a person a list a project can extend. Adds a review procedure for an agent that approves, and a model axis to independence.
---

# 0140. Escalations are a setting

Builds on [0040](0040-behavior-judgment.md), [0080](0080-approval-gates-are-settings.md),
[0110](0110-core-approval-gates-and-the-approvals-ledger.md), and
[0120](0120-decision-records-are-an-approval-gate.md).

## Context

Each gate in `[approvals]` lists who may approve it. [0080](0080-approval-gates-are-settings.md),
[0110](0110-core-approval-gates-and-the-approvals-ledger.md), and
[0120](0120-decision-records-are-an-approval-gate.md) each add that a new privacy, security, ownership, destructive,
stored-format, or hash-compatibility consequence still goes to a person. That list lives in prose, in three records and
the shared rules. A project cannot add to it. A project with its own stops, such as a push, an edit to its settings, or a
new dependency, keeps them in `AGENTS.md`, where no check reads them and no setting says they outrank a gate.

Two things are also missing for a project that lists `agent` on its gates. The rules say an agent approves only when its
gate lists `agent`, and say nothing about how the approver reviews, so an approval can be a rubber stamp from a session
that happened to differ from the author's. `independence` also cannot tell two sessions of the same model from two
different models, and a reviewer that shares the author's model shares its blind spots. They also do not say whether an agent should pause to ask a person when its
gate allows an agent, so each project writes that down itself.

## Decision

**Escalations are a list in `[approvals]`.** `escalations` in `.threnos/config.toml` holds sentences, each naming a case
that goes to a person.

```toml
[approvals]
contracts = ["person", "agent"]
escalations = [
  "A push to a remote.",
  "An edit to .threnos/config.toml.",
  "A new dependency.",
]
```

- **The built-in cases always apply.** They are the six in [0040](0040-behavior-judgment.md), and a conflict between
  principles. `escalations` adds to them and cannot remove one.
- **The key is project-only.** A user file that sets it is an error, as for any key that shapes shared files. A person
  can hand-approve anything locally, so a user layer would only be a way to remove a stop.
- **The default is an empty list.** A project that sets nothing changes nothing.
- **Sync validates the shape.** The value must be a list of non-empty strings.
- **The list does not depend on the gate.** A listed case goes to a person whichever gate the work passes, and whoever
  the gate allows to approve.

**A listed case is a stop for an agent, not a check.** The text is natural language. No check can tell whether an edit
matches "a new dependency". An agent that meets a listed case stops and asks a person, and a person reading the change
in review is the check, as for the built-in cases.

**An agent approves without asking when its gate lists `agent`.** When `approvals.<gate>` lists `agent`, the agent does
not stop to ask a person for that routine approval. It gets a review from a session that did not write the artifact,
using the `independent-approval-review` skill, and approves only when that review leaves no finding it cannot answer. It
stops when the case is built in or listed under `escalations`. When the gate lists only `person`, the agent stops, as
today.

**Model is a separate axis.** `independence` keeps its values, `session` and `harness`. A harness can run several
models and a model can run in several harnesses, so a `model` value would overlap `harness`. The approver and author
identities of [0110](0110-core-approval-gates-and-the-approvals-ledger.md) and
[0120](0120-decision-records-are-an-approval-gate.md) gain an optional `model` field on an agent, such as
`{kind: agent, harness, session, model}`. A new setting, `independence_model`, is `"off"` by default or `"differ"`.

```toml
[approvals]
independence = "session"
independence_model = "differ"
```

- **Under `"differ"`, an agent approval must name a model on both parties, and the two must differ.** A missing model
  fails the check, so a project cannot turn the rule on and then leave it unmet.
- **A different vendor is the strongest case.** A different model id from the same vendor is weaker, because the models
  may share training data and habits. The check compares ids as strings and cannot tell the two cases apart. The
  documentation says so, and a project that cares about vendor names its vendors in review.
- **The value is self-reported,** like a session identifier. It leaves a trail and stops a careless same-model approval.
  It does not prove which model ran.
- **A person approver is unaffected,** as under `independence`.
- **The key is project-only,** for the same reason as `escalations`.

**Per-gate lists stay.** This decision adds no stance setting. The gate lists already carry who may approve each gate,
and a global value would override that detail.

**The review procedure is a skill.** `independent-approval-review` says what the reviewing session reads, what it looks
for at each gate, and when it approves. The reviewer reads the artifact and the records it depends on, not the author's
reasoning, and goes in looking for a reason to reject.

## Consequences

- A project moves its own stops out of prose in `AGENTS.md` into a setting that sync validates and the rules cite.
- A project that lists `agent` gets a stated default and a stated review. It no longer writes its own.
- The identity schema gains `model`, and the records checker gains the model rule. Sync validates `independence_model`.
  The decision record front matter template and `rules/regenerative.md` document the field.
- The independence rule is still self-reported, and the review's quality is not checkable. A weak review passes the
  check the same as a strong one. The mutation tool, the second independent build, and the human step on a running
  build of [0110](0110-core-approval-gates-and-the-approvals-ledger.md) still carry the weight there.
- A listed case is only as reliable as the agent's reading of it. A narrow, concrete sentence works better than a broad
  one.
- The shared rules and the sync tool need edits once this is accepted: the `Approvals` section of
  `rules/regenerative.md` states the default and cites the skill, and sync validates `escalations`. The skill alone
  works without them, so it can ship first.
- Projects that already carry an approvals section in `AGENTS.md` can reduce it to a pointer and a list.

## Alternatives considered

- **A `stance = "agent-first"` setting.** It repeats what a gate's list already says, and a project-wide value would
  override the gate-by-gate choice. The behavior it names is stated here as the meaning of listing `agent`.
- **A `model` value for `independence`.** It would read as a stricter step above `harness`, and it is not one. A project
  may run one harness with several models, or one model across harnesses, so the two axes need separate settings.
- **A record of each review.** It helps only when something evaluates review quality, and nothing does yet. Scoring a
  reviewer on artifacts with known defects, as the wrong-implementation variants of
  [0030](0030-contracts-and-tests.md) do for tests, is the better test if quality becomes a worry.
- **A per-gate escalation list.** A stop that matters for one gate usually matters for all of them, and a second matrix
  is harder to read than one list.
- **Let the user layer add or remove entries.** Adding is harmless, and removing defeats the list. A person who wants
  extra stops can say so in a request.
- **Structured entries with machine matching.** A pattern on file paths could be checked, but the interesting cases,
  such as a new privacy consequence, have no pattern. A mix of checked and unchecked entries would imply that unchecked
  ones are safe.
- **Leave the stops in each project's `AGENTS.md`.** It works today and forces each project to restate the built-in
  cases and say how they relate to the gates.
