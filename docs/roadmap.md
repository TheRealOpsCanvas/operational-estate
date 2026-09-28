# Roadmap

The prose specification comes first. What follows turns it into files a machine can check, and
tests it against estates other than the one it was first drawn from.

## Vocabulary and constraints

- `estate.ttl`: every class and relation in OWL under the `estate:` prefix, each with its
  definition, what it is not, its `skos:altLabel` aliases, its key, and its maturity. Relations that
  carry data are relation classes (the n-ary pattern); every object property has an inverse.
- PROV-O used directly for provenance: `prov:wasDerivedFrom` for a citation, `prov:Activity` for a
  scan, `prov:wasAttributedTo` a `prov:Agent` for a confirmation, `prov:generatedAtTime` for the
  as-of.
- `estate-shapes.ttl`: SHACL for what OWL cannot state. Key derivation; exactly one owner per
  runtime thing; at most one `instantiatedFrom` per Service Instance, targeting a Service; relation
  endpoint classes; no individual `prov:Person` and no relation touching one; no value on a
  `readsSecretsFrom`; every alias carrying its source; `ownedBy` targeting only a Team.

## Competency questions and worked estates

- A SPARQL query for each competency question, over the pointer set it names.
- A primary worked estate: an application with a service built in its own repository and deployed
  from a separate deploy repository, an upstream service deployed from a public chart with the
  resources its chart provisions, a production environment spanning two cloud accounts, a cluster
  owned by core infrastructure, a deploy role and its trust, a secret read, observability
  identifiers per instance, and a team that owns the service.
- Four archetypes: a single serverless function in one account; a large Kubernetes estate with a
  platform team and a service shared across applications; serverless on managed services with no
  cluster; virtual machines deployed by scripts with no pipeline. Any fact that has to be forced in
  is recorded as a defect in the model.
- A deliberately wrong example the shapes must reject: an environment with two applications, a
  cloud resource with no owner, a `prov:Person` individual, and a secret reference carrying a value.

## Tooling

- A check that parses the vocabulary and shapes, runs a structural consistency check (declared
  domains and ranges, symmetric inverses, two endpoints per relation class, no class in two
  groupings), validates every example, confirms the wrong one fails, and runs every competency
  question over every example.
- A generated human rendering of the vocabulary, checked for staleness.

## Later

- A JSON-LD context, so JSON that implementations already produce can be read as the vocabulary.
- Alignments to OpenTelemetry semantic conventions and FOCUS, the two standards an estate's
  telemetry and cost rows already use, with a note on each lossy mapping.
- Alignments to TOSCA, Backstage, or CSDM, when a conversation needs one.
- Serving the vocabulary at its namespace.
- A neutral home for the project.
