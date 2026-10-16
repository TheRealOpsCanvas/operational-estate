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
  open once pointed at it. A value copied verbatim at a pinned commit is not a reading.
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

Terms: Declared Resource, Deployed Resource, `declaredAs`, `provisionedFor`; `instantiatedFrom`.

- **Estate returns.** The resource by declared address, or by provider id and the Declared
  Resource its Deployed Resource is `declaredAs`; `provisionedFor` the Instance,
  Environment, Application, Service, or Core Infrastructure whose declaration creates it; from an
  Instance, `instantiatedFrom` Service, and from a Service, `memberOf` Application.
- **Last mile.** None. At most four hops.
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

### What commit of the service is in prod, and does it include my fix?

Terms: the `deploys` write location and declared value, `builds`; git history (tool).

- **Estate returns.** The deploy edge's write location, `services/user-svc/values-prod.yaml`
  at commit `abc123`, field `userServiceImageTag`, and the value declared there,
  `main-851dfd9c`; the build edge's tag scheme, `$CI_COMMIT_SHA`.
- **Last mile.** Apply the scheme to the value to get the commit; ask the git host whether that
  commit contains the fix, starting from the merge commit of the fix's pull request, since a
  squash merge leaves the fix's own commits out of the default branch.
- **Same for everyone.** Path, field, commit, value, and scheme are pinned, so the answer is the
  same whatever a checkout is at. The honest answer is "declared as of", never "running": what is
  running is a query to the tool that observes it.

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

Terms: `deploys` with its variables and write location; Declared Resource address; git
diff (tool).

- **Estate returns.** Recent `deploys` edges, the variables each job sets, such as one selecting
  infrastructure or configuration, and the paths they write; every Declared Resource's
  address in the same Repository.
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

Terms: `deploys` and its write location; Declared Resource, `runsOn`, `connectsTo`,
`provisionedFor`, `observedBy` identifiers; git diff and monitoring tool (tool).

- **Estate returns.** Prod's Instances and their pinned write paths; the Declared Resources they
  `runsOn` and `connectsTo`, with the declared addresses of each and of the Core Infrastructure
  that the shared ones are provisioned for; the monitoring identifiers.
- **Last mile.** `git diff` at the pinned paths since yesterday; latency from the tool.
- **Same for everyone.** The set of paths to diff is the estate's, so nobody diffs a different
  set.

### Were there config changes in critical components of an app that explain pod thrashing in a cluster?

Terms: `connectsTo`, `readsSecretsFrom`, `runsOn`; git diff and cluster events
(tool).

- **Estate returns.** The Application's Instances that `runsOn` that cluster; what each
  `connectsTo` and `readsSecretsFrom`, with paths; their deploy write paths.
- **Last mile.** Diff those paths; read cluster events from the tool.
- **Same for everyone.** "Critical" is the practitioner's word: the estate lists, it does not
  rank. Dependencies, what a workload reaches, are what blast radius is made of.

## Cost

### How much does prod cost per month, and what are the most expensive resources?

Terms: Deployed Resource, `declaredAs`, `provisionedFor`, Cloud Account; cost store (tool).

- **Estate returns.** Prod's resources by owner, Instance-owned and Environment-owned; the
  shared resources of the Core Infrastructure prod's Instances run on; the Deployed Resources
  `declaredAs` each, by provider id; the Cloud Accounts billed, for charges that belong to no
  resource.
- **Last mile.** Sum the rows those provider ids match and sort; report shared Core
  Infrastructure cost as shared.
- **Same for everyone.** Provider ids and ownership are pinned. How shared cost is split is decided
  downstream of the estate, so the estate's answer is the exact owned cost plus the shared cost
  beside it, never a silent split.

### What does a service cost across every environment?

Terms: Declared Resource, `declaredAs`, `provisionedFor`; `instantiatedFrom`; cost store
(tool).

- **Estate returns.** The climb by software: Deployed Resource, `declaredAs` its Declared
  Resource, `provisionedFor` Instance,
  `instantiatedFrom` Service, `memberOf` Application; a resource `provisionedFor` the Service
  itself joins the climb at the Service.
- **Last mile.** Sum along that climb.
- **Same for everyone.** The question names which climb it takes, by place or by software.
  They agree for a service in one Application and disagree, correctly, for a shared one.

### Show me the resources whose cost went up the most in the last 30 days.

Terms: Deployed Resource, `declaredAs`; cost store (tool).

- **Estate returns.** Every Deployed Resource by provider id, with the Declared Resource it is
  `declaredAs` and that resource's owner.
- **Last mile.** Two periods from the cost store, diff, rank, climb to owners.
- **Same for everyone.** Rows land by provider id, the same string the cost store carries. A
  Deployed Resource `declaredAs` nothing is a gap, cost with no declaration, never "other".

### What is deployed that no declaration accounts for, and what does it cost?

Terms: Deployed Resource, `declaredAs`, `within`, Cloud Account; cost store (tool).

- **Estate returns.** Every Deployed Resource with no current `declaredAs`, by provider id, with
  the source that reported it and as of when, and the Cloud Account it is `within`; and the
  sources the scan read, so a resource whose declaration sits somewhere the scan never read is
  told apart from one nothing the scan read declares.
- **Last mile.** Sum each one's rows from the cost store by provider id.
- **Same for everyone.** The set is a query over the graph, never a search of the cloud, and each
  member cites what reported it. Whether it was built by hand, imported, or declared somewhere
  unread is said by what the scan read, not guessed.

## Capacity and dependencies

### Can I upgrade my EKS clusters from 1.28 to 1.32 without issues? Which pods need upgrading?

Terms: Core Infrastructure, Declared Resource address, `runsOn`; file reads (tool).

- **Estate returns.** Each cluster, a Declared Resource with its declared address and the Core
  Infrastructure it is provisioned for; every Instance that `runsOn` it; each Instance's deploy
  evidence pointing at its manifests.
- **Last mile.** Read the declared version at the commit; read each manifest for APIs removed
  by 1.32 against the model's own knowledge.
- **Same for everyone.** The set of manifests is the estate's. The version is a pinned read at
  the declared address, not a stored value.

### Can I scale a service from one pod to two without issues?

Terms: `connectsTo`; `deploys`; manifest reads (tool).

- **Estate returns.** The Instance, its manifest path, what it `connectsTo`, and what connects
  to it.
- **Last mile.** Read the manifest for state, sessions, leader election; check dependencies
  for connection limits.
- **Same for everyone.** What a dependency means at runtime is the model's reading of the
  manifest the edge cites.

### Which workloads depend on the Redis cluster, and what happens if it is restarted?

Terms: `connectsTo`, Declared Resource, Deployed Resource, `declaredAs`; manifest reads (tool).

- **Estate returns.** The Redis Declared Resource and the Deployed Resources `declaredAs` it;
  everything that `connectsTo` any of them; their Instances and Environments.
- **Last mile.** One walk for "which". The model reasons about restart behavior from the
  manifests.
- **Same for everyone.** Dependencies are evidence-cited from configuration, never inferred
  from a name.

### Which workloads lose their route out if this NAT gateway is removed?

Terms: Deployed Resource, `declaredAs`, `connectsTo`, `runsOn`; route reads (tool).

- **Estate returns.** The NAT gateway, a Deployed Resource `declaredAs` the network module call that
  declares it; the Deployed Resources joined to it by `connectsTo` in either direction, its route
  tables, routes, and subnets, and those joined to them in turn, as candidates; the clusters and
  machines among them, the Declared Resources they are `declaredAs`, and the Instances that `runsOn`
  them.
- **Last mile.** One read of the cited routes, for which of those candidates route through this
  gateway rather than merely sharing a network with it; routes the provider propagates from
  elsewhere are a query to the provider.
- **Same for everyone.** The one NAT gateway is its own entity, not a module call that declares
  three of them, so the walk starts from the same resource for everyone. A route is read where it
  is cited, never computed into an effective path.

### How do I reach prod's state, or prod's cluster, from this workstation?

Terms: Cloud Account, Identity, `within`, `accessedAs`; a local credential
(outside the estate).

- **Estate returns.** The Cloud Account holding the state bucket, or the cluster; the Identities
  `within` it; and the credential name prod's repositories declare on `accessedAs`.
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

### Which pipelines act in this account, and as what?

Terms: Pipeline, Identity, `runsAs`, `within`, Cloud Account; policy reads (tool).

- **Estate returns.** The Identities `within` the account, each Pipeline that `runsAs` one with
  the job that does, and the line each is read from, pinned to a commit.
- **Last mile.** Read each Identity's cited policy for what it permits.
- **Same for everyone.** Which job acts as which role is read from its definition at a commit,
  never from a run log or an audit trail, which are live and the provider's. A job whose role
  names a variable no cited file sets is not in the answer, and the answer does not claim it acts
  nowhere: it says that role is unread.

## Network placement

Network questions use the walks the specification defines under Networks: placement, from an
Instance through the resource it `runsOn` or is `providedAs` to a subnet and the network it is
`within`; and attachment, from a network to the connectors, exits, and entries joined to it. Every
walk follows `declaredAs` both ways.

### Which networks does `checkout` in prod run in?

Terms: `runsOn`, `providedAs`, `connectsTo`, `within`, `networkRole`, `declaredAs`.

- **Estate returns.** The Instance; the resource it `runsOn` or is `providedAs`; the subnets that
  resource `connectsTo` and the network each is `within`, or the network it `connectsTo` directly;
  each step with its citation.
- **Last mile.** None.
- **Same for everyone.** Placement is a walk over cited references that ends at resources whose
  role is `network`, never a guess from a name or an address range.

### Which Service Instances run in this network?

Terms: `within`, `connectsTo`, `runsOn`, `providedAs`, `networkRole`, `inScope`.

- **Estate returns.** The subnets `within` the network; the resources that `connectsTo` them or the
  network itself; the Instances that `runsOn` or are `providedAs` those resources, each with its
  Scope.
- **Last mile.** None for what is declared. What is running in the network now is a query to the
  provider.
- **Same for everyone.** It is the placement walk read backwards, so the two directions agree.

### Which networks are prod's own, and which hold Instances of more than one Environment?

Terms: `networkRole`, `provisionedFor`, `declaredAs`, `inScope`; the placement walk.

- **Estate returns.** The networks `provisionedFor` prod, through `declaredAs` for those reported
  by the provider; for each network prod's Instances are placed in, its owner, and the Scopes of
  every Instance placed in it.
- **Last mile.** None.
- **Same for everyone.** Ownership is read from the declaration's boundary and use from placement,
  and the two are reported apart. A Core Infrastructure network only prod uses is not shared; an
  Environment's network that another Environment's Instances are placed in is use across
  Environments, a gap worth surfacing.

### Which account and region is this network in?

Terms: `within`, Cloud Account, `provider`, `region`, `declaredAs`.

- **Estate returns.** The network; the Cloud Account it is `within`, directly or through
  `declaredAs`, with that account's `provider`, which is the cloud; its `region` as the provider
  writes it.
- **Last mile.** None. Where no region is recorded, the answer says so, and it is one read of the
  cited declaration or one query to the provider by provider id.
- **Same for everyone.** The region is copied verbatim from a source, never read from a name or a
  provider id.

## Network connectivity

### Which networks is this network directly connected to, and through what?

Terms: `networkRole`, `connectsTo`, `within`, `declaredAs`; one read per connector (tool).

- **Estate returns.** The connectors attached to the network; the connectors chained to them; the
  networks at the other end of each chain; each connector with its declared address or provider id
  and its citation.
- **Last mile.** Whether each connector is a peering, a transit attachment, a tunnel, or a dedicated
  link: one read of its cited declaration.
- **Same for everyone.** Connectors are picked out by role, so a workload that reaches a database in
  another network is never counted as a connection between networks.

### Is network A connected to network B, and through which connectors?

Terms: `networkRole`, `connectsTo`, `within`, `declaredAs`; route reads and the provider (tool).

- **Estate returns.** Every chain of connectors that joins A and B without passing through a third
  network; apart from them, the paths that pass through a third network, as candidates.
- **Last mile.** None for "connected". Whether traffic takes a chain, or passes on through a third
  network, is a read of the cited routes, and routes the provider propagates are a query to it.
- **Same for everyone.** "Connected" means joined by cited references. Effective reachability is
  never stored, so the estate's answer is the same for everyone and never claims that traffic flows.

### Which networks are connected to on-premises, and through which hybrid connector?

Terms: `networkRole`, `connectsTo`, External System, `provider`.

- **Estate returns.** Every chain of connectors that ends at an External System whose provider is
  `on-premises`, and the networks attached to it; apart from them, every connector whose chain ends
  only at another External System, such as an interconnection fabric.
- **Last mile.** None. For a link that ends at a fabric, what is beyond the fabric is outside the
  estate, and the answer says the link reaches a fabric.
- **Same for everyone.** The far side is an External System on a stable key, its provider part of
  that key, never guessed from an address range.

### Which networks are connected to the internet, and through which exit?

Terms: `networkRole`, `connectsTo`, `within`; route reads (tool).

- **Estate returns.** Each network's attached resources whose role is `exit`, with their citations.
- **Last mile.** Which subnets route through which exit: one read of the cited routes.
- **Same for everyone.** An exit is a resource cited where it is declared or reported, never
  inferred from a subnet's name.

### Which networks accept connections from the internet, and through which entry?

Terms: `networkRole`, `connectsTo`, `within`, `runsOn`; rule reads (tool).

- **Estate returns.** Each network's attached resources whose role is `entry`; what each
  `connectsTo` behind it, and the Instances that `runsOn` or are `providedAs` those resources; the
  network's exits, which an entry may depend on.
- **Last mile.** Whether the cited security rules admit the traffic: one read of each. A machine
  given a public address by a setting on its subnet, rather than by a resource of its own, is found
  by one read of each cited subnet declaration in the network.
- **Same for everyone.** An entry is recorded where its declaration makes it internet-facing, cited,
  so the set of ways in does not depend on who searched for them.

### Which connectors are hubs?

Terms: `networkRole`, `connectsTo`, `within`.

- **Estate returns.** Every connector, with the number of networks attached to it directly or
  through the connectors chained to it.
- **Last mile.** None. How many makes a hub is the asker's threshold.
- **Same for everyone.** The count is over cited attachments; no threshold is stored on the
  estate's behalf.

### What leaves the cloud over this dedicated link, and what is on the other side?

Terms: Declared Resource, Deployed Resource, `declaredAs`, `connectsTo`, `within`, External
System, `provider`, `networkRole`, `runsOn`; route reads and the provider (tool).

- **Estate returns.** The link, a Deployed Resource `within` its Cloud Account; the External System
  it `connectsTo` on its far side, and who runs it; the gateways and networks joined to the link by
  `connectsTo` in either direction, and those joined to them in turn, as candidates; the clusters
  and machines among them, the Declared Resources they are `declaredAs`, and the Instances that
  `runsOn` them.
- **Last mile.** One read of the cited routes, for which candidates route over the link; routes
  learned over the link from its far side are a query to the provider.
- **Same for everyone.** Every link that lands on the same far side reaches the same External
  System, so the walk ends at one node for everyone. What crosses the link at runtime is the
  tool's.

### Which networks in different accounts or clouds are connected, and through what?

Terms: Declared Resource, Deployed Resource, `declaredAs`, `connectsTo`, `within`, Cloud Account,
External System, `networkRole`.

- **Estate returns.** The resources whose role is `network`, each `within` its Cloud Account; the
  connectors attached to them, including those whose references reach a network in another account
  or cloud directly; and every External System that resources in more than one account or cloud
  `connectsTo`, each a place where those networks meet. A Declared Resource and the Deployed
  Resources `declaredAs` it are walked as one.
- **Last mile.** None for which networks are connected and through what. Whether traffic between
  two of them takes a given path is a separate question, answered from the routes each side cites.
- **Same for everyone.** The paths are walks over declared and reported references. Two clouds are
  connected only where one side's references reach the other directly or both reach the same
  External System, never by a guess from names or regions.

### How much traffic crossed this link or gateway last week?

Terms: `observedBy` and its identifiers, Deployed Resource, `declaredAs`, `provisionedFor`; the
observing tool (tool).

- **Estate returns.** The link or gateway, a Deployed Resource; the tool it is `observedBy` and the
  identifiers the tool knows it by, as the tool spells them; the owner it takes through
  `declaredAs` and `provisionedFor`.
- **Last mile.** One query to the tool with those identifiers.
- **Same for everyone.** The identifiers are the same strings for everyone, and the estate never
  holds a traffic volume, only the join to the tool that measures it.

## Cross-boundary dependencies

### Does `checkout`'s connection to `user-svc` cross a network, account, region, zone, or cloud?

Terms: `connectsTo`, `within`, Cloud Account, `provider`, `region`, `zone`, `accountZone`,
`networkRole`; the placement walk; route reads and the provider (tool).

- **Estate returns.** The `connectsTo` between the two Instances; the placement of each, and of a
  target that is a Declared or Deployed Resource placed the same way; each side's network, Cloud
  Account and its `provider`, `region`, and `zone` or `accountZone`; the chains of connectors that
  join the two networks.
- **Last mile.** Which chain the traffic takes: one read of the cited routes. Two `accountZone`
  values in different accounts are compared by one query per account for the stable identifiers
  of its zone names.
- **Same for everyone.** Each boundary is a comparison of recorded values: the cloud is the
  provider of the Cloud Account, and zones are compared only in a form that means the same thing on
  both sides.

### If the `hub` connector is removed, which Instances lose a connection, and to what?

Terms: `networkRole`, `connectsTo`, `within`; the placement walk; route reads (tool).

- **Estate returns.** The networks joined through `hub`; every `connectsTo` from an Instance placed
  in one of them to a target placed in another; for each, the other chains of connectors that join
  the same two networks without passing through `hub`.
- **Last mile.** For a pair with another chain, whether its routes would take it: one read of the
  cited routes. A pair with none loses its connection as far as the estate records.
- **Same for everyone.** The pairs are a walk over cited references, and no effective route is
  computed on the estate's behalf.

### Which services depend on on-premises systems, and through which hybrid connector?

Terms: `connectsTo`, External System, `provider`, `instantiatedFrom`; the placement walk; route
reads (tool).

- **Estate returns.** The Instances that `connectsTo` an External System whose provider is
  `on-premises`, each with its Service; the hybrid connectors attached to each Instance's networks.
- **Last mile.** Which of those connectors carries a dependency: one read of the cited routes for
  the system's address.
- **Same for everyone.** The dependency is read from the Instance's configuration, and the system
  is on-premises by its key, the same for every reader.

## Network ownership and confirmation

### Which declaration declares this network or connector, and which pipeline deploys it?

Terms: `declaredAs`, `declaredIn`, `provisionedFor`, `deploys`.

- **Estate returns.** The Declared Resource it is, or is `declaredAs`, with its Repository, address,
  and applied configuration; the owner it is `provisionedFor`; the Pipeline and job that `deploys`
  that owner.
- **Last mile.** None.
- **Same for everyone.** The Pipeline is one join through the owner, never a search for which job
  applies a directory.

### Which agent recorded this network fact, and is it older than its declaration's last change?

Terms: `prov:wasDerivedFrom`, `prov:wasGeneratedBy`, `prov:wasAttributedTo`,
`prov:generatedAtTime`; git history (tool).

- **Estate returns.** The fact's citation, pinned to a commit, or for a fact a provider reported,
  the report's as-of; the scan that generated it; the agent it is attributed to where an agent
  confirmed it; when it was generated.
- **Last mile.** One query to the git host for commits to the cited path since the pinned commit.
- **Same for everyone.** The answer names an agent, never a person, and the pinned commit is the
  same for every reader.

### Which networks and connectors are Core Infrastructure's rather than one Environment's?

Terms: `networkRole`, `declaredAs`, `provisionedFor`.

- **Estate returns.** Each resource whose role is `network` or `connector`, with the owner it is
  `provisionedFor`, through `declaredAs` for one the provider reported: an Environment, a Core
  Infrastructure, an Application, a Service, or a Service Instance; and those `declaredAs` nothing,
  which have no owner.
- **Last mile.** None.
- **Same for everyone.** The owner is read from the declaration's boundary. One with no declaration
  is listed as a gap, never counted as shared.

## Network migration

### If `checkout` moves network, what needs a new connection, and which connectors does it leave?

Terms: `connectsTo`, `networkRole`, `within`; the placement walk.

- **Estate returns.** What `checkout`'s Instance `connectsTo`, and the network each target is placed
  in; the chains of connectors between its current network and each target's network; the chains
  between the network it would move to and each target's network.
- **Last mile.** None for which. Whether an existing chain would carry the traffic is a read of the
  cited routes.
- **Same for everyone.** A move is a question over the graph as it stands, and no future state is
  stored. The network it would move to is one the estate holds: for a move to a network not yet
  declared, every dependency outside it needs a connection, and the answer says so.

### Which connectors would carry no dependency after that move?

Terms: `connectsTo`, `networkRole`; the placement walk.

- **Estate returns.** Every connector in the chains `checkout` would stop using, with every other
  `connectsTo` between Instances and targets placed in the networks it joins.
- **Last mile.** None.
- **Same for everyone.** A connector with no other dependency across it is a count over cited
  references; what crosses it at runtime is a query to the tool that observes it.

## Network gaps

### Which Service Instances have no recorded network placement?

Terms: `runsOn`, `providedAs`, `connectsTo`, `within`, `networkRole`; the sources a scan read.

- **Estate returns.** Every Instance with no placement path; for each, the resource it `runsOn` or
  is `providedAs`, if any, with its citation; the sources the scan read.
- **Last mile.** Whether each resource attaches to a network at all: one read of its cited
  declaration.
- **Same for everyone.** "Attaches to no network" and "not recorded" are told apart by what was
  read, never assumed.

### Which connectors are reported deployed but declared nowhere?

Terms: Deployed Resource, `networkRole`, `declaredAs`, `within`, Cloud Account; cost store (tool).

- **Estate returns.** Every Deployed Resource whose role is `connector`, `exit`, or `entry` and that
  has no current `declaredAs`, by provider id, with the source that reported it, as of when, and the
  Cloud Account it is `within`.
- **Last mile.** None for what a source reported. A cost row that matches no Deployed Resource is
  from something no source the estate read reported; whether it is a connector is the row's own
  type, read in the cost store.
- **Same for everyone.** The set is a query over the graph, never a search of the cloud.

## Retiring infrastructure

### What pushes to and pulls from this registry?

Terms: `deliversTo`, `pullsFrom`, `connectsTo`; `within`.

- **Estate returns.** The registry, a managed Declared Resource or the Service Instance serving a
  self-hosted one, and its image repositories `within` it; every Pipeline that `deliversTo` them
  with its job; every Service Instance that `pullsFrom` them with its image reference and pull
  secret name; everything that `connectsTo` the registry's hostname.
- **Last mile.** None for what is declared. Whether anything pulled recently is a query to the
  registry, and a workload whose image is cached on its node may not have pulled for weeks.
- **Same for everyone.** The set is a walk over declared references, never a search for the
  hostname across repositories.

### What runs on this cluster, including what the platform installs?

Terms: `runsOn`, `inScope`, Core Infrastructure; `instantiatedFrom`.

- **Estate returns.** Every Service Instance that `runsOn` the cluster, each with its Scope: an
  Application's Environment, or the Core Infrastructure whose declaration installs it, such as an
  ingress controller or a CI runner; each Instance's Service.
- **Last mile.** None for what is declared. What is running now is a query to the cluster.
- **Same for everyone.** Platform software has a Scope like any other, so it is never left out
  for lacking an Application.

### What breaks if this cluster is deleted?

Terms: `connectsTo`, `provisionedFor`, `trusts`, `runsOn`; Deployed Resource, `declaredAs`.

- **Estate returns.** The Instances that `runsOn` it; what it `connectsTo`, its subnets and security
  groups, and whatever else `connectsTo` those; the Declared Resources provisioned for the same Core
  Infrastructure, which share its declaration; every Identity that `trusts` its OIDC provider; the
  Deployed Resources `declaredAs` each, with their as-of; the Core Infrastructure it is
  provisioned for, the Pipeline job that `deploys` it, and the commit its declaration was read at.
- **Last mile.** Read the cited declarations for what a shared resource would lose; whether each
  still exists is a query to the cloud. Before any plan or destroy from the declaring job, compare
  the declaration at its commit with the live resource: a resource changed from somewhere else,
  such as a cluster upgraded past the version its declaration names, makes that job's plan
  destructive or failing.
- **Same for everyone.** Shared use is read from references in declarations, never inferred from
  names, and anything not declared is a gap rather than "unaffected".

## Adding questions

Add them the way they come, without thinking. The ones that arrive without thinking are the ones
a practitioner asks every day. Each new question is written in the three parts above before any
term is added for it; a question that needs a term the ontology lacks is how a term gets
proposed.
