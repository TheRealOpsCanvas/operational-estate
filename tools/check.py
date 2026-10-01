"""Check the Operational Estate vocabulary.

Parses ontology/estate.ttl and asserts what an OWL reasoner would catch structurally, without being
one: every term is documented, every domain and range names a declared class, every relation
between entities has an inverse, every detail class names the one relation it describes, and no
class sits in two groupings. It then checks that the vocabulary and the prose specification agree:
the same classes, the same relations, the same endpoints, the same relations carrying data, and the
same values for each property that allows only a listed set.
Last, it parses every Turtle example in the specification as RDF 1.2 and checks the rules every
detail keeps, after proving on a broken example that each rule still fires.

Run from the repository root:  python tools/check.py
Exits non-zero, listing every finding, if anything fails.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pyoxigraph as ox
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD

ROOT = Path(__file__).resolve().parent.parent
VOCABULARY = ROOT / "ontology" / "estate.ttl"
SPEC = ROOT / "docs" / "spec" / "operational-estate.md"
ESTATE = Namespace("https://w3id.org/operational-estate#")
MATURITIES = {"draft", "stable"}

findings: list[str] = []


def finding(message: str) -> None:
    findings.append(message)


def local(term: URIRef) -> str:
    return str(term).removeprefix(str(ESTATE))


def is_estate(term: object) -> bool:
    return isinstance(term, URIRef) and str(term).startswith(str(ESTATE)) and term != ESTATE[""]


def members(graph: Graph, expression: object) -> set[URIRef] | None:
    """The named classes a class expression covers: itself, or the members of a union."""
    if isinstance(expression, URIRef):
        return {expression}
    if isinstance(expression, BNode):
        union = graph.value(expression, OWL.unionOf)
        if union is not None:
            return {m for m in Collection(graph, union) if isinstance(m, URIRef)}
    return None


def between_entities(graph: Graph, prop: URIRef, entity_classes: set[URIRef]) -> bool:
    """Whether a property's declared domain and range are both entity classes."""
    domain = members(graph, graph.value(prop, RDFS.domain))
    rng = members(graph, graph.value(prop, RDFS.range))
    return bool(domain) and bool(rng) and domain <= entity_classes and rng <= entity_classes


def value_set(graph: Graph, expression: object) -> list[Literal] | None:
    """The values a closed datatype allows, when it is a datatype listing them with owl:oneOf."""
    if not isinstance(expression, BNode):
        return None
    listed = graph.value(expression, OWL.oneOf)
    if listed is None:
        return None
    return list(Collection(graph, listed))


def superclasses(graph: Graph, cls: URIRef) -> set[URIRef]:
    seen: set[URIRef] = set()
    stack = [cls]
    while stack:
        for parent in graph.objects(stack.pop(), RDFS.subClassOf):
            if isinstance(parent, URIRef) and parent not in seen:
                seen.add(parent)
                stack.append(parent)
    return seen


def main() -> int:
    graph = Graph()
    try:
        graph.parse(VOCABULARY, format="turtle")
    except Exception as error:  # a parse error is the only finding worth reporting
        print(f"{VOCABULARY.relative_to(ROOT)}: does not parse: {error}")
        return 1

    classes = {c for c in graph.subjects(RDF.type, OWL.Class) if is_estate(c)}
    object_properties = {p for p in graph.subjects(RDF.type, OWL.ObjectProperty) if is_estate(p)}
    datatype_properties = {p for p in graph.subjects(RDF.type, OWL.DatatypeProperty) if is_estate(p)}
    annotation_properties = {p for p in graph.subjects(RDF.type, OWL.AnnotationProperty) if is_estate(p)}

    entity = ESTATE.Entity
    groupings = {ESTATE.Software, ESTATE.Runtime, ESTATE.Scope}
    entity_classes = {c for c in classes if entity in superclasses(graph, c) or c == entity}

    # Every term is documented, and every term but an annotation carries a maturity.
    for term in classes | object_properties | datatype_properties | annotation_properties:
        if graph.value(term, RDFS.label) is None:
            finding(f"{local(term)}: no rdfs:label")
        if graph.value(term, SKOS.definition) is None:
            finding(f"{local(term)}: no skos:definition")
        if term in annotation_properties:
            continue
        maturity = graph.value(term, ESTATE.maturity)
        if maturity is None or str(maturity) not in MATURITIES:
            finding(f"{local(term)}: estate:maturity is {maturity!r}, not one of {sorted(MATURITIES)}")

    # Every domain and range names declared classes, or a datatype for a datatype property.
    for prop in object_properties | datatype_properties:
        for axis in (RDFS.domain, RDFS.range):
            for expression in graph.objects(prop, axis):
                if prop in datatype_properties and axis == RDFS.range:
                    if value_set(graph, expression) is not None:
                        continue
                    if not str(expression).startswith(str(XSD)):
                        finding(f"{local(prop)}: range {expression} is not an XSD datatype or a list of values")
                    continue
                named = members(graph, expression)
                if named is None:
                    finding(f"{local(prop)}: {axis.fragment} is not a class or a union of classes")
                    continue
                for cls in named - classes:
                    finding(f"{local(prop)}: {axis.fragment} names undeclared class {cls}")

    # Every relation between entities has exactly one declared inverse, declared in one direction.
    inverse_of = {p: graph.value(p, OWL.inverseOf) for p in object_properties}
    inverses = {q for q in inverse_of.values() if q is not None}
    for prop, inverse in inverse_of.items():
        if inverse is None:
            continue
        if inverse not in object_properties:
            finding(f"{local(prop)}: inverse {inverse} is not a declared object property")
        elif inverse_of.get(inverse) is not None:
            finding(f"{local(prop)}: inverse {local(inverse)} declares an inverse too; declare it once")
        elif any(graph.value(inverse, axis) is not None for axis in (RDFS.domain, RDFS.range)):
            finding(f"{local(inverse)}: an inverse takes its domain and range from {local(prop)}")
    for prop in object_properties - inverses:
        if between_entities(graph, prop, entity_classes) and inverse_of[prop] is None:
            finding(f"{local(prop)}: a relation between entities needs an owl:inverseOf")

    # A detail class names one relation between entities, sits under Detail, and is the only
    # detail class of that relation; every class under Detail names one.
    detail_root = ESTATE.Detail
    detail_classes = {c for c in classes if detail_root in superclasses(graph, c)}
    detail_of = {c: graph.value(c, ESTATE.detailOf) for c in classes}
    detail_of = {c: r for c, r in detail_of.items() if r is not None}
    for cls, relation in detail_of.items():
        if cls not in detail_classes:
            finding(f"{local(cls)}: names a relation with estate:detailOf but is not a subclass of Detail")
        if relation not in object_properties:
            finding(f"{local(cls)}: is a detail of {relation}, which is not a declared object property")
        elif not between_entities(graph, relation, entity_classes):
            finding(f"{local(cls)}: is a detail of {local(relation)}, not a relation between entities")
    for cls in sorted(detail_classes - set(detail_of)):
        finding(f"{local(cls)}: a subclass of Detail needs estate:detailOf")
    for relation in set(detail_of.values()):
        named = sorted(local(c) for c, r in detail_of.items() if r == relation)
        if len(named) > 1:
            finding(f"{local(relation)}: has several detail classes {named}; a relation has one")

    # A property's domain holds details or entities, never both.
    for prop in object_properties | datatype_properties:
        domain = members(graph, graph.value(prop, RDFS.domain)) or set()
        if domain & detail_classes and domain - detail_classes:
            finding(f"{local(prop)}: its domain mixes detail classes with other classes")

    # No class sits in two groupings.
    for cls in classes:
        both = superclasses(graph, cls) & groupings
        if len(both) > 1:
            finding(f"{local(cls)}: sits in {sorted(local(g) for g in both)}; a class has one grouping")

    check_against_spec(graph, classes, entity_classes, object_properties, inverses, set(detail_of.values()))
    check_examples()

    for message in findings:
        print(message)
    print(f"{len(findings)} finding(s) in {VOCABULARY.relative_to(ROOT)}")
    return 1 if findings else 0


def check_against_spec(
    graph: Graph,
    classes: set[URIRef],
    entity_classes: set[URIRef],
    object_properties: set[URIRef],
    inverses: set[URIRef],
    carrying: set[URIRef],
) -> None:
    """The vocabulary and the prose specification name the same classes, relations, and endpoints."""
    text = SPEC.read_text(encoding="utf-8")
    label_of = {c: str(graph.value(c, RDFS.label)) for c in classes}
    class_by_label = {label: c for c, label in label_of.items()}

    # Classes: every heading under "## 4. Classes" is a class, and every leaf entity class has one.
    section = text.split("## 4. Classes", 1)[1].split("\n## ", 1)[0]
    headings = set(re.findall(r"^### (.+)$", section, flags=re.MULTILINE))
    groupings = {ESTATE.Software, ESTATE.Runtime, ESTATE.Scope, ESTATE.Entity}
    leaves = {label_of[c] for c in entity_classes - groupings}
    for heading in sorted(headings - set(class_by_label)):
        finding(f"spec: class '{heading}' has no class in the vocabulary")
    for label in sorted(leaves - headings):
        finding(f"vocabulary: class '{label}' has no section under '4. Classes' in the spec")

    # Value sets: every value a closed datatype lists is named in the specification.
    for prop in sorted(graph.subjects(RDF.type, OWL.DatatypeProperty)):
        values = value_set(graph, graph.value(prop, RDFS.range))
        for value in values or []:
            if not isinstance(value, Literal):
                finding(f"{local(prop)}: its value set lists {value}, which is not a literal")
            elif f"`{value}`" not in text:
                finding(f"{local(prop)}: the value '{value}' is not named in the spec")

    # Relations: every row of the relation table exists, with the same endpoints.
    rows = re.findall(r"^\| `(\w+)` \| ([^|]+) \| ([^|]+) \|([^|]*)\|", text, flags=re.MULTILINE)
    by_name: dict[str, tuple[set[URIRef], set[URIRef]]] = {}
    for prop in object_properties - inverses:
        if between_entities(graph, prop, entity_classes):
            by_name[local(prop)] = (
                members(graph, graph.value(prop, RDFS.domain)) or set(),
                members(graph, graph.value(prop, RDFS.range)) or set(),
            )

    def classes_named(cell: str, where: str) -> set[URIRef]:
        named = set()
        for label in (part.strip() for part in cell.split(",")):
            if label not in class_by_label:
                finding(f"spec: relation table {where} names '{label}', which is no class's label")
            else:
                named.add(class_by_label[label])
        return named

    table_names = set()
    for name, source, target, carries in rows:
        table_names.add(name)
        if name not in by_name:
            finding(f"spec: relation '{name}' is not in the vocabulary")
            continue
        dom, ran = by_name[name]
        if classes_named(source, f"'{name}' From") != dom:
            finding(f"'{name}': the spec's From column and the vocabulary's source differ")
        if classes_named(target, f"'{name}' To") != ran:
            finding(f"'{name}': the spec's To column and the vocabulary's target differ")
        if bool(carries.strip()) != (ESTATE[name] in carrying):
            finding(f"'{name}': the spec's Carries column and the vocabulary's detail class disagree")
    for name in sorted(set(by_name) - table_names):
        finding(f"vocabulary: relation '{name}' is not in the spec's relation table")


# What every estate graph satisfies about details, as SPARQL 1.2 over the graph and the vocabulary.
# Each query returns the reifiers that break its rule.
DETAIL_RULES = {
    "a detail is named by an IRI, never a blank node": """
        SELECT ?r WHERE { ?r rdf:reifies ?t FILTER isBlank(?r) }""",
    "the relation a detail reifies is asserted": """
        SELECT ?r WHERE { ?r rdf:reifies <<( ?s ?p ?o )>> FILTER NOT EXISTS { ?s ?p ?o } }""",
    "a detail reifies one relation": """
        SELECT ?r WHERE { ?r rdf:reifies ?a, ?b FILTER (?a != ?b) }""",
    "a detail reifies a relation that carries data": """
        SELECT ?r WHERE { ?r rdf:reifies <<( ?s ?p ?o )>> FILTER NOT EXISTS { ?d estate:detailOf ?p } }""",
    "a relation's data is on a detail of that relation": """
        SELECT ?r WHERE {
            ?r ?data ?v .
            ?data rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)? ?c . ?c rdfs:subClassOf estate:Detail .
            FILTER NOT EXISTS {
                ?r rdf:reifies <<( ?s ?p ?o )>> .
                ?data rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)? ?d . ?d estate:detailOf ?p .
            }
        }""",
}
PREFIXES = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX estate: <https://w3id.org/operational-estate#>
PREFIX : <https://example.org/estate/>
"""
# Breaks every rule above once, so the check proves each rule still fires.
BROKEN = """
:p1 estate:deploys :i1 ~ :ok {| estate:job "deploy-prod" |} .
:p1 estate:deploys :i1 {| estate:job "unnamed" |} .
:unasserted rdf:reifies <<( :p1 estate:deploys :i2 )>> ; estate:job "deploy-dev" .
:two rdf:reifies <<( :p1 estate:deploys :i1 )>>, <<( :p1 estate:builds :s1 )>> .
:plain rdf:reifies <<( :i1 estate:inScope :e1 )>> .
:wrong rdf:reifies <<( :i1 estate:readsSecretsFrom :v1 )>> ; estate:job "deploy-prod" .
:i1 estate:readsSecretsFrom :v1 .
:p1 estate:builds :s1 .
:i1 estate:inScope :e1 .
"""
BROKEN_EXPECTED = {
    "a detail is named by an IRI, never a blank node": 1,
    "the relation a detail reifies is asserted": 1,
    "a detail reifies one relation": 1,
    "a detail reifies a relation that carries data": 1,
    "a relation's data is on a detail of that relation": 1,
}


def detail_violations(turtle: str) -> dict[str, int]:
    """How many reifiers in the Turtle 1.2 text break each detail rule."""
    store = ox.Store()
    store.load(VOCABULARY.read_bytes(), format=ox.RdfFormat.TURTLE)
    store.load((PREFIXES + turtle).encode(), format=ox.RdfFormat.TURTLE, to_graph=ox.DefaultGraph())
    return {
        rule: len({row["r"] for row in store.query(PREFIXES + query, use_default_graph_as_union=True)})
        for rule, query in DETAIL_RULES.items()
    }


def check_examples() -> None:
    """Every Turtle example in the specification parses as RDF 1.2 and keeps the detail rules."""
    got = detail_violations(BROKEN)
    for rule, count in got.items():
        if count != BROKEN_EXPECTED[rule]:
            finding(f"detail rule '{rule}' caught {count} of {BROKEN_EXPECTED[rule]} in the broken example")
    blocks = re.findall(r"^```turtle\n(.*?)^```", SPEC.read_text(encoding="utf-8"), flags=re.MULTILINE | re.DOTALL)
    for number, block in enumerate(blocks, 1):
        try:
            got = detail_violations(block)
        except (SyntaxError, ValueError) as error:
            finding(f"spec: Turtle example {number} does not parse: {error}")
            continue
        for rule, count in got.items():
            if count:
                finding(f"spec: Turtle example {number} breaks '{rule}'")


if __name__ == "__main__":
    sys.exit(main())
