"""Check a project's decision records against the front matter schema.

Usage: check.py [-v] [--framework] [--settings] [project root]

The schema is templates/decision-record-front-matter.md. Exits 1 when a check
fails. Notes are printed only with -v. A project must have an architecture.yaml.
--settings checks only .threnos/config.toml and the user layer .threnos/local.toml, which sync runs.
The record check reads the project file and never the user file, so it judges every record the way CI does.
--framework is for Threnos itself, which holds records but is not a project, and skips that requirement.
"""
import datetime
import re
import sys
import tomllib
from pathlib import Path

import yaml

import ledger

DECISIONS = "docs/decisions"
CATEGORIES = ["architecture", "behavior", "ux", "regenerative-process", "operations"]
STATUSES = ["proposed", "accepted", "superseded", "withdrawn"]
APPROVALS = ["person", "agent", "unrecorded"]
PRODUCT_REQUIRED = ["behavior", "ux"]
PRODUCT_ALLOWED = ["architecture", "behavior", "ux"]
FIELDS = {
    "category", "status", "approval", "approver", "author", "note", "affects", "builds-on", "principle",
    "supersedes", "superseded-by", "partly-supersedes", "partly-superseded-by",
}
LINK_FIELDS = ["builds-on", "supersedes", "superseded-by", "partly-supersedes", "partly-superseded-by"]
REVERSE = {
    "supersedes": "superseded-by",
    "superseded-by": "supersedes",
    "partly-supersedes": "partly-superseded-by",
    "partly-superseded-by": "partly-supersedes",
}
PRINCIPLES = "docs/reference/product-principles.md"
PRINCIPLES_FIELDS = {"approval", "reviewed"}
APPROVERS = ["person", "agent"]
GATES = ["principles", "decisions"] + ledger.LEDGER_GATES
GATED_STATUSES = ["accepted", "superseded"]
UNRECORDED = "approval is unrecorded"
DEFAULT_APPROVERS = ["person"]
USER_SETTINGS = {"approvals"}
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
    if "principle" in one.front and (category != "behavior" or one.front["principle"] != "none"):
        problems.append(f"{one.file}: principle may only be none, and only on a behavior record")
    return problems


def approval_gate_problems(one, config):
    """Check a gated record's approval against the decisions gate, and its parties."""
    problems = []
    table = config.get("approvals") or {}
    approval = one.front.get("approval")
    if one.front.get("status") in GATED_STATUSES and approval in ("person", "agent"):
        allowed = table.get("decisions", DEFAULT_APPROVERS)
        if approval not in allowed:
            problems.append(
                f"{one.file}: approval {approval} is not in approvals.decisions {allowed}. "
                "A person ratifies it by reading it and setting approval: person"
            )
    parties = {field: one.front[field] for field in ("approver", "author") if field in one.front}
    for field, who in parties.items():
        problems += ledger.party_problems(one.file, field, who)
    approver = parties.get("approver")
    if isinstance(approver, dict) and approver.get("kind") in ledger.KINDS and approval in ("person", "agent"):
        if approver["kind"] != approval:
            problems.append(f"{one.file}: approver kind {approver['kind']} does not match approval {approval}")
    if approval == "agent" and one.front.get("status") in GATED_STATUSES:
        for field in ("approver", "author"):
            if field not in parties:
                problems.append(f"{one.file}: approval agent needs {field}, so independence can be checked")
        if len(parties) == 2:
            problems += ledger.independence_problems(one.file, parties, table.get("independence", "session"))
    return problems


def unrecorded_note(one):
    if one.front.get("status") in GATED_STATUSES and one.front.get("approval") == "unrecorded":
        return f"{one.file}: {UNRECORDED}"
    return None


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


def load_toml(path):
    """Return (settings, problem). A file that does not parse is a problem and no settings."""
    if not path.is_file():
        return {}, None
    try:
        return tomllib.loads(path.read_text()), None
    except tomllib.TOMLDecodeError as error:
        return {}, f".threnos/{path.name}: {error}"


def approvals_problems(settings, label):
    problems = []
    table = settings.get("approvals") or {}
    if not isinstance(table, dict):
        return [f"{label}: approvals must be a table of gates"]
    for gate, who in table.items():
        if gate == "independence":
            if who not in ledger.INDEPENDENCE:
                problems.append(f"{label}: approvals.independence must be {' or '.join(ledger.INDEPENDENCE)}")
        elif gate not in GATES:
            problems.append(f"{label}: approvals.{gate} is not a gate. Gates: {', '.join(GATES)}")
        elif not isinstance(who, list) or not who or any(each not in APPROVERS for each in who):
            problems.append(f"{label}: approvals.{gate} must be a non-empty list of {' or '.join(APPROVERS)}")
    return problems


def local_problems(local):
    problems = [
        f".threnos/local.toml: {key} is project-only. A user file may set only {', '.join(sorted(USER_SETTINGS))}"
        for key in sorted(set(local) - USER_SETTINGS)
    ]
    return problems + approvals_problems(local, ".threnos/local.toml")


def approvers(config, gate):
    return (config.get("approvals") or {}).get(gate, DEFAULT_APPROVERS)


def settings_problems(root):
    """Validate the project settings and the user layer. Returns (problems, warnings)."""
    config, config_error = load_toml(root / ".threnos" / "config.toml")
    local, local_error = load_toml(root / ".threnos" / "local.toml")
    problems = [each for each in (config_error, local_error) if each]
    problems += approvals_problems(config, ".threnos/config.toml") + local_problems(local)
    warnings = [
        f"{label}: approvals.{gate} lists only agent, so a person may not approve"
        for label, settings in ((".threnos/config.toml", config), (".threnos/local.toml", local))
        for gate, who in (settings.get("approvals") or {}).items()
        if gate != "independence" and who == ["agent"]
    ]
    warnings += [
        f"{label}: approvals.build lists agent, so no person reviews a running build"
        for label, settings in ((".threnos/config.toml", config), (".threnos/local.toml", local))
        if "agent" in (settings.get("approvals") or {}).get("build", [])
    ]
    return problems, warnings


def principle_sections(body):
    sections, current = [], None
    for line in body.split("\n"):
        if line.startswith("### P"):
            current = (line, [])
            sections.append(current)
        elif line.startswith("## ") or line.startswith("# "):
            current = None
        elif current is not None:
            current[1].append(line)
    return sections


def principles_problems(root, records, config):
    path = root / PRINCIPLES
    if not path.is_file():
        return []
    name = PRINCIPLES
    text = path.read_text()
    if not text.startswith("---\n"):
        return [f"{name}: no front matter. It needs approval and reviewed"]
    block, closed, body = text[4:].partition("\n---\n")
    if not closed:
        return [f"{name}: front matter is not closed"]
    try:
        front = yaml.safe_load(block) or {}
    except yaml.YAMLError as error:
        return [f"{name}: front matter: {error}"]
    problems = []
    unknown = sorted(set(front) - PRINCIPLES_FIELDS)
    if unknown:
        problems.append(f"{name}: front matter has unknown fields: {', '.join(unknown)}")
    approval = front.get("approval")
    allowed = approvers(config, "principles")
    if approval not in APPROVERS:
        problems.append(f"{name}: approval {approval!r} is not one of {', '.join(APPROVERS)}")
    elif approval not in allowed:
        problems.append(
            f"{name}: approval {approval} is not in approvals.principles {allowed}. "
            "A person ratifies it by reading the changes and setting approval: person"
        )
    if not isinstance(front.get("reviewed"), datetime.date):
        problems.append(f"{name}: reviewed must be a date, such as 2026-01-31")
    by_number = {one.number: one for one in records}
    cited = set()
    for heading, lines in principle_sections(body):
        label = heading[4:].split(".")[0]
        found = next((line for line in lines if line.startswith("Records:")), None)
        if found is None:
            problems.append(f"{name}: {label} has no Records line. List the records it comes from, or none")
            continue
        for number in re.findall(r"\b\d{4}\b", found):
            target = by_number.get(number)
            if target is None:
                problems.append(f"{name}: {label} cites {number}, which is not a record")
            elif target.front.get("status") in ("superseded", "withdrawn"):
                problems.append(f"{name}: {label} cites {number}, which is {target.front['status']}. Update the principle")
            cited.add(number)
    for one in records:
        if (
            one.front.get("category") == "behavior"
            and one.front.get("status") == "accepted"
            and one.number not in cited
            and one.front.get("principle") != "none"
        ):
            problems.append(f"{one.file}: no principle cites this record. Cite it in {name}, or set principle: none")
    return problems


def check(root, require_architecture=True):
    """Return (problems, notes) for the project at root."""
    records, problems = load_records(root)
    components, contracts_root = load_architecture(root)
    contracts = load_contracts(root, contracts_root)
    if components is None:
        contracts = {}
        if require_architecture:
            problems.append(f"{root / 'architecture.yaml'} does not exist. Every project needs one, and affects ids and contract citations are checked against it")
    config, config_error = load_toml(root / ".threnos" / "config.toml")
    if config_error:
        problems.append(config_error)
    by_number = {one.number: one for one in records}
    notes = []
    for one in records:
        problems += field_problems(one) + affects_problems(one, components) + link_problems(one, by_number)
        problems += citation_problems(one, contracts) + approval_gate_problems(one, config)
        notes += [note for note in (uncited_note(one, contracts), unrecorded_note(one)) if note]
    problems += approvals_problems(config, ".threnos/config.toml") + principles_problems(root, records, config)
    architecture = yaml.safe_load((root / "architecture.yaml").read_text()) or {} if (root / "architecture.yaml").is_file() else {}
    problems += ledger.ledger_problems(root, config, architecture)
    return sorted(problems), notes


def main_settings(root):
    problems, warnings = settings_problems(root)
    for warning in warnings:
        print("warning:", warning, file=sys.stderr)
    if problems:
        print("found problems:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    return 0


def main(args):
    verbose = "-v" in args
    paths = [each for each in args if each not in ("-v", "--framework", "--settings")]
    if "--settings" in args:
        return main_settings(Path(paths[0]) if paths else Path("."))
    problems, notes = check(Path(paths[0]) if paths else Path("."), require_architecture="--framework" not in args)
    unrecorded = [note for note in notes if note.endswith(UNRECORDED)]
    uncited = [note for note in notes if note not in unrecorded]
    if verbose:
        for note in notes:
            print("note:", note)
    else:
        if uncited:
            print(f"records that list a component whose contract does not cite them: {len(uncited)}, see check.py -v")
        if unrecorded:
            print(f"accepted records with approval unrecorded: {len(unrecorded)}, see check.py -v")
    if problems:
        print("found problems:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    print("decision records are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
