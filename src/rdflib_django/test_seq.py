"""
Taken from https://github.com/RDFLib/rdflib/blob/master/test/test_seq.py
"""
import unittest

from rdflib.term import URIRef
from rdflib.graph import Graph
from rdflib_django.store import DjangoStore


class SeqTestCase(unittest.TestCase):
    """
    Tests sequences.
    """

    def setUp(self):
        store = self.store = Graph(store=DjangoStore())
        store.open(None)
        store.parse(data=s)

    def tearDown(self):
        self.store.close()

    def testSeq(self):
        """
        Tests sequences.
        """
        items = self.store.seq(URIRef("http://example.org/Seq"))
        self.assertEquals(len(items), 6)
        self.assertEquals(items[-1].concrete(), URIRef("http://example.org/six"))
        self.assertEquals(items[2].concrete(), URIRef("http://example.org/three"))
        # just make sure we can serialize
        self.store.serialize()


s = """\
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns="http://purl.org/rss/1.0/"
 xmlns:nzgls="http://www.nzgls.govt.nz/standard/"
>
 <rdf:Seq rdf:about="http://example.org/Seq">
   <rdf:li rdf:resource="http://example.org/one" />
   <rdf:li rdf:resource="http://example.org/two" />
   <rdf:li rdf:resource="http://example.org/three" />
   <rdf:li rdf:resource="http://example.org/four" />
   <rdf:li rdf:resource="http://example.org/five_five" />
   <rdf:li rdf:resource="http://example.org/six" />
 </rdf:Seq>
</rdf:RDF>
"""
