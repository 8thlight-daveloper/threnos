---
category: regenerative-process
status: accepted
approval: person
builds-on: ['0040', '0050', '0070']
note: Starts with the principles gate. The gates on contracts, acceptance scenarios, and architecture.yaml stay fixed.
---

# 0080. Approval gates are settings

Builds on [0040](0040-behavior-judgment.md), [0050](0050-records-and-checked-files.md), and
[0070](0070-settings-live-in-settings-files.md).

## Context

The method says a person approves certain changes. Some projects and some people want to run with fewer stops, or none.
A fixed rule forces a choice between a process that blocks automation and a process that drops human review. A team may
also want its default to be review while one member works hands-off on their own branch.

The ADR `approval` field already says who approved: `person`, `agent`, or `unrecorded`. What is missing is a setting for
who may approve, and a check that holds the project's policy at the point where work merges.

## Decision

**An approval gate is a setting that lists who may approve.** The list holds `person`, `agent`, or both. A gate is named
in `.threnos/config.toml` under `[approvals]`.

```toml
[approvals]
principles = ["person"]
```

- The default for every gate is `["person"]`. A project opts into `agent` on purpose.
- `["person", "agent"]` lets either approve. `["agent"]` lets only an agent approve, and sync warns.
- An empty list is an error. It would mean nobody can approve.

**The gated file shows who approved.** A change that passes a gate is recorded with `approval: person` or
`approval: agent` in the file's front matter, next to a `reviewed` date. The checker fails when that `approval` is not
in the list for its gate. The principles file is the only gated file today.

**A person has a user layer.** `.threnos/local.toml` is gitignored and holds one person's settings for their own
checkout. Sync reads it after the project file.

- A setting names the layers that may set it. `[approvals]` may be set by either. Everything else in `config.toml` is
  project-only, because it shapes shared files. A project-only key in the user file is an error.
- The user file's list replaces the project's list for that person. Lists do not merge.
- CI does not have the user file, so CI judges every gated file against the project list. Sync validates both files and
  writes `.threnos/.gitignore`, so the user file stays out of Git.

**Project policy holds at merge.** A person may run hands-off on their branch with `["agent"]` and produce
`approval: agent` edits. When the project's list is `["person"]`, the checker fails the file until a person reads the
edits and sets `approval: person` in review.

**A setting changes who approves, not what an agent may decide alone.** The escalation rules in the behavior judge stay
in force: a new privacy, security, ownership, destructive, stored-format, or hash-compatibility consequence, and a
conflict between principles, still go to a person. Agent approvals are labeled as agent approvals, never as human
approval.

**The core gates stay fixed.** Approval of contracts, acceptance scenarios, `architecture.yaml`, and the domain model
stays with a person. [0030](0030-contracts-and-tests.md) and [0060](0060-acceptance-scenarios-as-data-or-code.md) rest
on an independent check of the tests that judge a build. Making those gates configurable needs its own record.

## Consequences

- A project chooses its own level of review, and the choice is a file a check can read.
- A person can work hands-off without changing project policy. The merge check keeps the team's default.
- `config.toml` gains an `[approvals]` table, a second file layer, and a rule for which keys a user may set.
- The records checker gains a rule on `approval` against the gate list. A local `just check` fails on an agent edit
  until a person ratifies it, because the check never reads the user file.
- Sync writes `.threnos/.gitignore` with the user file's name.
- Only the principles gate exists. A new gate needs a name, a place in the rules, and a check.

## Alternatives considered

- **A single `automated` switch.** Simple, but it removes review from every gate at once, including the core gates.
- **Project layer only.** A team that wants review by default blocks a member who wants to run unattended, or the whole
  team gives up review.
- **A global user file in `~/.config`.** It adds a third layer, and a value's source gets harder to see. It can be added
  later.
- **Let the user layer win at merge.** The team's policy would depend on each person's local file, which no one else can
  see.
