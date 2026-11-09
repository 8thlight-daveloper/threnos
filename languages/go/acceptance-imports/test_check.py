import unittest

import check

MODULE = "example.com/app"


def run(imports, may_import=()):
    return check.violations({"acceptance": set(imports)}, MODULE, list(may_import))


class AcceptanceImports(unittest.TestCase):
    def test_the_standard_library_is_allowed(self):
        self.assertEqual(run(["os", "testing", "path/filepath", "os/exec"]), [])

    def test_a_project_package_is_a_violation(self):
        self.assertEqual(run([MODULE + "/internal/session"]), [("acceptance", MODULE + "/internal/session")])

    def test_the_module_root_package_is_a_violation(self):
        self.assertEqual(run([MODULE]), [("acceptance", MODULE)])

    def test_packages_under_acceptance_are_allowed(self):
        self.assertEqual(run([MODULE + "/acceptance/runner", MODULE + "/acceptance"]), [])

    def test_a_package_that_only_starts_with_acceptance_is_not_under_it(self):
        self.assertEqual(run([MODULE + "/acceptancex"]), [("acceptance", MODULE + "/acceptancex")])

    def test_a_third_party_package_needs_a_listing(self):
        self.assertEqual(run(["github.com/hinshun/vt10x"]), [("acceptance", "github.com/hinshun/vt10x")])
        self.assertEqual(run(["github.com/hinshun/vt10x"], ["github.com/hinshun/vt10x"]), [])

    def test_a_listing_allows_the_packages_below_it_but_not_a_sibling(self):
        self.assertEqual(run(["github.com/a/b/c"], ["github.com/a/b"]), [])
        self.assertEqual(run(["github.com/a/bc"], ["github.com/a/b"]), [("acceptance", "github.com/a/bc")])

    def test_a_listed_project_package_is_allowed(self):
        self.assertEqual(run([MODULE + "/internal/version"], [MODULE + "/internal/version"]), [])

    def test_cgo_and_unsafe_are_ignored(self):
        self.assertEqual(run(["C", "unsafe"]), [])


if __name__ == "__main__":
    unittest.main()
