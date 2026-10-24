# Choosing component boundaries

Status: proposed guidance. The example below illustrates the reasoning; it is
not a record of a decomposition tested on a second project.

Choose boundaries that contain likely changes and let each implementation be
regenerated from its own contract. Small components help when their contracts
are coherent and their dependencies explicit. Line count alone does not tell
us where to split.

## Sources and what we borrow

Robert C. Martin's [Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html)
connects a module's reasons for change to the people responsible for a business
function. Use that to identify which policies change together and which have
different owners or purposes. A responsibility can require several operations.

Martin's [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
keeps source dependencies directed toward policy. External mechanisms translate
data at the boundary; domain rules do not depend on a database, UI framework,
or external representation. Its diagram does not prescribe a fixed number of
layers.

The regeneration checks below are this collection's application of those ideas.
They extend the [existing principles](principles.md), including the separation
of durable specifications from replaceable implementations. They do not require
an object-oriented design, a service per component, or a particular folder
scheme from Clean Architecture.

## Principles

### Group behavior by its reason to change

Name who needs a behavior and what requirement would change it. Keep operations
together when they enforce one policy or invariant. Separate policies that
change independently, even when they currently use the same data or run next
to each other. A pipeline stage or a verb in a name is a candidate boundary;
check its responsibility before making it a component.

### Keep domain policy independent of mechanisms

A selection rule consumes domain values. A file reader, parser, or screen
adapter supplies or translates those values. Changing the UI or storage library
should leave the selection contract intact. Keep framework objects, database
rows, and parser nodes out of policy interfaces.

When policy needs an external capability, define the required interface in the
protected contract and supply an adapter from the outside. The policy must not
import its concrete adapter. For pure core components, prefer passing values
in and returning decisions or proposed actions; drivers perform the effects.

### Separate layers by expected change

Record which commitments should stay stable while an implementation changes.
Stored formats, shared domain meanings, contracts, and code have different
[change rules](principles.md#things-change-at-different-speeds).

Pace layers describe stability and the care a change requires. Dependency order
describes which components may import which others. Two implementations can
occupy different dependency positions while belonging to the same pace layer.
A policy can also consume frequently edited configuration as input without
depending on the configuration loader's implementation.

### Make regeneration local

For each proposed component, check whether a builder could replace its folder
using its contract, relevant decisions, declared dependency interfaces, and
shared domain types. Needing to inspect a neighbor's internals indicates a
missing contract rule or a boundary that needs revisiting. A replacement should
preserve neighboring contracts and pass the existing integration scenarios.

### Keep shared knowledge small and explicit

Put a shared type in the domain model when it expresses meaning several
contracts need. Keep component-specific representations private. A type used
in two places does not automatically justify a shared abstraction: confirm that
both uses have the same meaning and reason to change.

### Split when the boundary helps

Extract a component when it gives a responsibility a clearer contract, contains
a likely change, or enables independent replacement. Keep helper functions
inside a component when they share its policy and change with it. If each
change repeatedly crosses the same boundary, reconsider the split. If unrelated
requests repeatedly change one component, look for separate responsibilities.

## Worked example

Consider a fictional tool that reads a document, checks its rules, selects
sections, and writes a formatted result. One large function could perform the
whole workflow. These are candidate responsibilities:

| Responsibility | Contract boundary | Reason to change |
| -- | -- | -- |
| File driver | Paths and process options to bytes, or output bytes to a file | File access and command behavior |
| Decoder | Bytes to domain values or syntax problems | Supported input representation |
| Validator | Domain values to semantic problems | What makes a document valid |
| Selector | Domain values and explicit selection inputs to selected sections | Which sections a request should include |
| Renderer | Selected sections to formatted output | Output presentation |

The decoder hides parser-specific objects. The validator and selector use
domain values without knowing where they came from. The renderer receives the
selection instead of repeating selection policy. The driver handles effects
and the entry point wires the operations together.

A change from terminal output to HTML should affect presentation. A new
selection rule should affect the selector's contract and implementation. A
stored-format change may need an ADR and coordinated decoder changes; pace
layers make the scope explicit rather than promising every change stays local.

These boundaries still need judgment. If validity and selection implement one
inseparable policy, keeping them together may give a clearer contract. If one
small renderer handles all required formats coherently, it needs no extra
component per format. Keep an invariant intact before optimizing component size.

## Record and check the decision

For each boundary, record the responsibility, its likely reasons for change,
inputs and outputs, invariants, dependencies, effects, and what remains private.
Name a change it should contain and a change that should leave it untouched.
Put the chosen boundaries and dependency order in the architecture documents;
put durable tradeoffs in an ADR.

Review the proposed split against those change examples. After the contracts
exist, an independent regeneration is a practical check: if it requires changes
to neighboring contracts, investigate what the specification or boundary missed.
