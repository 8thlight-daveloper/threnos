package main

import (
	"fmt"
	"os"
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
	split       bool
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

// detect reports the layout the project is in. A contracts folder with a specifications folder is the split layout of
// record 0150, where the tests run from contract-tests/wiring/<component>. Otherwise the tests run from
// contracts/<component>.
func (place layout) detect(root string) layout {
	info, err := os.Stat(filepath.Join(root, place.contracts, "specifications"))
	place.split = err == nil && info.IsDir()
	return place
}

// testPackage is the folder, relative to the project, of the package whose tests judge a component.
func (place layout) testPackage(component string) string {
	if place.split {
		return path.Join(place.tests, "wiring", component)
	}
	return path.Join(place.contracts, component)
}

// suiteFolders are the folders whose content decides a component's results. A change in any of them changes the cache
// key. The harness is shared, so a change there invalidates every component.
func (place layout) suiteFolders(component string) []string {
	if !place.split {
		return []string{path.Join(place.contracts, component)}
	}
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
