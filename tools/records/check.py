"""Check a project's decision records against the front matter schema.

Usage: check.py [-v] [--framework] [project root]

The schema is templates/decision-record-front-matter.md. Exits 1 when a check
fails. Notes are printed only with -v. A project must have an architecture.yaml.
--framework is for Threnos itself, which holds records but is not a project, and skips that requirement.
"""
import re
import sys
from pathlib import Path

import yaml

DECISIONS = "docs/decisions"
CATEGORIES = ["architecture", "behavior", "ux", "regenerative-process", "operations"]
STATUSES = ["proposed", "accepted", "superseded", "withdrawn"]
APPROVALS = ["person", "agent", "unrecorded"]
PRODUCT_REQUIRED = ["behavior", "ux"]
PRODUCT_ALLOWED = ["architecture", "behavior", "ux"]
FIELDS = {
    "category", "status", "approval", "note", "affects", "builds-on",
    "supersedes", "superseded-by", "partly-supersedes", "partly-superseded-by",
}
LINK_FIELDS = ["builds-on", "supersedes", "superseded-by", "partly-supersedes", "partly-superseded-by"]
REVERSE = {
    "supersedes": "superseded-by",
    "superseded-by": "supersedes",
    "partly-supersedes": "partly-superseded-by",
    "partly-superseded-by": "partly-supersedes",
}
RECORD_FILE = re.compile(r"^(\d{4})-.+\.md$")
CITATION = re.compile(r"\[(\d{4})\]|decisions/(\d{4})-|\bADRs? (\d{4})\b")


class Record:
    def __init__(self, number, file, heading, front):
        self.number = number
        self.file = file
        self.heading = heading
        self.front = front

    def list_of(self, field):
        return [str(each) for each in (self.front.get(field) or [])]

    @property
    def has_affects(self):
        return "affects" in self.front


def parse_record(number, file, text):
    if not text.startswith("---\n"):
        return None, f"{file}: no front matter"
    block, closed, body = text[4:].partition("\n---\n")
    if not closed:
        return None, f"{file}: front matter is not closed"
    try:
        front = yaml.safe_load(block) or {}
    except yaml.YAMLError as error:
        return None, f"{file}: front matter: {error}"
    if not isinstance(front, dict):
        return None, f"{file}: front matter is not a mapping"
    unknown = sorted(set(front) - FIELDS)
    if unknown:
        return None, f"{file}: front matter has unknown fields: {', '.join(unknown)}"
    heading = next((line for line in body.split("\n") if line.startswith("# ")), "")
    return Record(number, file, heading, front), None


def load_records(root):
    folder = root / DECISIONS
    if not folder.is_dir():
        return [], []
    records, problems = [], []
    for path in sorted(folder.iterdir()):
        match = RECORD_FILE.match(path.name)
        if not match:
            continue
        record, problem = parse_record(match.group(1), path.name, path.read_text())
        if problem:
            problems.append(problem)
        else:
            records.append(record)
    return records, problems


def load_architecture(root):
    path = root / "architecture.yaml"
    if not path.is_file():
        return None, "contracts"
    data = yaml.safe_load(path.read_text()) or {}
    components = data.get("components") or []
    if isinstance(components, dict):
        ids = set(components)
    else:
        ids = {each["name"] for each in components if isinstance(each, dict) and "name" in each}
    return ids, data.get("contracts_root") or "contracts"


def load_contracts(root, contracts_root):
    base = root / contracts_root
    contracts = {}
    if not base.is_dir():
        return contracts
    for path in sorted(base.rglob("contract.md")):
        cited = {number for found in CITATION.findall(path.read_text()) for number in found if number}
        contracts[path.parent.relative_to(base).as_posix()] = cited
    return contracts


def field_problems(one):
    problems = []
    if not one.heading.startswith(f"# {one.number}. "):
        problems.append(f"{one.file}: the first heading must start with \"# {one.number}. \"")
    category, status = one.front.get("category"), one.front.get("status")
    if category not in CATEGORIES:
        problems.append(f"{one.file}: category {category!r} is not one of {', '.join(CATEGORIES)}")
    if status not in STATUSES:
        problems.append(f"{one.file}: status {status!r} is not one of {', '.join(STATUSES)}")
    approval = one.front.get("approval")
    if status != "proposed" and approval not in APPROVALS:
        problems.append(f"{one.file}: approval {approval!r} is not one of {', '.join(APPROVALS)}")
    return problems


def affects_problems(one, components):
    problems = []
    category = one.front.get("category")
    if one.has_affects and category not in PRODUCT_ALLOWED:
        problems.append(f"{one.file}: a {category} record has no affects field")
    if not one.has_affects and category in PRODUCT_REQUIRED:
        problems.append(f"{one.file}: a {category} record needs an affects field, empty while the component is not built")
    if components is not None:
        for each in one.list_of("affects"):
            if each not in components:
                problems.append(f"{one.file}: affects {each!r} is not a component in architecture.yaml")
    return problems


def link_problems(one, by_number):
    problems = []
    for field in LINK_FIELDS:
        for number in one.list_of(field):
            target = by_number.get(number)
            if number == one.number:
                problems.append(f"{one.file}: {field} lists the record itself")
            elif target is None:
                problems.append(f"{one.file}: {field} {number} is not a record")
            elif field in REVERSE and one.number not in target.list_of(REVERSE[field]):
                problems.append(
                    f"{one.file}: {field} {number}, but {target.file} does not list {one.number} in {REVERSE[field]}"
                )
    return problems


def citation_problems(one, contracts):
    if not one.has_affects or one.front.get("category") not in PRODUCT_ALLOWED:
        return []
    affected = one.list_of("affects")
    return [
        f"{one.file}: the contract of {component} cites this record, so affects must list it"
        for component, cited in sorted(contracts.items())
        if one.number in cited and component not in affected
    ]


def uncited_note(one, contracts):
    missing = [each for each in one.list_of("affects") if each in contracts and one.number not in contracts[each]]
    return f"{one.file}: contracts of {', '.join(missing)} do not cite it" if missing else None


def check(root, require_architecture=True):
    """Return (problems, notes) for the project at root."""
    records, problems = load_records(root)
    components, contracts_root = load_architecture(root)
    contracts = load_contracts(root, contracts_root)
    if components is None:
        contracts = {}
        if require_architecture:
            problems.append(f"{root / 'architecture.yaml'} does not exist. Every project needs one, and affects ids and contract citations are checked against it")
    by_number = {one.number: one for one in records}
    notes = []
    for one in records:
        problems += field_problems(one) + affects_problems(one, components) + link_problems(one, by_number)
        problems += citation_problems(one, contracts)
        note = uncited_note(one, contracts)
        if note:
            notes.append(note)
    return sorted(problems), notes


def main(args):
    verbose = "-v" in args
    paths = [each for each in args if each not in ("-v", "--framework")]
    problems, notes = check(Path(paths[0]) if paths else Path("."), require_architecture="--framework" not in args)
    if verbose:
        for note in notes:
            print("note:", note)
    elif notes:
        print(f"records that list a component whose contract does not cite them: {len(notes)}, see check.py -v")
    if problems:
        print("found problems:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    print("decision records are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
