# Rename continuity conformance scenarios

These scenarios exercise the [identity contract](../spec/operational-estate.md#6-identity-and-keys)
for six classes. They specify fixtures, operations, and semantic invariants for any implementation.
A valid snapshot alone cannot prove continuity: both an original and an incorrectly rekeyed graph
can satisfy structural constraints.

## Fixture and comparison

Load two Repositories, `shop-code` and `platform-code`, with distinct canonical remotes. Load
Application `shop`; Service `user-svc` declared and implemented in `shop-code`, a member of `shop`;
Environment `prod` placed under `shop`; and Instance `user-svc-prod` in `prod`, instantiated from
`user-svc`. Load Core Infrastructure declared in `platform-code`, root `platform`, configuration
`shared`, initially with no descriptive name. Add a Service `gateway` declared in `platform-code`
and an Instance `gateway-shared` in that Core Infrastructure, instantiated from `gateway`.
Record every established class/key pair and every relationship endpoint before editing.

These labels describe fixture entities, not a prescribed key encoding. Include the forward edges
`declaredIn`, `implementedIn`, `memberOf`, `placedUnder`, `inScope`, and `instantiatedFrom` just
specified. Implementations may materialize inverses; comparison treats those as the same relations.
Use a fresh baseline for each case, then repeat with successive renames to check accumulated aliases.

Compare established identities, descriptive values, and relationship endpoints. Ignore ordering,
installation-local IDs and base URI prefixes. Do not ignore changes to keys embedded in dependent
keys. Full-record digests may change when descriptive content changes.

## Common sequence

For each case below:

1. Export the loaded fixture and retain the identity and relationship baseline.
2. Apply only the specified descriptive edit. Export again. The edited entity keeps its key, has
   the new name, and retains the former name as an alternate name where that class supports it.
   All existing alternate names remain. No duplicate entity appears.
3. Compare all dependent keys and relationship endpoints with the baseline. They remain unchanged,
   including any relation details whose identity incorporates those endpoints.
4. Import into a second instance with different local identifiers and export. Canonical identities,
   names, alternate names, and references equal the first export. Historical attribution is
   preserved when available, never fabricated to account for an old name.
5. Rename the same established entity again in the second instance and import the export back into
   the first. Check the same invariants and the accumulated former names in both directions.

## Class cases

- **Application:** rename `shop` to `store`. Preserve Service memberships, Environment placements,
  and the established keys of the Environment and its Instance.
- **Service:** rename `user-svc` to `account-svc`. Preserve its Repository-scoped key, declaration,
  implementation, membership, and the Instance's Service reference.
- **Environment:** rename `prod` to `live`. Preserve placement under the Application and the scope
  key embedded in `user-svc-prod`'s established key.
- **Service Instance:** rename `user-svc-prod` to `account-live`. Preserve Scope and Service
  references. Repeat independently for `gateway-shared` in the Core Infrastructure scope.
- **Core Infrastructure:** add the name `foundation` to the unnamed entity, then rename it to
  `shared-platform`. Preserve Repository/root/applied-configuration identity and scoped Instance
  keys. No alternate name is required for this class. The wire profile maps the initial unknown
  name to `null` and later names to strings.
- **Repository:** rename the descriptive label `shop-code` to `store-code`. Preserve canonical
  remote identity and all dependent keys and references. Repeat with access spellings or transports
  that the implementation resolves to that same canonical remote. No alternate name is required.

## Collisions and identifying-input changes

Add a second Service with the same descriptive name in a different Repository, and a second
Environment with the same name under a different Application. Both identities remain distinct
through export/import. Reusing names in these different scopes is permitted.

For a conflicting name or alternate name in the same identity scope, record the implementation's
explicit collision policy and exercise it. It may refuse the edit or preserve distinct established
identities and report ambiguity; it must not silently merge or rekey either entity. The ontology
does not prescribe global descriptive-name uniqueness or automatic matching by an alias.

Separately attempt to change each of these identifying inputs:

- A Repository's actual canonical host/path, rather than access spelling for the same remote.
- A Core Infrastructure's declaration root, and then its applied configuration.
- An Instance's Scope, including an Environment-to-Core Infrastructure move.

Record the specified identity-transition behavior or explicit refusal. A refusal leaves the
original graph intact. An implemented transition must have a separate explicit contract and retain
referential integrity according to it; it is not evidence of a descriptive-rename pass. These
scenarios do not require an automatic migration or deduplication of independent discoveries.

## Evidence and tooling

A report records implementation revision, fixture, operation, observed exports, expected invariants,
and result for each case. Use pass only for an exercised invariant, fail for a demonstrated
violation, and unverified for missing evidence. Static inspection of a test is evidence of its
intended coverage, not a successful execution. Report partial coverage at the invariant level.
File focused implementation issues for demonstrated failures; extra implementation tests are
separate work.

An executable conformance runner is separate tooling work. It would need adapters for loading
fixtures, applying edits, exporting graphs, and comparing semantic identities. Neither such a
runner nor a full synchronization suite is required to publish this ontology amendment.
