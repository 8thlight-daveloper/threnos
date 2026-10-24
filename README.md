# Regenerative software

A working process for building software that an agent or a person can delete and rebuild, one component at a time, without losing what the software is supposed to do.

Status: draft. It describes the process used on onboard-kit, a Go command-line tool, from October 2026. It has been used on one project, in one language. Treat every rule as a starting point.

## The idea

Code is cheap to write now, and cheap to throw away. What is expensive is knowing what correct means. So the process keeps that knowledge in a few small, slow-changing artifacts and treats the code as disposable.

| Permanent, changed deliberately | Disposable, rebuilt freely |
| -- | -- |
| Decisions (ADRs) | Each component's code |
| The domain model: the types components pass to each other | Unit tests inside a component |
| Contracts: one per component, with fixtures and tests | |
| Acceptance scenarios: the whole program, from outside, as data | |
| Dependency rules, as data | |

A component is rebuilt by deleting its folder and regenerating it from its contract. A person reviews the rebuild by reading test results, not code. That only works when the contract can tell a right implementation from a wrong one, so most of the process is about making contracts strong and keeping their authors honest.

The idea comes from Chad Fowler's [Regenerative Software](https://aicoding.leaflet.pub/3majnyfydzs2y): interfaces, behavior, and evaluations are permanent, and implementations are replaceable. The rate-of-change model borrows Stewart Brand's pace layers.

## What is here

| Folder | Holds |
| -- | -- |
| [process/](process/README.md) | The process, one topic per file, in the order you meet it |
| [skills/](skills/README.md) | Agent skills that carry out parts of the process, vendor-neutral |
| [templates/](templates/README.md) | Starting files for a new project: `AGENTS.md`, a contract, a scenario, ADRs, issue templates, the dependency rules |
| [languages/](languages/README.md) | How the neutral structure maps to a language. Go is worked out; others are candidates |

## Start a project

1. Read [principles](process/principles.md), [structure](process/structure.md), and the proposed [decomposition guidance](process/decomposition.md).
2. Copy [templates/AGENTS.md](templates/AGENTS.md) to the new repo and fill in the placeholders.
3. Copy the skills you want into `.agents/skills/`, including the [writing reference](skills/ai-tells/SKILL.md), as [skills/README.md](skills/README.md) describes.
4. Write the first ADRs: the functional core, the structure, and contracts and tests. [templates/decisions/](templates/decisions/) has starting versions.
5. Pick a language mapping from [languages/](languages/README.md), and record it in the project's stack docs.
6. Write the domain model, then the first contract, then build against it. [The lifecycle](process/README.md) gives the order.

## When it pays off

The process costs more up front than a single tree of code. It pays when:

- Agents write most of the code, and you want to bound the debt one bad run can add.
- Components have rich inputs, such as a file format, where a rebuild could quietly read things differently.
- The project will outlive its first implementation, or its first language.

It does not pay for a throwaway script, or for code whose correctness is mostly visual. Those are better judged by a person using them.
