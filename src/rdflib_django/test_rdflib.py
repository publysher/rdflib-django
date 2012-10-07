"""
Unittests based on the tests in the rdflib-extras package
"""
from django import test
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.namespace import RDF
from rdflib.term import URIRef, BNode


# pylint: disable=C0111,R0915
class GraphTest(test.TestCase):
    """
    Testing the basic graph functionality.

    Heavily based on https://github.com/RDFLib/rdflib-postgresql/blob/master/test/graph_case.py
    """
    store_name = "Django"
    storetest = True
    path = ''
    create = True

    michel = URIRef(u'michel')
    tarek = URIRef(u'tarek')
    bob = URIRef(u'bob')
    likes = URIRef(u'likes')
    hates = URIRef(u'hates')
    pizza = URIRef(u'pizza')
    cheese = URIRef(u'cheese')

    def setUp(self):
        self.graph = Graph(store=self.store_name)
        self.graph.destroy(self.path)
        self.graph.open(self.path, create=self.create)

    def tearDown(self):
        self.graph.destroy(self.path)
        self.graph.close()

    def addStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.graph.add((tarek, likes, pizza))
        self.graph.add((tarek, likes, cheese))
        self.graph.add((michel, likes, pizza))
        self.graph.add((michel, likes, cheese))
        self.graph.add((bob, likes, cheese))
        self.graph.add((bob, hates, pizza))
        self.graph.add((bob, hates, michel))
        self.graph.commit()

    def removeStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.graph.remove((tarek, likes, pizza))
        self.graph.remove((tarek, likes, cheese))
        self.graph.remove((michel, likes, pizza))
        self.graph.remove((michel, likes, cheese))
        self.graph.remove((bob, likes, cheese))
        self.graph.remove((bob, hates, pizza))
        self.graph.remove((bob, hates, michel))

    def testAdd(self):
        self.addStuff()

    def testRemove(self):
        self.addStuff()
        self.removeStuff()

    def testTriples(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        triples = self.graph.triples
        Any = None

        self.addStuff()

        # unbound subjects
        self.assertEquals(len(list(triples((Any, likes, pizza)))), 2)
        self.assertEquals(len(list(triples((Any, hates, pizza)))), 1)
        self.assertEquals(len(list(triples((Any, likes, cheese)))), 3)
        self.assertEquals(len(list(triples((Any, hates, cheese)))), 0)

        # unbound objects
        self.assertEquals(len(list(triples((michel, likes, Any)))), 2)
        self.assertEquals(len(list(triples((tarek, likes, Any)))), 2)
        self.assertEquals(len(list(triples((bob, hates, Any)))), 2)
        self.assertEquals(len(list(triples((bob, likes, Any)))), 1)

        # unbound predicates
        self.assertEquals(len(list(triples((michel, Any, cheese)))), 1)
        self.assertEquals(len(list(triples((tarek, Any, cheese)))), 1)
        self.assertEquals(len(list(triples((bob, Any, pizza)))), 1)
        self.assertEquals(len(list(triples((bob, Any, michel)))), 1)

        # unbound subject, objects
        self.assertEquals(len(list(triples((Any, hates, Any)))), 2)
        self.assertEquals(len(list(triples((Any, likes, Any)))), 5)

        # unbound predicates, objects
        self.assertEquals(len(list(triples((michel, Any, Any)))), 2)
        self.assertEquals(len(list(triples((bob, Any, Any)))), 3)
        self.assertEquals(len(list(triples((tarek, Any, Any)))), 2)

        # unbound subjects, predicates
        self.assertEquals(len(list(triples((Any, Any, pizza)))), 3)
        self.assertEquals(len(list(triples((Any, Any, cheese)))), 3)
        self.assertEquals(len(list(triples((Any, Any, michel)))), 1)

        # all unbound
        self.assertEquals(len(list(triples((Any, Any, Any)))), 7)
        self.removeStuff()
        self.assertEquals(len(list(triples((Any, Any, Any)))), 0)

    def xxx_testStatementNode(self):
        graph = self.graph

        from rdflib.term import Statement

        c = URIRef("http://example.org/foo#c")
        r = URIRef("http://example.org/foo#r")
        s = Statement((self.michel, self.likes, self.pizza), c)
        graph.add((s, RDF.value, r))
        self.assertEquals(r, graph.value(s, RDF.value))
        self.assertEquals(s, graph.value(predicate=RDF.value, object=r))

    def xxx_testGraphValue(self):
        from rdflib.graph import GraphValue

        graph = self.graph

        alice = URIRef("alice")
        bob = URIRef("bob")
        pizza = URIRef("pizza")
        cheese = URIRef("cheese")

        g1 = Graph()
        g1.add((alice, RDF.value, pizza))
        g1.add((bob, RDF.value, cheese))
        g1.add((bob, RDF.value, pizza))

        g2 = Graph()
        g2.add((bob, RDF.value, pizza))
        g2.add((bob, RDF.value, cheese))
        g2.add((alice, RDF.value, pizza))

        gv1 = GraphValue(store=graph.store, graph=g1)
        gv2 = GraphValue(store=graph.store, graph=g2)
        graph.add((gv1, RDF.value, gv2))
        v = graph.value(gv1)
        self.assertEquals(gv2.identifier, v.identifier)
        graph.remove((gv1, RDF.value, gv2))

    def testConnected(self):
        graph = self.graph
        self.addStuff()
        self.assertEquals(True, graph.connected())

        jeroen = URIRef("jeroen")
        unconnected = URIRef("unconnected")

        graph.add((jeroen, self.likes, unconnected))

        self.assertEquals(False, graph.connected())

    def testSub(self):
        g1 = Graph()
        g2 = Graph()

        g1.add((self.tarek, self.likes, self.pizza))
        g1.add((self.bob, self.likes, self.cheese))

        g2.add((self.bob, self.likes, self.cheese))

        g3 = g1 - g2

        self.assertEquals(len(g3), 1)
        self.assertEquals((self.tarek, self.likes, self.pizza) in g3, True)
        self.assertEquals((self.tarek, self.likes, self.cheese) in g3, False)

        self.assertEquals((self.bob, self.likes, self.cheese) in g3, False)

        g1 -= g2

        self.assertEquals(len(g1), 1)
        self.assertEquals((self.tarek, self.likes, self.pizza) in g1, True)
        self.assertEquals((self.tarek, self.likes, self.cheese) in g1, False)

        self.assertEquals((self.bob, self.likes, self.cheese) in g1, False)

    def testGraphAdd(self):
        g1 = Graph()
        g2 = Graph()

        g1.add((self.tarek, self.likes, self.pizza))

        g2.add((self.bob, self.likes, self.cheese))

        g3 = g1 + g2

        self.assertEquals(len(g3), 2)
        self.assertEquals((self.tarek, self.likes, self.pizza) in g3, True)
        self.assertEquals((self.tarek, self.likes, self.cheese) in g3, False)

        self.assertEquals((self.bob, self.likes, self.cheese) in g3, True)

        g1 += g2

        self.assertEquals(len(g1), 2)
        self.assertEquals((self.tarek, self.likes, self.pizza) in g1, True)
        self.assertEquals((self.tarek, self.likes, self.cheese) in g1, False)

        self.assertEquals((self.bob, self.likes, self.cheese) in g1, True)

    def testGraphIntersection(self):
        g1 = Graph()
        g2 = Graph()

        g1.add((self.tarek, self.likes, self.pizza))
        g1.add((self.michel, self.likes, self.cheese))

        g2.add((self.bob, self.likes, self.cheese))
        g2.add((self.michel, self.likes, self.cheese))

        g3 = g1 * g2

        self.assertEquals(len(g3), 1)
        self.assertEquals((self.tarek, self.likes, self.pizza) in g3, False)
        self.assertEquals((self.tarek, self.likes, self.cheese) in g3, False)

        self.assertEquals((self.bob, self.likes, self.cheese) in g3, False)

        self.assertEquals((self.michel, self.likes, self.cheese) in g3, True)

        g1 *= g2

        self.assertEquals(len(g1), 1)

        self.assertEquals((self.tarek, self.likes, self.pizza) in g1, False)
        self.assertEquals((self.tarek, self.likes, self.cheese) in g1, False)

        self.assertEquals((self.bob, self.likes, self.cheese) in g1, False)

        self.assertEquals((self.michel, self.likes, self.cheese) in g1, True)


xmltestdoc = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns="http://example.org/"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <rdf:Description rdf:about="http://example.org/a">
    <b rdf:resource="http://example.org/c"/>
  </rdf:Description>
</rdf:RDF>
"""


n3testdoc = """@prefix : <http://example.org/> .

:a :b :c .
"""


nttestdoc = "<http://example.org/a> <http://example.org/b> <http://example.org/c> .\n"


class ContextTest(test.TestCase):
    """
    Testing different contexts.

    Heavily based on https://github.com/RDFLib/rdflib-postgresql/blob/master/test/context_case.py
    """
    store_name = "Django"
    storetest = True
    path = ""
    create = True

    michel = URIRef(u'michel')
    tarek = URIRef(u'tarek')
    bob = URIRef(u'bob')
    likes = URIRef(u'likes')
    hates = URIRef(u'hates')
    pizza = URIRef(u'pizza')
    cheese = URIRef(u'cheese')
    c1 = URIRef(u'context-1')
    c2 = URIRef(u'context-2')

    def setUp(self):
        self.graph = ConjunctiveGraph(store=self.store_name)
        self.graph.destroy(self.path)
        self.graph.open(self.path, create=self.create)

    def tearDown(self):
        self.graph.destroy(self.path)
        self.graph.close()

    def get_context(self, identifier):
        assert isinstance(identifier, URIRef) or isinstance(identifier, BNode), type(identifier)
        return Graph(store=self.graph.store, identifier=identifier, namespace_manager=self)

    def addStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        c1 = self.c1
        graph = Graph(self.graph.store, c1)

        graph.add((tarek, likes, pizza))
        graph.add((tarek, likes, cheese))
        graph.add((michel, likes, pizza))
        graph.add((michel, likes, cheese))
        graph.add((bob, likes, cheese))
        graph.add((bob, hates, pizza))
        graph.add((bob, hates, michel))

    def removeStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        c1 = self.c1
        graph = Graph(self.graph.store, c1)

        graph.remove((tarek, likes, pizza))
        graph.remove((tarek, likes, cheese))
        graph.remove((michel, likes, pizza))
        graph.remove((michel, likes, cheese))
        graph.remove((bob, likes, cheese))
        graph.remove((bob, hates, pizza))
        graph.remove((bob, hates, michel))

    def addStuffInMultipleContexts(self):
        c1 = self.c1
        c2 = self.c2
        triple = (self.pizza, self.hates, self.tarek)

        # add to default context
        self.graph.add(triple)
        # add to context 1
        graph = Graph(self.graph.store, c1)
        graph.add(triple)
        # add to context 2
        graph = Graph(self.graph.store, c2)
        graph.add(triple)

    def testConjunction(self):
        self.addStuffInMultipleContexts()
        triple = (self.pizza, self.likes, self.pizza)
        # add to context 1
        graph = Graph(self.graph.store, self.c1)
        graph.add(triple)
        self.assertEquals(len(self.graph), len(graph))

    def testAdd(self):
        self.addStuff()

    def testRemove(self):
        self.addStuff()
        self.removeStuff()

    def testLenInOneContext(self):
        c1 = self.c1
        # make sure context is empty

        self.graph.remove_context(self.get_context(c1))
        graph = Graph(self.graph.store, c1)
        oldLen = len(self.graph)

        for _ in range(0, 10):
            graph.add((BNode(), self.hates, self.hates))
        self.assertEquals(len(graph), oldLen + 10)
        self.assertEquals(len(self.get_context(c1)), oldLen + 10)
        self.graph.remove_context(self.get_context(c1))
        self.assertEquals(len(self.graph), oldLen)
        self.assertEquals(len(graph), 0)

    def testLenInMultipleContexts(self):
        oldLen = len(self.graph)
        self.addStuffInMultipleContexts()

        # addStuffInMultipleContexts is adding the same triple to
        # three different contexts. So it's only + 1
        self.assertEquals(len(self.graph), oldLen + 1)

        graph = Graph(self.graph.store, self.c1)
        self.assertEquals(len(graph), oldLen + 1)

    def testRemoveInMultipleContexts(self):
        c1 = self.c1
        c2 = self.c2
        triple = (self.pizza, self.hates, self.tarek)

        self.addStuffInMultipleContexts()

        # triple should be still in store after removing it from c1 + c2
        self.assertIn(triple, self.graph)
        graph = Graph(self.graph.store, c1)
        graph.remove(triple)
        self.assertIn(triple, self.graph)
        graph = Graph(self.graph.store, c2)
        graph.remove(triple)
        self.assertIn(triple, self.graph)
        self.graph.remove(triple)
        # now gone!
        self.assertNotIn(triple, self.graph)

        # add again and see if remove without context removes all triples!
        self.addStuffInMultipleContexts()
        self.graph.remove(triple)
        self.assertNotIn(triple, self.graph)

    def testContexts(self):
        triple = (self.pizza, self.hates, self.tarek)

        self.addStuffInMultipleContexts()

        def cid(c):
            if not isinstance(c, basestring):
                return c.identifier
            return c

        self.assert_(self.c1 in [cid(c) for c in self.graph.contexts()])
        self.assert_(self.c2 in [cid(c) for c in self.graph.contexts()])

        contextList = [cid(c) for c in self.graph.contexts(triple)]
        self.assert_(self.c1 in contextList)
        self.assert_(self.c2 in contextList)

    def testRemoveContext(self):
        c1 = self.c1

        self.addStuffInMultipleContexts()
        self.assertEquals(len(Graph(self.graph.store, c1)), 1)
        self.assertEquals(len(self.get_context(c1)), 1)

        self.graph.remove_context(self.get_context(c1))
        self.assert_(self.c1 not in self.graph.contexts())

    def testRemoveAny(self):
        Any = None
        self.addStuffInMultipleContexts()
        self.graph.remove((Any, Any, Any))
        self.assertEquals(len(self.graph), 0)

    def testTriples(self):
        triples = self.graph.triples
        graph = self.graph
        c1graph = Graph(self.graph.store, self.c1)
        c1triples = c1graph.triples
        Any = None

        self.addStuff()

        # unbound subjects with context
        self.assertEquals(len(list(c1triples((Any, self.likes, self.pizza)))), 2)
        self.assertEquals(len(list(c1triples((Any, self.hates, self.pizza)))), 1)
        self.assertEquals(len(list(c1triples((Any, self.likes, self.cheese)))), 3)
        self.assertEquals(len(list(c1triples((Any, self.hates, self.cheese)))), 0)

        # unbound subjects without context, same results!
        self.assertEquals(len(list(triples((Any, self.likes, self.pizza)))), 2)
        self.assertEquals(len(list(triples((Any, self.hates, self.pizza)))), 1)
        self.assertEquals(len(list(triples((Any, self.likes, self.cheese)))), 3)
        self.assertEquals(len(list(triples((Any, self.hates, self.cheese)))), 0)

        # unbound objects with context
        self.assertEquals(len(list(c1triples((self.michel, self.likes, Any)))), 2)
        self.assertEquals(len(list(c1triples((self.tarek, self.likes, Any)))), 2)
        self.assertEquals(len(list(c1triples((self.bob, self.hates, Any)))), 2)
        self.assertEquals(len(list(c1triples((self.bob, self.likes, Any)))), 1)

        # unbound objects without context, same results!
        self.assertEquals(len(list(triples((self.michel, self.likes, Any)))), 2)
        self.assertEquals(len(list(triples((self.tarek, self.likes, Any)))), 2)
        self.assertEquals(len(list(triples((self.bob, self.hates, Any)))), 2)
        self.assertEquals(len(list(triples((self.bob, self.likes, Any)))), 1)

        # unbound predicates with context
        self.assertEquals(len(list(c1triples((self.michel, Any, self.cheese)))), 1)
        self.assertEquals(len(list(c1triples((self.tarek, Any, self.cheese)))), 1)
        self.assertEquals(len(list(c1triples((self.bob, Any, self.pizza)))), 1)
        self.assertEquals(len(list(c1triples((self.bob, Any, self.michel)))), 1)

        # unbound predicates without context, same results!
        self.assertEquals(len(list(triples((self.michel, Any, self.cheese)))), 1)
        self.assertEquals(len(list(triples((self.tarek, Any, self.cheese)))), 1)
        self.assertEquals(len(list(triples((self.bob, Any, self.pizza)))), 1)
        self.assertEquals(len(list(triples((self.bob, Any, self.michel)))), 1)

        # unbound subject, objects with context
        self.assertEquals(len(list(c1triples((Any, self.hates, Any)))), 2)
        self.assertEquals(len(list(c1triples((Any, self.likes, Any)))), 5)

        # unbound subject, objects without context, same results!
        self.assertEquals(len(list(triples((Any, self.hates, Any)))), 2)
        self.assertEquals(len(list(triples((Any, self.likes, Any)))), 5)

        # unbound predicates, objects with context
        self.assertEquals(len(list(c1triples((self.michel, Any, Any)))), 2)
        self.assertEquals(len(list(c1triples((self.bob, Any, Any)))), 3)
        self.assertEquals(len(list(c1triples((self.tarek, Any, Any)))), 2)

        # unbound predicates, objects without context, same results!
        self.assertEquals(len(list(triples((self.michel, Any, Any)))), 2)
        self.assertEquals(len(list(triples((self.bob, Any, Any)))), 3)
        self.assertEquals(len(list(triples((self.tarek, Any, Any)))), 2)

        # unbound subjects, predicates with context
        self.assertEquals(len(list(c1triples((Any, Any, self.pizza)))), 3)
        self.assertEquals(len(list(c1triples((Any, Any, self.cheese)))), 3)
        self.assertEquals(len(list(c1triples((Any, Any, self.michel)))), 1)

        # unbound subjects, predicates without context, same results!
        self.assertEquals(len(list(triples((Any, Any, self.pizza)))), 3)
        self.assertEquals(len(list(triples((Any, Any, self.cheese)))), 3)
        self.assertEquals(len(list(triples((Any, Any, self.michel)))), 1)

        # all unbound with context
        self.assertEquals(len(list(c1triples((Any, Any, Any)))), 7)
        # all unbound without context, same result!
        self.assertEquals(len(list(triples((Any, Any, Any)))), 7)

        for c in [graph, self.get_context(self.c1)]:
            # unbound subjects
            self.assertEquals(set(c.subjects(self.likes, self.pizza)), {self.michel, self.tarek})
            self.assertEquals(set(c.subjects(self.hates, self.pizza)), {self.bob})
            self.assertEquals(set(c.subjects(self.likes, self.cheese)), {self.tarek, self.bob, self.michel})
            self.assertEquals(set(c.subjects(self.hates, self.cheese)), set())

            # unbound objects
            self.assertEquals(set(c.objects(self.michel, self.likes)), {self.cheese, self.pizza})
            self.assertEquals(set(c.objects(self.tarek, self.likes)), {self.cheese, self.pizza})
            self.assertEquals(set(c.objects(self.bob, self.hates)), {self.michel, self.pizza})
            self.assertEquals(set(c.objects(self.bob, self.likes)), {self.cheese})

            # unbound predicates
            self.assertEquals(set(c.predicates(self.michel, self.cheese)), {self.likes})
            self.assertEquals(set(c.predicates(self.tarek, self.cheese)), {self.likes})
            self.assertEquals(set(c.predicates(self.bob, self.pizza)), {self.hates})
            self.assertEquals(set(c.predicates(self.bob, self.michel)), {self.hates})

            self.assertEquals(set(c.subject_objects(self.hates)), {(self.bob, self.pizza), (self.bob, self.michel)})
            self.assertEquals(set(c.subject_objects(self.likes)),
                    {(self.tarek, self.cheese), (self.michel, self.cheese), (self.michel, self.pizza), (self.bob, self.cheese), (self.tarek, self.pizza)})

            self.assertEquals(set(c.predicate_objects(self.michel)), {(self.likes, self.cheese), (self.likes, self.pizza)})
            self.assertEquals(set(c.predicate_objects(self.bob)), {(self.likes, self.cheese), (self.hates, self.pizza), (self.hates, self.michel)})
            self.assertEquals(set(c.predicate_objects(self.tarek)), {(self.likes, self.cheese), (self.likes, self.pizza)})

            self.assertEquals(set(c.subject_predicates(self.pizza)), {(self.bob, self.hates), (self.tarek, self.likes), (self.michel, self.likes)})
            self.assertEquals(set(c.subject_predicates(self.cheese)), {(self.bob, self.likes), (self.tarek, self.likes), (self.michel, self.likes)})
            self.assertEquals(set(c.subject_predicates(self.michel)), {(self.bob, self.hates)})

            self.assertEquals(set(c), {(self.bob, self.hates, self.michel), (self.bob, self.likes, self.cheese), (self.tarek, self.likes, self.pizza),
                (self.michel, self.likes, self.pizza), (self.michel, self.likes, self.cheese), (self.bob, self.hates, self.pizza),
                (self.tarek, self.likes, self.cheese)})

        # remove stuff and make sure the graph is empty again
        self.removeStuff()
        self.assertEquals(len(list(c1triples((Any, Any, Any)))), 0)
        self.assertEquals(len(list(triples((Any, Any, Any)))), 0)
