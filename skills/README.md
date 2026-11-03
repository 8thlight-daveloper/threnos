# Skills

Agent skills that carry out parts of the process. Each is a folder with a `SKILL.md` and any files it needs, written with no agent vendor in mind.

## Process skills

These exist because of the regenerative process, and assume its structure.

| Skill | Use it to | Reads |
| -- | -- | -- |
| [behavior-judge](behavior-judge/SKILL.md) | Decide an open product behavior question, or escalate it | The project's behavior judgment ADR |
| [contract-hardening](contract-hardening/SKILL.md) | Remove ambiguity from a contract with broken variants, mutation, a second build, and a differential run | The contract, the mutation tool, the [dump format](contract-hardening/references/dump-format.md) |
| [writing-issues](writing-issues/SKILL.md) | Write, split, and size issues so each is reviewable in one sitting | The issue templates |

## Code and craft skills

General skills the process leans on. They work in any project.

| Skill | Use it to |
| -- | -- |
| [ai-tells](ai-tells/SKILL.md) | Edit prose for clarity, evidence, repetitive phrasing, and unnecessary formatting; the repository's writing reference |
| [comments-review](comments-review/SKILL.md) | Dissolve comments into names, types, shared code, and tests before a commit |
| [wall-of-code-review](wall-of-code-review/SKILL.md) | Split long functions so the caller reads as a table of contents |
| [commit-message](commit-message/SKILL.md) | Write a subject-line commit, with a body only for a why recorded nowhere else |
| [pr-draft](pr-draft/SKILL.md) | Audit branch history and draft a PR using the repository's template and conventions |
| [pr-review](pr-review/SKILL.md) | Review a PR with checked assumptions, test evidence, and paste-ready comments |
| [ux-designer](ux-designer/SKILL.md) | Review and shape an interface, and judge it against the project's interface principles |

## Install into a project

1. Copy each skill folder into the project's `.agents/skills/`. Include `ai-tells` when using the agent instructions template; it supplies the shared writing reference.
2. Link each one into the vendor's discovery folder. For Claude Code:

   ```sh
   mkdir -p .claude/skills
   for skill in .agents/skills/*/; do
     name="$(basename "$skill")"
     ln -s "../../.agents/skills/$name" ".claude/skills/$name"
   done
   ```

3. Name them in the project's `AGENTS.md`, as [the template](../templates/AGENTS.md) does.

Edit the copies in `.agents/skills/`, never the links. To share an improvement across projects, bring it back here.

## Commands the skills assume

The process skills read the check command, the mutation command, and the mutation cadence from the project settings in `AGENTS.md`. The template defaults are `just check`, which runs every check, and `just mutate <component>`, which runs the mutation tool on one component and prints survivors in the accepted list's format. The cadence is `nightly`, where CI runs mutation and agents read the result, or `local`, where agents run it. A project with other commands or a different cadence sets them there, and the skills follow that.
