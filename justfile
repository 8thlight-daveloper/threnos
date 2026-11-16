# Recipes CI and agents call. See process/task-recipes.md.

default:
    @just --list

# Flake checks (records tests, drift, seeds), offline links, and Markdown lint and format.
check:
    nix flake check
    lychee --offline --include-fragments --no-progress "**/*.md"
    markdownlint-cli2 $(git ls-files '*.md')
    mdformat --check $(git ls-files '*.md')
