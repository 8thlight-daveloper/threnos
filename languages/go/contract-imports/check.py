"""Check that a Go project's contract tests import only what their role allows.

Usage: check.py [project root]

Reads `contract_tests_root`, `components_root`, `model`, and `contracts.may_import` from architecture.yaml, and the
imports of every package under the contract tests folder, test files included, from `go list`. A package's role is its
first folder under the contract tests folder: `runner`, `wiring`, or `harness`. Record 0150 sets the rules.

- A runner or harness package imports the standard library, the model, the harness, and the libraries in
  `contracts.may_import`.
- A wiring package imports the standard library, its own component, and its own runner, and nothing else.

An import of any other package in the project's module is a violation, and so is an import of a third-party package that
is not listed. A component that imports the contract tests is reported by the dependency check, not here. Exits 1 on a
violation.

An entry in `may_import` is an import path. It also allows the packages below it.
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROLES = ["runner", "wiring", "harness"]


def stdlib(path):
    return "." not in path.split("/")[0]


def under(path, base):
    return path == base or path.startswith(base.rstrip("/") + "/")


def is_standard(path, module):
    return path in ("C", "unsafe") or (stdlib(path) and not under(path, module))


def listed(path, may_import):
    return any(under(path, entry) for entry in may_import)


def role_of(directory, tests_root):
    """Return (role, component) for a package folder under the tests root, or (None, None)."""
    parts = Path(directory).relative_to(tests_root).parts
    if not parts or parts[0] not in ROLES:
        return None, None
    return parts[0], "/".join(parts[1:])


def allowed(path, role, component, module, rules):
    if is_standard(path, module):
        return True
    own = module + "/"
    inside = {
        "model": own + rules["model"],
        "harness": f"{own}{rules['tests_root']}/harness",
        "component": f"{own}{rules['components_root']}/{component}",
        "runner": f"{own}{rules['tests_root']}/runner/{component}",
    }
    if role == "wiring":
        return under(path, inside["component"]) or path == inside["runner"]
    if under(path, inside["model"]) or under(path, inside["harness"]):
        return True
    return listed(path, rules["may_import"])


def violations(packages, module, rules):
    """Return (package folder, import path) for each import its role does not allow.

    packages maps a package folder, relative to the project root, to the set of its import paths. rules holds
    tests_root, components_root, model, and may_import.
    """
    found = []
    for directory, imports in sorted(packages.items()):
        role, component = role_of(directory, rules["tests_root"])
        if role is None:
            found += [(directory, path) for path in sorted(imports) if not is_standard(path, module)]
            continue
        for path in sorted(imports):
            if not allowed(path, role, component, module, rules):
                found.append((directory, path))
    return found


def go_packages(root, tests_root):
    """Return {package folder: imports} for the real packages under the contract tests folder, tests included."""
    run = subprocess.run(
        ["go", "list", "-e", "-json", "-test", f"./{tests_root}/..."],
        cwd=root, capture_output=True, text=True,
    )
    if run.returncode != 0:
        raise SystemExit(f"go list failed:\n{run.stderr}")
    packages, decoder, text, position = {}, json.JSONDecoder(), run.stdout, 0
    while True:
        text_left = text[position:].lstrip()
        if not text_left:
            break
        position = len(text) - len(text_left)
        package, end = decoder.raw_decode(text, position)
        position = end
        if package.get("ForTest") or package["ImportPath"].endswith(".test"):
            continue
        imports = set(package.get("Imports") or []) | set(package.get("TestImports") or []) | set(package.get("XTestImports") or [])
        directory = Path(package["Dir"]).relative_to(root.resolve()).as_posix()
        packages.setdefault(directory, set()).update(imports)
    return packages


def rules_from(architecture):
    return {
        "tests_root": architecture.get("contract_tests_root") or "contract-tests",
        "components_root": (architecture.get("components_root") or "internal").strip("/"),
        "model": (architecture.get("model") or "internal/model").strip("/"),
        "may_import": (architecture.get("contracts") or {}).get("may_import") or [],
    }


def main(args):
    root = Path(args[0] if args else ".").resolve()
    architecture = yaml.safe_load((root / "architecture.yaml").read_text()) or {}
    rules = rules_from(architecture)
    if not (root / rules["tests_root"]).is_dir():
        print(f"no {rules['tests_root']}/ folder, so there is nothing to check")
        return 0
    module = subprocess.run(["go", "list", "-m"], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
    found = violations(go_packages(root, rules["tests_root"]), module, rules)
    for directory, path in found:
        print(f"{directory}: imports {path}, which its role in {rules['tests_root']}/ does not allow", file=sys.stderr)
    if found:
        return 1
    print(f"{rules['tests_root']} imports are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
