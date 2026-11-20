package main

import (
	"fmt"
	"path"
	"path/filepath"
	"strings"
)

type layout struct {
	components  string
	contracts   string
	tests       string
	accepted    string
	gomuVersion string
}

func defaultLayout() layout {
	return layout{
		components:  "internal",
		contracts:   "contracts",
		tests:       "contract-tests",
		accepted:    "tools/mutation/accepted",
		gomuVersion: "v0.3.0",
	}
}

func (place layout) normalized() (layout, error) {
	folders := []struct {
		flag  string
		value *string
	}{
		{"--components", &place.components},
		{"--contracts", &place.contracts},
		{"--contract-tests", &place.tests},
		{"--accepted", &place.accepted},
	}
	for _, each := range folders {
		clean := path.Clean(filepath.ToSlash(*each.value))
		if !insideProject(clean) {
			return layout{}, fmt.Errorf("%s must be a folder inside the project, got %q", each.flag, *each.value)
		}
		*each.value = clean
	}
	return place, nil
}

// testPackage is the folder, relative to the project, of the package whose tests judge a component. It is the wiring
// package of record 0150, because that package holds the test that calls the suite.
func (place layout) testPackage(component string) string {
	return path.Join(place.tests, "wiring", component)
}

// suiteFolders are the folders whose content decides a component's results. A change in any of them changes the cache
// key. The harness is shared, so a change there invalidates every component.
func (place layout) suiteFolders(component string) []string {
	return []string{
		path.Join(place.contracts, "specifications", component),
		path.Join(place.contracts, "fixtures", component),
		path.Join(place.tests, "runner", component),
		path.Join(place.tests, "wiring", component),
		path.Join(place.tests, "harness"),
	}
}

func insideProject(clean string) bool {
	return !path.IsAbs(clean) && clean != ".." && !strings.HasPrefix(clean, "../")
}

func segments(clean string) int {
	if clean == "." {
		return 0
	}
	return len(strings.Split(clean, "/"))
}
