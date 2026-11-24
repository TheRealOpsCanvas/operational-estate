# Shared-class wire mapping

This mapping covers Application, Environment, Instance, Repository, and Core Infrastructure. It
maps existing vocabulary into a JSON profile; it adds no classes or RDF terms. Team retains its
ontology support for alternate names without joining this five-class profile.

A profile built on an earlier six-class mapping, which carried Service, `memberOf`, and
`instantiatedFrom`, is not this one. A consuming profile moves to this mapping under a new profile
version, or rejects it explicitly: a Service record has no class to import into, and an Instance's
code is its `implementedIn`, not a Service reference.

## Names and alternate names

`estate:name` represents the current descriptive name. For Core Infrastructure it maps to required
`properties.name`: a nonblank string when known, otherwise JSON `null`. In RDF, unknown means no
`estate:name` assertion. An omitted required JSON member, an empty string, and a literal string
`"null"` do not represent that unknown value.

For Application, Environment, and Instance, each `estate:alternateName` value maps
to an entry in required, non-null `properties.aliases`. Entries are unique nonblank strings, and
`[]` is valid. On import each entry becomes an alternate-name value; order has no meaning. There is
no `estate:aliases` predicate. Former names retained on rename survive this mapping and import.

Names and alternate names do not replace established keys. Import preserves the canonical class
and key, even when an installation uses different local identifiers or serialization base URIs.

## Repository properties and compatibility

`estate:monorepo`, `estate:hasIaC`, and `estate:hasPipelines` are independent boolean properties.
The ontology permits any of them to be absent when unknown, and permits every combination of
confirmed boolean values. In particular, `monorepo` and `hasIaC` both `false` can mean a single
software project without infrastructure as code. Recorded software
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
- Positive and negative examples covering unknowns, every combination of the booleans, and
  software relationships independently of any of them.

Those coordinated downstream changes are separate from the ontology amendment. Retaining local
legacy role storage does not itself conflict with the ontology; exporting it as the removed
predicate does. The existing `estate:contains` remains the inverse of infrastructure `within`.

## Migrating from a six-class profile

A consuming profile that moves to this mapping from one built on the earlier six-class mapping
converts the facts it already holds by these rules. Every way it converts one graph, such as on
first import and on each later read of a graph still held in the earlier profile, gives the same
result, and its shared vectors cover each rule.

- A Service, a `memberOf`, an `instantiatedFrom`, and an `implementedIn` whose source is a Service
  or an Application have no class or relation in this mapping and are not carried. Neither is a
  record of any other class or relation this mapping does not cover, or a record that depends on
  one not carried: an edge with an endpoint not carried, a detail of a relation not carried, and a
  record whose key names a record not carried.
- An Instance keeps its class and key. A Service name it carries is not carried.
- An Instance is `implementedIn` a Repository where a practitioner placed it under a Service, by
  that practitioner's own choice, and that Service was `implementedIn` the Repository. It has one
  such edge for each Repository the Service was `implementedIn`. The edge carries no
  Implementation, because the earlier mapping records no code path.
- An Instance placed under a Service by matching their names gets no `implementedIn` from that
  placement: the placement was inferred from a name, and an `implementedIn` never is. Neither does
  an Instance whose code was recorded only against its Application, since nothing says which of
  the Application's Instances runs it.
- A migrated `implementedIn` records that it was migrated and the facts it was migrated from, as
  the consuming profile records provenance, so it is never mistaken for one read through
  `pullsFrom`.

A migrated `implementedIn` is read from two facts a practitioner confirmed, not from the estate's
files, and is the only `implementedIn` not read through `pullsFrom`. An Instance with none after
migration has its `implementedIn` read when its estate is next read through `pullsFrom`.
