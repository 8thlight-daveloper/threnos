# Mutation testing

A mutation tool makes one small change to the built code at a time, such as flipping a comparison or deleting a
statement, and runs the contract tests. A change no test notices is a **survivor**. In this process a survivor measures
the contract, not the code: it is either a gap in the contract or a change that alters no behavior the contract allows.

The tool generates the changes, not the builder, so the builder does not grade itself.

## What a survivor is

| Kind                        | Example                                                                 | Next step                                                                                       |
| --------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Contract gap                | A removed check that no fixture exercises                               | Add a fixture and a contract sentence. A different agent patches the code if the new test fails |
| Equivalent                  | A loop bound that differs only on lists of a length the input never has | Prove it, then a person may accept it                                                           |
| Library detail              | A negative limit the language treats the same as any other negative     | Accept, noting that a rebuild in another language will not produce this mutant                  |
| Outside the supported input | A difference only on input the validator rejects first                  | Check the validation path really rejects it, then state the excluded input                      |
| Product choice              | Two plausible behaviors that serve different goals                      | Ask the [behavior judge](judgment.md), or a person                                              |

A removed guard for an absent value (nil, null, empty) is a gap unless a fixture already passes the absent value in. A
rebuilt component must survive that input even when today's result looks the same.

## Proving a survivor is harmless

Never take "harmless" or "equivalent" on trust. On onboard-kit, three of the first four survivors an agent called
equivalent crashed the component, and a fourth read a quoted value as a different type.

1. Copy everything the tests read into a scratch folder.
1. Run the tests on the unmutated copy. They must pass. A broken copy makes every mutant look killed.
1. Apply the one mutation.
1. Run an input that reaches the changed line, and compare the result with the unmutated copy.

Write the reason in terms of the contract, not the code: which inputs the contract allows, and why none of them can tell
the two versions apart. A person must be able to judge it without reading the implementation. If the only reason is "the
code means the same", look again for an input, in another language or a rebuilt component, that would differ.

## The accepted list

Each component has a list of survivors a person accepted, one per line: a stable key, the file, the change in words, and
why it alters nothing.

```text
# Mutants of <component> that a person checked and accepted.
# Each line: key | file | change | why it alters nothing. Only a person adds a line.
4b1fc81b921f29d7 | tokenprefix.go | the scan resumes two characters after a failed prefix instead of one | A prefix counts only at the start of the text or after a character that is not a letter or digit. ...
```

- **Only a person adds a line.** A builder reports survivors and never edits the list.
- **The key must be stable.** Hash the file name, the mutator, the original and mutated text, and the text of the line.
  The key then survives a line moving, and changes when the line is edited, so an edited line comes back for a fresh
  look. Number identical mutations in source order across the full report, including killed ones, so killing an earlier
  one does not hand its exception to a later one.
- **A rebuild clears the list in effect.** Old keys match nothing in new code.
- **Print survivors in the list's format.** A person then adds a line by copying the tool's output and writing the
  reason.

### Accepting risk in bulk

A long survivor review can block real work. onboard-kit once accepted a batch of 224 survivors across 12 components as
deferred testing risk, by an ADR that delegated the call to the behavior judge for that batch only. The ADR said plainly
that this was not a finding that the mutations were harmless, kept agent and human approval separate in the list, and
did not apply to future survivors. If you do this, write the same limits down.

## Reviewing survivors with a person

Group survivors by kind. Explain each with a concrete input and output, for a reader who has not read the source. A
mutation ID is a lookup reference, not an explanation. The
[survivor review format](../skills/contract-hardening/references/survivor-review.md) is the standard.

## What the wrapper around the tool must do

Most mutation tools need a thin wrapper to fit this process. Whatever the language, it should:

- **Run the component's contract tests,** which often live in another module from the component. Some tools test only
  the mutated module's own tests, and are unusable here.
- **Never change a source file in place.** Build each mutant from an overlay or a copy, so the run can sit beside the
  normal check.
- **Skip mutants that do not compile,** and leave them out of the score.
- **Stop each mutant's test run with its own timeout,** and make sure the test process dies too. A mutant that loops
  forever otherwise leaves a process spinning after the tool gives up.
- **Throttle.** Run one mutant at a time by default, cap the build's parallelism, and run at low priority. Each mutant
  is a build plus a test run, and parallel tools multiply far past the core count.
- **Read the accepted list** and print the remaining survivors in its format.

On onboard-kit an unthrottled comparison of three tools on a 14-core laptop coincided with two kernel panics. Later,
test processes orphaned by looping mutants pushed the load average to 130. Never run two mutation runs at once.

## Tools by language

Candidates, not verified in this collection. Check each against the wrapper list above before choosing.

| Language               | Tool                                                                                                                                           |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Go                     | gomu, used on onboard-kit. go-mutesting skipped struct and map assignments and edits files in place. gremlins ran only the package's own tests |
| JavaScript, TypeScript | Stryker                                                                                                                                        |
| Java, Kotlin           | PIT                                                                                                                                            |
| C#                     | Stryker.NET                                                                                                                                    |
| Python                 | mutmut, cosmic-ray                                                                                                                             |
| Rust                   | cargo-mutants                                                                                                                                  |
