package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func writeFile(t *testing.T, root string, name string, text string) {
	t.Helper()
	path := filepath.Join(root, filepath.FromSlash(name))
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(text), 0o644); err != nil {
		t.Fatal(err)
	}
}

func splitProject(t *testing.T) string {
	t.Helper()
	root := t.TempDir()
	writeFile(t, root, "internal/noun/role/role.go", "package role")
	writeFile(t, root, "contracts/specifications/noun/role/contract.md", "spec")
	writeFile(t, root, "contracts/fixtures/noun/role/cases.json", "[]")
	writeFile(t, root, "contract-tests/runner/noun/role/suite.go", "package role")
	writeFile(t, root, "contract-tests/wiring/noun/role/wire_test.go", "package role")
	writeFile(t, root, "contract-tests/harness/load.go", "package harness")
	return root
}

func TestTheWiringPackageRunsTheTests(t *testing.T) {
	place := defaultLayout()
	if got, want := contractPathFrom(place, "noun/role"), "../../../contract-tests/wiring/noun/role/"; got != want {
		t.Errorf("contractPathFrom = %q, want %q", got, want)
	}
}

func TestACustomTestsFolderMovesTheWiringPackage(t *testing.T) {
	place := layout{components: "src/parts", contracts: "specs", tests: "judge"}
	if got, want := contractPathFrom(place, "record/joiner"), "../../../../judge/wiring/record/joiner/"; got != want {
		t.Errorf("contractPathFrom = %q, want %q", got, want)
	}
}

func TestAComponentNeedsAWiringPackage(t *testing.T) {
	root := splitProject(t)
	place := defaultLayout()
	if err := checkComponent(root, place, "noun/role"); err != nil {
		t.Fatal(err)
	}
	if err := os.RemoveAll(filepath.Join(root, "contract-tests", "wiring")); err != nil {
		t.Fatal(err)
	}
	err := checkComponent(root, place, "noun/role")
	if err == nil || !strings.Contains(err.Error(), "contract-tests/wiring/noun/role is not a folder") {
		t.Fatalf("got %v", err)
	}
}

func TestSuiteDigestCoversEveryFolderAndTheHarness(t *testing.T) {
	root := splitProject(t)
	place := defaultLayout()
	first, err := suiteDigest(root, place, "noun/role")
	if err != nil {
		t.Fatal(err)
	}
	for _, name := range []string{
		"contracts/specifications/noun/role/contract.md",
		"contracts/fixtures/noun/role/cases.json",
		"contract-tests/runner/noun/role/suite.go",
		"contract-tests/wiring/noun/role/wire_test.go",
		"contract-tests/harness/load.go",
	} {
		original, err := os.ReadFile(filepath.Join(root, filepath.FromSlash(name)))
		if err != nil {
			t.Fatal(err)
		}
		writeFile(t, root, name, "changed")
		changed, err := suiteDigest(root, place, "noun/role")
		if err != nil {
			t.Fatal(err)
		}
		if changed == first {
			t.Errorf("a change to %s kept the digest", name)
		}
		writeFile(t, root, name, string(original))
	}
}

func TestSuiteDigestIgnoresAnotherComponent(t *testing.T) {
	root := splitProject(t)
	place := defaultLayout()
	first, _ := suiteDigest(root, place, "noun/role")
	writeFile(t, root, "contracts/fixtures/noun/other/cases.json", "[1]")
	second, _ := suiteDigest(root, place, "noun/role")
	if first != second {
		t.Error("another component's fixtures changed this component's digest")
	}
}

func TestAMissingHarnessDoesNotStopTheDigest(t *testing.T) {
	root := splitProject(t)
	if err := os.RemoveAll(filepath.Join(root, "contract-tests", "harness")); err != nil {
		t.Fatal(err)
	}
	if _, err := suiteDigest(root, defaultLayout(), "noun/role"); err != nil {
		t.Fatal(err)
	}
}
