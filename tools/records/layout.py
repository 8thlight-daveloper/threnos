"""Folder layout checks that need no parser, only the file system.

`acceptance/` has three folders. `scenarios/` holds the scenarios, `testdata/` holds the files they start from and the
outputs they compare with, and `runner/` holds what runs them in this repository. See process/acceptance.md.
"""
from pathlib import Path

ACCEPTANCE = "acceptance"
FOLDERS = ["scenarios", "testdata", "runner"]
FORMS = ["data", "code"]
SOURCE_SUFFIXES = {".go", ".py", ".rs", ".ts", ".js", ".java", ".rb", ".swift", ".kt", ".c", ".cpp", ".h", ".sh"}
IGNORED = {".DS_Store"}
ALLOWED_FILES = {"README.md"}


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
        if entry.is_file() or entry.name not in FOLDERS:
            problems.append(
                f"{ACCEPTANCE}/{entry.name}: acceptance holds only {', '.join(each + '/' for each in FOLDERS)}. "
                "Scenarios go in scenarios/, their files in testdata/, and what runs them in runner/"
            )
    scenarios, testdata, runner = (base / each for each in FOLDERS)
    for path in files_under(testdata) if testdata.is_dir() else []:
        if is_source(path):
            problems.append(f"{path.relative_to(root).as_posix()}: testdata holds data, not source files")
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
