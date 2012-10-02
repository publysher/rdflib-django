"""
Unittests for namespace management.
"""
from django.utils import unittest
from rdflib.graph import Graph
from rdflib.term import URIRef
from rdflib_django.store import DjangoStore


XML_NAMESPACE = ("xml", URIRef("http://www.w3.org/XML/1998/namespace"))
RDF_NAMESPACE = ("rdf", URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#"))
RDFS_NAMESPACE = ("rdfs", URIRef("http://www.w3.org/2000/01/rdf-schema#"))


class NamespaceTestCase(unittest.TestCase):
    """
    Tests for the weird behavior of RDFlib graphs and the default
    namespaces.
    """

    def setUp(self):
        self.store = DjangoStore()

    def testDefaultNamespaces(self):
        """
        Test the presence of the default namespaces.
        """
        g = Graph(store=self.store)
        namespaces = list(g.namespaces())
        self.assertIn(XML_NAMESPACE, namespaces)
        self.assertIn(RDF_NAMESPACE, namespaces)
        self.assertIn(RDFS_NAMESPACE, namespaces)

        # and again; by default, initializing the graph will re-bind the namespaces
        # using a naive implementation, this will fail.
        g = Graph(store=self.store)
        g_namespaces = list(g.namespaces())
        self.assertIn(XML_NAMESPACE, g_namespaces)
        self.assertIn(RDF_NAMESPACE, g_namespaces)
        self.assertIn(RDFS_NAMESPACE, g_namespaces)
