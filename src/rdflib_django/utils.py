"""
Utility functions for using rdflib_django.
"""
from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.store import VALID_STORE
from rdflib.term import URIRef
from rdflib_django.store import DjangoStore, DEFAULT_STORE


def get_conjunctive_graph(store_id=None):
    """
    Returns an open conjunctive graph.
    """
    if not store_id:
        store_id = DEFAULT_STORE

    store = DjangoStore(DEFAULT_STORE)
    graph = ConjunctiveGraph(store=store, identifier=store_id)
    if graph.open(None) != VALID_STORE:
        raise ValueError("The store identified by {0} is not a valid store".format(store_id))
    return graph


def get_named_graph(identifier, store_id=DEFAULT_STORE, create=True):
    """
    Returns an open named graph.
    """
    if not isinstance(identifier, URIRef):
        identifier = URIRef(identifier)

    store = DjangoStore(store_id)
    graph = Graph(store, identifier=identifier)
    if graph.open(None, create=create) != VALID_STORE:
        raise ValueError("The store identified by {0} is not a valid store".format(store_id))
    return graph
