---
category: regenerative-process
status: proposed
approval: unrecorded
builds-on: ['0040', '0050', '0070', '0080']
partly-supersedes: ['0040']
note: Replaces the part of 0040 that has each project write its principles as a record. The method in 0040 stays.
---

# 0090. Product principles live in a file

Builds on [0040](0040-behavior-judgment.md), [0050](0050-records-and-checked-files.md),
[0070](0070-settings-live-in-settings-files.md), and [0080](0080-approval-gates-are-settings.md). It replaces the part of
0040 that has each project write its principles as a decision record.

## Context

A behavior judgment needs the project's principles. When the principles are one record, later records amend them, such
as a record that sharpens one principle. An agent that judges must then read the principles record and every record that
amends it, and decide which wording wins. An agent that skips an amendment makes a confident wrong call. Projects using
the method already show this: one holds its principles in the method record and amends them through later records, and
another holds them in one record that cites the records it came from.

## Decision

**The principles live in one file that is edited in place.** The default path is `docs/reference/product-principles.md`.
The `AGENTS.md` pointer for product principles names it. The behavior judge reads this file and does not aggregate
records.

**Each principle has a label, what to prefer, what it does not permit, and the records it comes from.** The records stay
the source of truth for what was decided and why. The file holds the current wording and points back to them. It also
holds a short list of known tensions between principles, so an agent knows which cases to escalate, and a "last
reviewed" date.

**A change to the file is an approval gate.** The gate is `principles` in `[approvals]`, as in
[0080](0080-approval-gates-are-settings.md). The behavior judge may propose an edit when a ruling generalizes. It may
make the edit only when the setting lists `agent`, and it marks the change as an agent approval.

**The checker keeps the file honest.**

- Every record a principle cites exists.
- A cited record that is superseded fails the check until the principle is updated.
- A `behavior` record is cited by a principle, or its front matter says `principle: none`. The field forces a decision on
  whether a new behavior adds a principle.

**Threnos ships a skeleton and no principles.** The skeleton moves from a record template to a file template. A person
writes the first version, because a placeholder could pass for real principles.

## Consequences

- The judge reads one file of known size and does not reconcile amendments.
- A project holds principles in one place that a person can review, and in the records that justify them.
- The file can be wrong where a record changed and the file did not. The checker catches a cited record that is
  superseded, but not a record whose text changed in place. A review of the file covers that.
- `templates/product-principles.md` becomes a file template. `behavior-judge`, `templates/AGENTS.md`, the README, and
  the schema doc change. The schema gains the `principle` field.
- A project with its principles in a record, such as an existing project, moves them into the file and cites the record.

## Alternatives considered

- **Keep the principles as a record and amend by new records.** Each amendment is a clear decision, but the judge reads
  many records, and a skipped one gives a wrong call.
- **Generate the file from the records.** No drift, but principles are curated wording, and a generator needs a field on
  every record that says what it contributes.
- **Put principles in the method record, as 0040 first did in one project.** The method and one product's principles
  then change together, and a second project cannot share the method.
