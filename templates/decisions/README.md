# Decisions

Each file here is one decision record: what the project chose and why. A new record supersedes an old one, so records
are not rewritten.

## Write a record

1. Copy `docs/reference/templates/adr.md` to `docs/decisions/<NNNN>-<name>.md`. Number records by tens, so a missed
   decision can slot in between.
1. Fill in the front matter. `docs/reference/decision-record-front-matter.md` holds the fields, the categories, and the
   checks. `nix flake check` runs those checks.
1. Link the records and contracts that depend on it. Put language and tooling details in `docs/stack/`, not here.

## First record

Write the product principles first, from `docs/reference/templates/product-principles.md`. The behavior judge skill
reads them to decide open product questions, and it stops when the project has none. Name the file in the "Product
principles" row of the document pointers in `AGENTS.md`. A person writes and approves it before the first mutation
survivor review.

## Not here

The method decisions behind this process are Threnos's own and are not copied into a project. The shared rules in
`.agents/rules/regenerative.md` hold what an agent needs from them.
