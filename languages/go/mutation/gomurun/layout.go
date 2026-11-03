package main

type layout struct {
	components  string
	contracts   string
	accepted    string
	gomuVersion string
}

func defaultLayout() layout {
	return layout{
		components:  "internal",
		contracts:   "contracts",
		accepted:    "tools/mutation/accepted",
		gomuVersion: "v0.3.0",
	}
}
