# Docs and decisions

Documents change at different speeds, like code. Put each where its speed belongs, so a fast change never has to touch a slow document.

## Four folders

| Folder | Holds | Pace |
| -- | -- | -- |
| `docs/decisions/` | ADRs: what we chose and why | Slowest. A new ADR supersedes an old one |
| `docs/reference/` | Exact definitions of formats, with worked examples | Changes with the format |
| `docs/architecture/` | Views of the current system: components, data flow, sequences, the side effects and data access table | Changes as components change |
| `docs/stack/` | Language and tooling, one file per topic, including the code layout | Fastest |

Only ADRs are numbered. The rest are named for their topic.

## ADRs

- An ADR records a decision that the contracts or acceptance tests depend on.
- Number by tens, so a missed decision can slot in between.
- A status line says proposed, accepted, or superseded, and links the ADR that changed it.
- Write the context, the decision, the consequences, and the alternatives considered. [templates/decisions/adr.md](../templates/decisions/adr.md) is the skeleton.
- The language-specific half of a decision goes in the stack docs, so a change of language leaves the ADR in place.

## Stack docs

The stack docs record language, libraries, and tooling. These are cheap to change, so they live outside ADRs. A stack change that forces a test change is probably an ADR.

Each topic file has three tables: Current, Retired, and Considered and not chosen. To change a row:

1. Record the options you weighed under Considered, with the date and the evidence.
2. Move the old row from Current to Retired, with why it changed.
3. Add the new Current row with a Since date.
4. Run the contract and acceptance suites.

Git holds the diffs. The Retired table holds the reasons.

## Writing rules

Use the [AI-tells writing reference](../skills/ai-tells/SKILL.md) for drafting
and editing prose. In a new project, copy it into `.agents/skills/ai-tells/`
with the other shared skills.

- **Link, do not copy.** A copied paragraph goes stale. Each fact has one home, and everything else links to it.
- **Plain words.** Define a term the first time, with an example. Do not coin words. Keep a glossary.
- **Language-neutral names.** Docs say "section selector", not a package path, unless the doc is about the code layout.
- **No history in rules.** Counts, scores, and dates belong in issues and commit messages, not in contracts or principles.

## Mechanical checks

Use tools, not ad hoc scripts, for what can be checked mechanically: Markdown format, Markdown lint, offline link and anchor checks, and prose rules such as banned words and heading case. Run them in the same check as the tests.

## Scratch and output

Two folders that git ignores:

- `.scratch/` for throwaway notes, drafts, and an agent's own working files.
- `output/` for generated plans, documents, and review records.

Nothing from either is committed. An agent writes nowhere else in the repo unless the task says so.
