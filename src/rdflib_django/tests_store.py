"""
Unit tests for the store class. Includes all unit tests that are hard or annoying to doctest.
"""
from django import test
import rdflib
from rdflib.namespace import RDF, RDFS
from rdflib.term import URIRef, Literal, BNode


artis = URIRef('http://zoowizard.eu/resource/Artis')
zoo = URIRef('http://schema.org/Zoo')
org = URIRef('http://schema.org/Organisation')
artis_label = Literal('Artis')
anonymous = BNode()


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

    def test_triples_1(self):
        """
        Returning the triples should give the correct result
        """
        self.graph.add((artis, RDF.type, zoo))
        triples = list(self.graph.triples((None, None, None)))
        self.assertEquals(len(triples), 1)

        self.assertTupleEqual(triples[0], (artis, RDF.type, zoo))

    def test_triples_2(self):
        """
        Returning the triples should give the correct result
        """
        self.graph.add((artis, RDF.type, zoo))
        self.graph.add((artis, RDF.type, org))
        self.assertEquals(len(list(self.graph.triples((None, None, None)))), 2)

        self.assertEquals(len(list(self.graph.triples((artis, None, None)))), 2)
        self.assertEquals(len(list(self.graph.triples((None, RDF.type, None)))), 2)
        self.assertEquals(len(list(self.graph.triples((None, None, zoo)))), 1)
        self.assertEquals(len(list(self.graph.triples((None, None, org)))), 1)

    def test_blank_nodes(self):
        """
        Adding and querying for blank nodes should also work.
        """
        self.graph.add((artis, RDFS.seeAlso, anonymous))
        self.graph.add((anonymous, RDF.type, zoo))

        triple = list(self.graph.triples((None, None, zoo)))[0]
        self.assertTupleEqual(triple, (anonymous, RDF.type, zoo))
