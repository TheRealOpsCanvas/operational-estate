# Operational Estate

**Status:** draft. Every term in this document is `draft`.
**Prefix:** `estate:` **Namespace:** `https://w3id.org/operational-estate#` (reserved)
**Built on:** RDF 1.2, full conformance, whose concrete syntaxes are not yet W3C Recommendations

## 1. Scope

An organization's **software estate** is what it builds, where that software is placed, what
exists in the cloud to run it, who owns it, how it is delivered, and how to reach it. Operational
Estate is a vocabulary for that estate: a set of classes and relations, the keys that identify each
thing, and the constraints a correct estate satisfies.

It describes the problem, not any tool. That a Terraform file declares a role as a resource, or
that one program reads two kinds of thing, does not make them one class. How an implementation
stores, discovers, or serves an estate is outside this specification.

An **estate graph** is a set of facts about one estate, each attributed to whoever asserted it.
Its facts are about **entities**, the things section 4 defines, each identified by a key, and the
relations between them.
The graph describes what has been confirmed: candidates not yet confirmed are not in it.

## 2. Principles

**One word, one class.** Every overloaded word resolves to exactly one class. Each definition says
what the term is and what it is not, and the shorthand practitioners use is declared as an alias
(`skos:altLabel`).

**Connections, not interpretations.** The estate holds identity, containment, and relations between
things, each with evidence citing where it was read. It does not hold a reading of a file's
contents, such as whether a CI job is manual, because a reader handed the file reads that in one
step, and a stored reading is a verdict true only at one reading of a file nothing re-checks. A
property belongs in the model only if it could not be rebuilt from one file the estate already
points at, or it is a value copied verbatim from a pinned file, such as the version a deploy
writes: a copy at a pinned commit is never stale, and it outlives the commit if that is lost.

**For anything live, the join and not the value.** The last error, the current cost, what is
running now: the estate holds which tool, which identifier, and as of when, and the tool holds the
value. The version declared in an environment is a declared value, not a live one: the estate holds
it with the path, the field, and the commit it was read at, and what is running is the tool's.

**Every pointer is a citation pinned to a commit.** "Read `values-prod.yaml`" gives different
answers on different days; "read it at `abc123`, field `imageTag`" gives one, and the as-of says how
old it is. A pin is taken from a repository's default branch or a tag, the history everyone shares,
never from a branch only one checkout has. A commit that later becomes unreachable, through a
rewritten history, invalidates the facts pinned to it (section 8), and they are read again.

**The same answer for everyone.** The estate does not answer questions; it points a reader, often
an AI model, at the answer, so that different people asking the same thing get the same one. What
remains after the estate has answered is at most one bounded step: nothing, one read of a cited
file at a pinned commit, or one query to a tool by a pinned identifier. Never a search.

**Nothing about a person.** No individual appears in an estate graph, and no relation in this
vocabulary has a person as its subject or object. A fact is attributed to the agent that asserted
it; ownership is by Team; who is on a Team, and which person an agent acts for, are outside the
estate.

## 3. Groupings and roles

A grouping is a class only where a relation needs exactly that set of classes.

| Grouping | Members | Needed by |
|---|---|---|
| **Software** | Application, Service | domain of `implementedIn`, range of `provisionedFor` |
| **Runtime** | Service Instance, Cloud Resource | domain and range of `connectsTo` |
| **Scope** | Environment, Core Infrastructure | range of `inScope` |

Scope is the named unit runtime things are placed in and owned by: an Application's Environment, or
the Core Infrastructure a platform declares. Every other class sits directly under `estate:Entity`.

**A role is not a class.** Where what a relation points at crosses classes, the relation carries the
role. What a workload reads secrets from may be a Service Instance (a self-hosted Vault), a Cloud
Resource (a cloud secrets manager), or an External System (a hosted secrets service), so there is no
Secret Store class: the secret stores in an estate are the targets of `readsSecretsFrom`. An
observability tool is the same, through `observedBy`.

## 4. Classes

### Application

A product or capability that delivers value to its users: a set of Services and the Environments
they are deployed into. Not a single deployable (a Service), and not what it runs on: its Service
Instances run on Cloud Resources, provisioned by its own Environments, by Core Infrastructure, by
the Application itself or one of its Services across every Environment, such as the Application's
DNS zone or a Service's image registry, or by one Service Instance, when the deployment code
declares a resource for that Instance alone, such as its queue, or its chart creates one, such as a
load balancer. An Application needs no repository of its own: in an estate of services, it is named
where it is composed and deployed.

### Service

A deployable unit of software that implements all or part of an Application. The unit itself,
never a running copy of one, so it is the same Service in every Environment. A monolith is an
Application with one Service; a presentation may show the Application alone when it has exactly
one. A Service may be `memberOf` several Applications.

A Service may be **upstream**: deployed from a chart or image nobody in the estate builds, such as
Superset from `apache/superset`. An upstream Service has no `implementedIn` and no `builds`, and is
not incomplete for lacking them. The version of it in an Environment is the chart or image version
read at a pinned commit.

*Aliases:* "the service" (with the contrast that a running copy is a Service Instance).

### Environment

A named set of runtime things belonging to one Application, as a practitioner means it: "shop prod"
across whatever clouds, accounts, and clusters it spans. Nothing structural defines it, and each
Application has its own, so shop dev and checkout dev are two Environments. An Environment does not
run; its Service Instances do.

A runtime thing is in an Environment in one of two ways. A Cloud Resource declared in the
Environment's own code, such as a database in `envs/dev/`, is `provisionedFor` it. A Service
Instance deployed into it has the Environment in its key; a file name, a pipeline stage, a tag, or
an account name is the evidence for which Environment that is, confirmed where that evidence is only
a naming convention.

*Aliases:* "app-env", "the environment", "stage".

### Service Instance

One deployment of one Service into one Scope: an Environment, or a Core Infrastructure for software
the platform installs, such as an ingress controller or a CI runner its cluster declaration deploys.
It is `instantiatedFrom` exactly one Service, never an Application, so every question about software
takes one path, from an Instance through its Service to its Application.

*Draft rename:* **Deployed Instance**. "Service Instance" reads wrong for a monolith, and
"Instance" alone collides with a virtual machine instance and with OpenTelemetry's
`service.instance.id`, which is one replica. "Deployed" is what the evidence shows, where "running"
is a live fact the estate never holds.

### Core Infrastructure

Infrastructure declared outside the declarations of any single Environment, Application, or Service:
a platform team's repository, stack, or module. The test is where the declaration lives, not how
many Environments use it today, so a cluster a shared infrastructure repository declares is Core
Infrastructure while only dev uses it. It is an owner, not a place: Cloud Resources and Identities
are provisioned for it, the Service Instances of the software it installs are in it, and it is not
the cluster provisioned for it.

*Aliases:* "landing zone".

### Cloud Resource

A provisioned thing in a cloud or cluster: a database, a bucket, a load balancer, a cluster, a
function, a registry repository, a declared secret. It has exactly one owner. A Cloud Resource with
no declaration is a gap, because its cost and its failures belong to nobody the estate can name.

### Identity

Something that acts: the role a deploy job assumes, the role a workload runs as, a service
principal, a managed identity, a permission set people assume, a Kubernetes user. Not a Cloud
Resource: many identities have no owner in the estate and no declaration, such as a permission set
created in a console, and that is normal rather than a gap; and some live in no cloud account, such
as an identity provider's group or the OIDC subject a role trusts. Never a human principal: a user
account named after a person stays out.

### Cloud Account

An AWS account, a GCP project, an Azure subscription: the provider-defined unit that Cloud
Resources, Identities, and credentials sit `within`, and that charges belonging to no resource land
on. A place things live, not a thing that runs, so it is not a Cloud Resource, and not in Scope,
which holds the units a practitioner defines. Member accounts are `within` the payer or organization
they bill to.

*Aliases:* "account", "project", "subscription".

### Repository

A version-controlled store of files, such as a Git repository, whose role is `app`, `iac`, or
`mixed`. Where things are declared; neither software nor runtime.

*Aliases:* "repo".

### Pipeline

A CI/CD definition file, such as a GitHub Actions workflow or a `.gitlab-ci.yml`, contained by its
Repository, with the events it listens for. Every definition file is a Pipeline, whether or not any
of its jobs relates it to anything else. A job is never an entity: it is a discriminator on the
relations out of a Pipeline.

### External System

Something the estate references and nothing in it provisions: the tools a thing is observed by,
such as Datadog or PagerDuty, and the hosted destinations a Pipeline delivers to, such as npmjs.org
or Docker Hub. Anything with a class of its own is not an External System: a role is an Identity; a
cluster, registry repository, or bucket is a Cloud Resource; an account is a Cloud Account.

### Team

A group of people who work on part of the estate, named as its sources name it: `@acme/platform` in
`CODEOWNERS`, `group:platform` in a catalog, `team=platform` as a tag, each an alias of one Team. A
Team owns things and contains no one.

*Aliases:* "owner".

## 5. Relations

Every relation joins two entities and declares its inverse. Provenance relations read from subject
to context (`implementedIn`, `deployedFrom`, `provisionedFor`); causal relations read from cause to
effect (`triggers`, `deploys`, `deliversTo`).

A relation that carries data of its own, a deployment's job and write location, is stated as the
relation, and the data is put on a **detail**: an RDF 1.2 reifier of that relation's triple. The
relation is the fact: `pipeline deploys instance`. A detail is optional, and one relation may have
several, told apart by their key (section 6). The detail's class names the relation it describes
(`Deployment` for `deploys`); it is how the vocabulary stores a relation's data, and it is not an
entity. In Turtle the annotation syntax states both at once:

```turtle
:deploy-yml estate:deploys :user-svc-prod
    ~ :deploy-yml.deploys.user-svc-prod.deploy-prod
    {| estate:job "deploy-prod" ; estate:writesPath "values-prod.yaml" ; estate:writesField "image.tag" |} .
```

A reifier describes a triple without asserting it, so the relation a detail reifies must be
asserted too; the annotation syntax does this, and section 7 requires it of every estate graph.

| Relation | From | To | Carries |
|---|---|---|---|
| `declaredIn` | Service, Pipeline, Core Infrastructure, Cloud Resource | Repository | |
| `inScope` | Service Instance | Scope | |
| `memberOf` | Service | Application | |
| `implementedIn` | Software | Repository | |
| `placedUnder` | Environment | Application | |
| `instantiatedFrom` | Service Instance | Service | |
| `deployedFrom` | Environment, Service Instance | Repository | |
| `triggers` | Pipeline | Pipeline | job, variables sent |
| `deploys` | Pipeline | Environment, Core Infrastructure, Software, Service Instance | job, pinned write location |
| `builds` | Pipeline | Service | job, tag scheme |
| `deliversTo` | Pipeline | Service Instance, Cloud Resource, External System | job |
| `pullsFrom` | Service Instance | Service Instance, Cloud Resource, External System | image reference, pull secret name |
| `provisionedFor` | Cloud Resource, Identity | Environment, Core Infrastructure, Software, Service Instance | |
| `runsOn` | Service Instance | Cloud Resource | |
| `providedAs` | Service Instance | Cloud Resource | |
| `within` | Cloud Resource, Identity, Cloud Account | Cloud Account, Cloud Resource | |
| `connectsTo` | Runtime | Runtime | |
| `readsSecretsFrom` | Service Instance, Pipeline | Service Instance, Cloud Resource, External System | path or name |
| `observedBy` | Service Instance, Environment, Pipeline | Service Instance, Cloud Resource, External System | the tool's identifiers |
| `accessedAs` | Environment | Identity | declared credential name |
| `runsAs` | Service Instance, Pipeline | Identity | |
| `trusts` | Identity | Pipeline, Repository, Identity, Cloud Resource | |
| `ownedBy` | Application, Service, Repository, Core Infrastructure, Cloud Account, Cloud Resource, Identity | Team | |

### Containment

`declaredIn` and `inScope` are containment: the parent is part of the child's key, so each has
exactly one. `declaredIn` is the Repository whose files declare a Service, Pipeline, Core
Infrastructure, or Cloud Resource; it is not `implementedIn`, the Repository whose code implements
software, and an upstream Service has the first and never the second. `inScope` is the one Scope a
Service Instance is deployed into: an Environment, or the Core Infrastructure whose declaration
installs it.

### Placement

`placedUnder` and `instantiatedFrom` attach a parent the practitioner's picture has but the evidence
that produced the entity did not assert. Each is resolved by name when either side arrives, or
chosen where names do not settle it. How it was resolved is provenance, as for any fact (section 8):
a match is generated by the activity that made it, and a choice is attributed to the agent that
confirmed it.

### Delivery

`deploys` runs from a Pipeline to any owner `provisionedFor` names: an Environment or Service
Instance it deploys into, or the Core Infrastructure, Application, or Service whose declarations it
applies. So the Pipeline and job that change a Cloud Resource are one join from it, through its
owner. `deploys` carries the job, the variables the job sets, such as one that selects which
component it deploys, and, where the deploy writes a version, the pinned write location: the
repository, path, and field it writes, at the commit it was read at, with the value declared there.
`builds` carries the job and the tag scheme, `$CI_COMMIT_SHA` or a version scheme, which links what
is declared in an Environment to the commit it came from; the artifact itself is not modeled.
`triggers` carries the variables one Pipeline sends another. Neither `triggers` nor `deploys` says
whether it runs automatically or on which branch: that is the job's rule, read in the cited file.

A registry is where build meets runtime. A Pipeline `deliversTo` the image repository it pushes to,
and a Service Instance `pullsFrom` the one its manifest's image reference names, with that
reference and the name of any pull secret on the relation. Push and pull meet at the image
repository, a Cloud Resource `within` its registry, or at the Service Instance that serves a
self-hosted registry. As with secret stores, a registry is a role: the registries in an estate are
the targets of these two relations. Tags, digests, and what was pushed or pulled when are live and
the registry's.

### Where a Service Instance runs, and what it is

`runsOn` is the Cloud Resource an Instance runs on: a cluster, a virtual machine, a function
runtime. `providedAs` is the Cloud Resource an Instance is, such as a serverless function. A
Kubernetes workload `runsOn` its cluster; a serverless deployment is `providedAs` its function. An
Instance's Cloud Account is derived through them, never stored beside them.

### Ownership

`provisionedFor` is read from the module or chart boundary a declaration sits inside, a structural
fact rather than a path token. A module for one Application or one Service outside any Environment,
such as a deploy repository's `app/` declaring the Application's DNS zone or its
`services/user-svc/` declaring that Service's image registry, is the Application's or the Service's;
the same Service's module inside an Environment's declarations is its Instance's there. `ownedBy`
names a Team and only a Team. An Environment's owner and a Pipeline's are derived from their
Application and Repository. Evidence that names only individuals, `@jane` in `CODEOWNERS`,
establishes no owner. Membership is not ownership: `memberOf` says which Application a Service is
part of, `ownedBy` says whose it is.

### Access

`accessedAs` is the credential a repository declares for deploying or operating an Environment: a
role the deploy job assumes, or the profile name its scripts pass. It is not where the Environment
runs, and it is not derivable, because it is read from the repository's own deploy configuration. An
Environment spanning accounts has one per credential. A declared role is an Identity; a declared
profile name is not an estate thing but the team's agreed name for a credential, carried on the
relation so that whoever holds a local credential by that name can match it to the Identity.

`runsAs` is the Identity a workload or a pipeline acts as.

`trusts` runs from an Identity to the Pipeline, Repository, Identity, or Cloud Resource its trust
policy allows to assume it, read from the declaration; the Cloud Resource is a federation provider,
such as a cluster's OIDC provider that workloads assume roles through. A question that starts from a
role needs no relation, because the policy is in the file the Identity cites; a question that starts
from a repository, what it can reach if compromised, would otherwise be a search across every
repository that declares roles. Chained assumption is a multi-hop walk. The walk ends at roles and
the accounts they are within: what a role permits is a read of its cited policy, never an effective
permission.

### Reach

`connectsTo` is what an Instance reaches, read from the connection strings, hostnames, environment
variables, and service references in its configuration: a Cloud Resource such as a Redis cluster, or
another Instance it calls. A Cloud Resource `connectsTo` what its declaration references: a cluster
its subnets and security groups, a load balancer its target group. That is what deleting a shared
resource breaks. It is cited, never inferred from a name. What a connection means at runtime,
sessions, retries, leader election, is a reading of the manifest the relation cites.

*Aliases:* "depends on".

`readsSecretsFrom` carries the path or name read, never the value. Where the secret is itself
declared, the relation targets that Cloud Resource; otherwise it targets the store, with the path on
the relation. What a self-hosted store's outage reaches is a walk back along these relations.

### Observation

`observedBy` carries the tool's identifiers exactly as the tool spells them, `service` and `env` for
Datadog, `service.name` and `deployment.environment` for OpenTelemetry, never normalized: the reader
knows the tool and the values and writes the query. Identifiers are recorded where their evidence
is. Each Instance's relation carries what its own manifest declares, so an inconsistency across one
Environment's Instances is visible; an identifier declared once for a whole Environment, such as an
agent's environment tag, sits on the Environment's relation and is not copied onto its Instances. An
Instance a tool knows by an identifier no file declares is a gap. A Pipeline has the relation only
where its CI system knows it by something other than its key: a pipeline in GitHub Actions or GitLab
is known by its repository and path, which its key holds, while a Jenkins job, a CircleCI project,
or a Buildkite pipeline has a name of its own.

## 6. Identity and keys

**A key is what independent readings agree on, and nothing another repository would have to say
first.** A parent is in a key when two readings of different repositories must agree on it to
produce the same entity; otherwise it is a relation. Nothing infrastructural is in a key: a cluster
or account name would put "cluster" in identifiers read by people who think "prod".

| Class | Key |
|---|---|
| Application | its name |
| Environment | its asserted Application name and its name |
| Service | the Repository that declares it and its name |
| Service Instance | its Scope's key and its deployed name |
| Repository | its canonical remote |
| Pipeline | its Repository and its definition path |
| Core Infrastructure | the Repository, the stack, module, or root that declares it, and its applied configuration |
| Cloud Resource | the Repository that declares it, a source kind, the declared address, and its root's applied configuration |
| Identity | its provider and the provider's identifier for it |
| Cloud Account | its provider and the provider's id |
| External System | its provider, kind, and name |
| Team | its name |

**A Cloud Resource is keyed by where it is declared.** The source kind names the address grammar, as
one of `terraform`, `cloudformation`, `cdk`, `pulumi`, or `kubernetes`: a Terraform resource address
in its root module, a CloudFormation stack and logical id, a CDK construct path, a Pulumi URN, or a
Kubernetes manifest path and object. The last is how controller-created resources are declared: a
`Service` of type `LoadBalancer` declares a load balancer, a `PersistentVolumeClaim` a volume, an
`Ingress` an application load balancer, a Karpenter `NodePool` a fleet, a Crossplane managed
resource anything.

**A declaration may be a module call, and one root may be applied more than once.** A resource
declared through a module, such as a cluster created by a call to a registry module, is declared by
that call: its address is the module call's address in the root, and the address of the resource
inside the module, which the repository does not contain, is read from state as an alias. A root
applied once per environment, with a var file, a workspace, a stack, or an overlay, declares a
separate resource for each, so the applied configuration is part of the key of every Cloud Resource
and Core Infrastructure it declares: one module call applied with `prod.tfvars` and with
`dev.tfvars` is two clusters, and two Core Infrastructures. A name computed from variables is read
with every file it is computed from cited.

**Identity and Cloud Account are keyed by their provider identifier**, because it is fixed before
anything is applied: an account id is issued when the account exists, and a role ARN is derivable
from its account and name. A declaration is cited when one exists.

**A live identifier is an alias, and it says where it came from.** The binding of a declared address
to its id or ARN is read from a source that holds both halves: Terraform state, a CloudFormation
stack listing, a Pulumi checkpoint, a Kubernetes object's status, or a controller's tags on the
cloud side, such as `kubernetes.io/cluster/<name>`, which the alias marks as weaker than a
declaration. An alias carries its source, the source's serial or version, and its as-of. When a
source moves on and an address maps to a new id, the former alias is kept and marked
`prov:invalidatedAtTime`, the time it stopped holding, because older cost rows still carry it; an
alias with no invalidation time is current. Environment and Team also carry
alternate names.

**A detail is keyed by the relation it reifies**, meaning its source's key, the relation, and its
target's key, and, where one relation can have several details, by what tells them apart: the job
for a `triggers`, `deploys`, `builds`, or `deliversTo`, the secret path for a `readsSecretsFrom`. An
`observedBy`, `accessedAs`, or `pullsFrom` has at most one detail. A detail is named by an
identifier derived from its key, never a blank node, so two graphs that say the same thing about one
relation merge into one detail.

**An individual's identifier is relative: its kind and key, resolved under a base.** For example
`service_instance/shop/prod/user-svc`. A serialization sets `@base`, and how an implementation
chooses its base is its own. Two graphs of one estate merge by kind and key with no identifier
rewritten, because keys are derived and the base is a prefix.

## 7. Constraints

**Every runtime thing has exactly one owner, so Environments never overlap.** A Service Instance is
in exactly one Scope, by its key. A Cloud Resource is `provisionedFor` exactly one of an
Environment, a Core Infrastructure, an Application, a Service, or a Service Instance; one
provisioned for an Application or Service is in no Environment. Use across Environments is
`connectsTo`, never shared membership, and a `connectsTo` from one Environment into another is a gap
worth surfacing. An Identity is `provisionedFor` its declaring owner when it has one.

Further constraints, each to be stated as a SHACL shape. The ones about details are checked today as
SPARQL 1.2 queries, until SHACL 1.2 is published:

- A detail is named by an identifier derived from its key, never a blank node.
- A detail reifies exactly one relation, that relation carries data, and it is asserted.
- A relation's data is on a detail of that relation: a `job` is on a `triggers`, `deploys`,
  `builds`, or `deliversTo`, never on a `readsSecretsFrom`.
- A Service Instance has at most one `instantiatedFrom`, and its target is a Service.
- An Environment has exactly one asserted Application.
- A Pipeline that `deploys` an Environment or Instance is in the Repository it is `deployedFrom`.
- `ownedBy` targets only a Team.
- A `readsSecretsFrom` carries no secret value.
- Every alias carries its source.
- At most one alias per declared address and source has no `prov:invalidatedAtTime`.
- No individual `prov:Person` appears in an estate graph.

## 8. Provenance

Provenance uses PROV-O directly, under the `prov:` prefix. A fact `prov:wasDerivedFrom` each
citation; a scan is a `prov:Activity` that generated it; a confirmation `prov:wasAttributedTo` the
`prov:Agent` that made it; `prov:generatedAtTime` is its as-of; `prov:invalidatedAtTime` is when a
fact that was true stopped being so, such as an alias its source has moved past, or a fact pinned
to a commit that became unreachable. A fact is never rewritten to say it no longer holds.

A scan records what it looked at: it `prov:used` each repository it read, at the commit it read.
That is what tells "not recorded", where nothing that would show a thing was read, from "looked and
not found", where it was read and the thing is not there. An answer about something the estate
does not hold says which.

## 9. Cost

Cost adds no terms. Cost rows are not in the estate. A row lands on a Cloud Resource by alias, or,
for a charge that belongs to no resource (a commitment, support, a credit, tax), on the Cloud
Account billed for it, and climbs by ownership. It climbs two ways that answer different questions:
by place, Instance to Environment to Application, "what does checkout's prod cost", or Instance to
Core Infrastructure for software the platform installs; by software, Instance to Service to
Application, "what does `auth-svc` cost everywhere". A resource provisioned for an Application or
Service is in no Environment's cost: it joins the climb at the Application or the Service. They
agree for a Service in one Application and differ, correctly, for a shared one. A tag, or a
controller's tag, is evidence for a relation the model already has. How cost shared through Core
Infrastructure is split is decided downstream: the estate serves the ownership. A cost row that
matches no declared resource is a gap, never "other".

## 10. Testing the model

**Competency questions are the test.** There is no ground truth an ontology is correct against: it
is correct to the extent the questions it claims are answerable, and complete to the extent the
questions that matter are on the list. Each question in
[competency-questions.md](../competency-questions.md) is written as what the estate returns, the
last mile, and what makes the answer the same for everyone, and will run as a query over worked
estates. A question whose last mile is a search fails.

**Worked estates** test the model against estates other than the one it was drawn from. The failure
signal is a fact that has to be forced in, the sentence "a Service too, if we need it": wherever it
is said, the model is wrong there.

## 11. Evolution

Every term is `draft` until the first published version, and a draft term may be renamed or
removed. After publication a term is `stable`: it is added and never removed or repurposed, and one
that turns out wrong is marked `owl:deprecated` with a pointer to its replacement. `owl:versionInfo`
carries a version; the namespace never carries one and never moves. The first published version
waits for RDF 1.2 to become a W3C Recommendation, so that nothing this specification depends on
changes after its terms are stable.

## Appendix: rationale

**OWL for the vocabulary, SHACL for constraints.** OWL states classes, properties, domain, range,
subclass, inverses, and keys, and it is what the industry reads a model in. It cannot state "exactly
one owner" or "no value on a secret reference"; SHACL can, and validating an estate graph against
shapes makes the specification checkable by anyone. Rejected: a programming-language schema, which
speaks to nobody outside one codebase; LinkML, which adds a generator between the model and OWL for
a model this size; prose alone, because nothing checks a description.

**RDF 1.2 reifiers for a relation's data, rather than qualified details.** RDF 1.1 can put data on a
relation only through a separate resource that repeats the relation's target, PROV-O's
qualification pattern, which then needs a rule that the two agree. A reifier is bound to the triple
it describes, so the target cannot disagree, and several reifiers of one triple are part of the
model. The cost is that RDF 1.2 is newer than the tools most estates already use; the W3C's RDF 1.2
Interoperability note gives a lossless translation to RDF 1.1 for any tool that needs one.

**How a placement was resolved is provenance, not a property.** An earlier draft gave `placedUnder`
and `instantiatedFrom` a placement origin, a name match or an operator's choice. It was rejected:
how a fact came to be is what PROV-O states for every fact, a private two-value copy of it on two
relations would say it for those alone, and the graph holds only what has been confirmed.

**When an alias stopped holding is provenance, not a status.** An earlier draft gave an alias a
status, `current` or `former`. It was rejected: a status goes stale when the source moves on and has
to be rewritten, while `prov:invalidatedAtTime` is written once and says when, which is what
attributing an older cost row needs.

**`connectsTo` rather than `dependsOn`.** The relation is read from connection strings and
references, and "connects to" says exactly that. "Depends on" claims the connection is critical,
which the estate does not know, invites dependencies no configuration shows, and in Terraform and
Compose means apply or startup order. It is kept as an alias. The credential relation, once
`connectedVia`, is `accessedAs`, beside `runsAs`, so the two names do not collide.

**Platform software is in a Scope, not an Application.** An ingress controller or a CI runner a
platform's cluster declaration installs is software with versions, deploys, and connections, so it
is a Service Instance. Its Scope is the Core Infrastructure that installs it. Rejected: treating it
as a Cloud Resource, which puts software in the resource class; and a "platform" Application,
whose Environments would be a fiction.

**A declared value is stored with its pin.** Reading the field at the pinned commit gives the value,
so storing it was once excluded. But a value copied at a pinned commit never goes stale, it survives
the commit being lost, and a reader without it tends to substitute the repository's latest commit
for what was declared.

**Software, Scope, Runtime rather than Logical and Deployed.** Environment is not something that
runs, and Core Infrastructure is not something deployed. A grouping named for meaning but populated
by whichever relation needed a union drifts from its name.

**A Service Instance is always of a Service.** The alternative, an Instance of the Application
directly when it has no Services, matches how monolith teams speak, but gives every question about
software two paths and needs a rule for which applies; and a monolith that grows a second deployable
would move its existing Instance from Application to Service.

**Identity is not a Cloud Resource.** As a subclass it would need exceptions to both the one-owner
rule and the undeclared-is-a-gap rule on the day it landed, and it could not hold identities that
live in no cloud account.

**Cloud Account is not a Cloud Resource.** Nothing runs in it; what makes it matter is what it
holds.

**Core Infrastructure is not an Application.** A tenant is not an Application's Environment, and
Application should keep meaning something that delivers value.

**A Cloud Resource is keyed by its declaration, not its provider id.** For most resources the
provider id exists only after apply, so two readings could never agree on it.

**Environments belong to an Application, not the organization.** Organization-level environments
would remove the hierarchy practitioners work in, and what several Applications' environments share
is Core Infrastructure, which the model already has.

**Nothing infrastructural in a key.** A key derived from the deploy boundary would put "cluster" in
every identifier read by people who think "prod".
