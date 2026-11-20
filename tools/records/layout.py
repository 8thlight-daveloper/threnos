"""Folder layout checks that need no parser, only the file system.

`acceptance/` has three folders. `scenarios/` holds the scenarios, `fixtures/` holds the files they start from and the
outputs they compare with, and `runner/` holds what runs them in this repository. See process/acceptance.md.

Contracts split the same way, as record 0150 says. `contracts/` holds `specifications/` and `fixtures/`, which are
language-neutral. `contract-tests/` holds `runner/`, `wiring/`, and a shared `harness/`, which are language-bound. Each
component with a specification has a path in `specifications/`, `fixtures/`, `runner/`, and `wiring/`.
"""
from pathlib import Path

ACCEPTANCE = "acceptance"
FOLDERS = ["scenarios", "fixtures", "runner"]
FORMS = ["data", "code"]
SOURCE_SUFFIXES = {".go", ".py", ".rs", ".ts", ".js", ".java", ".rb", ".swift", ".kt", ".c", ".cpp", ".h", ".sh"}
IGNORED = {".DS_Store"}
ALLOWED_FILES = {"README.md"}
SPECIFICATIONS = "specifications"
CONTRACT_FOLDERS = [SPECIFICATIONS, "fixtures"]
TEST_FOLDERS = ["runner", "wiring", "harness"]
MIRRORED = [("fixtures", "contracts"), ("runner", "tests"), ("wiring", "tests")]
DATA_SUFFIXES = {
    ".json", ".yaml", ".yml", ".toml", ".csv", ".tsv", ".txt", ".md", ".xml", ".html", ".bin", ".hex", ".golden",
}


def files_under(folder):
    return sorted(each for each in folder.rglob("*") if each.is_file() and each.name not in IGNORED)


def is_source(path):
    return path.suffix in SOURCE_SUFFIXES


DATA_SCENARIO_SUFFIXES = {".yaml", ".yml"}
SAMPLE_SUFFIX = ".example"


def is_sample_or_note(path):
    return path.suffix == SAMPLE_SUFFIX or path.name in ALLOWED_FILES


def is_scenario(path, form):
    """A data scenario is a YAML file. In code form every file that is not a sample or a README is scenario code."""
    if is_sample_or_note(path):
        return False
    return path.suffix in DATA_SCENARIO_SUFFIXES if form == "data" else True


def acceptance_problems(root, architecture):
    """Return problems with the layout of `acceptance/`. A project with no such folder has none."""
    base = Path(root) / ACCEPTANCE
    if not base.is_dir():
        return []
    form = (architecture.get("acceptance") or {}).get("scenarios", "data")
    if form not in FORMS:
        return [f"architecture.yaml: acceptance.scenarios is {form!r}, which is not one of {', '.join(FORMS)}"]
    problems = []
    for entry in sorted(base.iterdir()):
        if entry.name in IGNORED or (entry.is_file() and entry.name in ALLOWED_FILES):
            continue
        if entry.name == "testdata":
            problems.append(f"{ACCEPTANCE}/testdata: record 0150 renames it to fixtures/")
        elif entry.is_file() or entry.name not in FOLDERS:
            problems.append(
                f"{ACCEPTANCE}/{entry.name}: acceptance holds only {', '.join(each + '/' for each in FOLDERS)}. "
                "Scenarios go in scenarios/, their files in fixtures/, and what runs them in runner/"
            )
    scenarios, fixtures, runner = (base / each for each in FOLDERS)
    for path in files_under(fixtures) if fixtures.is_dir() else []:
        if is_source(path):
            problems.append(f"{path.relative_to(root).as_posix()}: fixtures hold data, not source files")
    if form == "data" and scenarios.is_dir():
        for path in files_under(scenarios):
            if not is_sample_or_note(path) and path.suffix not in DATA_SCENARIO_SUFFIXES:
                problems.append(
                    f"{path.relative_to(root).as_posix()}: scenarios are YAML data in this project. "
                    "Put code in runner/, or set acceptance.scenarios to code"
                )
    has_scenarios = scenarios.is_dir() and any(is_scenario(path, form) for path in files_under(scenarios))
    has_runner = runner.is_dir() and any(path.name not in ALLOWED_FILES for path in files_under(runner))
    if has_scenarios and not has_runner:
        problems.append(f"{ACCEPTANCE}/runner: scenarios exist and nothing runs them. Add the runner here")
    return problems


def contract_roots(architecture):
    """Return the folders of the contracts and of the contract tests, from architecture.yaml or the defaults."""
    return (architecture.get("contracts_root") or "contracts", architecture.get("contract_tests_root") or "contract-tests")


def uses_split_layout(root, architecture):
    """True when the project has moved to specifications/ or contract-tests/. Older projects keep one folder per contract."""
    contracts, tests = contract_roots(architecture)
    return (Path(root) / contracts / SPECIFICATIONS).is_dir() or (Path(root) / tests).is_dir()


def specification_ids(root, architecture):
    """Return the component ids that have a contract.md under specifications/."""
    contracts, _ = contract_roots(architecture)
    base = Path(root) / contracts / SPECIFICATIONS
    if not base.is_dir():
        return []
    return sorted(each.parent.relative_to(base).as_posix() for each in base.rglob("contract.md"))


def mirror_folders(root, architecture, component):
    """Return the four folders of one component's contract, specification first."""
    contracts, tests = contract_roots(architecture)
    root = Path(root)
    return [
        root / contracts / SPECIFICATIONS / component,
        root / contracts / "fixtures" / component,
        root / tests / "runner" / component,
        root / tests / "wiring" / component,
    ]


def under_a_component(relative, ids):
    return any(relative == each or relative.startswith(each + "/") for each in ids)


def contracts_problems(root, architecture):
    """Return problems with the layout of the contracts and the contract tests. An older layout has none."""
    if not uses_split_layout(root, architecture):
        return []
    root = Path(root)
    contracts, tests = contract_roots(architecture)
    base, tests_base = root / contracts, root / tests
    problems = []
    for folder, allowed in ((base, CONTRACT_FOLDERS), (tests_base, TEST_FOLDERS)):
        if not folder.is_dir():
            continue
        for entry in sorted(folder.iterdir()):
            if entry.name in IGNORED or (entry.is_file() and entry.name in ALLOWED_FILES):
                continue
            if entry.is_file() or entry.name not in allowed:
                problems.append(
                    f"{entry.relative_to(root).as_posix()}: {folder.name}/ holds only "
                    f"{', '.join(each + '/' for each in allowed)}"
                )
    specifications = base / SPECIFICATIONS
    ids = specification_ids(root, architecture)
    for path in files_under(specifications) if specifications.is_dir() else []:
        relative = path.relative_to(root).as_posix()
        if path.suffix != ".md":
            problems.append(f"{relative}: specifications hold Markdown only")
        elif not under_a_component(path.parent.relative_to(specifications).as_posix(), ids):
            problems.append(f"{relative}: no contract.md in this folder or above it")
    extra = {each if each.startswith(".") else "." + each for each in (architecture.get("contracts") or {}).get("fixture_suffixes") or []}
    for path in files_under(base / "fixtures") if (base / "fixtures").is_dir() else []:
        if path.name not in ALLOWED_FILES and path.suffix not in DATA_SUFFIXES | extra:
            problems.append(
                f"{path.relative_to(root).as_posix()}: fixtures hold data. "
                "Add its suffix to contracts.fixture_suffixes in architecture.yaml if it is a data file"
            )
    for component in ids:
        for folder in mirror_folders(root, architecture, component)[1:]:
            if not folder.is_dir() or not files_under(folder):
                problems.append(f"{folder.relative_to(root).as_posix()}: the contract of {component} has nothing here")
    for name, where in MIRRORED:
        tree = (base if where == "contracts" else tests_base) / name
        orphans = set()
        for path in files_under(tree) if tree.is_dir() else []:
            relative = path.parent.relative_to(tree).as_posix()
            if not under_a_component(relative, ids):
                orphans.add(path.parent.relative_to(root).as_posix())
        for orphan in sorted(orphans):
            problems.append(f"{orphan}: no specification for this component under {contracts}/{SPECIFICATIONS}/")
    return problems
