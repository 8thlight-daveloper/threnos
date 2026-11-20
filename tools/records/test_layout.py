import tempfile
import unittest
from pathlib import Path

import layout


def build(files):
    root = tempfile.TemporaryDirectory()
    for name, text in files.items():
        path = Path(root.name) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


def problems(files, architecture=None):
    root = build(files)
    with root:
        return layout.acceptance_problems(Path(root.name), architecture or {})


class AcceptanceLayout(unittest.TestCase):
    def assertProblem(self, found, fragment):
        self.assertTrue(any(fragment in each for each in found), f"{fragment!r} not in {found}")

    def test_a_project_without_acceptance_has_no_problems(self):
        self.assertEqual(problems({"README.md": ""}), [])

    def test_the_seeded_examples_alone_pass(self):
        self.assertEqual(problems({"acceptance/scenarios/example-command.yaml.example": ""}), [])

    def test_data_scenarios_with_a_runner_pass(self):
        files = {
            "acceptance/scenarios/assemble.yaml": "name: assemble\n",
            "acceptance/fixtures/plan.yaml": "a: 1\n",
            "acceptance/runner/main.go": "package runner\n",
        }
        self.assertEqual(problems(files), [])

    def test_scenarios_with_no_runner_fail(self):
        found = problems({"acceptance/scenarios/assemble.yaml": "name: assemble\n"})
        self.assertProblem(found, "nothing runs them")

    def test_a_readme_alone_is_not_a_runner(self):
        found = problems({"acceptance/scenarios/a.yaml": "", "acceptance/runner/README.md": ""})
        self.assertProblem(found, "nothing runs them")

    def test_the_old_testdata_folder_is_pointed_at_fixtures(self):
        found = problems({"acceptance/testdata/a.json": "{}"})
        self.assertProblem(found, "record 0150 renames it to fixtures/")

    def test_source_files_beside_the_folders_fail(self):
        found = problems({"acceptance/landline_test.go": "package acceptance\n"})
        self.assertProblem(found, "acceptance/landline_test.go: acceptance holds only")

    def test_a_folder_outside_the_three_fails(self):
        found = problems({"acceptance/helpers/x.go": ""})
        self.assertProblem(found, "acceptance/helpers: acceptance holds only")

    def test_source_in_fixtures_fails(self):
        found = problems({"acceptance/fixtures/helper.go": ""})
        self.assertProblem(found, "fixtures hold data, not source files")

    def test_source_in_data_scenarios_fails(self):
        found = problems({"acceptance/scenarios/a_test.go": ""})
        self.assertProblem(found, "scenarios are YAML data in this project")

    def test_any_non_yaml_file_in_data_scenarios_fails_whatever_the_language(self):
        found = problems({"acceptance/scenarios/a.rb": "", "acceptance/scenarios/b.exs": ""})
        self.assertEqual(len([each for each in found if "scenarios are YAML data" in each]), 2)

    def test_code_scenarios_pass_with_a_runner(self):
        files = {
            "acceptance/scenarios/menubar_test.go": "package scenarios\n",
            "acceptance/runner/driver.go": "package runner\n",
            "acceptance/fixtures/legacy/a.md": "x\n",
        }
        self.assertEqual(problems(files, {"acceptance": {"scenarios": "code"}}), [])

    def test_code_scenarios_with_no_runner_fail(self):
        found = problems({"acceptance/scenarios/menubar_test.go": ""}, {"acceptance": {"scenarios": "code"}})
        self.assertProblem(found, "nothing runs them")

    def test_an_unknown_form_fails(self):
        found = problems({"acceptance/scenarios/a.yaml": ""}, {"acceptance": {"scenarios": "both"}})
        self.assertProblem(found, "acceptance.scenarios is 'both'")


SPLIT = {
    "contracts/specifications/plan/decoder/contract.md": "Decodes.\n",
    "contracts/fixtures/plan/decoder/cases.json": "[]\n",
    "contract-tests/runner/plan/decoder/suite.go": "package decoder\n",
    "contract-tests/wiring/plan/decoder/wire_test.go": "package decoder\n",
    "contract-tests/harness/load.go": "package harness\n",
}


def contract_problems(files, architecture=None):
    root = build(files)
    with root:
        return layout.contracts_problems(Path(root.name), architecture or {})


class ContractLayout(unittest.TestCase):
    def assertProblem(self, found, fragment):
        self.assertTrue(any(fragment in each for each in found), f"{fragment!r} not in {found}")

    def test_a_project_with_neither_folder_has_no_problems(self):
        self.assertEqual(contract_problems({"README.md": ""}), [])

    def test_one_folder_per_contract_is_no_longer_accepted(self):
        found = contract_problems({"contracts/plan/decoder/contract.md": "x\n", "contracts/plan/decoder/a.go": ""})
        self.assertProblem(found, "contracts/plan: contracts/ holds only specifications/, fixtures/")

    def test_a_complete_split_layout_passes(self):
        self.assertEqual(contract_problems(SPLIT), [])

    def test_a_missing_mirror_is_reported_for_each_folder(self):
        for gone in ("contracts/fixtures/plan/decoder/cases.json", "contract-tests/runner/plan/decoder/suite.go", "contract-tests/wiring/plan/decoder/wire_test.go"):
            files = {name: text for name, text in SPLIT.items() if name != gone}
            found = contract_problems(files)
            self.assertProblem(found, "the contract of plan/decoder has nothing here")

    def test_a_path_with_no_specification_is_an_orphan(self):
        files = dict(SPLIT)
        files["contract-tests/wiring/plan/encoder/wire_test.go"] = ""
        self.assertProblem(contract_problems(files), "contract-tests/wiring/plan/encoder: no specification")

    def test_source_in_specifications_is_reported_whatever_the_language(self):
        files = dict(SPLIT)
        files["contracts/specifications/plan/decoder/api.rb"] = ""
        self.assertProblem(contract_problems(files), "specifications hold Markdown only")

    def test_a_fixture_must_be_a_data_suffix_unless_the_project_adds_it(self):
        files = dict(SPLIT)
        files["contracts/fixtures/plan/decoder/golden.out"] = ""
        self.assertProblem(contract_problems(files), "fixtures hold data")
        self.assertEqual(contract_problems(files, {"contracts": {"fixture_suffixes": ["out"]}}), [])

    def test_code_beside_the_folders_is_reported(self):
        files = dict(SPLIT)
        files["contracts/helper.go"] = ""
        files["contract-tests/other/x.go"] = ""
        found = contract_problems(files)
        self.assertProblem(found, "contracts/helper.go: contracts/ holds only")
        self.assertProblem(found, "contract-tests/other: contract-tests/ holds only")

    def test_a_markdown_file_with_no_contract_is_reported(self):
        files = dict(SPLIT)
        files["contracts/specifications/plan/notes/readme-ish.md"] = "x\n"
        self.assertProblem(contract_problems(files), "no contract.md in this folder or above it")

    def test_the_roots_come_from_architecture_yaml(self):
        files = {name.replace("contract-tests", "judge").replace("contracts/", "specs/"): text for name, text in SPLIT.items()}
        self.assertEqual(contract_problems(files, {"contracts_root": "specs", "contract_tests_root": "judge"}), [])


if __name__ == "__main__":
    unittest.main()
