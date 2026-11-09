# Lessons from onboard-kit

onboard-kit is a Go command-line tool that turns onboarding templates and an organization's answers into a plan and a
document. It was the first project built this way, from 14 October 2026, mostly by agents with one person reviewing.
These notes record what went wrong and what changed because of it. The rules elsewhere in this collection already
include the fixes.

## Contracts

- **The first decoder issue was too big.** It held 89 cases and 94 fixture files in one review. It should have been a
  draft and a hardening pass, each of medium size. The size table in the writing-issues skill came from this.
- **A draft contract had about 38 gaps that tests did not catch.** Broken variants found about 20, the mutation tool 6,
  and a second build with a differential run about 12. Three rounds and about 20,000 inputs brought the differences to
  zero. The hardening skill is that procedure, written down.
- **Contracts that recorded their own scores went stale.** Every edit changed the counts. Now a contract holds rules,
  fixtures, and the wrong-implementations table, and the numbers go in the issue.
- **A case expecting no problems passed for a component that reported nothing.** Every case now expects an output or at
  least one problem, and a test guards it.
- **Pointer printing made false differences.** The default value printer showed memory addresses, so two identical
  results looked different. The difference runner now prints values by reflection and follows pointers.

## Mutation testing

- **"Harmless" survivors were not.** An agent called a batch of decoder survivors harmless. Applying each in a scratch
  copy showed four were not: three crashed on a plain value where a map belonged, and one read a quoted `"true"` as a
  boolean. The person caught that the claim had been repeated before it was checked. "Trust but verify" went into the
  agent instructions the same day.
- **The first tool hid gaps.** It skipped every mutant that assigned to a struct, slice, or map field, so missing deep
  copies went unseen. It also edited source files in place, so it could not run beside the normal check. The replacement
  builds mutants over an overlay.
- **A laptop crashed twice.** An unthrottled comparison of three mutation tools coincided with two kernel panics. Later,
  mutants that looped forever left their test processes spinning after the tool's timeout, and the load average reached
  130\. The fix was a per-mutant test timeout, one mutant at a time, capped build parallelism, and a load guard.
- **Survivor keys were unstable.** Checksums of whole files brought every survivor back on any edit. Keys now hash the
  file, the mutator, the change, and the line text, numbered in order for identical mutations.
- **Review stalled the work.** A backlog of 224 survivors across 12 components blocked application work. An ADR accepted
  the batch as deferred risk, with the limits written down. It is a scoped exception, not a precedent.

## Agents

- **A build agent started from the wrong commit.** The harness made its worktree from the last pushed commit, and the
  contract was still local. Now the person or the lead agent makes the worktree from the local tip.
- **A wait loop never ended.** A background `pgrep -f` matched its own command line, and kept waking the agent with
  repeated reports.
- **Jargon slowed decisions.** Terms like "projection", used in a sense the person did not recognize, cost round trips.
  Docs now define each term with an example the first time, and avoid coined words.

## Process

- **The human gate before each build was dropped.** From the project's sixth day, builds started from a contract's
  listed decisions, each marked cheap or hard to reverse, and hardening and mutation found the gaps. The acceptance
  scenarios stayed the main artifact a person approves.
- **A behavior question kept coming back with every survivor.** Writing the product principles down, and giving a judge
  skill bounded authority to apply them, turned most of those into recorded decisions instead of conversations.
- **Rules kept being restated in several places.** The terminal screen spec described the same "preview before you
  destroy" rule in two confirmation flows, and a third was coming. The plan is to move the rule into an interface
  principles document that the screens link to.
