# Issues

An issue is one unit of work a person can review in one sitting and accept or reject. What the person reviews is a
contract, a scenario, or a decision, not code. The [writing-issues skill](../skills/writing-issues/SKILL.md) has the
full rules, the size table, and a checklist.

## Four kinds

| Kind        | Settles                                          | Ends when                                                                             | Template                                             |
| ----------- | ------------------------------------------------ | ------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Decision    | One question                                     | The answer is in an ADR, a doc, or a stack row, and a person accepted it              | [decision.md](../templates/issues/decision.md)       |
| Contract    | One component's contract, or one increment of it | All four parts exist, wrong implementations were tried, a person approved             | [contract.md](../templates/issues/contract.md)       |
| Build       | One component, once                              | Tests failed against a stub, then passed. Survivors reported. Only the folder changed | [build.md](../templates/issues/build.md)             |
| Integration | Wiring components into the program               | Named scenarios pass. No component's folder changed                                   | [integration.md](../templates/issues/integration.md) |

## The short version

- One verb and one noun in the title. A title that needs "and" is two issues.
- Cut on a seam: a verb, a component, a contract increment, a stage, a scenario, a document.
- Size by what a person reviews: XS, S, or M. L means split it. XL is an epic.
- Done criteria are checks a machine can run, five at most.
- Link, do not copy.
- Name the sibling that takes the next slice.
- A rebuild after a contract change is not its own issue. It is a criterion on the contract change.
- A change to an ADR, the domain model, or the dependency rules gets a `slow-change` label, whatever its size.
