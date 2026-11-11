---
category: regenerative-process
status: accepted
approval: person
builds-on: ['0080', '0110']
partly-supersedes: ['0080']
note: Replaces the part of 0080 that makes every user-file key except approvals project-only, and its rejection of a global file.
---

# 0130. User identity lives in the user's own settings

Builds on [0080](0080-approval-gates-are-settings.md) and [0110](0110-core-approval-gates-and-the-approvals-ledger.md).
It replaces the part of 0080 that lets the user file set only `[approvals]` and rejects a global file.

## Context

A person who approves a gate with `nix run .#approve` types their name each time. A default would help, but a default
that an agent can use is worse than none: the ledger and the decisions gate exist to need a human, and a silent `person`
entry would remove that. The tool must also never read an email address or another contact detail to find a name.

[0080](0080-approval-gates-are-settings.md) rejected a global user file because a global approvals list would apply one
project's choice to every project. A person's name is not such a choice. It describes the person, who has the same name
in most projects.

## Decision

**A person's name is a user setting.** `[identity]` with `name` is set in one of two files, and neither is committed:

- `.threnos/local.toml`, for one person in one project. It already exists and is gitignored.
- A global file, `$XDG_CONFIG_HOME/threnos/config.toml`, or `~/.config/threnos/config.toml` when that variable is unset,
  for the person in every project.

The global file holds `[identity]` only. `[approvals]` stays per project, because whether an agent may approve is a
decision about one project. An unknown key in either file is an error. A project's `config.toml` may not set `identity`,
since the name belongs to a person and not to the project.

**`approve` resolves the approver in this order:**

1. `--approver`, which always wins. A person passes `person:<name>`, and an agent passes `agent:<harness>:<session>`.
1. `identity.name` in `.threnos/local.toml`.
1. `identity.name` in the global file.
1. Otherwise it asks "Your name:".

**A default applies only at a terminal.** When `--approver` is missing and standard input is a terminal, `approve`
resolves a name by steps 2 to 4 and asks "Approve <gate> <unit> as <name>? [y/N]". Anything but `y` or `yes` writes
nothing. When standard input is not a terminal, it refuses and says to pass `--approver`. An agent's shell is not a
terminal, so an agent cannot take the default by accident. It still records an agent approval by passing its own harness
and session.

**A name is a plain label.** The tool never reads an email address, `git config`, or the environment for a name, and
writes only what the person set or typed. The ledger records the label as given.

## Consequences

- A person sets a name once in the global file and approves with a confirmation. A person with a different handle in one
  project overrides it in that project's `local.toml`.
- The guard stops an accident. It does not stop a deliberate false claim. An agent can pass `--approver person:<name>`
  today and still can. An agent could also allocate a pseudo-terminal and answer the prompt. The name is self-reported,
  as [0110](0110-core-approval-gates-and-the-approvals-ledger.md) says, and a person reading the ledger in review is the
  check.
- Sync and the checker validate `identity` in both user files and reject it in the project file. The global file is read
  at sync time, from outside the repository.
- The global file is a third settings location. It holds one key and has no merge rule, so a value's source stays clear.

## Alternatives considered

- **The local part of `git config user.email`.** It needs no setup, and it reads a contact detail into a committed file.
- **`git config user.name`.** It often has spaces and is set for other purposes.
- **Always require `--approver`.** It is the safest and keeps the typing the peer asked to remove.
- **A global file that also holds `approvals`.** It would apply one project's choice to every project and hide where a
  value came from.
- **Default without a terminal check.** An agent's shell would then record `person` silently.
