"""The approvals ledger, `.threnos/approvals.yaml`, and the checks over it.

A ledger entry records that a person or an agent approved one protected unit, with a hash of the unit's content. The
check fails when a unit has no entry, when a unit changed after its approval, when the approver's kind is not in the
project's list for the gate, or when an agent approver is not independent of the author. See ADR 0110.

Entry: {gate, unit, hash, approver, author, date, note}. A party is {kind: person, name} or
{kind: agent, harness, session}. A `build` entry has a commit for its unit, and no hash or author.
"""
import datetime
import hashlib
import re
from pathlib import Path

import yaml

LEDGER = ".threnos/approvals.yaml"
LEDGER_GATES = ["contracts", "acceptance", "architecture", "model", "build"]
KINDS = ["person", "agent"]
INDEPENDENCE = ["session", "harness"]
ENTRY_FIELDS = {"gate", "unit", "hash", "approver", "author", "date", "note"}
PARTY_FIELDS = {"kind", "name", "harness", "session"}
IGNORED_FILES = {".DS_Store"}
IGNORED_FOLDERS = {"__pycache__"}
COMMIT = re.compile(r"^[0-9a-f]{7,40}$")


def digest(path):
    """Return `sha256:<hex>` over a file, or over a folder's relative paths and contents in sorted order."""
    if path.is_file():
        items = [(path.name, path)]
    else:
        items = sorted(
            (found.relative_to(path).as_posix(), found)
            for found in path.rglob("*")
            if found.is_file()
            and not found.is_symlink()
            and found.name not in IGNORED_FILES
            and not IGNORED_FOLDERS & set(found.relative_to(path).parts)
        )
    total = hashlib.sha256()
    for name, found in items:
        data = found.read_bytes()
        total.update(name.encode() + b"\0" + str(len(data)).encode() + b"\0" + data)
    return "sha256:" + total.hexdigest()


def units(root, architecture):
    """Return {gate: [unit path, ...]} for the protected units that exist, except `build`."""
    contracts_root = architecture.get("contracts_root") or "contracts"
    model = (architecture.get("model") or "").strip("/")
    base = root / contracts_root
    contracts = sorted(each.parent.relative_to(root).as_posix() for each in base.rglob("contract.md")) if base.is_dir() else []
    return {
        "contracts": contracts,
        "acceptance": ["acceptance"] if (root / "acceptance").is_dir() else [],
        "architecture": ["architecture.yaml"] if (root / "architecture.yaml").is_file() else [],
        "model": [model] if model and (root / model).is_dir() else [],
    }


def party_problems(label, field, who):
    if not isinstance(who, dict):
        return [f"{label}: {field} must be a mapping with a kind"]
    problems = []
    unknown = sorted(set(who) - PARTY_FIELDS)
    if unknown:
        problems.append(f"{label}: {field} has unknown fields: {', '.join(unknown)}")
    kind = who.get("kind")
    required = {"person": ["name"], "agent": ["harness", "session"]}.get(kind)
    if required is None:
        return problems + [f"{label}: {field} kind {kind!r} is not one of {', '.join(KINDS)}"]
    for key in required:
        if not isinstance(who.get(key), str) or not who[key].strip():
            problems.append(f"{label}: {'an' if kind == 'agent' else 'a'} {kind} {field} needs {key}")
    return problems


def independence_problems(label, entry, mode):
    approver, author = entry.get("approver"), entry.get("author")
    if not isinstance(approver, dict) or approver.get("kind") != "agent" or entry.get("gate") == "build":
        return []
    if not isinstance(author, dict):
        return [f"{label}: an agent approval needs an author, so independence can be checked"]
    if author.get("kind") != "agent":
        return []
    same_harness = approver.get("harness") == author.get("harness")
    same_session = same_harness and approver.get("session") == author.get("session")
    if mode == "harness" and same_harness:
        return [f"{label}: the approving agent and the author use the same harness, {approver.get('harness')}"]
    if mode == "session" and same_session:
        return [f"{label}: the approving agent is the author's session, {approver.get('harness')} {approver.get('session')}"]
    return []


def entry_problems(entry, known, approvers, mode):
    """Return the problems in one entry. known maps each gate to the units that exist for it."""
    gate, unit = entry.get("gate"), entry.get("unit")
    label = f"{LEDGER}: {gate} {unit}"
    unknown = sorted(set(entry) - ENTRY_FIELDS)
    if unknown:
        return [f"{label}: unknown fields: {', '.join(unknown)}"]
    if gate not in LEDGER_GATES:
        return [f"{label}: gate {gate!r} is not one of {', '.join(LEDGER_GATES)}"]
    problems = party_problems(label, "approver", entry.get("approver"))
    if "author" in entry:
        problems += party_problems(label, "author", entry.get("author"))
    if not isinstance(entry.get("date"), datetime.date):
        problems.append(f"{label}: date must be a date, such as 2026-01-31")
    kind = (entry.get("approver") or {}).get("kind") if isinstance(entry.get("approver"), dict) else None
    if kind in KINDS and kind not in approvers:
        problems.append(f"{label}: approver {kind} is not in approvals.{gate} {approvers}")
    if gate == "build":
        if not isinstance(unit, str) or not COMMIT.match(unit):
            problems.append(f"{label}: the unit of a build entry is a commit, as 7 to 40 hex digits")
        return problems
    if unit not in known.get(gate, []):
        problems.append(
            f"{label}: is not a {gate} unit in this project. If it was renamed or deleted, run: "
            f"nix run .#approve -- --remove {gate} {unit}"
        )
    return problems + independence_problems(label, entry, mode)


def ledger_problems(root, config, architecture):
    """Return the problems with the ledger. A project without a ledger has none."""
    path = root / LEDGER
    if not path.is_file():
        return []
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except yaml.YAMLError as error:
        return [f"{LEDGER}: {error}"]
    if not isinstance(data, dict) or set(data) - {"approvals"} or not isinstance(data.get("approvals") or [], list):
        return [f"{LEDGER}: it must hold one key, approvals, with a list of entries"]
    table = config.get("approvals") or {}
    mode = table.get("independence", "session")
    known = units(root, architecture)
    problems, seen = [], {}
    for entry in data.get("approvals") or []:
        if not isinstance(entry, dict):
            problems.append(f"{LEDGER}: an entry is not a mapping")
            continue
        gate, unit = entry.get("gate"), entry.get("unit")
        approvers = table.get(gate, ["person"])
        problems += entry_problems(entry, known, approvers, mode)
        if (gate, unit) in seen:
            problems.append(f"{LEDGER}: {gate} {unit} has more than one entry")
        seen[(gate, unit)] = entry
        if gate in known and unit in known[gate] and entry.get("hash") != digest(root / unit):
            problems.append(f"{LEDGER}: {gate} {unit} changed since it was approved on {entry.get('date')}. Review it and approve it again")
    for gate, found in known.items():
        for unit in found:
            if (gate, unit) not in seen:
                problems.append(f"{LEDGER}: {gate} {unit} has no approval. Run: nix run .#approve -- {gate} {unit}")
    return problems
