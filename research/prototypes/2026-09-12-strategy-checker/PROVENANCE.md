# Provenance and license scope

This packet is original OrbitSynthesis code under the repository's existing
[MIT license](../../../LICENSE). It adds no third-party code dependency. Python
standard-library imports are inspected by the tests. The checker performs
explicit finite product exploration and cycle detection for a supplied
controller; it does not implement Tau's language, algebraic quantifier
elimination, type-reduction synthesis, or plugin machinery.

## Source exposure and authorship record

The authoring agent read public Tau source and issue #111 to identify integration
failure families. This is source-informed requirements work, not a formally
isolated clean-room process. The finite checker and its matrix-closure test
oracle were written independently from the mathematical contract in this
packet. No Tau function, header, parser, test fixture, generated controller,
or runtime is copied into the new OrbitSynthesis implementation.

Tau source excerpts inspected during review are in a temporary review directory
outside this repository. The durable upstream receipt records source URLs and
hashes, not redistributed Tau source. Neither the local tool nor its tests
download or execute Tau. No upstream submission or publication was made.

## Current Tau license reviewed

The `LICENSE.md` files at main `43b480d4a5e6a553f1fa1b0514e1d27ab3e7da34`
and feature/plugins `b3964f6d7a3e2a7df94c18711e5523e85b3701be` were fetched
on 2026-09-12 and are byte-identical.

The current text permits educational, research and noncommercial uses and
specified uses solely associated with Tau Net. Its listed free-use grants
exclude redistribution of the Tau product or its portions. Uses outside the
listed scope require an additional license. Section 3 assigns rights in
materials proposed as contributions through the Product's public repositories.
See the [pinned Tau license](https://github.com/IDNI/tau-lang/blob/43b480d4a5e6a553f1fa1b0514e1d27ab3e7da34/LICENSE.md).

The user selected an **application solely for Tau Net** under the current
license, superseding the provisional research/noncommercial target. The
[application profile](../../../examples/controllers/TAU_NET_APPLICATION.md)
records that scope, including the license's commercial-use permission within
its Tau Net related instances. The first delivered tool runs locally without
Tau. A native Tau adapter will use a separately obtained installation solely
for the Tau Net application. No separate agreement is being assumed.

The producer bridge reuses OrbitSynthesis's existing finite safety solver and
exports ordinary finite positional tables. Its application example is original
OrbitSynthesis code, not Tau-generated code. No native Tau adapter or Tau Net
deployment is implemented by labeling the intended application scope.

The subsequent table encoder, loader, and runtime are original OrbitSynthesis
code. Their OSMC format is a finite byte table, not a Tau-generated executable.
The runtime uses only fixed Python code and the independently checked table;
it neither loads candidate source code nor adds an external dependency.

## Limits of this record

This documents engineering separation and the license text reviewed. It is not
a legal opinion, patent claim chart, novelty review, or guarantee of freedom
to operate. No separate patent clearance was established. The repository's
MIT license does not grant rights belonging to IDNI or other third parties.
Existing project boundaries in [IP_BOUNDARY.md](../../IP_BOUNDARY.md) and
[PROJECT_ARCHITECTURE.md](../../../PROJECT_ARCHITECTURE.md) remain applicable.
