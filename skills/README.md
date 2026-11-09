# Skills

Agent skills that carry out parts of the process. Each is a folder with a `SKILL.md` and any files it needs, written
with no agent vendor in mind.

## Process skills

These exist because of the regenerative process, and assume its structure.

| Skill                                             | Use it to                                                                                               | Reads                                                                                            |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| [behavior-judge](behavior-judge/SKILL.md)         | Decide an open product behavior question, or escalate it                                                | The project's product principles record                                                          |
| [contract-hardening](contract-hardening/SKILL.md) | Remove ambiguity from a contract with broken variants, mutation, a second build, and a differential run | The contract, the mutation tool, the [dump format](contract-hardening/references/dump-format.md) |
| [writing-issues](writing-issues/SKILL.md)         | Write, split, and size issues so each is reviewable in one sitting                                      | The issue templates                                                                              |

## Code and craft skills

General skills the process leans on. They work in any project.

| Skill                                               | Use it to                                                                                                             |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| [ai-tells](ai-tells/SKILL.md)                       | Edit prose for clarity, evidence, repetitive phrasing, and unnecessary formatting; the repository's writing reference |
| [comments-review](comments-review/SKILL.md)         | Dissolve comments into names, types, shared code, and tests before a commit                                           |
| [wall-of-code-review](wall-of-code-review/SKILL.md) | Split long functions so the caller reads as a table of contents                                                       |
| [commit-message](commit-message/SKILL.md)           | Write a subject-line commit, with a body only for a why recorded nowhere else                                         |
| [pr-draft](pr-draft/SKILL.md)                       | Audit branch history and draft a PR using the repository's template and conventions                                   |
| [pr-review](pr-review/SKILL.md)                     | Review a PR with checked assumptions, test evidence, and paste-ready comments                                         |
| [ux-designer](ux-designer/SKILL.md)                 | Review and shape an interface, and judge it against the project's interface principles                                |

## Install into a project

With Nix, a project takes the skills through its flake. [scaffold/](../scaffold/) is the starting flake.
`nix run .#sync` installs each skill into `.agents/skills/` read-only, links it from `.claude/skills/`, and removes any
the project turned off. `nix flake check` fails when an installed file differs from Threnos, or when the justfile lacks
a recipe the project lists. A flake in a Git repository sees only tracked files, so run `git add .agents .claude` after
sync and before the check. Until then the drift check fails on the new files.

The project's `.agents/threnos.toml` sets each skill to one of three states:

| State     | Sync does                                         | Use it when                                                                       |
| --------- | ------------------------------------------------- | --------------------------------------------------------------------------------- |
| `on`      | Installs the skill read-only and keeps it current | The skill fits as written. This is the default                                    |
| `off`     | Removes the skill, so the project has none        | The skill does not apply. Disabled means absent, which works for any agent vendor |
| `ejected` | Leaves the files alone and stops owning them      | The project needs a different policy and will edit its own copy                   |

`manifest.toml` in this folder records what the flake knows about each skill. Turning off a skill that another present
skill `requires` is refused. Turning off a skill the shared rules name is a warning. Sync also refuses to overwrite a
file that exists, differs, and was not installed by sync, so a project with its own copy sets it to `ejected` first.

Edit a skill here, never in a project's `.agents/skills/`. To change one for a single project, eject it.

### Without Nix

1. Copy each skill folder into the project's `.agents/skills/`. Include `ai-tells`; it supplies the shared writing
   reference.

1. Link each one into the vendor's discovery folder. For Claude Code:

   ```sh
   mkdir -p .claude/skills
   for skill in .agents/skills/*/; do
     name="$(basename "$skill")"
     ln -s "../../.agents/skills/$name" ".claude/skills/$name"
   done
   ```

1. Copy [rules/regenerative.md](../rules/regenerative.md) to `.agents/rules/` and
   [templates/AGENTS.md](../templates/AGENTS.md) to the repo root.

## Commands the skills assume

The process skills use the fixed recipe names from [task recipes](../process/task-recipes.md): `just check`, which runs
every check, and `just mutate <component>`, which runs the mutation tool on one component and prints survivors in the
accepted list's format. They read `rules.mutation_cadence` in `.agents/threnos.toml`. The cadence is `nightly`, where CI
runs mutation and agents read the result, or `local`, where agents run it. Sync validates the value.
