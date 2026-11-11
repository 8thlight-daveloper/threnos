import datetime
import tempfile
import unittest
from pathlib import Path

import approve
import check
import ledger

ARCHITECTURE = "components:\n  - name: plan/decoder\nmodel: model\n"
PERSON = {"kind": "person", "name": "Dana"}
AUTHOR = {"kind": "agent", "harness": "claude-code", "session": "aaa"}
REVIEWER = {"kind": "agent", "harness": "claude-code", "session": "bbb"}


def write(root, files):
    for name, text in files.items():
        path = Path(root) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def entry(root, gate, unit, approver=PERSON, author=None, **changes):
    found = {"gate": gate, "unit": unit, "approver": approver, "date": datetime.date(2026, 11, 11)}
    if gate != "build":
        found["hash"] = ledger.digest(Path(root) / unit)
    if author:
        found["author"] = author
    return {**found, **changes}


class LedgerChecks(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        write(self.root, {
            "architecture.yaml": ARCHITECTURE,
            "contracts/plan/decoder/contract.md": "Decodes.\n",
            "contracts/plan/decoder/cases.json": "[]\n",
            "contracts/harness/helper.go": "package harness\n",
            "acceptance/scenarios/a.yaml": "name: a\n",
            "model/model.go": "package model\n",
        })

    def everything(self, **per_gate):
        return [
            entry(self.root, "contracts", "contracts/plan/decoder", **per_gate.get("contracts", {})),
            entry(self.root, "acceptance", "acceptance", **per_gate.get("acceptance", {})),
            entry(self.root, "architecture", "architecture.yaml", **per_gate.get("architecture", {})),
            entry(self.root, "model", "model", **per_gate.get("model", {})),
        ]

    def problems(self, entries, config=None):
        text = "approvals: []\n" if not entries else None
        if entries:
            import yaml
            text = yaml.safe_dump({"approvals": entries}, sort_keys=False)
        write(self.root, {".threnos/approvals.yaml": text})
        architecture = {"contracts_root": "contracts", "model": "model"}
        return ledger.ledger_problems(self.root, config or {}, architecture)

    def assertProblem(self, problems, fragment):
        self.assertTrue(any(fragment in each for each in problems), f"{fragment!r} not in {problems}")

    def test_no_ledger_means_no_checks(self):
        self.assertEqual(ledger.ledger_problems(self.root, {}, {"model": "model"}), [])

    def test_a_complete_ledger_passes(self):
        self.assertEqual(self.problems(self.everything()), [])

    def test_a_contract_folder_is_a_unit_and_a_shared_helper_folder_is_not(self):
        known = ledger.units(self.root, {"model": "model"})
        self.assertEqual(known["contracts"], ["contracts/plan/decoder"])

    def test_a_unit_with_no_entry_is_reported(self):
        problems = self.problems(self.everything()[:3])
        self.assertProblem(problems, "model model has no approval. Run: nix run .#approve -- model model")

    def test_a_unit_that_changed_after_approval_is_reported(self):
        entries = self.everything()
        write(self.root, {"contracts/plan/decoder/cases.json": "[1]\n"})
        self.assertProblem(self.problems(entries), "contracts contracts/plan/decoder changed since it was approved on 2026-11-11")

    def test_a_new_file_in_a_unit_changes_its_hash(self):
        entries = self.everything()
        write(self.root, {"acceptance/runner/run.go": "package runner\n"})
        self.assertProblem(self.problems(entries), "acceptance acceptance changed")

    def test_an_unknown_unit_is_reported(self):
        entries = self.everything() + [{**entry(self.root, "contracts", "contracts/plan/decoder"), "unit": "contracts/ghost"}]
        self.assertProblem(self.problems(entries), "is not a contracts unit in this project")

    def test_two_entries_for_one_unit_are_reported(self):
        self.assertProblem(self.problems(self.everything() + [self.everything()[0]]), "has more than one entry")

    def test_an_approver_kind_outside_the_list_is_reported(self):
        problems = self.problems(self.everything(model={"approver": REVIEWER, "author": AUTHOR}))
        self.assertProblem(problems, "approver agent is not in approvals.model ['person']")

    def test_an_agent_may_approve_when_the_gate_allows_it_and_the_session_differs(self):
        config = {"approvals": {"model": ["person", "agent"]}}
        problems = self.problems(self.everything(model={"approver": REVIEWER, "author": AUTHOR}), config)
        self.assertEqual(problems, [])

    def test_the_author_may_not_approve_in_their_own_session(self):
        config = {"approvals": {"model": ["agent"]}}
        problems = self.problems(self.everything(model={"approver": AUTHOR, "author": AUTHOR}), config)
        self.assertProblem(problems, "the approving agent is the author's session")

    def test_the_same_harness_in_another_session_passes_by_default_and_fails_when_harness_is_required(self):
        entries = self.everything(model={"approver": REVIEWER, "author": AUTHOR})
        config = {"approvals": {"model": ["agent"]}}
        self.assertEqual(self.problems(entries, config), [])
        config["approvals"]["independence"] = "harness"
        self.assertProblem(self.problems(entries, config), "use the same harness")

    def test_an_agent_approval_needs_an_author(self):
        config = {"approvals": {"model": ["agent"]}}
        self.assertProblem(self.problems(self.everything(model={"approver": REVIEWER}), config), "needs an author")

    def test_a_person_may_approve_what_an_agent_wrote(self):
        self.assertEqual(self.problems(self.everything(model={"author": AUTHOR})), [])

    def test_a_party_needs_its_fields(self):
        problems = self.problems(self.everything(model={"approver": {"kind": "agent", "harness": "claude-code"}}))
        self.assertProblem(problems, "an agent approver needs session")
        problems = self.problems(self.everything(model={"approver": {"kind": "robot"}}))
        self.assertProblem(problems, "kind 'robot'")

    def test_the_date_must_parse(self):
        self.assertProblem(self.problems(self.everything(model={"date": "soon"})), "date must be a date")

    def test_a_build_entry_names_a_commit_and_needs_no_hash_or_author(self):
        build = entry(self.root, "build", "a" * 40)
        self.assertEqual(self.problems(self.everything() + [build]), [])
        bad = entry(self.root, "build", "main")
        self.assertProblem(self.problems(self.everything() + [bad]), "is a commit, as 7 to 40 hex digits")

    def test_an_agent_build_review_needs_the_gate_to_allow_it(self):
        build = entry(self.root, "build", "abc1234", approver=REVIEWER)
        self.assertProblem(self.problems(self.everything() + [build]), "approver agent is not in approvals.build")
        config = {"approvals": {"build": ["person", "agent"]}}
        self.assertEqual(self.problems(self.everything() + [build], config), [])

    def test_the_hash_ignores_editor_files_and_bytecode(self):
        before = ledger.digest(self.root / "model")
        write(self.root, {"model/.DS_Store": "x", "model/__pycache__/m.pyc": "x"})
        self.assertEqual(ledger.digest(self.root / "model"), before)

    def test_a_ledger_that_does_not_parse_is_reported(self):
        write(self.root, {".threnos/approvals.yaml": "approvals: [\n"})
        self.assertProblem(ledger.ledger_problems(self.root, {}, {}), "approvals.yaml:")

    def test_the_records_check_runs_the_ledger(self):
        write(self.root, {".threnos/approvals.yaml": "approvals: []\n"})
        problems, _ = check.check(self.root)
        self.assertProblem(problems, "contracts contracts/plan/decoder has no approval")

    def test_independence_is_validated_in_settings(self):
        problems = check.approvals_problems({"approvals": {"independence": "never"}}, "config")
        self.assertProblem(problems, "independence must be session or harness")
        self.assertEqual(check.approvals_problems({"approvals": {"independence": "harness", "build": ["person"]}}, "c"), [])


class Approve(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        write(self.root, {
            "architecture.yaml": ARCHITECTURE,
            "contracts/plan/decoder/contract.md": "Decodes.\n",
            "model/model.go": "package model\n",
        })

    def run_approve(self, *args, config=None, local=None):
        if config is not None:
            write(self.root, {".threnos/config.toml": config})
        if local is not None:
            write(self.root, {".threnos/local.toml": local})
        return approve.main(["--root", str(self.root), *args])

    def read(self):
        import yaml
        return yaml.safe_load((self.root / ledger.LEDGER).read_text())["approvals"]

    def test_it_writes_an_entry_with_the_current_hash(self):
        self.assertEqual(self.run_approve("architecture", "--approver", "person:Dana", "--date", "2026-11-11"), 0)
        written = self.read()[0]
        self.assertEqual(written["unit"], "architecture.yaml")
        self.assertEqual(written["hash"], ledger.digest(self.root / "architecture.yaml"))
        self.assertEqual(written["approver"], {"kind": "person", "name": "Dana"})

    def test_a_gate_with_one_unit_needs_no_unit_name(self):
        self.assertEqual(self.run_approve("model", "--approver", "person:Dana"), 0)
        self.assertEqual(self.read()[0]["unit"], "model")

    def test_a_second_approval_replaces_the_first(self):
        self.run_approve("model", "--approver", "person:Dana")
        write(self.root, {"model/model.go": "package model\n\ntype T struct{}\n"})
        self.run_approve("model", "--approver", "person:Ana")
        entries = self.read()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["approver"]["name"], "Ana")
        self.assertEqual(entries[0]["hash"], ledger.digest(self.root / "model"))

    def test_an_entry_the_settings_reject_is_not_written(self):
        code = self.run_approve("model", "--approver", "agent:claude-code:bbb", "--author", "agent:claude-code:aaa")
        self.assertEqual(code, 1)
        self.assertFalse((self.root / ledger.LEDGER).exists())

    def test_a_local_list_lets_an_agent_write_and_a_warning_says_ci_will_fail(self):
        code = self.run_approve(
            "model", "--approver", "agent:claude-code:bbb", "--author", "agent:claude-code:aaa",
            config="", local='[approvals]\nmodel = ["agent"]\n',
        )
        self.assertEqual(code, 0)
        self.assertEqual(self.read()[0]["approver"]["kind"], "agent")
        problems, _ = check.check(self.root)
        self.assertTrue(any("approver agent is not in approvals.model" in each for each in problems), problems)

    def test_a_unit_that_is_not_one_is_refused(self):
        self.assertEqual(self.run_approve("contracts", "contracts/ghost", "--approver", "person:Dana"), 1)

    def test_a_gate_with_many_units_needs_a_name(self):
        write(self.root, {"contracts/plan/other/contract.md": "Other.\n"})
        self.assertEqual(self.run_approve("contracts", "--approver", "person:Dana"), 1)

    def stale_entry(self):
        self.run_approve("contracts", "contracts/plan/decoder", "--approver", "person:Dana")
        self.run_approve("model", "--approver", "person:Dana")
        (self.root / "contracts/plan/decoder/contract.md").rename(self.root / "contracts/plan/decoder/old.md")
        write(self.root, {"contracts/plan/codec/contract.md": "Codec.\n"})
        import shutil
        shutil.rmtree(self.root / "contracts/plan/decoder")

    def test_remove_drops_the_entry_of_a_unit_that_is_gone_and_keeps_the_others(self):
        self.stale_entry()
        problems, _ = check.check(self.root)
        self.assertTrue(any("run: nix run .#approve -- --remove contracts contracts/plan/decoder" in each for each in problems), problems)
        self.assertEqual(self.run_approve("--remove", "contracts", "contracts/plan/decoder"), 0)
        self.assertEqual([(each["gate"], each["unit"]) for each in self.read()], [("model", "model")])

    def test_remove_refuses_while_the_unit_exists(self):
        self.run_approve("model", "--approver", "person:Dana")
        self.assertEqual(self.run_approve("--remove", "model", "model"), 1)
        self.assertEqual(len(self.read()), 1)

    def test_remove_refuses_when_there_is_no_entry_and_for_build(self):
        self.run_approve("model", "--approver", "person:Dana")
        self.assertEqual(self.run_approve("--remove", "contracts", "contracts/ghost"), 1)
        self.assertEqual(self.run_approve("--remove", "build", "abc1234"), 1)

    def test_remove_needs_a_unit_and_no_approver(self):
        self.assertEqual(self.run_approve("--remove", "contracts"), 1)

    def test_approve_still_needs_an_approver(self):
        with self.assertRaises(SystemExit):
            self.run_approve("model")

    def test_a_malformed_party_is_refused(self):
        with self.assertRaises(SystemExit):
            self.run_approve("model", "--approver", "agent:claude-code")


if __name__ == "__main__":
    unittest.main()
