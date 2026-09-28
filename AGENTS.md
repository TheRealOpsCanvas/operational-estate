# AGENTS.md

Instructions for AI agents working in this repository. Humans: see
[CONTRIBUTING.md](CONTRIBUTING.md), which says the same things for people.

## What this repository is

Operational Estate is an open, vendor-neutral specification: an ontology of a
software estate. It is a standard, not a product. Read
[spec/operational-estate.md](spec/operational-estate.md) before changing
anything, and [competency-questions.md](competency-questions.md) before
proposing a term.

## How changes land

- Never push to `main`. Work on a branch and open a pull request; a maintainer
  reviews and merges it on GitHub.
- One concern per pull request. A change to the model and a change to tooling
  are two pull requests.
- Commit messages say what changed and why. Do not include links to agent
  sessions, chat transcripts, or anything a reader of this public repository
  cannot open. A `Co-Authored-By` trailer naming the agent is welcome.
- Do not add a `Signed-off-by` line on a person's behalf. The Developer
  Certificate of Origin is a person's certification; the human who opens or
  merges the pull request signs off.

## Rules for the model

- **Write against the problem, never a product.** No term, definition, example,
  or rationale names a vendor's product, service, or storage. Examples use
  neutral names (`shop`, `checkout`, `user-svc`).
- **A term needs a question.** A new class or relation comes with the
  competency question it serves, written in the three parts
  competency-questions.md uses. A term no question needs is not added.
- **State a term completely.** Its definition, what it is not, its aliases,
  its key, its domain and range, its direction and inverse.
- **Connections, not interpretations.** A property belongs in the model only if
  it could not be rebuilt from one file the estate already points at.
- **Nothing about a person.** No class, relation, or example identifies an
  individual.
- **Maturity.** Every term is `draft` until the first published version and
  may change. After that, terms are added and deprecated, never removed or
  repurposed.

## Style

- Plain declarative prose that states what is true. No narrative of how a
  decision was reached; alternatives considered go in the rationale appendix.
- Wrap Markdown at 100 columns.
- Class names are Title Case in prose (Service Instance) and PascalCase in the
  vocabulary (`estate:ServiceInstance`); relations are camelCase (`runsOn`).