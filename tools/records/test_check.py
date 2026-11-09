import tempfile
import unittest
from pathlib import Path

import check

ARCHITECTURE = "components:\n  - name: plan/decoder\n  - name: tui\n"


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
            "docs/decisions/0030-third.md": record("0030", "category: operations\nstatus: accepted\napproval: agent\n"),
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


if __name__ == "__main__":
    unittest.main()
