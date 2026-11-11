import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import check

ARCHITECTURE = "components:\n  - name: plan/decoder\n  - name: tui\n"

_HOME = None
_PATCH = None


def setUpModule():
    global _HOME, _PATCH
    _HOME = tempfile.TemporaryDirectory()
    _PATCH = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": _HOME.name})
    _PATCH.start()


def tearDownModule():
    _PATCH.stop()
    _HOME.cleanup()


def record(number, front, title="Title"):
    return f"---\n{front}---\n\n# {number}. {title}\n\n## Context\n"


def run(files, architecture=ARCHITECTURE):
    with tempfile.TemporaryDirectory() as root:
        files = dict(files)
        if architecture is not None:
            files["architecture.yaml"] = architecture
        for name, text in files.items():
            path = Path(root) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        return check.check(Path(root))


class RecordChecks(unittest.TestCase):
    def assertProblem(self, problems, fragment):
        self.assertTrue(any(fragment in each for each in problems), f"{fragment!r} not in {problems}")

    def test_a_consistent_set_has_no_problems(self):
        problems, _ = run({
            "docs/decisions/0010-first.md": record("0010", "category: behavior\nstatus: accepted\napproval: person\naffects: [plan/decoder]\n"),
            "docs/decisions/0020-second.md": record("0020", "category: architecture\nstatus: proposed\nbuilds-on: ['0010']\n"),
            "docs/decisions/0030-third.md": record("0030", "category: operations\nstatus: accepted\napproval: person\n"),
        })
        self.assertEqual(problems, [])

    def test_a_file_without_front_matter_is_reported(self):
        problems, _ = run({"docs/decisions/0010-first.md": "# 0010. First\n"})
        self.assertProblem(problems, "no front matter")

    def test_an_unknown_field_is_reported(self):
        problems, _ = run({"docs/decisions/0010-first.md": record("0010", "category: ux\nstatus: proposed\naffects: []\ncolour: red\n")})
        self.assertProblem(problems, "unknown fields: colour")

    def test_a_value_outside_its_list_is_reported(self):
        problems, _ = run({"docs/decisions/0010-first.md": record("0010", "category: tasty\nstatus: done\n")})
        self.assertProblem(problems, "category 'tasty'")
        self.assertProblem(problems, "status 'done'")

    def test_a_proposed_record_needs_no_approval_but_an_accepted_one_does(self):
        proposed, _ = run({"docs/decisions/0010-first.md": record("0010", "category: operations\nstatus: proposed\n")})
        accepted, _ = run({"docs/decisions/0010-first.md": record("0010", "category: operations\nstatus: accepted\n")})
        self.assertEqual(proposed, [])
        self.assertProblem(accepted, "approval None")

    def test_the_heading_must_carry_the_file_number(self):
        problems, _ = run({"docs/decisions/0010-first.md": record("0020", "category: operations\nstatus: proposed\n")})
        self.assertProblem(problems, "first heading must start with")

    def test_affects_is_required_on_behavior_and_ux_and_barred_on_process(self):
        missing, _ = run({"docs/decisions/0010-first.md": record("0010", "category: ux\nstatus: proposed\n")})
        barred, _ = run({"docs/decisions/0010-first.md": record("0010", "category: regenerative-process\nstatus: proposed\naffects: []\n")})
        self.assertProblem(missing, "needs an affects field")
        self.assertProblem(barred, "has no affects field")

    def test_affects_must_name_components_and_never_all(self):
        problems, _ = run({"docs/decisions/0010-first.md": record("0010", "category: behavior\nstatus: proposed\naffects: [all, nope/none]\n")})
        self.assertProblem(problems, "affects 'all'")
        self.assertProblem(problems, "affects 'nope/none'")

    def test_a_link_to_no_record_or_to_itself_is_reported(self):
        problems, _ = run({"docs/decisions/0010-first.md": record("0010", "category: operations\nstatus: proposed\nbuilds-on: ['0010', '0990']\n")})
        self.assertProblem(problems, "lists the record itself")
        self.assertProblem(problems, "0990 is not a record")

    def test_a_replacement_must_be_listed_on_both_records(self):
        files = {
            "docs/decisions/0010-first.md": record("0010", "category: operations\nstatus: superseded\napproval: person\nsuperseded-by: ['0020']\n"),
            "docs/decisions/0020-second.md": record("0020", "category: operations\nstatus: accepted\napproval: person\n"),
        }
        problems, _ = run(files)
        self.assertProblem(problems, "does not list 0010 in supersedes")
        files["docs/decisions/0020-second.md"] = record("0020", "category: operations\nstatus: accepted\napproval: person\nsupersedes: ['0010']\n")
        problems, _ = run(files)
        self.assertEqual(problems, [])

    def test_a_contract_that_cites_a_product_record_must_be_in_its_affects(self):
        files = {
            "docs/decisions/0010-first.md": record("0010", "category: behavior\nstatus: proposed\naffects: [tui]\n"),
            "contracts/plan/decoder/contract.md": "Follows [0010].\n",
        }
        problems, _ = run(files)
        self.assertProblem(problems, "the contract of plan/decoder cites this record")

    def test_a_contract_may_cite_architecture_and_process_records(self):
        files = {
            "docs/decisions/0010-first.md": record("0010", "category: architecture\nstatus: proposed\n"),
            "docs/decisions/0020-second.md": record("0020", "category: regenerative-process\nstatus: proposed\n"),
            "contracts/plan/decoder/contract.md": "See [0010] and ADR 0020.\n",
        }
        problems, _ = run(files)
        self.assertEqual(problems, [])

    def test_a_file_mode_is_not_a_citation(self):
        files = {
            "docs/decisions/0640-first.md": record("0640", "category: behavior\nstatus: proposed\naffects: [tui]\n"),
            "contracts/plan/decoder/contract.md": "Writes the file with mode 0640.\n",
        }
        problems, _ = run(files)
        self.assertEqual(problems, [])

    def test_a_listed_component_that_does_not_cite_the_record_is_only_a_note(self):
        files = {
            "docs/decisions/0010-first.md": record("0010", "category: behavior\nstatus: proposed\naffects: [plan/decoder]\n"),
            "contracts/plan/decoder/contract.md": "No citation here.\n",
        }
        problems, notes = run(files)
        self.assertEqual(problems, [])
        self.assertEqual(notes, ["0010-first.md: contracts of plan/decoder do not cite it"])

    def test_a_map_of_components_is_read_as_well_as_a_list(self):
        problems, _ = run(
            {"docs/decisions/0010-first.md": record("0010", "category: behavior\nstatus: proposed\naffects: [plan/decoder]\n")},
            architecture="components:\n  plan/decoder:\n    kind: core\n",
        )
        self.assertEqual(problems, [])

    def test_a_project_without_an_architecture_file_fails_and_the_message_names_the_path(self):
        problems, _ = run(
            {"docs/decisions/0010-first.md": record("0010", "category: operations\nstatus: proposed\n")},
            architecture=None,
        )
        self.assertProblem(problems, "architecture.yaml does not exist")

    def test_a_project_with_neither_decisions_nor_architecture_still_fails(self):
        problems, _ = run({}, architecture=None)
        self.assertProblem(problems, "architecture.yaml does not exist")

    def test_the_framework_flag_skips_the_architecture_requirement(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "docs/decisions/0010-first.md"
            path.parent.mkdir(parents=True)
            path.write_text(record("0010", "category: regenerative-process\nstatus: proposed\n"))
            problems, _ = check.check(Path(root), require_architecture=False)
        self.assertEqual(problems, [])

    def test_a_project_with_no_decisions_folder_passes(self):
        problems, _ = run({})
        self.assertEqual(problems, [])


BEHAVIOR = "category: behavior\nstatus: accepted\napproval: person\naffects: [tui]\n"


def principles(records="0010", approval="person", reviewed="2026-11-10"):
    return (
        f"---\napproval: {approval}\nreviewed: {reviewed}\n---\n\n# Product principles\n\n## Principles\n\n"
        f"### P1. Ground claims\n\nPrefer cited facts.\n\nRecords: {records}\n"
    )


PRINCIPLES_PATH = "docs/reference/product-principles.md"


class ApprovalSettings(unittest.TestCase):
    def assertProblem(self, problems, fragment):
        self.assertTrue(any(fragment in each for each in problems), f"{fragment!r} not in {problems}")

    def project(self, config="", local=None):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root) / ".threnos"
            base.mkdir()
            (Path(root) / "architecture.yaml").write_text(ARCHITECTURE)
            (base / "config.toml").write_text(config)
            if local is not None:
                (base / "local.toml").write_text(local)
            return check.settings_problems(Path(root)), check.check(Path(root))[0]

    def test_a_valid_list_passes(self):
        (problems, warnings), record_problems = self.project('[approvals]\nprinciples = ["person", "agent"]\n')
        self.assertEqual((problems, warnings, record_problems), ([], [], []))

    def test_a_file_that_does_not_parse_is_reported_not_raised(self):
        (problems, _), record_problems = self.project("[approvals\n")
        self.assertProblem(problems, "config.toml:")
        self.assertProblem(record_problems, "config.toml:")

    def test_an_unknown_gate_is_reported(self):
        (problems, _), _ = self.project('[approvals]\nghost = ["agent"]\n')
        self.assertProblem(problems, "approvals.ghost is not a gate")

    def test_an_empty_list_is_reported(self):
        (problems, _), _ = self.project("[approvals]\nprinciples = []\n")
        self.assertProblem(problems, "non-empty list")

    def test_an_unknown_approver_is_reported(self):
        (problems, _), _ = self.project('[approvals]\nprinciples = ["robot"]\n')
        self.assertProblem(problems, "non-empty list")

    def test_agent_alone_warns(self):
        (problems, warnings), _ = self.project('[approvals]\nprinciples = ["agent"]\n')
        self.assertEqual(problems, [])
        self.assertProblem(warnings, "lists only agent")

    def test_the_user_file_may_set_approvals_only(self):
        (problems, _), _ = self.project("", local='[rules]\nregenerative = "ejected"\n')
        self.assertProblem(problems, "rules is project-only")

    def test_a_bad_value_in_the_user_file_is_reported(self):
        (problems, _), _ = self.project("", local='[approvals]\nprinciples = []\n')
        self.assertProblem(problems, "local.toml: approvals.principles")

    def test_the_record_check_ignores_the_user_file(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root) / ".threnos"
            base.mkdir()
            (base / "local.toml").write_text('[approvals]\nprinciples = ["agent"]\n')
            for name, text in {
                "architecture.yaml": ARCHITECTURE,
                "docs/decisions/0010-first.md": record("0010", BEHAVIOR),
                PRINCIPLES_PATH: principles(approval="agent"),
            }.items():
                path = Path(root) / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            problems, _ = check.check(Path(root))
        self.assertProblem(problems, "approval agent is not in approvals.principles ['person']")


class PrincipleFile(unittest.TestCase):
    def assertProblem(self, problems, fragment):
        self.assertTrue(any(fragment in each for each in problems), f"{fragment!r} not in {problems}")

    def run_files(self, files, config=None):
        files = dict(files)
        if config is not None:
            files[".threnos/config.toml"] = config
        problems, _ = run(files)
        return problems

    def decisions(self, extra=None):
        files = {"docs/decisions/0010-first.md": record("0010", BEHAVIOR)}
        files.update(extra or {})
        return files

    def test_a_consistent_file_passes(self):
        self.assertEqual(self.run_files(self.decisions({PRINCIPLES_PATH: principles()})), [])

    def test_no_file_means_no_principle_checks(self):
        self.assertEqual(self.run_files(self.decisions()), [])

    def test_a_cited_record_must_exist(self):
        problems = self.run_files(self.decisions({PRINCIPLES_PATH: principles(records="0010, 0099")}))
        self.assertProblem(problems, "P1 cites 0099, which is not a record")

    def test_a_superseded_record_cannot_be_cited(self):
        files = self.decisions({
            "docs/decisions/0020-second.md": record(
                "0020", "category: behavior\nstatus: superseded\napproval: person\naffects: [tui]\nsuperseded-by: ['0010']\n"
            ),
            PRINCIPLES_PATH: principles(records="0010, 0020"),
        })
        files["docs/decisions/0010-first.md"] = record("0010", BEHAVIOR + "supersedes: ['0020']\n")
        self.assertProblem(self.run_files(files), "cites 0020, which is superseded")

    def test_an_accepted_behavior_record_must_be_cited_or_excused(self):
        files = self.decisions({
            "docs/decisions/0020-second.md": record("0020", BEHAVIOR),
            PRINCIPLES_PATH: principles(),
        })
        self.assertProblem(self.run_files(files), "0020-second.md: no principle cites this record")
        files["docs/decisions/0020-second.md"] = record("0020", BEHAVIOR + "principle: none\n")
        self.assertEqual(self.run_files(files), [])

    def test_a_proposed_behavior_record_needs_no_citation(self):
        files = self.decisions({
            "docs/decisions/0020-second.md": record("0020", "category: behavior\nstatus: proposed\naffects: []\n"),
            PRINCIPLES_PATH: principles(),
        })
        self.assertEqual(self.run_files(files), [])

    def test_principle_none_belongs_on_behavior_records_only(self):
        files = self.decisions({
            "docs/decisions/0020-second.md": record("0020", "category: operations\nstatus: proposed\nprinciple: none\n"),
        })
        self.assertProblem(self.run_files(files), "principle may only be none")

    def test_a_principle_needs_a_records_line(self):
        text = principles().replace("Records: 0010\n", "")
        self.assertProblem(self.run_files(self.decisions({PRINCIPLES_PATH: text})), "P1 has no Records line")

    def test_front_matter_is_required_and_the_date_must_parse(self):
        no_front = self.run_files(self.decisions({PRINCIPLES_PATH: "# Product principles\n"}))
        self.assertProblem(no_front, "no front matter")
        bad_date = self.run_files(self.decisions({PRINCIPLES_PATH: principles(reviewed="soon")}))
        self.assertProblem(bad_date, "reviewed must be a date")

    def test_an_agent_approval_passes_only_when_the_project_allows_it(self):
        files = self.decisions({PRINCIPLES_PATH: principles(approval="agent")})
        self.assertProblem(self.run_files(files), "A person ratifies it")
        self.assertEqual(self.run_files(files, config='[approvals]\nprinciples = ["person", "agent"]\n'), [])


OPERATIONS = "category: operations\nstatus: accepted\n"
AGENT_AUTHOR = "author: {kind: agent, harness: claude-code, session: aaa}\n"
AGENT_APPROVER = "approver: {kind: agent, harness: claude-code, session: bbb}\n"


class DecisionGate(unittest.TestCase):
    def assertProblem(self, problems, fragment):
        self.assertTrue(any(fragment in each for each in problems), f"{fragment!r} not in {problems}")

    def run_records(self, front, config=None):
        files = {"docs/decisions/0010-first.md": record("0010", front)}
        if config is not None:
            files[".threnos/config.toml"] = config
        return run(files)

    def test_a_person_approval_passes_by_default(self):
        problems, _ = self.run_records(OPERATIONS + "approval: person\n")
        self.assertEqual(problems, [])

    def test_an_agent_approval_fails_unless_the_project_allows_it(self):
        front = OPERATIONS + "approval: agent\n" + AGENT_APPROVER + AGENT_AUTHOR
        problems, _ = self.run_records(front)
        self.assertProblem(problems, "approval agent is not in approvals.decisions ['person']")
        self.assertProblem(problems, "A person ratifies it")
        problems, _ = self.run_records(front, '[approvals]\ndecisions = ["person", "agent"]\n')
        self.assertEqual(problems, [])

    def test_a_proposed_record_is_not_gated(self):
        problems, _ = self.run_records("category: operations\nstatus: proposed\napproval: agent\n")
        self.assertEqual(problems, [])

    def test_an_agent_approval_needs_both_parties(self):
        config = '[approvals]\ndecisions = ["agent"]\n'
        problems, _ = self.run_records(OPERATIONS + "approval: agent\n", config)
        self.assertProblem(problems, "approval agent needs approver")
        self.assertProblem(problems, "approval agent needs author")

    def test_the_approver_may_not_be_the_authors_session(self):
        config = '[approvals]\ndecisions = ["agent"]\n'
        same = "approver: {kind: agent, harness: claude-code, session: aaa}\n"
        problems, _ = self.run_records(OPERATIONS + "approval: agent\n" + same + AGENT_AUTHOR, config)
        self.assertProblem(problems, "the approving agent is the author's session")

    def test_a_person_may_approve_what_an_agent_wrote(self):
        front = OPERATIONS + "approval: person\napprover: {kind: person, name: Dana}\n" + AGENT_AUTHOR
        problems, _ = self.run_records(front)
        self.assertEqual(problems, [])

    def test_the_approver_kind_must_match_the_approval(self):
        front = OPERATIONS + "approval: person\n" + AGENT_APPROVER
        problems, _ = self.run_records(front, '[approvals]\ndecisions = ["person"]\n')
        self.assertProblem(problems, "approver kind agent does not match approval person")

    def test_a_malformed_party_is_reported(self):
        problems, _ = self.run_records(OPERATIONS + "approval: person\napprover: {kind: robot}\n")
        self.assertProblem(problems, "approver kind 'robot'")

    def test_unrecorded_passes_and_is_counted(self):
        problems, notes = self.run_records(OPERATIONS + "approval: unrecorded\n")
        self.assertEqual(problems, [])
        self.assertIn("0010-first.md: approval is unrecorded", notes)

    def test_decisions_is_a_known_gate_and_the_default_list_applies_without_config(self):
        self.assertEqual(check.approvals_problems({"approvals": {"decisions": ["person", "agent"]}}, "c"), [])
        self.assertTrue(check.approvals_problems({"approvals": {"decisions": []}}, "c"))


if __name__ == "__main__":
    unittest.main()
