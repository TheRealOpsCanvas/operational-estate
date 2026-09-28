# Operational Estate

**Operational Estate** is an open, vendor-neutral ontology of a software estate: what an
organization builds, where it is placed, what exists in the cloud to run it, who owns it, how it is
delivered, and how to reach it.

Every catalog, cost tool, observability tool, and CI system describes part of the same estate in
its own words, and none of them joins the others. "Prod" names an application's environment and the
cluster it runs in; "the service" names a unit of software and a running copy of it; "the platform"
names a team, a repository, and a tenant. Operational Estate gives each of those words exactly one
meaning, and gives the connections between them a form that people, tools, and AI models can all
read and check.

## Status

**Draft.** Every term is `draft` and may change until the first published version. The prose
specification is the current source; the machine-readable vocabulary (OWL), constraints (SHACL),
worked examples, and checks are on the [roadmap](ROADMAP.md).

| Document | What it holds |
|---|---|
| [spec/operational-estate.md](spec/operational-estate.md) | The model: principles, classes, relations, keys, constraints |
| [competency-questions.md](competency-questions.md) | The questions the model must answer, and how each is answered |
| [ROADMAP.md](ROADMAP.md) | What comes next |

## Identifiers

| | |
|---|---|
| Name | Operational Estate |
| Prefix | `estate:` |
| Namespace | `https://w3id.org/operational-estate#` (reserved; not yet served) |

## Governance

Operational Estate was started by [OpsCanvas](https://opscanvas.com), which maintains a reference
implementation. The specification names no product and depends on none, and it is written so that
anyone can implement it. It is hosted here while it is young, and it will move to a neutral home as
it gains contributors. The namespace does not depend on where this repository lives.

## Contributing

Questions, disagreements, and new competency questions are the most useful contributions. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

[Apache License 2.0](LICENSE), for the specification text and every file in this repository.
