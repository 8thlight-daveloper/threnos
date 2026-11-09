# Working with agents

Agents do most of the drafting and building. The process gives them small, fixed context and checks their work by
evidence rather than by their account of it.

## One instructions file, any vendor

- `AGENTS.md` at the repo root holds the project's settings and its own rules.
  [templates/AGENTS.md](../templates/AGENTS.md) is a starting version.
- The shared rules live in `.agents/rules/regenerative.md`, a read-only copy of
  [rules/regenerative.md](../rules/regenerative.md). A project may add rules in `AGENTS.md` and may not relax the shared
  ones. Only a person changes the shared copy, by taking a new version.
- A vendor-specific file imports both rather than repeating them. For Claude Code, `CLAUDE.md` holds the two lines
  `@AGENTS.md` and `@.agents/rules/regenerative.md`.
- Skills live in `.agents/skills/<name>/`, written with no vendor in mind. A vendor's discovery path, such as
  `.claude/skills/<name>`, is a symlink to the shared folder. Edit the shared files, never a copy.
- `AGENTS.md` lists the documents to read first: the README, the architecture and stack overviews, and the ADRs.

## Small context by design

A rebuild needs the component's contract, its architecture doc, the dependency rules, and the domain model. Nothing
else. The functional core makes that true: with no hidden state, there is nothing else to trace. If an agent needs to
read three other components to change one, the boundary is wrong.

## Retrieve focused repository context

Use local Repowise to find relevant modules, inspect dependencies, and assess change impact before broad source reads.
Sync seeds the [setup and usage guide](../templates/repowise.md) to `docs/stack/repowise.md` in a new project. A project
that is not ready for Repowise sets `repository_context = "off"` under `[rules]` in `.agents/threnos.toml`. Sync then
leaves this rule and the guide out, and setting it back to `on` restores both. Use the open-source engine with model
calls and external embeddings disabled. Read maintained ADRs and contracts directly, check index freshness, and verify
consequential claims against the source and tests. Use targeted search if the index is unavailable.

The full index is for coordinators and ordinary development or review. An independent regeneration builder must not
retrieve an old or reference implementation, including summaries, call flows, and history. Its brief contains only the
permitted specifications and dependency interfaces. Restrict retrieval to those sources or leave the full index
disconnected from that builder.

## Briefs

A delegated agent starts with nothing but the brief. Write it like a handover to a capable colleague:

- The goal and the issue.
- The files to read, in order.
- The one folder it may change, and what it must never touch.
- The order of work, such as stub red, then green, then the full check, then mutation.
- The report it owes, item by item.
- What has already been ruled out.

[building.md](building.md#delegating-a-build-to-an-agent) has the build brief in full.

## Reports are data

An agent's report is a claim. Before acting on it:

- Re-run the tests and checks it says passed.
- Read the diff, at least its scope and its imports.
- For an "equivalent" or "harmless" survivor, apply the mutation yourself and run an input that reaches it. See
  [mutation testing](mutation-testing.md#proving-a-survivor-is-harmless).
- Show a person the evidence before anything is recorded as accepted.

An agent asked to confirm a hypothesis tends to confirm it. Give a verifying agent the code and the question, not your
conclusion.

## Code style that helps regeneration

- **No comments.** A comment is a smell. Say it in a name, a type, shared code, or a test. Keep a comment only for a
  fact that none of those can carry, such as an upstream quirk. Run the
  [comments-review skill](../skills/comments-review/SKILL.md) before committing.
- **Functions read as a table of contents.** The [wall-of-code-review skill](../skills/wall-of-code-review/SKILL.md)
  finds long functions to split.
- **Follow the linter, with no exceptions.**

Keep lasting facts in docs and contracts so deleting code does not delete its specification.

## Commits and pushes

- Subject line only by default. See the [commit-message skill](../skills/commit-message/SKILL.md).
- Stage named paths, not everything.
- Never skip the pre-commit check.
- An agent never pushes without explicit confirmation, and never force-pushes a branch it did not create.

## Pitfalls seen in practice

- **Worktree base.** A harness-made worktree may start from the last pushed commit, not your local tip. Make the
  worktree yourself from `HEAD` when the work depends on local commits.
- **Self-matching waits.** A background loop that waits with `pgrep -f <pattern>` matches its own command line and never
  ends. Wait on a process id, or on an output file.
- **Copy semantics.** `rsync -a ./ dest/` copies the folder's contents. `rsync -a . dest/` and `rsync -a .. dest/`
  behave differently, and a mistake nests a copy inside the destination. Check with `ls` and `diff -rq`.
- **Heavy runs.** Tell every agent that runs mutation or many tests to throttle. See
  [mutation testing](mutation-testing.md#what-the-wrapper-around-the-tool-must-do).
- **Agents in parallel on one checkout.** Two agents editing one working tree collide. Give each its own worktree, or
  say which files each may touch.
