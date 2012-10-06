"""
Essential implementation of the Store interface defined by RDF lib.
"""
import itertools
import logging
from django.db.utils import IntegrityError
import rdflib
from rdflib.store import VALID_STORE
from rdflib.term import Literal, Identifier, BNode
from rdflib_django import models
from rdflib_django.models import Namespace


DEFAULT_STORE = "Default Store"
GLOBAL_CONTEXT = BNode("Global Context")


DEFAULT_NAMESPACES = (
    ("xml", u"http://www.w3.org/XML/1998/namespace"),
    ("rdf", u"http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("rdfs", u"http://www.w3.org/2000/01/rdf-schema#")
)


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

    The implementation provides a single store with the identifier DEFAULT_STORE. This store
    is always present and needs not be opened.

    >>> g.store.identifier
    'Default Store'

    Using other stores is not allowed

    >>> g = DjangoStore(identifier='HelloWorld')
    Traceback (most recent call last):
        ...
    ValueError: multiple stores are not allowed


    """

    context_aware = True
    formula_aware = False
    transaction_aware = False

    def __init__(self, configuration=None, identifier=DEFAULT_STORE):
        if identifier and identifier != DEFAULT_STORE:
            raise ValueError("multiple stores are not allowed")

        self.identifier = DEFAULT_STORE
        self.default_context = models.ContextRef.objects.get(identifier=GLOBAL_CONTEXT)
        self.context_cache = dict()
        super(DjangoStore, self).__init__(configuration, identifier)
        self.open()

    def open(self, configuration=None, create=False):
        """
        Opens the underlying store. This is only necessary when opening
        a store with another identifier than the default identifier.

        >>> g = rdflib.Graph('Django')
        >>> g.open(configuration=None, create=False) == rdflib.store.VALID_STORE
        True
        """
        return VALID_STORE

    def destroy(self, configuration=None):
        """
        Completely destroys a store and all the contexts and triples in the store.

        >>> store = DjangoStore()
        >>> g = rdflib.Graph(store=store)
        >>> g.open(configuration=None, create=True) == rdflib.store.VALID_STORE
        True
        >>> g.open(configuration=None, create=False) == rdflib.store.VALID_STORE
        True
        >>> g.destroy(configuration=None)
        >>> g.open(configuration=None, create=False) == rdflib.store.VALID_STORE
        True
        """
        models.Statement.objects.all().delete()
        models.LiteralStatement.objects.all().delete()
        models.ContextRef.objects.exclude(identifier=GLOBAL_CONTEXT).delete()

    def _get_context_ref(self, context):
        """
        Returns a ContextRef for the specified context. Raises DoesNotExist if it does not exist.
        """
        if context is None:
            return self.default_context
        elif context in self.context_cache:
            return self.context_cache.get(context)
        else:
            identifier = context.identifier if hasattr(context, 'identifier') else unicode(context)
            result = models.ContextRef.objects.get(identifier=identifier)
            self.context_cache[context] = result
            return result

    def _get_or_create_context_ref(self, context):
        """
        Returns a ContextRef for the specified context. Creates a new one if it does not yet exist.
        """
        if context is None:
            return self.default_context
        elif context in self.context_cache:
            return self.context_cache.get(context)
        else:
            identifier = context.identifier if hasattr(context, 'identifier') else unicode(context)
            result = models.ContextRef.objects.get_or_create(identifier=identifier)[0]
            self.context_cache[context] = result
            return result

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
        )[0]
        context_ref = self._get_or_create_context_ref(context)
        if context_ref and context_ref not in statement.context_refs.all():
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

    def bind(self, prefix, namespace):
        for ns in DEFAULT_NAMESPACES:
            if ns[0] == prefix or unicode(ns[1]) == unicode(namespace):
                return

        try:
            ns = Namespace(prefix=prefix, uri=namespace)
            ns.save()
        except IntegrityError:
            Namespace.objects.filter(prefix=prefix).delete()
            Namespace.objects.filter(uri=namespace).delete()
            Namespace(prefix=prefix, uri=namespace).save()

    def prefix(self, namespace):
        try:
            ns = Namespace.objects.get(uri=namespace)
            return ns.prefix
        except Namespace.DoesNotExist:
            return None

    def namespace(self, prefix):
        try:
            ns = Namespace.objects.get(prefix=prefix)
            return ns.uri
        except Namespace.DoesNotExist:
            return None

    def namespaces(self):
        for ns in Namespace.objects.all():
            yield ns.prefix, ns.uri
