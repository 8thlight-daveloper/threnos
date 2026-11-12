---
name: independent-approval-review
description: Review a protected unit or decision record as a session that did not write it, and approve it only when the review finds no reason to reject. Use when a gate lists `agent` in `approvals` and an artifact is ready for approval, not to review a PR or to approve one's own work.
---

# Independent approval review

Decide whether a gated artifact should be approved, as an agent that did not write it. The job is to find reasons to
reject. Approve only when none is left.

Use this skill when the gate's list in `.threnos/config.toml` (or `.threnos/local.toml` for this person) holds `agent`.
When it does not, stop and ask a person. When it does, a review under this skill replaces asking a person, except for
the escalations below.

## Start from a separate session

The approver's `(harness, session)` must differ from the author's, and under `independence = "harness"` the harness
must differ too. Do not review work from your own session. Do not invent or reuse a session identifier. If the only
available session is the author's, stop and say so.

Work from what the gate stores, not from the author's account of it:

- **Read:** the artifact as it stands now, and the records it depends on. Those are the product principles, the accepted
  decisions it cites, and the contracts or scenarios on either side of it.
- **Do not read:** the author's summary, rationale, chat, or a message that says the work is ready. If a fact is only in
  that account, it is not in the records, and that is a finding.

## Look for reasons to reject

Go through the artifact for each question below that applies to its gate. Write each finding down with the line or
section it concerns.

| Gate | Ask |
| ---- | --- |
| `contracts` | Can two builds satisfy every rule and still differ in observable behavior? Is any rule unfalsifiable? Does a fixture agree with the rule it illustrates? Does it contradict an accepted decision or principle? |
| `acceptance` | Would a plausible wrong build pass each scenario? Is the expected result computed independently of the code it judges? Does a scenario need behavior no contract states? |
| `architecture` | Does a dependency rule hold up against the components and the decisions it cites? Does it allow what an accepted decision forbids? |
| `model` | Do names and relations match the contracts? Does it add stored state no decision accounts for? |
| `decisions` | Do the context, decision, and alternatives agree with the cited records? Does it change a stored format, ownership, privacy, or security rule without saying so? Is a superseded record still cited as live? |
| `principles` | Does the edit follow from the records it cites? Does it widen what an agent may decide alone? |
| `build` | Does the running program do what the acceptance scenarios and principles say? Run it and use it. Reading the code is not enough. |

Run the checks the project already has (`nix flake check`, the contract tests, the mutation tool) when the gate rests on
them. A passing check is evidence. It does not replace the questions above.

## Escalate, do not approve

Stop and ask a person when the artifact has a new privacy, security, ownership, destructive, stored-format, or
hash-compatibility consequence, when principles conflict, or when it matches an entry in the project's `escalations`
list under `[approvals]`. An approval setting changes who approves a routine change, not what an agent may decide alone.
Report the case with an example, a recommendation, and the alternatives.

## Decide

1. **A finding you cannot answer from the records:** do not approve. Report each finding, the artifact it concerns, and
   what would settle it. Return it to the author's session.
1. **No finding left:** approve, and say what you checked.

Record the approval with `nix run .#approve -- <gate> [unit] --approver agent:<harness>:<session>`. For a decision
record, set `approval: agent` with `approver` and `author`. Never record `person` as the approver, and never write
`approval: person` on a unit no person read. An approval records that the review found nothing. It does not claim the
artifact is correct.

## Report

Keep the report short: the gate and unit, the session you reviewed as, the records you read, the findings or "none",
and whether anything went to a person. Do not praise the work.
