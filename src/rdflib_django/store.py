"""
Essential implementation of the Store interface defined by RDF lib.
"""
import itertools
import logging
import rdflib
from rdflib.store import VALID_STORE, NO_STORE
from rdflib.term import Literal, Identifier
from rdflib_django import models


DEFAULT_STORE = "rdflib_django.store.DEFAULT_STORE"      # self-referentiality is so nice


log = logging.getLogger(__name__)


def _get_query_sets_for_object(o):
    """
    Determines the correct query set based on the object.

    If the object is a literal, it will return a query set over LiteralStatements.
    If the object is a URIRef or BNode, it will return a query set over Statements.
    If the object is unknown, it will return both the LiteralStatement and Statement query sets.

    This method always returns a list of size at least one.
    """
    if o:
        if isinstance(o, Literal):
            query_sets = [models.LiteralStatement.objects]
        else:
            query_sets = [models.Statement.objects]
    else:
        query_sets = [models.Statement.objects, models.LiteralStatement.objects]
    return query_sets


class DjangoStore(rdflib.store.Store):
    """
    RDFlib Store implementation the uses Django Models for storage and retrieval.

    >>> g = rdflib.Graph('Django')

    The implementation is context aware, and uses Django transactions.

    >>> g.store.context_aware
    True
    >>> g.store.transaction_aware
    False

    The implementation does not support formula's.

    >>> g.store.formula_aware
    False

    The implementation provides a default store with the identifier DEFAULT_STORE. This store
    is always present and needs not be opened.

    >>> g.store.identifier
    'rdflib_django.store.DEFAULT_STORE'

    """

    context_aware = True
    formula_aware = False
    transaction_aware = False

    def __init__(self, configuration=None, identifier=DEFAULT_STORE):
        super(DjangoStore, self).__init__(configuration, identifier)
        self.identifier = identifier
        self.store = None
        if identifier == DEFAULT_STORE:
            self.open(configuration, create=True)

    def open(self, configuration=None, create=False):
        """
        Opens the underlying store. This is only necessary when opening
        a store with another identifier than the default identifier.

        >>> g = rdflib.Graph('Django')
        >>> g.open(configuration=None, create=False) == rdflib.store.VALID_STORE
        True
        >>> store = DjangoStore(identifier='hello-world')
        >>> g = rdflib.Graph(store=store)
        >>> g.open(configuration=None, create=False) == rdflib.store.NO_STORE
        True
        >>> g.open(configuration=None, create=True) == rdflib.store.VALID_STORE
        True
        """
        if self.identifier == DEFAULT_STORE or create:
            self.store = models.Store.objects.get_or_create(identifier=self.identifier)[0]
        else:
            try:
                self.store = models.Store.objects.get(identifier=self.identifier)
            except models.Store.DoesNotExist:
                return NO_STORE

        return VALID_STORE

    def destroy(self, configuration=None):
        """
        Completely destroys a store and all the contexts and triples in the store.

        >>> store = DjangoStore(identifier='destroy-me')
        >>> g = rdflib.Graph(store=store)
        >>> g.open(configuration=None, create=True) == rdflib.store.VALID_STORE
        True
        >>> g.open(configuration=None, create=False) == rdflib.store.VALID_STORE
        True
        >>> g.destroy(configuration=None)
        >>> g.open(configuration=None, create=False) == rdflib.store.NO_STORE
        True
        """
        if self.store:
            self.store.delete()

    def add(self, (s, p, o), context, quoted=False):
        """
        Adds a triple to the store.

        >>> from rdflib.term import URIRef
        >>> from rdflib.namespace import RDF

        >>> subject = URIRef('http://zoowizard.org/resource/Artis')
        >>> object = URIRef('http://schema.org/Zoo')
        >>> g = rdflib.Graph('Django')
        >>> g.add((subject, RDF.type, object))
        >>> len(g)
        1

        """
        assert isinstance(s, Identifier)
        assert isinstance(p, Identifier)
        assert isinstance(o, Identifier)

        query_set = _get_query_sets_for_object(o)[0]

        query_set.get_or_create(
            subject=s,
            predicate=p,
            object=o,
            store=self.store
        )

    def remove(self, (s, p, o), context=None):
        """
        Removes a triple from the store.
        """
        query_sets = _get_query_sets_for_object(o)

        for qs in query_sets:
            try:
                qs.get(
                    subject=s,
                    predicate=p,
                    object=o,
                    store=self.store
                ).delete()
            except models.Statement.DoesNotExist:
                pass

    def triples(self, (s, p, o), context=None):
        """
        Returns all triples in the current store.
        """
        query_sets = _get_query_sets_for_object(o)

        if s:
            query_sets = [qs.filter(subject=s) for qs in query_sets]
        if p:
            query_sets = [qs.filter(predicate=p) for qs in query_sets]
        if o:
            query_sets = [qs.filter(object=o) for qs in query_sets]

        for statement in itertools.chain(*[qs.all() for qs in query_sets]):
            yield statement.as_triple()

    def __len__(self, context=None):
        """
        Returns the number of statements in this Graph.
        """
        statement_qs = models.Statement.objects
        literal_qs = models.LiteralStatement.objects

        return statement_qs.count() + literal_qs.count()
