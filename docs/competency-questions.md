# Competency questions

The questions practitioners ask of a software estate, and for each one: what the estate hands a
model, the last mile the model does, and what makes the answer the same for everyone who asks.
Each question will gain a SPARQL query that runs over the worked estates (see the
[roadmap](roadmap.md)).

## What a competency question is

The estate does not answer questions. It points a model at the answer, so that two people asking
the same thing about the same estate get the same answer without either rebuilding the operating
context from scratch. The test is therefore not "does a query return it" but "does the estate
return the same pointers to everyone, and is what remains one bounded step no model can get
wrong". A question is written in three parts:

- **Estate returns.** The pointers: entities on stable keys, edges with their evidence, identifiers
  a tool knows a thing by, paths pinned to a commit.
- **Last mile.** What the model does with them: nothing, one read of a cited file at a pinned
  commit, or one query to a tool by a pinned identifier.
- **Same for everyone.** Why two readers get one answer: what is pinned, what is never
  interpreted on the estate's behalf.

A question whose last mile is a search fails, because a search is where two people get two
answers.

Five rules the questions are written against:

- **Connections, not interpretations.** The estate holds what a model cannot rebuild per
  prompt, with evidence citing where it was read, and never a reading of a file the model can
  open once pointed at it.
- **The join, not the value.** For anything live, which tool, which identifier, as of when.
- **Every pointer is pinned.** A path at a commit, a field, a tool identifier. Never "the
  current file".
- **Identity is what evidence asserts.** Keys carry what the manifest or repository asserts;
  Application is attached by edges resolved by name; nothing infrastructural is in a key.
- **Nothing about a person.** Facts are attributed to the agent that asserted them, ownership
  is by Team, and "who" lives in the CI system or the identity provider, outside the estate.

Every question is stated against the graph alone. Each lists the terms it uses; `(tool)` marks the
live half that belongs to a tool or git.

## Topology and ownership

### Which code repositories deploy which application environments?

Terms: `deployedFrom`; Pipeline, `deploys`.

- **Estate returns.** Every Environment's `deployedFrom` Repository; with pipelines, the Pipeline in
  that Repository and its `deploys` edge per job.
- **Last mile.** None.
- **Same for everyone.** Committed facts on stable keys with the citation that established each.

### What deploys `user-svc` into prod?

Terms: Pipeline, `deploys` and its write location.

- **Estate returns.** The Instance; its `deploys` edge naming the Pipeline and job; the job's
  rule, cited.
- **Last mile.** None for "what". One read of the cited rule for "is it gated".
- **Same for everyone.** The job and its citation are pinned; nobody interprets the rule on the
  estate's behalf.

### What happens when I merge to `main` in this repository?

Terms: Pipeline, `triggers`, `deploys`; one file read (tool).

- **Estate returns.** From the Repository: its Pipeline, each `triggers` edge with the variables it
  sends and the target Pipeline's key. From the target Pipeline: its `deploys` edges per job and
  their targets.
- **Last mile.** Two steps on stable keys, then one read of the cited rule where the question
  turns on a gate.
- **Same for everyone.** A chain of connections on keys the model can re-resolve, rather than a
  computed verdict true at one reading of files nothing re-checks. An effective gate or a
  deployment path is deliberately not computed.

### What software owns this cloud resource?

Terms: Cloud Resource, `provisionedBy`; `instantiatedFrom`.

- **Estate returns.** The resource by declared address or alias; `provisionedBy` the Instance,
  Environment, Application, Service, or Core Infrastructure whose declaration creates it; from an
  Instance, `instantiatedFrom` Service, and from a Service, `memberOf` Application.
- **Last mile.** None. At most three hops.
- **Same for everyone.** Ownership is read from the module or chart boundary the declaration
  sits inside, never a name match.

### What team owns this service or application?

Terms: Team, `ownedBy`.

- **Estate returns.** `ownedBy` Team, from `CODEOWNERS`, a catalog file's `owner:`, or a
  `team=` tag, cited.
- **Last mile.** None.
- **Same for everyone.** A Team carries no personal data; who is on it is outside the estate.
  A thing whose only owners are individuals has no Team owner, which is a gap.

## Deployments and pipelines

### What commit of the service is in prod?

Terms: the `deploys` write location, `builds`; one pinned read (tool).

- **Estate returns.** The deploy edge's write location, `services/user-svc/values-prod.yaml`
  at commit `abc123`, field `userServiceImageTag`; the build edge's tag scheme,
  `$CI_COMMIT_SHA`.
- **Last mile.** Read the field at that commit, apply the scheme. The value is never stored.
- **Same for everyone.** Path, field, commit, and scheme are pinned, so the read is the same
  whatever HEAD a checkout is at. The honest answer is "declared as of", never "running".

### Which pipelines deployed unsuccessfully?

Terms: Pipeline; `observedBy` a CI system; CI system (tool).

- **Estate returns.** Every Pipeline that deploys, and what its CI system knows it by: its
  repository and path for GitHub Actions or GitLab, which its key already holds, or the job,
  project, or pipeline name `observedBy` carries for Jenkins, CircleCI, or Buildkite.
- **Last mile.** One query per CI system for recent runs by those identifiers.
- **Same for everyone.** The identifiers are the same strings for everyone; the CI system is
  the source of truth for runs. Without them, "ask Jenkins" has nothing to ask with.

### Which pipeline jobs fail the most, and why?

Terms: Pipeline, jobs on edges; `observedBy` a CI system; CI system and
logs (tool).

- **Estate returns.** The Pipelines with their CI identifiers; the job names on each edge.
- **Last mile.** Run history grouped by job from the CI system; the "why" is reading logs.
- **Same for everyone.** Job names on edges are the job names the CI system reports.

### Show me every app that changed in the last 24 hours, with links to the pipelines.

Terms: `implementedIn`; Pipeline; `observedBy` a CI system; git
and CI system (tool).

- **Estate returns.** Application to Services to the Repositories that implement them; each
  Repository's Pipelines with their CI identifiers.
- **Last mile.** `git log` per repository since yesterday; run links from the CI system by
  identifier.
- **Same for everyone.** The set of repositories is the estate's; the links are the CI
  system's URLs for pinned identifiers.

### Which recent deployments changed both infrastructure and application behavior?

Terms: `deploys` and its write location; Cloud Resource declared address; git
diff (tool).

- **Estate returns.** Recent `deploys` edges and the paths they write; every Cloud Resource's
  declared address in the same Repository.
- **Last mile.** For each run's commit, diff it: did it touch a resource declaration and
  application code?
- **Same for everyone.** Declared addresses are what classify a diff as infrastructure; without
  them it is a guess by directory name.

### Who triggered the last rollout of a service? What commit, pipeline, and resources changed?

Terms: `deploys` and its write location, `builds`; `observedBy` a CI system; CI
system and git (tool).

- **Estate returns.** The Instance, its deploy edge and pinned write path, the Pipeline with CI
  identifiers, the build's tag scheme.
- **Last mile.** The CI system says who and when; git says the commit; the diff at the pinned
  paths says the resources.
- **Same for everyone.** "Who" never enters the estate. The CI system answers it to someone
  authorized to ask.

## Change and incidents

### What was the last error in prod?

Terms: `observedBy` and its identifiers; monitoring tool
(tool).

- **Estate returns.** Each Instance in prod, the tool it is `observedBy`, and the identifiers
  the tool knows it by, `service.name` and `deployment.environment` in the tool's terms.
- **Last mile.** One query to the tool with those identifiers.
- **Same for everyone.** The identifiers are the same strings for everyone, as the tool spells
  them; the estate never holds an error. Without them, the join to the tool is a guess.

### Top three deployments last week that spiked error rates, with links to their pipelines.

Terms: `deploys`, Pipeline; `observedBy` identifiers on both; monitoring tool and CI
system (tool).

- **Estate returns.** Instances with monitoring identifiers; their deploy edges; Pipelines with
  CI identifiers.
- **Last mile.** Error series from the tool, run times from the CI system, correlate, rank.
- **Same for everyone.** Both queries are by pinned identifiers; the ranking is arithmetic
  over the same inputs.

### What changed in production since yesterday that explains the latency spike?

Terms: `deploys` and its write location; Cloud Resource, `runsOn`, `dependsOn`,
`provisionedBy`, `observedBy` identifiers; git diff and monitoring tool (tool).

- **Estate returns.** Prod's Instances and their pinned write paths; the Cloud Resources they
  `runsOn` and `dependsOn`, with the declared addresses of each and of the Core Infrastructure
  that provisions the shared ones; the monitoring identifiers.
- **Last mile.** `git diff` at the pinned paths since yesterday; latency from the tool.
- **Same for everyone.** The set of paths to diff is the estate's, so nobody diffs a different
  set.

### Were there config changes in critical components of an app that explain pod thrashing in a cluster?

Terms: `dependsOn`, `readsSecretsFrom`, `runsOn`; git diff and cluster events
(tool).

- **Estate returns.** The Application's Instances that `runsOn` that cluster; what each
  `dependsOn` and `readsSecretsFrom`, with paths; their deploy write paths.
- **Last mile.** Diff those paths; read cluster events from the tool.
- **Same for everyone.** "Critical" is the practitioner's word: the estate lists, it does not
  rank. Dependencies, what a workload reaches, are what blast radius is made of.

## Cost

### How much does prod cost per month, and what are the most expensive resources?

Terms: Cloud Resource aliases, `provisionedBy`, Cloud Account; cost store (tool).

- **Estate returns.** Prod's resources by owner, Instance-owned and Environment-owned; the
  shared resources of the Core Infrastructure prod's Instances run on; each resource's aliases;
  the Cloud Accounts billed, for charges that belong to no resource.
- **Last mile.** Sum the rows those aliases match and sort; report shared Core Infrastructure
  cost as shared.
- **Same for everyone.** Aliases and ownership are pinned. How shared cost is split is decided
  downstream of the estate, so the estate's answer is the exact owned cost plus the shared cost
  beside it, never a silent split.

### What does a service cost across every environment?

Terms: Cloud Resource, `provisionedBy`; `instantiatedFrom`; cost store
(tool).

- **Estate returns.** The climb by software: resource, `provisionedBy` Instance,
  `instantiatedFrom` Service, `memberOf` Application; a resource `provisionedBy` the Service
  itself joins the climb at the Service.
- **Last mile.** Sum along that climb.
- **Same for everyone.** The question names which climb it takes, by place or by software.
  They agree for a service in one Application and disagree, correctly, for a shared one.

### Show me the resources whose cost went up the most in the last 30 days.

Terms: Cloud Resource aliases; cost store (tool).

- **Estate returns.** Every resource with its aliases and owner.
- **Last mile.** Two periods from the cost store, diff, rank, climb to owners.
- **Same for everyone.** Rows that match no alias are a gap, cost with no declared resource,
  never "other".

## Capacity and dependencies

### Can I upgrade my EKS clusters from 1.28 to 1.32 without issues? Which pods need upgrading?

Terms: Core Infrastructure, Cloud Resource declared address, `runsOn`; file reads (tool).

- **Estate returns.** Each cluster, a Cloud Resource with its declared address and the Core
  Infrastructure that provisions it; every Instance that `runsOn` it; each Instance's deploy evidence pointing at its
  manifests.
- **Last mile.** Read the declared version at the commit; read each manifest for APIs removed
  by 1.32 against the model's own knowledge.
- **Same for everyone.** The set of manifests is the estate's. The version is a pinned read at
  the declared address, not a stored value.

### Can I scale a service from one pod to two without issues?

Terms: `dependsOn`; `deploys`; manifest reads (tool).

- **Estate returns.** The Instance, its manifest path, what it `dependsOn`, and what depends
  on it.
- **Last mile.** Read the manifest for state, sessions, leader election; check dependencies
  for connection limits.
- **Same for everyone.** What a dependency means at runtime is the model's reading of the
  manifest the edge cites.

### Which workloads depend on the Redis cluster, and what happens if it is restarted?

Terms: `dependsOn`, Cloud Resource; manifest reads (tool).

- **Estate returns.** The Redis Cloud Resource; everything that `dependsOn` it; their
  Instances and Environments.
- **Last mile.** One walk for "which". The model reasons about restart behavior from the
  manifests.
- **Same for everyone.** Dependencies are evidence-cited from configuration, never inferred
  from a name.

### How do I reach prod's state, or prod's cluster, from this workstation?

Terms: Cloud Account, Identity, `within`, `connectedVia`; a local credential
(outside the estate).

- **Estate returns.** The Cloud Account holding the state bucket, or the cluster; the Identities
  `within` it; and the credential name prod's repositories declare on `connectedVia`.
- **Last mile.** Use the local profile or kube context that maps to one of those Identities.
- **Same for everyone.** Every workstation maps its own credentials to the same Identities; the
  estate never holds a credential or a person.

### If this repository is compromised, what can it reach?

Terms: Pipeline; Identity, `trusts`, `within`; policy reads (tool).

- **Estate returns.** The repository's Pipelines, every Identity that `trusts` them or trusts one
  that does, and the Cloud Account or cluster each is `within`, each cited to its trust policy.
- **Last mile.** Read each role's cited policy for what it permits.
- **Same for everyone.** The set of roles is a walk over declared trust, never a search across
  the repositories that declare roles.

## Adding questions

Add them the way they come, without thinking. The ones that arrive without thinking are the ones
a practitioner asks every day. Each new question is written in the three parts above before any
term is added for it; a question that needs a term the ontology lacks is how a term gets
proposed.
