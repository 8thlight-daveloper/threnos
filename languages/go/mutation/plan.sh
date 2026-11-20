#!/usr/bin/env bash
set -eu
cd "$(git rev-parse --show-toplevel)"

base="${1:-}"
components_dir="${COMPONENTS_DIR:-internal}"
contracts_dir="${CONTRACTS_DIR:-contracts}"
tests_dir="${CONTRACT_TESTS_DIR:-contract-tests}"
model_dir="${MODEL_DIR:-$components_dir/model}"
# The split layout of record 0150 has a specifications folder. The older layout has one folder per contract.
split=false
[ -d "$contracts_dir/specifications" ] && split=true
shared_default="$model_dir go.mod go.sum tools/mutation flake.nix flake.lock justfile .github/workflows/mutate.yml"
[ "$split" = true ] && shared_default="$shared_default $tests_dir/harness"
read -ra shared_paths <<< "${SHARED_PATHS:-$shared_default}"

# The folders that decide a component's results, besides its own source.
suite_paths() {
    if [ "$split" = true ]; then
        echo "$contracts_dir/specifications/$1" "$contracts_dir/fixtures/$1" "$tests_dir/runner/$1" "$tests_dir/wiring/$1"
    else
        echo "$contracts_dir/$1"
    fi
}

has_suite() {
    if [ "$split" = true ]; then
        [ -d "$tests_dir/wiring/$1" ]
    else
        [ -d "$contracts_dir/$1" ]
    fi
}

components() {
    for folder in "$components_dir"/*/ "$components_dir"/*/*/; do
        name="${folder#"$components_dir"/}"
        name="${name%/}"
        has_suite "$name" || continue
        ls "$folder"*.go > /dev/null 2>&1 || continue
        echo "$name"
    done
}

everything() {
    components | jq -R . | jq -sc .
}

if [ -z "$base" ] || ! git cat-file -e "$base^{commit}" 2> /dev/null; then
    everything
    exit 0
fi

shared="$(git diff --name-only "$base" HEAD -- "${shared_paths[@]}")"
if [ -n "$shared" ]; then
    everything
    exit 0
fi

components | while read -r name; do
    read -ra suite <<< "$(suite_paths "$name")"
    if [ -n "$(git diff --name-only "$base" HEAD -- "$components_dir/$name" "${suite[@]}")" ]; then
        echo "$name"
    fi
done | jq -R . | jq -sc .
