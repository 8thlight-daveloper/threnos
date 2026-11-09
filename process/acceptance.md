# Acceptance scenarios

Component contracts check individual responsibilities. Acceptance scenarios check that those responsibilities are wired
together correctly and produce the promised user-visible behavior. They judge the whole program from outside and are the
lasting statement of what it does. They are few, high level, and approved by a person.

## Explicit I/O boundaries

Keep effects at explicit boundaries so acceptance scenarios can supply inputs and observe results through the program's
public interface. Control relevant environmental inputs, including files, time, randomness, and external-service
responses, so scenarios are reproducible. The same scenarios should continue to judge the program after an
implementation is regenerated.

A pure core makes component tests straightforward. Whole-program acceptance tests also exercise the shell, so they still
need environment setup and control over relevant external dependencies.

## Scenarios are data

A scenario is one file. It names the files a run starts with, the arguments and input it sends, and what must be true
afterward: the exit code, the output, and the files written. It never imports the implementation, so it keeps working if
the language changes.

```yaml
name: assemble-example
description: The example plan assembles into the same document each time.
source: docs/reference/examples/example/README.md
steps:
  - run: [program, assemble, --plan, plan.yaml]
    files:
      plan.yaml: {from: docs/reference/examples/example/plan.yaml}
    expect:
      exit: 0
      files:
        out.md: {same-as: docs/reference/examples/example/out.md}
```

`source` says where the expectation comes from, so a person can check the scenario against something trusted.
[templates/acceptance/](../templates/acceptance/README.md) has the full format.

## A protocol mode makes scenarios cheap

An interactive program is hard to drive from a scenario. Give it a mode that reads requests on standard input and writes
responses on standard output, one JSON object per line. A scenario then sends requests and checks each response. The
same mode serves tests and other tools.

## The runner is replaceable

A small program reads the scenarios, starts the built program, and compares results. It is the only language-specific
part. It holds no knowledge of the product, and the scenario format is its whole contract. You can replace it, or run a
second one in another language, without touching a scenario.

The scenario format is protected like the scenarios, because the runner and every scenario depend on it. Matching rules
belong to the format.

## Compare JSON by subset

An expected object matches when every key it names is present and matches. Extra keys are fine, and key order does not
matter. Lists must match in length and order. A scenario then says only what it cares about, so an added field does not
break it.

## Rules

- Each scenario gets its own temporary folder.
- Scenarios do not depend on each other, and may run in parallel.
- Each step has a time limit.
- Paths stay inside their root: no `..` and no absolute paths.
- An unknown field in a scenario is an error.
- Golden outputs regenerate only by an explicit command, never as a side effect of a test.

## What a scenario should not do

- Assert on internals. Only arguments, standard streams, exit code, and files.
- Duplicate a contract. A scenario proves the wiring and the user-visible behavior. The edge cases belong in contracts.
- Key on a transitional output that the product plans to retire.
