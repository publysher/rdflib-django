"""
Essential implementation of the Store interface defined by RDF lib.
"""
from django.db.utils import IntegrityError
import rdflib
from rdflib.store import VALID_STORE
from rdflib.term import Literal, Identifier
from rdflib_django import models
from rdflib_django.models import NamespaceModel


DEFAULT_STORE = "Default Store"

DEFAULT_NAMESPACES = (
    ("xml", u"http://www.w3.org/XML/1998/namespace"),
    ("rdf", u"http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("rdfs", u"http://www.w3.org/2000/01/rdf-schema#")
    )


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
            query_sets = [models.URIStatement.objects]
    else:
        query_sets = [models.URIStatement.objects, models.LiteralStatement.objects]
    return query_sets


def _get_named_graph(context):
    """
    Returns the named graph for this context.
    """
    if context is None:
        return None

    return models.NamedGraph.objects.get_or_create(identifier=context.identifier)[0]


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
        models.NamedGraph.objects.all().delete()
        models.URIStatement.objects.all().delete()
        models.LiteralStatement.objects.all().delete()

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

        named_graph = _get_named_graph(context)

        query_set = _get_query_sets_for_object(o)[0]
        query_set.get_or_create(
            subject=s,
            predicate=p,
            object=o,
            context=named_graph,
            )

    def remove(self, (s, p, o), context=None):
        """
        Removes a triple from the store.
        """
        named_graph = _get_named_graph(context)
        query_sets = _get_query_sets_for_object(o)

        filter_parameters = dict()
        if named_graph is not None:
            filter_parameters['context_id'] = named_graph.id
        if s:
            filter_parameters['subject'] = s
        if p:
            filter_parameters['predicate'] = p
        if o:
            filter_parameters['object'] = o

        query_sets = [qs.filter(**filter_parameters) for qs in query_sets]  # pylint: disable=W0142

        for qs in query_sets:
            qs.delete()

    def triples(self, (s, p, o), context=None):
        """
        Returns all triples in the current store.
        """
        named_graph = _get_named_graph(context)
        query_sets = _get_query_sets_for_object(o)

        filter_parameters = dict()
        if named_graph is not None:
            filter_parameters['context_id'] = named_graph.id
        if s:
            filter_parameters['subject'] = s
        if p:
            filter_parameters['predicate'] = p
        if o:
            filter_parameters['object'] = o

        query_sets = [qs.filter(**filter_parameters) for qs in query_sets]  # pylint: disable=W0142

        for qs in query_sets:
            for statement in qs:
                triple = statement.as_triple()
                yield triple, context

    def __len__(self, context=None):
        """
        Returns the number of statements in this Graph.
        """
        named_graph = _get_named_graph(context)
        if named_graph is not None:
            return (models.LiteralStatement.objects.filter(context_id=named_graph.id).count()
                    + models.URIStatement.objects.filter(context_id=named_graph.id).count())
        else:
            return (models.URIStatement.objects.values('subject', 'predicate', 'object').distinct().count()
                    + models.LiteralStatement.objects.values('subject', 'predicate', 'object').distinct().count())

    ####################
    # CONTEXT MANAGEMENT

    def contexts(self, triple=None):
        for c in models.NamedGraph.objects.all():
            yield c.identifier

    ######################
    # NAMESPACE MANAGEMENT

    def bind(self, prefix, namespace):
        for ns in DEFAULT_NAMESPACES:
            if ns[0] == prefix or unicode(ns[1]) == unicode(namespace):
                return

        try:
            ns = NamespaceModel(prefix=prefix, uri=namespace)
            ns.save()
        except IntegrityError:
            NamespaceModel.objects.filter(prefix=prefix).delete()
            NamespaceModel.objects.filter(uri=namespace).delete()
            NamespaceModel(prefix=prefix, uri=namespace).save()

    def prefix(self, namespace):
        try:
            ns = NamespaceModel.objects.get(uri=namespace)
            return ns.prefix
        except NamespaceModel.DoesNotExist:
            return None

    def namespace(self, prefix):
        try:
            ns = NamespaceModel.objects.get(prefix=prefix)
            return ns.uri
        except NamespaceModel.DoesNotExist:
            return None

    def namespaces(self):
        for ns in NamespaceModel.objects.all():
            yield ns.prefix, ns.uri
