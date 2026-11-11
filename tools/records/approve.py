"""Record an approval in the ledger, `.threnos/approvals.yaml`.

Usage: approve.py [--root DIR] GATE [UNIT] [--approver WHO] [--author WHO] [--date YYYY-MM-DD] [--note TEXT]
       approve.py [--root DIR] --remove GATE UNIT

WHO is `person:<name>` or `agent:<harness>:<session>`. Without --approver, a person at a terminal approves under the name
in `identity.name` of `.threnos/local.toml`, then of the global file, then one they type, and confirms it. Without a
terminal the tool refuses, so an agent must pass --approver. See ADR 0130. GATE is contracts, acceptance, architecture, model, or build.
UNIT is the folder or file the gate protects. It may be left out when the gate has one unit. For build it is a commit,
and defaults to HEAD. The entry holds the unit's current hash. An existing entry for the unit is replaced.

--remove drops the entry for a unit that no longer exists, such as a component folder that was renamed. It refuses while
the unit exists, and for `build`, whose entries name commits and are never stale. It grants no approval, so it needs no
approver. A renamed folder is a new unit and needs its own approval.

The entry is checked before it is written, against the lists in `.threnos/config.toml` and the user's
`.threnos/local.toml`, which replaces a list for this person. A write that the project's own list would reject, which is
what CI uses, is reported as a warning.
"""
import argparse
import datetime
import subprocess
import sys
from pathlib import Path

import yaml

import check
import ledger

HEADER = "# Managed by approve.py. Each entry records one approval of one unit, with a hash of its content.\n"


def party(text):
    kind, _, rest = text.partition(":")
    if kind == "person" and rest:
        return {"kind": "person", "name": rest}
    harness, _, session = rest.partition(":")
    if kind == "agent" and harness and session:
        return {"kind": "agent", "harness": harness, "session": session}
    raise argparse.ArgumentTypeError("use person:<name> or agent:<harness>:<session>")


def effective(config, local):
    merged = dict(config.get("approvals") or {})
    merged.update(local.get("approvals") or {})
    return {"approvals": merged}


def head(root):
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout.strip()


def read_entries(path):
    return (yaml.safe_load(path.read_text()) or {}).get("approvals") or [] if path.is_file() else []


def write_entries(path, entries):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER + yaml.safe_dump({"approvals": entries}, sort_keys=False))


def remove(root, gate, unit, known):
    """Drop the entry of a unit that no longer exists. Returns an exit code."""
    path = root / ledger.LEDGER
    if gate == "build":
        print("build entries name commits and are never stale, so there is nothing to remove", file=sys.stderr)
        return 1
    if unit is None:
        print("--remove needs the gate and the unit", file=sys.stderr)
        return 1
    entries = read_entries(path)
    kept = [each for each in entries if (each.get("gate"), each.get("unit")) != (gate, unit)]
    if len(kept) == len(entries):
        print(f"the ledger has no {gate} entry for {unit}", file=sys.stderr)
        return 1
    if unit in known[gate]:
        print(f"{unit} still exists. Approve it again instead of removing its entry", file=sys.stderr)
        return 1
    write_entries(path, kept)
    print(f"removed {gate} {unit}")
    return 0


def is_terminal():
    return sys.stdin.isatty()


def resolve_approver(gate, unit, local, global_settings, terminal, ask):
    """Return (approver, problem). A person at a terminal gets a named default after a confirmation."""
    if not terminal():
        return None, (
            "no --approver. Pass person:<name> or agent:<harness>:<session>. A person at a terminal may set "
            "identity.name in .threnos/local.toml or the global file to be asked instead"
        )
    name = check.identity_name(local, global_settings)
    try:
        if name is None:
            name = ask("Your name: ").strip()
            if not name or "\n" in name:
                return None, "no name given"
        answer = ask(f"Approve {gate} {unit} as {name}? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return None, "no answer. Nothing was written"
    if answer not in ("y", "yes"):
        return None, "not approved. Nothing was written"
    return {"kind": "person", "name": name}, None


def main(args, terminal=is_terminal, ask=input):
    parser = argparse.ArgumentParser(prog="approve.py", description=__doc__.split("\n")[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("gate", choices=ledger.LEDGER_GATES)
    parser.add_argument("unit", nargs="?")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--approver", type=party)
    parser.add_argument("--author", type=party)
    parser.add_argument("--date", type=datetime.date.fromisoformat, default=datetime.date.today())
    parser.add_argument("--note")
    given = parser.parse_args(args)
    root = Path(given.root).resolve()
    architecture = yaml.safe_load((root / "architecture.yaml").read_text()) if (root / "architecture.yaml").is_file() else {}
    architecture = architecture or {}
    config, config_error = check.load_toml(root / ".threnos" / "config.toml")
    local, local_error = check.load_toml(root / ".threnos" / "local.toml")
    if config_error or local_error:
        print(config_error or local_error, file=sys.stderr)
        return 1
    known = ledger.units(root, architecture)
    if given.remove:
        return remove(root, given.gate, given.unit, known)
    unit = given.unit
    if given.gate == "build":
        unit = unit or head(root)
    elif unit is None and len(known[given.gate]) == 1:
        unit = known[given.gate][0]
    elif unit is None:
        print(f"{given.gate} has {len(known[given.gate])} units. Name one: {', '.join(known[given.gate]) or 'none exist'}", file=sys.stderr)
        return 1
    entry = {"gate": given.gate, "unit": unit}
    if given.gate != "build":
        if unit not in known[given.gate]:
            print(f"{unit} is not a {given.gate} unit. Units: {', '.join(known[given.gate]) or 'none exist'}", file=sys.stderr)
            return 1
        entry["hash"] = ledger.digest(root / unit)
    approver = given.approver
    if approver is None:
        global_settings, global_error = check.load_toml(check.global_config_path(), str(check.global_config_path()))
        if global_error:
            print(global_error, file=sys.stderr)
            return 1
        approver, problem = resolve_approver(given.gate, unit, local, global_settings, terminal, ask)
        if problem:
            print(problem, file=sys.stderr)
            return 1
    entry["approver"] = approver
    if given.author:
        entry["author"] = given.author
    entry["date"] = given.date
    if given.note:
        entry["note"] = given.note

    mine = effective(config, local)
    problems = ledger.entry_problems(entry, known, mine["approvals"].get(given.gate, check.DEFAULT_APPROVERS), mine["approvals"].get("independence", "session"))
    if problems:
        print("not written:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    theirs = ledger.entry_problems(entry, known, (config.get("approvals") or {}).get(given.gate, check.DEFAULT_APPROVERS), (config.get("approvals") or {}).get("independence", "session"))
    if theirs:
        print("warning: the project's own settings reject this entry, so CI will fail until a person ratifies it:\n  " + "\n  ".join(theirs), file=sys.stderr)

    path = root / ledger.LEDGER
    existing = read_entries(path)
    kept = [each for each in existing if (each.get("gate"), each.get("unit")) != (entry["gate"], entry["unit"])]
    entries = sorted(kept + [entry], key=lambda each: (ledger.LEDGER_GATES.index(each["gate"]), str(each["unit"])))
    write_entries(path, entries)
    print(f"recorded {given.gate} {unit}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
