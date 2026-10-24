# Building a component

A build turns an approved contract into code that passes it. Builds are cheap, so most of the care goes into briefing the builder and checking what it reports.

## The order

1. **Create the component's folder with a stub.** The stub satisfies the interface and returns nothing useful.
2. **Run the contract tests against the stub.** Every test that exercises the output must fail. A property test, such as determinism, may pass against a stub that returns nothing. A test that passes against a stub proves nothing.
3. **Build until the tests pass.**
4. **Run the project's full check.**
5. **Run the mutation tool** on the component, and report each survivor as a contract gap or a candidate equivalence. See [mutation testing](mutation-testing.md).
6. **Report.** The builder lists what it built, the survivors, and any place it found the contract wrong or silent. It does not edit the contract.

## Contracts run only once their component exists

A contract can be approved and merged ahead of its component. The check command includes a contract's tests only when the matching component folder exists. The build turns them on by creating the folder, watches them fail against the stub on its own branch, and merges only when they pass. The main branch is never left red.

## A build touches one folder

A build or rebuild changes only the component's folder. It never edits the contracts, the acceptance scenarios, the dependency rules, or the domain model. If it needs any of those changed, it stops and asks. CI checks the folder scope.

## Delegating a build to an agent

**Workspace.** Give the agent its own working copy, such as a git worktree, made from your local tip. A harness-made worktree may branch from the last pushed commit and miss a contract you committed locally. Tell the agent to confirm the commit it starts from and never to touch the main checkout.

**Brief.** The agent knows only what the brief says.

- The issue, and the files to read in order: the agent instructions, the ADRs on structure and contracts, the domain model, and the contract.
- The one folder it may change.
- What it must never edit: contracts, the domain model, docs, build files.
- The order above: stub red, then green, then the full check, then mutation.
- The exact report it owes: files changed, test results, every survivor with its location and mutation, every contract problem it found.
- No reference implementation. A second build must not see the first.

**Check the report yourself.** Verify its claims against the diff and fresh test runs.

- The diff touches only the component's folder.
- Imports stay within the dependency rules.
- No comments in the code. See the [comments-review skill](../skills/comments-review/SKILL.md).
- Run the tests yourself, several times, with the race detector or its equivalent.
- Run the full check and the mutation tool yourself.

Remove the worktree and delete the branch once the build is merged.

## Rebuilding

1. Open a branch. Delete the component's folder.
2. Regenerate it from its contract, its architecture doc, and the dependency rules.
3. Run the contract tests and the acceptance scenarios.
4. CI checks that the change touched only that folder.

## When to regenerate

Regenerating is cheap, so the question is when it is worth a person's review.

- **A failing test does not call for regeneration.** Patch a local defect in place.
- **Regenerate** when the component's design is inadequate, when the domain model under it changes, or when patches have piled up.
- **A mutation survivor is a contract gap.** The fix goes to the contract's tests or fixtures, approved by a person. The code changes only if the new tests fail against it.
- **A contract change** runs first against the existing component. A different agent from the author of the new tests patches the failures.
- **After a large contract change, regenerate once** from the contract alone. If a second independent build also passes, the contract is enough. Where two builds differ, the contract is ambiguous.
- **A person reviews every regeneration.** Do not regenerate faster than that review can keep up.

## Splitting test and code authorship

| Work | Done by |
| -- | -- |
| Contract draft, fixtures, contract tests | A contract author, human or agent |
| First build | A different agent |
| A fixture that kills a survivor | The contract author |
| The patch that makes the new fixture pass | A different agent from the fixture's author |
| Acceptance scenarios | Anyone except the builder of what they judge. A person approves |
