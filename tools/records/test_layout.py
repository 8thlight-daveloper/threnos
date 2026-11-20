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
            "acceptance/testdata/plan.yaml": "a: 1\n",
            "acceptance/runner/main.go": "package runner\n",
        }
        self.assertEqual(problems(files), [])

    def test_scenarios_with_no_runner_fail(self):
        found = problems({"acceptance/scenarios/assemble.yaml": "name: assemble\n"})
        self.assertProblem(found, "nothing runs them")

    def test_a_readme_alone_is_not_a_runner(self):
        found = problems({"acceptance/scenarios/a.yaml": "", "acceptance/runner/README.md": ""})
        self.assertProblem(found, "nothing runs them")

    def test_source_files_beside_the_folders_fail(self):
        found = problems({"acceptance/landline_test.go": "package acceptance\n"})
        self.assertProblem(found, "acceptance/landline_test.go: acceptance holds only")

    def test_a_folder_outside_the_three_fails(self):
        found = problems({"acceptance/helpers/x.go": ""})
        self.assertProblem(found, "acceptance/helpers: acceptance holds only")

    def test_source_in_testdata_fails(self):
        found = problems({"acceptance/testdata/helper.go": ""})
        self.assertProblem(found, "testdata holds data, not source files")

    def test_source_in_data_scenarios_fails(self):
        found = problems({"acceptance/scenarios/a_test.go": ""})
        self.assertProblem(found, "scenarios are data in this project")

    def test_code_scenarios_pass_with_a_runner(self):
        files = {
            "acceptance/scenarios/menubar_test.go": "package scenarios\n",
            "acceptance/runner/driver.go": "package runner\n",
            "acceptance/testdata/legacy/a.md": "x\n",
        }
        self.assertEqual(problems(files, {"acceptance": {"scenarios": "code"}}), [])

    def test_code_scenarios_with_no_runner_fail(self):
        found = problems({"acceptance/scenarios/menubar_test.go": ""}, {"acceptance": {"scenarios": "code"}})
        self.assertProblem(found, "nothing runs them")

    def test_an_unknown_form_fails(self):
        found = problems({"acceptance/scenarios/a.yaml": ""}, {"acceptance": {"scenarios": "both"}})
        self.assertProblem(found, "acceptance.scenarios is 'both'")


if __name__ == "__main__":
    unittest.main()
