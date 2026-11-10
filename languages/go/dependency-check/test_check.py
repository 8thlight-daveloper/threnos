import shutil
import tempfile
import unittest
from pathlib import Path

import check

MODULE = "example.com/app"

ARCHITECTURE = {
    "components_root": "internal",
    "model": "model",
    "banned_in_core": ["filesystem", "network", "process", "terminal", "clock", "randomness", "environment"],
    "drivers": ["reader"],
    "libraries": {"terminal": ["charm.land/bubbletea/v2"]},
    "naming": {"component_path": "<role>", "segment_pattern": "^[a-z][a-z0-9]*$"},
    "components": [
        {"name": "analyzer", "position": 1, "depends_on": []},
        {"name": "planner", "position": 2, "depends_on": ["analyzer"]},
        {"name": "reader", "position": 2, "depends_on": ["analyzer"]},
        {"name": "shell", "position": 3, "depends_on": ["planner", "reader"]},
    ],
}


def rules(**changes):
    return check.Rules({**ARCHITECTURE, **changes})


def run(packages, **changes):
    return check.violations({k: set(v) for k, v in packages.items()}, MODULE, rules(**changes))


def own(path):
    return f"{MODULE}/{path}"


class Imports(unittest.TestCase):
    def assertOne(self, found, directory, fragment):
        self.assertEqual(len(found), 1, found)
        self.assertEqual(found[0][0], directory)
        self.assertIn(fragment, found[0][1])

    def test_a_clean_graph_has_no_violations(self):
        self.assertEqual(run({
            "internal/analyzer": ["fmt", "strings"],
            "internal/planner": [own("internal/analyzer"), own("model")],
            "internal/shell": [own("internal/planner"), own("internal/reader")],
            "internal/reader": ["os", own("internal/analyzer")],
        }), [])

    def test_an_import_outside_depends_on_is_reported(self):
        found = run({"internal/shell": [own("internal/analyzer")]})
        self.assertOne(found, "internal/shell", "not in depends_on of shell")

    def test_an_import_of_a_later_position_is_reported(self):
        found = run({"internal/analyzer": [own("internal/planner")]})
        self.assertEqual(len(found), 2)
        self.assertTrue(any("not in depends_on" in message for _, message in found))
        self.assertTrue(any("not earlier than analyzer" in message for _, message in found))

    def test_two_components_at_one_position_may_not_depend_on_each_other(self):
        found = run({"internal/planner": [own("internal/reader")]})
        self.assertTrue(any("position 2, not earlier than planner at position 2" in m for _, m in found))

    def test_a_package_inside_a_component_belongs_to_it(self):
        self.assertEqual(run({"internal/planner/rules": [own("internal/analyzer/deep"), own("internal/planner")]}), [])
        found = run({"internal/planner/rules": [own("internal/shell/deep")]})
        self.assertTrue(any("not earlier" in message for _, message in found))

    def test_a_package_under_the_root_with_no_component_is_reported(self):
        found = run({"internal/release": ["os"]})
        self.assertOne(found, "internal/release", "belongs to no component")

    def test_an_import_of_an_unowned_package_is_reported(self):
        found = run({"internal/planner": [own("internal/release")]})
        self.assertOne(found, "internal/planner", "belongs to no component")

    def test_an_import_outside_the_components_and_the_model_is_reported(self):
        found = run({"internal/planner": [own("binary")]})
        self.assertOne(found, "internal/planner", "outside the components and the model")

    def test_the_entry_point_is_not_checked(self):
        self.assertEqual(run({"binary": [own("internal/shell"), own("internal/analyzer"), "os"]}), [])

    def test_the_model_may_not_import_a_component(self):
        found = run({"model": [own("internal/analyzer")]})
        self.assertOne(found, "model", "is the model and imports component analyzer")

    def test_the_model_is_core(self):
        found = run({"model": ["os"]})
        self.assertOne(found, "model", "banned in core (filesystem, environment)")


class Categories(unittest.TestCase):
    def test_a_core_component_may_not_import_a_banned_library(self):
        for path, category in [("os", "filesystem"), ("io/fs", "filesystem"), ("net/http", "network"),
                               ("os/exec", "process"), ("math/rand", "randomness"), ("runtime/debug", "environment")]:
            found = run({"internal/analyzer": [path]})
            self.assertEqual(len(found), 1, path)
            self.assertIn(category, found[0][1])

    def test_a_project_listed_terminal_library_is_banned_with_its_subpackages(self):
        found = run({"internal/analyzer": ["charm.land/bubbletea/v2", "charm.land/bubbletea/v2/inner"]})
        self.assertEqual(len(found), 2)
        self.assertEqual(run({"internal/analyzer": ["charm.land/bubbletea/v20"]}), [])

    def test_os_does_not_ban_its_neighbors_by_prefix(self):
        self.assertEqual(run({"internal/analyzer": ["osx/tool"]}), [])

    def test_pure_net_packages_are_allowed(self):
        self.assertEqual(run({"internal/analyzer": ["net/url", "net/netip", "net/mail"]}), [])

    def test_a_driver_may_import_banned_libraries(self):
        self.assertEqual(run({"internal/reader": ["os", "os/exec", "io/fs"]}), [])

    def test_a_category_not_listed_is_not_banned(self):
        self.assertEqual(run({"internal/analyzer": ["os"]}, banned_in_core=["network"]), [])

    def test_a_driver_still_follows_depends_on(self):
        found = run({"internal/reader": [own("internal/planner")]})
        self.assertTrue(any("not in depends_on of reader" in message for _, message in found))


class RuleProblems(unittest.TestCase):
    def problems(self, **changes):
        return check.rule_problems(rules(**changes))

    def assertProblem(self, problems, fragment):
        self.assertTrue(any(fragment in each for each in problems), f"{fragment!r} not in {problems}")

    def test_a_consistent_file_has_no_problems(self):
        self.assertEqual(self.problems(), [])

    def test_a_driver_must_be_a_component(self):
        self.assertProblem(self.problems(drivers=["ghost"]), "driver ghost is not a component")

    def test_depends_on_must_name_an_earlier_component(self):
        components = [
            {"name": "analyzer", "position": 2, "depends_on": ["planner", "ghost"]},
            {"name": "planner", "position": 2, "depends_on": []},
        ]
        problems = self.problems(components=components, drivers=[])
        self.assertProblem(problems, "ghost, which is not a component")
        self.assertProblem(problems, "which is not earlier")

    def test_a_flat_name_fails_unless_listed(self):
        naming = {"component_path": "<noun>/<role>", "segment_pattern": "^[a-z][a-z0-9]*$"}
        components = [{"name": "about", "position": 1, "depends_on": []}]
        self.assertProblem(self.problems(naming=naming, components=components, drivers=[]), "component about does not follow")
        listed = {**naming, "exceptions": ["about"]}
        self.assertEqual(self.problems(naming=listed, components=components, drivers=[]), [])

    def test_a_stale_exception_is_reported(self):
        naming = {"component_path": "<role>", "segment_pattern": "^[a-z][a-z0-9]*$", "exceptions": ["analyzer", "ghost"]}
        problems = self.problems(naming=naming)
        self.assertProblem(problems, "analyzer is listed under naming.exceptions but follows")
        self.assertProblem(problems, "naming.exceptions lists ghost")

    def test_a_segment_must_match_the_pattern(self):
        naming = {"component_path": "<noun>/<role>", "segment_pattern": "^[a-z][a-z0-9]*$"}
        components = [{"name": "Repo/reader", "position": 1, "depends_on": []}]
        self.assertProblem(self.problems(naming=naming, components=components, drivers=[]), "does not follow")


@unittest.skipUnless(shutil.which("go"), "go is not installed")
class FromGo(unittest.TestCase):
    def project(self, files):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        (root / "go.mod").write_text(f"module {MODULE}\n\ngo 1.21\n")
        for name, text in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        return root

    def run_all(self, files, **changes):
        root = self.project(files)
        r = rules(**changes)
        imports, listed, problems = check.go_packages(root, r)
        found = problems + check.violations(imports, MODULE, r) + check.clock_violations(listed, r, root)
        return sorted(found)

    def test_a_project_graph_is_read_from_go_list(self):
        found = self.run_all({
            "model/model.go": "package model\n\ntype Section struct{}\n",
            "internal/analyzer/a.go": 'package analyzer\n\nimport _ "example.com/app/model"\n',
            "internal/planner/p.go": 'package planner\n\nimport _ "example.com/app/internal/analyzer"\n',
            "internal/shell/s.go": 'package shell\n\nimport _ "example.com/app/internal/analyzer"\n',
        })
        self.assertEqual(len(found), 1, found)
        self.assertIn("not in depends_on of shell", found[0][1])

    def test_test_files_are_not_checked(self):
        found = self.run_all({
            "internal/analyzer/a.go": "package analyzer\n",
            "internal/analyzer/a_test.go": 'package analyzer\n\nimport _ "os"\nimport _ "example.com/app/internal/shell"\n',
        })
        self.assertEqual(found, [])

    def test_clock_functions_are_found_whatever_the_alias(self):
        found = self.run_all({
            "internal/analyzer/a.go": (
                'package analyzer\n\nimport clk "time"\n\nfunc Stamp() clk.Time { return clk.Now() }\n'
                "var wait = clk.Sleep\n"
            ),
        })
        self.assertEqual(len(found), 2, found)
        self.assertTrue(all("banned in core (clock)" in message for _, message in found))
        self.assertEqual({folder for folder, _ in found}, {"internal/analyzer"})

    def test_time_types_are_allowed_in_core(self):
        found = self.run_all({
            "internal/analyzer/a.go": (
                'package analyzer\n\nimport "time"\n\nfunc Later(at time.Time, by time.Duration) time.Time { return at.Add(by) }\n'
            ),
        })
        self.assertEqual(found, [])

    def test_a_local_variable_named_time_is_not_the_package(self):
        found = self.run_all({
            "internal/analyzer/a.go": 'package analyzer\n\nimport "time"\n\nvar _ time.Duration\n\nfunc F(clock struct{ Now func() }) { clock.Now() }\n',
        })
        self.assertEqual(found, [])

    def test_a_driver_may_read_the_clock(self):
        found = self.run_all({
            "internal/reader/r.go": 'package reader\n\nimport "time"\n\nvar Start = time.Now()\n',
        })
        self.assertEqual(found, [])

    def test_a_dot_import_of_time_is_reported(self):
        found = self.run_all({"internal/analyzer/a.go": 'package analyzer\n\nimport . "time"\n\nvar _ Duration\n'})
        self.assertEqual(len(found), 1, found)
        self.assertIn("dot-imports time", found[0][1])


if __name__ == "__main__":
    unittest.main()
