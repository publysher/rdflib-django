"""
Essential implementation of the Store interface defined by RDF lib.
"""
import itertools
import logging
import rdflib
from rdflib.store import VALID_STORE, NO_STORE
from rdflib.term import Literal, Identifier, URIRef
from rdflib_django import models


DEFAULT_STORE = "rdflib_django.store.DEFAULT_STORE"      # self-referentiality is so nice
DEFAULT_CONTEXT = URIRef("rdflib_django.store.DEFAULT_CONTEXT")


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
        self.default_context = None
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

        self.default_context = models.ContextRef.objects.get_or_create(identifier=DEFAULT_CONTEXT, store=self.store)[0]
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

    def _get_context_ref(self, context):
        """
        Returns a ContextRef for the specified context. Raises DoesNotExist if it does not exist.
        """
        if context is None:
            return self.default_context
        else:
            identifier = context.identifier if hasattr(context, 'identifier') else unicode(context)
            return models.ContextRef.objects.get(identifier=identifier, store=self.store)

    def _get_or_create_context_ref(self, context):
        """
        Returns a ContextRef for the specified context. Creates a new one if it does not yet exist.
        """
        if context is None:
            return self.default_context
        else:
            identifier = context.identifier if hasattr(context, 'identifier') else unicode(context)
            return models.ContextRef.objects.get_or_create(identifier=identifier, store=self.store)[0]

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
        assert not quoted

        query_set = _get_query_sets_for_object(o)[0]
        statement = query_set.get_or_create(
            subject=s,
            predicate=p,
            object=o,
            store=self.store
        )[0]
        context_ref = self._get_or_create_context_ref(context)
        if context_ref:
            statement.context_refs.add(context_ref)

    def remove(self, (s, p, o), context=None):
        """
        Removes a triple from the store.
        """
        try:
            context_ref = self._get_context_ref(context)
        except models.ContextRef.DoesNotExist:
            return

        query_sets = _get_query_sets_for_object(o)
        query_sets = self._filter_query_sets(query_sets, (s, p, o), context_ref)

        for qs in query_sets:
            for stmt in qs.all():
                stmt.context_refs.remove(context_ref)
                if context_ref is self.default_context or not stmt.context_refs.count():
                    stmt.delete()

    def _filter_query_sets(self, query_sets, (s, p, o), context_ref):
        """
        Creates filtered versions of the specified query sets.
        """
        if s is not None:
            query_sets = [qs.filter(subject=s) for qs in query_sets]
        if p is not None:
            query_sets = [qs.filter(predicate=p) for qs in query_sets]
        if o is not None:
            query_sets = [qs.filter(object=o) for qs in query_sets]
        if context_ref is not self.default_context:
            query_sets = [qs.filter(context_refs=context_ref) for qs in query_sets]
        return query_sets

    def triples(self, (s, p, o), context=None):
        """
        Returns all triples in the current store.
        """
        context_ref = self._get_context_ref(context)
        query_sets = _get_query_sets_for_object(o)

        query_sets = self._filter_query_sets(query_sets, (s, p, o), context_ref)

        matching_statements = itertools.chain(*[qs.all() for qs in query_sets])
        for statement in matching_statements:
            yield statement.as_triple(), context

    def __len__(self, context=None):
        """
        Returns the number of statements in this Graph.
        """
        context_ref = self._get_context_ref(context)

        query_sets = _get_query_sets_for_object(None)
        if context_ref is not self.default_context:
            query_sets = [qs.filter(context_refs=context_ref) for qs in query_sets]

        counts = [qs.count() for qs in query_sets]
        return reduce(lambda x, y: x + y, counts, 0)

    def contexts(self, triple=None):
        for c in models.ContextRef.objects.all():
            yield c.identifier
