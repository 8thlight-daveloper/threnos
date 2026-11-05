# Contributing

Thanks for helping improve Threnos. This page says what to check before you open a pull request. Be kind to each other.

Threnos holds process docs, shared rules, skills, templates, a flake, and a Go mutation adapter. For a change to the
process, the shared rules, or what a skill tells an agent to do, open an issue first so we can agree on the approach.
Fixes to wording, links, and examples can go straight to a pull request.

## Keep clients and employers out

Shared material must not depend on any client or employer. Before you commit, check each change against these rules:

- No client or organization names, including in examples. Use placeholders such as `<Organization>` and `<Team>`.
- No real URLs, repo names, or tool tenants beyond this project's own. Use `<link to ...>`.
- No names of people at an organization. Use roles: "the tech lead", "the reviewer".
- No credentials, tokens, or anything from a contract.
- No figures, dates, or outcomes from a real engagement.

If a lesson only makes sense with a private system's details attached, state the general pattern and leave the details
out.

## Use your GitHub noreply address

This repository is public, and a commit carries its author's email forever. Turn on "Keep my email addresses private" in
your GitHub email settings. Then set `git config user.email` to the `<id>+<username>@users.noreply.github.com` address
GitHub shows there. Never commit with a work or personal address.

## Writing style

[skills/ai-tells/SKILL.md](skills/ai-tells/SKILL.md) is the writing reference for docs, skills, rules, and review text.
When you edit prose, keep the technical meaning, requirements, exceptions, evidence, and approval boundaries.

- Plain words, short sentences, and active voice.
- Imperative for steps: "Run `nix run .#sync`."
- Sentence case headings.
- Examples are fictional. A reader should not need to know any company to follow one.

## Set up and check your work

`nix develop` gives everyone the same tools, including `markdownlint-cli2`, `mdformat`, and `lychee`. Run these before
you push:

- `nix flake check --all-systems` checks that the flake evaluates and the scaffold resolves its skill manifest.
- `lychee --offline --include-fragments "**/*.md"` checks that relative links and anchors resolve.
- `markdownlint-cli2 <files>` checks Markdown rules, with lines wrapped at 120 columns.
- `mdformat --check <files>` checks Markdown formatting, wrapped at 120 columns.

Run the last two on the files you change. Many existing docs do not pass them yet, so do not reformat a file you are not
otherwise changing. Match the configs in `.markdownlint-cli2.jsonc` and `.mdformat.toml` in the files you write.

To test a flake change from a project's side, scaffold a project in a scratch directory and sync it against your
checkout:

```sh
mkdir /tmp/try && cd /tmp/try
nix flake init -t path:<your checkout>
nix run --override-input threnos path:<your checkout> path:.#sync
nix flake check --override-input threnos path:<your checkout> path:.
```

`languages/go/mutation/gomurun` is a Go package with no module of its own here. To run its tests, copy it into a Go
project, or into a scratch directory with a `go.mod`.

## Where files go

- `.scratch/` is for working files and drafts. Git ignores it.
- `output/` is for generated documents and review records. Git ignores it.
- Never commit what is in either folder.

## How the repository is organized

[README.md](README.md#what-is-here) lists the folders. Three things to know before you change one:

- A change to `rules/regenerative.md` or to a skill reaches every project that syncs. Say in the pull request what
  behavior changes for an agent.
- Edit a skill in `skills/`, never in a project's `.agents/skills/`. A skill is a folder with a `SKILL.md`, written with
  no agent vendor in mind.
- A new skill needs a row in [skills/README.md](skills/README.md). If the shared rules name it, add
  `citedByRules = true` for it in [skills/manifest.toml](skills/manifest.toml). If it cannot work without another skill,
  list that skill under `requires`.

## Commits and pull requests

- Write a subject-line commit message, as the [commit-message](skills/commit-message/SKILL.md) skill describes. Add a
  body only for a reason that no doc or issue records.
- Stage named paths, and keep one change per commit.
- Run the [comments-review](skills/comments-review/SKILL.md) skill on code you add. A comment is a smell here.
- The [pr-draft](skills/pr-draft/SKILL.md) skill audits a branch's history and drafts the pull request description.
- Never force-push a branch you did not create.
