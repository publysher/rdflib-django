"""
The rdflib_django implementation uses Django models to store its triples. It provides the following models:

Store - A specific store. Every triples is contained in exactly one store.
Statement - A generic triple
LiteralStatement - A triple where the object is a literal.
Context - A context. Every triple is contained in zero or more contexts.

"""
from django.db import models
from django_extensions.db.fields import UUIDField
from rdfextras.store.REGEXMatching import REGEXTerm
from rdfextras.utils import termutils
from rdflib.graph import Graph, QuotedGraph
from rdflib.term import Literal


class Store(models.Model):
    """
    Models a single store.
    """

    id = UUIDField(verbose_name="ID", primary_key=True)
    identifier = models.CharField(max_length=200, unique=True)

    class Meta:
        pass


def normalizeTerm(term):
    """
    Normalizes a term for suitable database representation.
    """
    if isinstance(term, (QuotedGraph, Graph)):
        return term.identifier.encode('utf-8')
    elif isinstance(term, Literal):
        return termutils.escape_quotes(term).encode('utf-8')
    elif term is None or isinstance(term, (tuple, list, REGEXTerm)):
        return term
    else:
        return term.encode('utf-8')


class Statement(models.Model):
    """
    A generic statement.
    """

    id = UUIDField("ID", primary_key=True)
    store = models.ForeignKey(Store)

    subject = models.TextField("Subject")
    predicate = models.TextField("Predicate")
    object = models.TextField("Object", null=True)
    context = models.TextField("Context")


class LiteralStatement(Statement):
    """
    A statement where the object is a literal.
    """

    object_language = models.CharField("Language", max_length=3, null=True)
    object_datatype = models.TextField("Data type", null=True)
