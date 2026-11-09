# Shared-class wire mapping

This mapping covers Application, Service, Environment, Service Instance, Repository, and Core
Infrastructure. It maps existing vocabulary into a JSON profile; it adds no classes or RDF terms.
Team retains its ontology support for alternate names without joining this six-class profile.

## Names and alternate names

`estate:name` represents the current descriptive name. For Core Infrastructure it maps to required
`properties.name`: a nonblank string when known, otherwise JSON `null`. In RDF, unknown means no
`estate:name` assertion. An omitted required JSON member, an empty string, and a literal string
`"null"` do not represent that unknown value.

For Application, Service, Environment, and Service Instance, each `estate:alternateName` value maps
to an entry in required, non-null `properties.aliases`. Entries are unique nonblank strings, and
`[]` is valid. On import each entry becomes an alternate-name value; order has no meaning. There is
no `estate:aliases` predicate. Former names retained on rename survive this mapping and import.

Names and alternate names do not replace established keys. Import preserves the canonical class
and key, even when an installation uses different local identifiers or serialization base URIs.

## Repository properties and compatibility

`estate:monorepo` and `estate:hasIaC` are independent boolean properties. The ontology permits either
to be absent when unknown, and permits every combination of confirmed boolean values. In particular,
`false, false` can mean a single software project without infrastructure as code. Recorded software
is expressed through `implements` / `implementedIn`; missing edges do not prove absence.

The removed draft `repositoryRole` and the proposed nested `contains.software` enum are not this
mapping. No general lossless conversion exists: an application role does not tell how many projects
a Repository holds. Incomplete discovery must not be converted into confirmed negative values.

A consuming profile must reconcile these properties before claiming compatibility. Its contract,
shared vectors, and adapters must agree on:

- JSON member names and requiredness, including representation of unknown values.
- Migration of confirmed legacy facts, with insufficient evidence left unknown or explicitly
  refused if the profile cannot represent it.
- Version negotiation or explicit rejection between old classification profiles and this mapping.
- Positive and negative examples covering unknowns, all four boolean combinations, and software
  relationships independently of either boolean.

Those coordinated downstream changes are separate from the ontology amendment. Retaining local
legacy role storage does not itself conflict with the ontology; exporting it as the removed
predicate does. The existing `estate:contains` remains the inverse of infrastructure `within`.
