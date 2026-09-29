"""Check the Operational Estate vocabulary.

Parses ontology/estate.ttl and asserts what an OWL reasoner would catch structurally, without being
one: every term is documented, every domain and range names a declared class, every relation
between entities has an inverse, every qualified detail agrees with the relation it qualifies, and
no class sits in two groupings. It then checks that the vocabulary and the prose specification
agree: the same classes, the same relations, and the same endpoints for each.

Run from the repository root:  python tools/check.py
Exits non-zero, listing every finding, if anything fails.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

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
    groupings = {ESTATE.Software, ESTATE.Runtime}
    entity_classes = {c for c in classes if entity in superclasses(graph, c) or c == entity}
    # A qualified... property names the plain relation it qualifies; its range is the detail class.
    qualified = {p: graph.value(p, ESTATE.qualifies) for p in object_properties}
    qualified = {q: r for q, r in qualified.items() if r is not None}

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
                    if not str(expression).startswith(str(XSD)):
                        finding(f"{local(prop)}: range {expression} is not an XSD datatype")
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

    # A qualified detail agrees with its plain relation: the same source, a target the relation
    # allows, and a property chain that derives the relation from the detail.
    for q, relation in qualified.items():
        if relation not in object_properties:
            finding(f"{local(q)}: qualifies {relation}, which is not a declared object property")
            continue
        if not between_entities(graph, relation, entity_classes):
            finding(f"{local(q)}: qualifies {local(relation)}, not a relation between entities")
        q_domain = members(graph, graph.value(q, RDFS.domain))
        if q_domain != members(graph, graph.value(relation, RDFS.domain)):
            finding(f"{local(q)}: its domain differs from {local(relation)}'s")
        detail = graph.value(q, RDFS.range)
        if detail not in classes:
            finding(f"{local(q)}: its range is not a declared detail class")
            continue
        targets = [
            members(graph, graph.value(r, OWL.allValuesFrom))
            for r in graph.objects(detail, RDFS.subClassOf)
            if graph.value(r, OWL.onProperty) == ESTATE.target
        ]
        if len(targets) != 1 or targets[0] is None:
            finding(f"{local(detail)}: needs exactly one owl:allValuesFrom on target")
        elif targets[0] != members(graph, graph.value(relation, RDFS.range)):
            finding(f"{local(detail)}: its target differs from {local(relation)}'s range")
        chain = graph.value(relation, OWL.propertyChainAxiom)
        if chain is None or list(Collection(graph, chain)) != [q, ESTATE.target]:
            finding(f"{local(relation)}: needs owl:propertyChainAxiom ( {local(q)} target )")
    for relation in object_properties:
        chain = graph.value(relation, OWL.propertyChainAxiom)
        if chain is None:
            continue
        steps = list(Collection(graph, chain))
        if not steps or qualified.get(steps[0]) != relation:
            finding(f"{local(relation)}: its property chain does not start from its qualifier")

    # No class sits in two groupings.
    for cls in classes:
        both = superclasses(graph, cls) & groupings
        if len(both) > 1:
            finding(f"{local(cls)}: sits in {sorted(local(g) for g in both)}; a class has one grouping")

    check_against_spec(graph, classes, entity_classes, object_properties, inverses)

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
) -> None:
    """The vocabulary and the prose specification name the same classes, relations, and endpoints."""
    text = SPEC.read_text(encoding="utf-8")
    label_of = {c: str(graph.value(c, RDFS.label)) for c in classes}
    class_by_label = {label: c for c, label in label_of.items()}

    # Classes: every heading under "## 4. Classes" is a class, and every leaf entity class has one.
    section = text.split("## 4. Classes", 1)[1].split("\n## ", 1)[0]
    headings = set(re.findall(r"^### (.+)$", section, flags=re.MULTILINE))
    groupings = {ESTATE.Software, ESTATE.Runtime, ESTATE.Entity}
    leaves = {label_of[c] for c in entity_classes - groupings}
    for heading in sorted(headings - set(class_by_label)):
        finding(f"spec: class '{heading}' has no class in the vocabulary")
    for label in sorted(leaves - headings):
        finding(f"vocabulary: class '{label}' has no section under '4. Classes' in the spec")

    # Relations: every row of the relation table exists, with the same endpoints.
    rows = re.findall(r"^\| `(\w+)` \| ([^|]+) \| ([^|]+) \|", text, flags=re.MULTILINE)
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
    for name, source, target in rows:
        table_names.add(name)
        if name not in by_name:
            finding(f"spec: relation '{name}' is not in the vocabulary")
            continue
        dom, ran = by_name[name]
        if classes_named(source, f"'{name}' From") != dom:
            finding(f"'{name}': the spec's From column and the vocabulary's source differ")
        if classes_named(target, f"'{name}' To") != ran:
            finding(f"'{name}': the spec's To column and the vocabulary's target differ")
    for name in sorted(set(by_name) - table_names):
        finding(f"vocabulary: relation '{name}' is not in the spec's relation table")


if __name__ == "__main__":
    sys.exit(main())
