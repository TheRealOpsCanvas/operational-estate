# Initial rename continuity investigation

## Evidence boundary

This report records static inspection on 9 November 2026 of implementation revision
`6c80027a34b3f0e9a7c3d21971c9249a1ef6664b`. It does not certify current implementation conformance.
The inspected tests were not executed for this report. No complete portable scenario is marked
passed, and missing coverage is not treated as a demonstrated failure.

The evidence is the pinned [mapping tests][mapping] and [reconciliation tests][reconciliation] in
an existing implementation. These sources are evidence about one adapter, not definitions of the
ontology or requirements for storage, local IDs, or key encoding.

## Coverage by scenario

- **Application:** reconciliation tests exercise collision refusal for names and aliases, and
  creation from canonical keys. Renaming an established Application while preserving dependent
  Environment and Instance keys and memberships remains unverified.
- **Service:** reconciliation test `a downloaded rename updates the row bound to its canonical key`
  asserts an unchanged key, membership, existing evidence, and a retained former-name alias. Mapping
  tests compare canonical identity across differing installation-local keys. A complete export,
  second-instance edit, and return import with Instance references remains unverified.
- **Environment:** mapping test `a rename changes the published name and leaves every key unchanged`
  compares Environment, Environment-scoped Instance, and placement identities before and after
  descriptive changes. It asserts the Environment's former-name alias. An applied rename through
  both installations with all dependent references remains unverified.
- **Service Instance:** that same test exercises an Environment-scoped Instance's name and identity.
  A separate test preserves a bound Core Infrastructure scope key when its Repository resolves
  elsewhere. Neither demonstrates the full Core Infrastructure-scoped rename sequence or
  accumulated aliases through two-way import. Those cases remain unverified.
- **Core Infrastructure:** mapping tests read a known descriptive name back from canonical data.
  The unnamed-to-named-to-renamed sequence with scoped dependents remains unverified.
- **Repository:** mapping tests cover canonical equivalence across access spellings and refuse a
  bound Repository whose resolved remote changes, with `repository_location_moved`. They also
  refuse two local repository records resolving to one canonical identity. Descriptive label
  rename with every dependent key and a two-way import remains unverified.

Reconciliation tests permit the same Service alternate name in different Repositories and refuse
same-scope name or alias collisions for the four alias-bearing classes. These assertions are
partial evidence for the collision scenarios, not an executed pass. Cross-Application Environment
name reuse through the complete round trip remains unverified.

Root and applied-configuration changes, Instance scope transitions, successive rename cycles, and
complete historical attribution preservation remain unverified. The repository-location refusal
is evidence of an explicit transition boundary, not of automatic migration. No rename-continuity
failure was demonstrated by this static inspection, so none is reported as a confirmed defect.
Additional implementation-specific coverage for the unverified cases is separate from publishing
the portable scenario specification; a generic executable runner is also separate tooling work.

## Repository compatibility finding

At this same revision, mapping tests expect a nested `contains.software` classification and derive
it from recorded implementation counts. That does not implement the revised independent Repository
booleans and unknown-value semantics. This is a confirmed difference in the specified output shape,
not a rename failure. Downstream contracts, vectors, and adapters need coordinated reconciliation
before claiming compatibility with the [shared-class mapping](../spec/shared-class-wire-mapping.md).
The ontology amendment does not assert that those downstream changes have landed.

[mapping]: https://github.com/TheRealOpsCanvas/opscanvas-operator/blob/6c80027a34b3f0e9a7c3d21971c9249a1ef6664b/packages/daemon/test/topology/team-graph-mapping.test.ts
[reconciliation]: https://github.com/TheRealOpsCanvas/opscanvas-operator/blob/6c80027a34b3f0e9a7c3d21971c9249a1ef6664b/packages/daemon/test/topology/team-graph-reconciliation.test.ts
