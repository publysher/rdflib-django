"""
Unit tests for the store class. Includes all unit tests that are hard or annoying to doctest.
"""
import datetime
from django import test
import rdflib
from rdflib.graph import Graph
from rdflib.namespace import RDF, RDFS, Namespace
from rdflib.term import URIRef, Literal, BNode


EX = Namespace("http://www.example.com/")


artis = URIRef('http://zoowizard.eu/resource/Artis')
berlin_zoo = URIRef('http://zoowizard.eu/resource/Berlin_Zoo')
zoo = URIRef('http://schema.org/Zoo')
org = URIRef('http://schema.org/Organisation')
anonymous = BNode()
artis_label = Literal('Artis')
date_literal = Literal(datetime.date.today())
number_literal = Literal(14)
bool_literal = Literal(True)
graph_context = Graph(identifier=EX['graph-context'])


class GraphTest(test.TestCase):
    """
    Several checks on the store by using it through the official Graph interface.
    """

    def setUp(self):
        self.graph = rdflib.Graph('Django')

    def test_add_uri_statement(self):
        """
        What happens if we add statements that are all URI's
        """
        self.graph.add((artis, RDF.type, zoo))
        self.assertEquals(len(self.graph), 1)

        self.graph.add((artis, RDF.type, org))
        self.assertEquals(len(self.graph), 2)

        self.graph.add((artis, RDF.type, zoo))
        self.assertEquals(len(self.graph), 2)

    def test_single_triple(self):
        """
        Returning the triples should give the correct result
        """
        self.graph.add((artis, RDF.type, zoo))
        triples = list(self.graph.triples((None, None, None)))
        self.assertEquals(len(triples), 1)

        self.assertTupleEqual(triples[0], (artis, RDF.type, zoo))

    def test_multiple_triples(self):
        """
        Returning the triples should give the correct result
        """
        self.graph.add((artis, RDF.type, zoo))
        self.graph.add((artis, RDF.type, org))
        self.graph.add((berlin_zoo, RDF.type, zoo))
        self.assertEquals(len(list(self.graph.triples((None, None, None)))), 3)

        self.assertEquals(len(list(self.graph.triples((artis, None, None)))), 2)
        self.assertEquals(len(list(self.graph.triples((None, RDF.type, None)))), 3)
        self.assertEquals(len(list(self.graph.triples((None, None, zoo)))), 2)
        self.assertEquals(len(list(self.graph.triples((None, None, org)))), 1)

    def test_blank_nodes(self):
        """
        Adding and querying for blank nodes should also work.
        """
        self.graph.add((artis, RDFS.seeAlso, anonymous))
        self.graph.add((anonymous, RDF.type, zoo))

        triple = list(self.graph.triples((None, None, zoo)))[0]
        self.assertTupleEqual(triple, (anonymous, RDF.type, zoo))

    def test_literals(self):
        """
        Adding and querying dates should also work.
        """
        self.graph.add((artis, RDFS.label, artis_label))
        self.graph.add((artis, EX['date'], date_literal))
        self.graph.add((artis, EX['bool'], bool_literal))
        self.graph.add((artis, EX['number'], number_literal))
        self.assertEquals(len(self.graph), 4)

        self.assertEquals(self.graph.value(artis, RDFS.label), artis_label)
        self.assertEquals(self.graph.value(artis, EX['date']), date_literal)
        self.assertEquals(self.graph.value(artis, EX['bool']), bool_literal)
        self.assertEquals(self.graph.value(artis, EX['number']), number_literal)
