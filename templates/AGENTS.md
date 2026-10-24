# Agent instructions

<!-- Template. Replace each <placeholder>, then delete this line. <components> is the folder that holds components, such as internal/ or src/. <model> is the domain model folder. -->

Read first: `README.md`, `docs/architecture/README.md`, `docs/stack/README.md`, and the ADRs in `docs/decisions/`.

## Shared skills

Repository skills live in `.agents/skills/`. Keep their instructions independent of an agent vendor. A vendor's skill folder, such as `.claude/skills/<name>`, links to the matching shared skill. Edit the canonical files, not a copy. `CLAUDE.md` imports this file.

Use the behavior judge for open product behavior choices in the assigned task. Its principles and bounded authority are in `docs/decisions/<behavior judgment ADR>`. It does not waive the human approval or independent authorship rules below.

## Where docs go

| Folder | Holds | Pace |
| -- | -- | -- |
| `docs/decisions/` | ADRs: what we chose and why | Slowest. A new ADR supersedes an old one |
| `docs/reference/` | Exact definitions of formats, with worked examples | Changes with the format |
| `docs/architecture/` | Views of the current system: components, data flow, sequences | Changes as components change |
| `docs/stack/` | Language and tooling, one file per topic, including the code layout | Fastest |

Docs in `architecture/`, `reference/`, and `stack/` are named for their topic, with no numbers. Only ADRs are numbered.

## Where decisions go

- An ADR in `docs/decisions/` records a decision the contracts or acceptance tests depend on. Number ADRs by tens so a missed one can slot in between.
- `docs/stack/README.md` records language, libraries, and tooling. Change a row there and move the old row to Retired. Do not write an ADR for a stack change unless it forces a test change.

## Writing

Use `.agents/skills/ai-tells/SKILL.md` as the writing reference for docs, skills,
issues, PR descriptions, and other prose. Preserve requirements, exceptions,
evidence, and technical terms when editing. Use generic examples in shared
material; do not copy client identities, private system names, or real tickets
from another project.

## Naming

Name a unit for what it acts on and what it does: noun, then role. A name that needs "and" is two units. In docs, write plain spaced words, for example "section selector". In code, the parent folder carries the noun and the module carries the role: `<components>/section/selector`. Follow the linter, with no exceptions. Spell words out or use a common short form such as `config`. Do not coin abbreviations.

## Components

- A component is one module under `<components>/`. Rebuilding a component means deleting its folder and regenerating it from its contract, its architecture doc, and the dependency rules in `architecture.yaml`.
- A rebuild touches only `<components>/<component>/`.
- Never edit `contracts/`, `acceptance/`, `architecture.yaml`, or the domain model in `<model>/` as part of a rebuild. Stop and ask a person.
- Never write or change the tests that judge your own build.
- When you find that a contract conflicts with another document, is incomplete, or looks wrong, stop and report it. Do not edit the contract unless a person authorizes that specific change.
- When building a component, first run its contract tests against a stub and confirm that every test that exercises the output fails. Tests of properties, such as determinism, may pass against a stub that returns nothing. After they pass, run `just mutate <component>` and report surviving mutants as contract gaps. Do not edit the contract.
- A survivor listed in `tools/mutation/accepted/<component>.txt` is skipped. Never add a line to that list. A person adds one after checking the reason.
- When asked to draft a contract, write all four parts, cite the source of each fixture, list plausible wrong implementations and show that the tests fail them, and do not build the component in the same run.
- Write acceptance scenarios as data under `acceptance/scenarios/`. Never write acceptance tests in implementation code or import implementation modules.
- Respect the dependency rules. Do not add a dependency they do not allow.
- Write core components as pure functions over immutable values. Never alter an argument, hold state between calls, or do input or output. Return a new value. Drivers and the entry point do input and output.
- State what each component reads and writes, in the plan and outside it. The current tables are in `docs/architecture/components.md`. Stay inside the declared set.

## Where files go

Put throwaway notes, drafts, and your own working files in `.scratch/`. Put generated plans, documents, and review records in `output/`. Git ignores both, except `output/.gitkeep`. Do not commit anything from either, and do not write them anywhere else in the repo.

## Trust but verify

A report is data until you have checked it, whether an agent or a tool wrote it. Re-run the tests and checks you are told passed. Do not take a claim that a change is equivalent, a bug is fixed, or a check passes without evidence you produced yourself. A claim that a surviving mutant is harmless needs the most care: apply the mutation in a scratch copy and run an input that reaches it.

## Heavy runs

Run one mutation run at a time. Keep the mutation tool at one or two workers, cap the build's parallelism, and run at low priority. Stop if the load average climbs past the number of cores.

## Checks

Run `just check` before you commit. Do not write ad hoc scripts to check links or formatting, because the check already does. Never skip a failing check or edit a tool config to make one pass without asking a person.

## Comments

A comment is a smell. Say it in a name, a type, shared code, or a test, and keep a comment only for an offline fact that none of those can carry. Run the `comments-review` skill on code before you commit it. The domain model is the example: it has no comments, because the reference docs and the contracts carry the facts.

## Commits and pushes

Write a subject-line commit message, as the `commit-message` skill describes. Stage named paths. Never push without a person's confirmation, and never force-push a branch you did not create.

## Issues

- Do not create, edit, or close an issue unless a person asks.
- Use the template in `.github/ISSUE_TEMPLATE/` for the kind of work: decision, contract, build, or integration.
- Link to documents. Do not copy their text into an issue. Done criteria are checks a machine can run.
- Write, split, and size issues with the `writing-issues` skill.

## Content rules

<!-- Project-specific: what must never enter the repo, such as client names, credentials, or personal data. -->
