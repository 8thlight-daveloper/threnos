# Recipes CI and agents call. See process/task-recipes.md.

default:
    @just --list

# Flake checks (records tests, drift, seeds) and offline links.
check:
    nix flake check
    lychee --offline --include-fragments --no-progress "**/*.md"
