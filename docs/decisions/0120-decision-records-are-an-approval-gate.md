---
category: regenerative-process
status: proposed
approval: unrecorded
builds-on: ['0050', '0080', '0110']
note: Adds the decisions gate. Records stay out of the approvals ledger.
---

# 0120. Decision records are an approval gate

Builds on [0050](0050-records-and-checked-files.md), [0080](0080-approval-gates-are-settings.md), and
[0110](0110-core-approval-gates-and-the-approvals-ledger.md).

## Context

A decision record's `approval` field says who approved it, and the process says a person approves every record. Nothing
checks either. An agent can write `approval: person` on its own draft, and a project that wants agents to approve
records has no setting for it. [0110](0110-core-approval-gates-and-the-approvals-ledger.md) made the core files gates
with a ledger that binds each approval to a content hash. A record does not fit that ledger, because a record changes
after approval for links and supersession fields, and each change would need a new entry.

## Decision

**Decision records are a gate.** `decisions` joins `[approvals]` in `.threnos/config.toml`. It is a list of `person`,
`agent`, or both, and the default is `["person"]`. The user layer, the empty-list error, and the merge rule of
[0080](0080-approval-gates-are-settings.md) apply.

**The record carries its own approval.** The check applies to a record whose status is `accepted` or `superseded`. Its
`approval` must be `person` or `agent` and must be in the project's list. A record that says `approval: agent` fails
when the project's list is `["person"]`, so a person ratifies it by reading it and changing the field to `person`.

**An agent approval names its parties.** The schema gains two optional fields, `approver` and `author`. Each is
`{kind: person, name}` or `{kind: agent, harness, session}`, as in the ledger. A record with `approval: agent` must have
both, and the approver's `(harness, session)` must differ from the author's, under the `independence` setting of
[0110](0110-core-approval-gates-and-the-approvals-ledger.md). A record with `approval: person` may leave them out.

**`unrecorded` stays valid.** It makes no claim, so the check lets it pass, and it does not count as an approval. A
project adopting the gate keeps its older records as they are. The check prints how many accepted records are
`unrecorded`, so the history stays visible. A new record needs a claim.

**Records stay out of the ledger.** A record has no content hash, so an edit to an accepted record is seen only in
review and not by the check.

**The escalation rules stay.** An agent approval does not widen what an agent may decide alone. A decision with a new
privacy, security, ownership, destructive, stored-format, or hash-compatibility consequence still goes to a person, as
[0040](0040-behavior-judgment.md) says.

## Consequences

- A project can let agents approve records by listing `agent`, and the record says which agent and session did it.
- A person can run hands-off locally with `.threnos/local.toml`. CI uses the project's list, so a person ratifies an
  agent approval before it merges.
- The schema gains `approver` and `author`, and the records check gains the list rule, the party rules, and the
  independence rule. Sync validates `decisions` in `[approvals]`.
- The independence fields are self-reported, so they leave a trail and stop a careless self-approval. They do not prove
  it.
- A record that a person approved can be edited by an agent afterward, and the check will not see it. A code review
  catches it. Binding records to a hash would close this and would cost an entry on every link edit.
- An agent can write `unrecorded` to avoid the claim. The count of unrecorded records makes that visible and does not
  prevent it.

## Alternatives considered

- **Put records in the approvals ledger.** A hash closes the edit gap, but each link or supersession edit would need a
  new entry, and an approval would then say little about the decision itself.
- **Require a person for every record.** It keeps one human gate in every project and blocks a project that chooses full
  automation.
- **Commit trailers.** They record who approved a commit, not which record, and they do not survive a squash.
- **Remove `unrecorded`.** Older records would fail the check for a claim nobody made.
