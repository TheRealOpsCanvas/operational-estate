# Operational Estate

**Status:** draft. Every term in this document is `draft`.
**Prefix:** `estate:` **Namespace:** `https://w3id.org/operational-estate#` (reserved)

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
points at.

**For anything live, the join and not the value.** The last error, the current cost, what is
running now: the estate holds which tool, which identifier, and as of when, and the tool holds the
value. The version declared in an environment is not stored either: the estate pins the path, the
field, and the commit, and reading the field at that commit gives everyone the same value.

**Every pointer is a citation pinned to a commit.** "Read `values-prod.yaml`" gives different
answers on different days; "read it at `abc123`, field `imageTag`" gives one, and the as-of says how
old it is.

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
| **Software** | Application, Service | domain of `implementedIn` |
| **Runtime** | Service Instance, Cloud Resource | range of `dependsOn` |

**Scope**, Environment and Core Infrastructure, the named units runtime things are placed in and
owned by, is vocabulary for explaining the model and not a class, because no relation ranges over
exactly those two. Every other class sits directly under `estate:Entity`.

**A role is not a class.** Where what a relation points at crosses classes, the relation carries the
role. What a workload reads secrets from may be a Service Instance (a self-hosted Vault), a Cloud
Resource (a cloud secrets manager), or an External System (a hosted secrets service), so there is no
Secret Store class: the secret stores in an estate are the targets of `readsSecretsFrom`. An
observability tool is the same, through `observedBy`.

## 4. Classes

### Application

A product or capability that delivers value to its users: a set of Services and the Environments
they are deployed into. Not a single deployable (a Service), and not the platform it runs on (Core
Infrastructure). An Application needs no repository of its own: in an estate of services, it is
named where it is composed and deployed.

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
Environment's own code, such as a database in `envs/dev/`, is `provisionedBy` it. A Service Instance
deployed into it has the Environment in its key; a file name, a pipeline stage, a tag, or an account
name is the evidence for which Environment that is, confirmed where that evidence is only a naming
convention.

*Aliases:* "app-env", "the environment", "stage".

### Service Instance

One deployment of one Service into one Environment. It is `instantiatedFrom` exactly one Service,
never an Application, so every question about software takes one path, from an Instance through its
Service to its Application.

*Draft rename:* **Deployed Instance**. "Service Instance" reads wrong for a monolith, and
"Instance" alone collides with a virtual machine instance and with OpenTelemetry's
`service.instance.id`, which is one replica. "Deployed" is what the evidence shows, where "running"
is a live fact the estate never holds.

### Core Infrastructure

Infrastructure declared outside any single Environment's declarations: a platform team's
repository, stack, or module. The test is where the declaration lives, not how many Environments
use it today, so a cluster a platform repository declares is Core Infrastructure while only dev
uses it. It is an owner, not a place: it provisions Cloud Resources, and it is not the cluster it
provisions.

*Aliases:* "platform", "landing zone".

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

### Repo

A version-controlled repository, whose role is `app`, `iac`, or `mixed`. Where things are declared;
neither software nor runtime.

### Pipeline

A CI/CD definition file, such as a GitHub Actions workflow or a `.gitlab-ci.yml`, contained by its
Repo, with the events it listens for. Every definition file is a Pipeline, whether or not any of its
jobs relates it to anything else. A job is never an entity: it is a discriminator on the relations
out of a Pipeline.

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
to context (`implementedIn`, `deployedFrom`, `provisionedBy`); causal relations read from cause to
effect (`triggers`, `deploys`, `deliversTo`).

A triple joins exactly two things, so a relation that carries data of its own, a deployment's job
and write location, is stated twice. The **plain relation** joins the two entities and is the fact:
`pipeline deploys instance`. Its **qualified detail** is optional: a small resource the source
points to with the relation's `qualified...` property (`qualifiedDeployment` for `deploys`), which
names the same `target` and carries the data. The detail is how the vocabulary stores a relation's
data; it is not an entity. The two must agree: wherever a qualified detail exists, its plain
relation holds between the same source and target. The vocabulary states this as a property chain,
so a reasoner derives the plain relation from the detail, and the constraints in section 7 require
it of every estate graph. The same pattern is PROV-O's qualification pattern.

| Relation | From | To | Carries |
|---|---|---|---|
| `declaredIn` | Service, Pipeline, Core Infrastructure, Cloud Resource | Repo | |
| `inEnvironment` | Service Instance | Environment | |
| `memberOf` | Service | Application | |
| `implementedIn` | Software | Repo | |
| `placedUnder` | Environment | Application | placement origin |
| `instantiatedFrom` | Service Instance | Service | placement origin |
| `deployedFrom` | Environment, Service Instance | Repo | |
| `triggers` | Pipeline | Pipeline | job, variables sent |
| `deploys` | Pipeline | Environment, Service Instance | job, pinned write location |
| `builds` | Pipeline | Service | job, tag scheme |
| `deliversTo` | Pipeline | Cloud Resource, External System | job |
| `provisionedBy` | Cloud Resource, Identity | Environment, Core Infrastructure, Service Instance | |
| `runsOn` | Service Instance | Cloud Resource | |
| `providedAs` | Service Instance | Cloud Resource | |
| `within` | Cloud Resource, Identity, Cloud Account | Cloud Account, Cloud Resource | |
| `dependsOn` | Service Instance | Runtime | |
| `readsSecretsFrom` | Service Instance, Pipeline | Service Instance, Cloud Resource, External System | path or name |
| `observedBy` | Service Instance, Environment, Pipeline | Service Instance, Cloud Resource, External System | the tool's identifiers |
| `connectedVia` | Environment | Identity | declared credential name |
| `runsAs` | Service Instance, Pipeline | Identity | |
| `trusts` | Identity | Pipeline, Repo, Identity | |
| `ownedBy` | Application, Service, Repo, Core Infrastructure, Cloud Account, Cloud Resource, Identity | Team | |

### Containment

`declaredIn` and `inEnvironment` are containment: the parent is part of the child's key, so each
has exactly one. `declaredIn` is the Repo whose files declare a Service, Pipeline, Core
Infrastructure, or Cloud Resource; it is not `implementedIn`, the Repo whose code implements
software, and an upstream Service has the first and never the second. `inEnvironment` is the one
Environment a Service Instance is deployed into.

### Placement

`placedUnder` and `instantiatedFrom` attach a parent the practitioner's picture has but the evidence
that produced the entity did not assert. Each is resolved by name when either side arrives, and
carries its placement origin: an automatic name match, or an operator's choice.

### Delivery

`deploys` carries the job and the pinned write location: the repository, path, and field a deploy
writes, at the commit it was read at. `builds` carries the job and the tag scheme, `$CI_COMMIT_SHA`
or a version scheme, which links what is declared in an Environment to the commit it came from; the
artifact itself is not modeled. `triggers` carries the variables one Pipeline sends another.

### Where a Service Instance runs, and what it is

`runsOn` is the Cloud Resource an Instance runs on: a cluster, a virtual machine, a function
runtime. `providedAs` is the Cloud Resource an Instance is, such as a serverless function. A
Kubernetes workload `runsOn` its cluster; a serverless deployment is `providedAs` its function. An
Instance's Cloud Account is derived through them, never stored beside them.

### Ownership

`provisionedBy` is read from the module or chart boundary a declaration sits inside, a structural
fact rather than a path token. `ownedBy` names a Team and only a Team. An Environment's owner and a
Pipeline's are derived from their Application and Repo. Evidence that names only individuals,
`@jane` in `CODEOWNERS`, establishes no owner. Membership is not ownership: `memberOf` says which
Application a Service is part of, `ownedBy` says whose it is.

### Access

`connectedVia` is the credential a repository declares for deploying or operating an Environment: a
role the deploy job assumes, or the profile name its scripts pass. It is not where the Environment
runs, and it is not derivable, because it is read from the repository's own deploy configuration. An
Environment spanning accounts has one per credential. A declared role is an Identity; a declared
profile name is not an estate thing but the team's agreed name for a credential, carried on the
relation so that whoever holds a local credential by that name can match it to the Identity.

`runsAs` is the Identity a workload or a pipeline acts as.

`trusts` runs from an Identity to the Pipeline, Repo, or Identity its trust policy allows to assume
it, read from the declaration. A question that starts from a role needs no relation, because the
policy is in the file the Identity cites; a question that starts from a repository, what it can
reach if compromised, would otherwise be a search across every repository that declares roles.
Chained assumption is a multi-hop walk. The walk ends at roles and the accounts they are within:
what a role permits is a read of its cited policy, never an effective permission.

### Reach

`dependsOn` is what an Instance reaches, read from the connection strings, hostnames, environment
variables, and service references in its configuration: a Cloud Resource such as a Redis cluster,
or another Instance it calls. It is cited, never inferred from a name. What a dependency means at
runtime, sessions, retries, leader election, is a reading of the manifest the relation cites.

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
| Service | the Repo that declares it and its name |
| Service Instance | its Environment's key and its deployed name |
| Repo | its canonical remote |
| Pipeline | its Repo and its definition path |
| Core Infrastructure | the Repo and the stack, module, or root that declares it |
| Cloud Resource | the Repo that declares it, a source kind, and the declared address |
| Identity | its provider and the provider's identifier for it |
| Cloud Account | its provider and the provider's id |
| External System | its provider, kind, and name |
| Team | its name |

**A Cloud Resource is keyed by where it is declared.** The source kind names the address grammar: a
Terraform resource address in its root module, a CloudFormation stack and logical id, a CDK
construct path, a Pulumi URN, or a Kubernetes manifest path and object. The last is how
controller-created resources are declared: a `Service` of type `LoadBalancer` declares a load
balancer, a `PersistentVolumeClaim` a volume, an `Ingress` an application load balancer, a
Karpenter `NodePool` a fleet, a Crossplane managed resource anything.

**Identity and Cloud Account are keyed by their provider identifier**, because it is fixed before
anything is applied: an account id is issued when the account exists, and a role ARN is derivable
from its account and name. A declaration is cited when one exists.

**A live identifier is an alias, and it says where it came from.** The binding of a declared
address to its id or ARN is read from a source that holds both halves: Terraform state, a
CloudFormation stack listing, a Pulumi checkpoint, a Kubernetes object's status, or a controller's
tags on the cloud side, such as `kubernetes.io/cluster/<name>`, which the alias marks as weaker than
a declaration. An alias carries its source, the source's serial or version, and its as-of. When a
source moves on and an address maps to a new id, the former alias is kept as former, because older
cost rows still carry it. Environment and Team also carry alternate names.

**An individual's identifier is relative: its kind and key, resolved under a base.** For example
`service_instance/shop/prod/user-svc`. A serialization sets `@base`, and how an implementation
chooses its base is its own. Two graphs of one estate merge by kind and key with no identifier
rewritten, because keys are derived and the base is a prefix.

## 7. Constraints

**Every runtime thing has exactly one owner, so Environments never overlap.** A Service Instance is
in exactly one Environment, by its key. A Cloud Resource is `provisionedBy` exactly one of an
Environment, a Core Infrastructure, or a Service Instance. Use across Environments is `dependsOn`,
never shared membership, and a `dependsOn` from one Environment into another is a gap worth
surfacing. An Identity is `provisionedBy` its declaring owner when it has one.

Further constraints, each to be stated as a SHACL shape:

- A qualified detail agrees with its plain relation: if an entity has a `qualified...` detail whose
  `target` is another entity, the plain relation it qualifies holds between the same two entities.
- A Service Instance has at most one `instantiatedFrom`, and its target is a Service.
- An Environment has exactly one asserted Application.
- A Pipeline that `deploys` an Environment or Instance is in the Repo it is `deployedFrom`.
- `ownedBy` targets only a Team.
- A `readsSecretsFrom` carries no secret value.
- Every alias carries its source.
- No individual `prov:Person` appears in an estate graph.

## 8. Provenance

Provenance uses PROV-O directly, under the `prov:` prefix. A fact `prov:wasDerivedFrom` each
citation; a scan is a `prov:Activity` that generated it; a confirmation `prov:wasAttributedTo` the
`prov:Agent` that made it; `prov:generatedAtTime` is its as-of.

## 9. Cost

Cost adds no terms. Cost rows are not in the estate. A row lands on a Cloud Resource by alias, or,
for a charge that belongs to no resource (a commitment, support, a credit, tax), on the Cloud
Account billed for it, and climbs by ownership. It climbs two ways that answer different questions:
by place, Instance to Environment to Application, "what does checkout's prod cost"; by software,
Instance to Service to Application, "what does `auth-svc` cost everywhere". They agree for a Service
in one Application and differ, correctly, for a shared one. A tag, or a controller's tag, is
evidence for a relation the model already has. How cost shared through Core Infrastructure is split
is decided downstream: the estate serves the ownership. A cost row that matches no declared resource
is a gap, never "other".

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
carries a version; the namespace never carries one and never moves.

## Appendix: rationale

**OWL for the vocabulary, SHACL for constraints.** OWL states classes, properties, domain, range,
subclass, inverses, and keys, and it is what the industry reads a model in. It cannot state "exactly
one owner" or "no value on a secret reference"; SHACL can, and validating an estate graph against
shapes makes the specification checkable by anyone. Rejected: a programming-language schema, which
speaks to nobody outside one codebase; LinkML, which adds a generator between the model and OWL for
a model this size; prose alone, because nothing checks a description.

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
