import unittest

import check

MODULE = "example.com/app"
RULES = {"tests_root": "contract-tests", "components_root": "internal", "model": "internal/model", "may_import": []}
RUNNER = "contract-tests/runner/plan/decoder"
WIRING = "contract-tests/wiring/plan/decoder"
HARNESS = "contract-tests/harness"


def run(directory, imports, **rules):
    return check.violations({directory: set(imports)}, MODULE, {**RULES, **rules})


class ContractImports(unittest.TestCase):
    def test_the_standard_library_is_allowed_everywhere(self):
        for directory in (RUNNER, WIRING, HARNESS):
            self.assertEqual(run(directory, ["testing", "os", "encoding/json"]), [])

    def test_a_runner_may_import_the_model_and_the_harness(self):
        self.assertEqual(run(RUNNER, [MODULE + "/internal/model", MODULE + "/contract-tests/harness"]), [])

    def test_a_runner_may_not_import_a_component(self):
        self.assertEqual(
            run(RUNNER, [MODULE + "/internal/plan/decoder"]),
            [(RUNNER, MODULE + "/internal/plan/decoder")],
        )

    def test_a_runner_may_not_import_a_wiring_package_or_a_neighbors_runner(self):
        found = run(RUNNER, [MODULE + "/contract-tests/wiring/plan/decoder", MODULE + "/contract-tests/runner/plan/encoder"])
        self.assertEqual(len(found), 2)

    def test_a_harness_may_import_the_model_and_listed_libraries_only(self):
        self.assertEqual(run(HARNESS, [MODULE + "/internal/model/sub"]), [])
        self.assertEqual(run(HARNESS, ["github.com/a/b"]), [(HARNESS, "github.com/a/b")])
        self.assertEqual(run(HARNESS, ["github.com/a/b"], may_import=["github.com/a/b"]), [])

    def test_a_harness_may_not_import_a_component(self):
        self.assertEqual(
            run(HARNESS, [MODULE + "/internal/plan/decoder"]),
            [(HARNESS, MODULE + "/internal/plan/decoder")],
        )

    def test_wiring_may_import_its_own_component_and_its_own_runner(self):
        imports = [MODULE + "/internal/plan/decoder", MODULE + "/contract-tests/runner/plan/decoder"]
        self.assertEqual(run(WIRING, imports), [])

    def test_wiring_may_import_the_packages_below_its_component(self):
        self.assertEqual(run(WIRING, [MODULE + "/internal/plan/decoder/sub"]), [])

    def test_wiring_may_not_import_another_component_the_model_or_the_harness(self):
        found = run(WIRING, [
            MODULE + "/internal/plan/encoder",
            MODULE + "/internal/plan/decoderx",
            MODULE + "/internal/model",
            MODULE + "/contract-tests/harness",
            MODULE + "/contract-tests/runner/plan/encoder",
        ])
        self.assertEqual(len(found), 5)

    def test_wiring_may_not_use_a_listed_library(self):
        self.assertEqual(run(WIRING, ["github.com/a/b"], may_import=["github.com/a/b"]), [(WIRING, "github.com/a/b")])

    def test_a_folder_under_the_tests_root_with_no_role_is_checked_strictly(self):
        self.assertEqual(
            run("contract-tests/other", [MODULE + "/internal/model", "testing"]),
            [("contract-tests/other", MODULE + "/internal/model")],
        )

    def test_cgo_and_unsafe_are_ignored(self):
        self.assertEqual(run(RUNNER, ["C", "unsafe"]), [])

    def test_the_roots_come_from_architecture_yaml(self):
        rules = check.rules_from({"contract_tests_root": "judge", "components_root": "src/parts", "model": "src/model"})
        self.assertEqual(rules["tests_root"], "judge")
        self.assertEqual(check.violations({"judge/wiring/a/b": {MODULE + "/src/parts/a/b"}}, MODULE, rules), [])
        self.assertEqual(
            check.violations({"judge/runner/a/b": {MODULE + "/src/model"}}, MODULE, rules),
            [],
        )


if __name__ == "__main__":
    unittest.main()
