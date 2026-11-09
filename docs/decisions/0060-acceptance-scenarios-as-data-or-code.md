---
category: regenerative-process
status: accepted
approval: person
builds-on: ['0020', '0030']
partly-supersedes: ['0030']
note: Replaces the rule in 0030 that scenarios are data. The other rules in 0030 stay.
---

# 0060. Acceptance scenarios as data or as code

Builds on [0020](0020-structure-and-regenerative-components.md) and [0030](0030-contracts-and-tests.md). It replaces the
part of 0030 that says scenarios are data.

## Context

Acceptance scenarios judge the whole built program from outside, and they must outlast every rebuild of a component. The
format is a means to that end. Data makes the guarantee mechanical, because a YAML file cannot import anything. Some
programs cannot be driven that way. A terminal interface needs a terminal emulator, a screen check, and timing, and a
scenario written as code can do that where a data format would need a large runner.

The first project to need this wrote its scenarios in Go. One test file imported a single implementation package for a
version constant. A reviewer who checked only non-test imports missed it. Discipline alone does not hold the boundary.

## Decision

A project chooses one form for its scenarios and records it in `architecture.yaml` as `acceptance.scenarios`: `data` or
`code`. The default is `data`.

Whichever form it chooses:

- A scenario drives the built program from outside: it starts the program, supplies arguments, input, and files, and
  checks the exit code, the standard streams, the files written, or the screen.
- A scenario imports no implementation module. The constants it needs come from the built program, such as its version
  output, or from a fixture.
- `architecture.yaml` lists in `acceptance.may_import` what scenario code may import. The list holds test libraries and
  runner helpers, and never a package of the project's own implementation. The dependency check reads the imports and
  reports each violation with the import that proves it, as it does for contracts.
- The scenarios, their fixtures, and the runner and helper code are protected like a contract. A person approves every
  change to them.

Data scenarios stay the default because they keep working if the language changes. Code scenarios survive component
rebuilds and the regeneration of the whole implementation in the same language. They do not survive a change of
language, and a project that chooses them accepts that.

## Consequences

- A project with an interactive or terminal interface can judge it through the real screen, without a large data format.
- The boundary is mechanical in both forms, so a reviewer does not have to read imports.
- A language change costs a rewrite of code scenarios. Data scenarios need only a new runner.

## Alternatives considered

- **Data only.** The strongest guarantee. It cannot drive a terminal emulator without a runner as large as the program.
- **Code on trust.** Cheapest to adopt. A single imported constant shows that review alone misses the boundary.
