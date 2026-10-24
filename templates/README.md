# Templates

Starting files for a new project. Copy them, replace each `<placeholder>`, and change what does not fit. Once copied they belong to the project, so they do not link back here.

| File | Goes to | Is |
| -- | -- | -- |
| [AGENTS.md](AGENTS.md) | Repo root | The instructions every agent reads |
| [CLAUDE.md](CLAUDE.md) | Repo root | One line that imports `AGENTS.md` for Claude Code |
| [architecture.yaml](architecture.yaml) | Repo root | The dependency rules, as data |
| [decisions/](decisions/) | `docs/decisions/` | The ADR skeleton and four starting ADRs: functional core, structure, contracts and tests, behavior judgment |
| [contract/](contract/) | `contracts/<noun>/<role>/` | A contract description and a fixture manifest |
| [acceptance/](acceptance/README.md) | `docs/reference/` and `acceptance/scenarios/` | The scenario format and two example scenarios |
| [issues/](issues/) | `.github/ISSUE_TEMPLATE/` | Decision, contract, build, and integration issues |
| [accepted-survivors.txt](accepted-survivors.txt) | `tools/mutation/accepted/<component>.txt` | The header of a component's accepted survivor list |
| [stack-topic.md](stack-topic.md) | `docs/stack/<topic>.md` | A stack topic with Current, Retired, and Considered tables |

## Order

1. `AGENTS.md`, `CLAUDE.md`, and the skills.
2. ADRs 0010 to 0040. Write the product principles in 0040 before the first survivor review, not after.
3. `docs/stack/code-layout.md` from a [language mapping](../languages/README.md).
4. `architecture.yaml` with the first components.
5. The scenario format, then the first scenario.
6. The domain model, then the first contract.
