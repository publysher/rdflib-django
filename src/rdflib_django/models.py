"""
The rdflib_django implementation uses Django models to store its triples. It provides the following models:

Store - A specific store. Every triples is contained in exactly one store.
Statement - A generic triple
LiteralStatement - A triple where the object is a literal.
Context - A context. Every triple is contained in zero or more contexts.

"""
from django.db import models
from django_extensions.db.fields import UUIDField
from rdflib_django import fields


class Store(models.Model):
    """
    Models a single store.
    """

    id = UUIDField(verbose_name="ID", primary_key=True)
    identifier = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return u"{0}".format(self.identifier)

    def triple_count(self):
        """
        The number of triples in this store.
        """
        return Statement.objects.filter(store=self).count() + LiteralStatement.objects.filter(store=self).count()


class ContextRef(models.Model):
    """
    Models a reference to a single context within a store.
    """

    id = UUIDField(verbose_name="ID", primary_key=True)
    identifier = fields.URIField(max_length=200)
    store = models.ForeignKey(Store)

    class Meta:
        verbose_name = "Context"
        verbose_name_plural = "Contexts"
        unique_together = ('store', 'identifier')

    def __unicode__(self):
        return u"{0} in {1}".format(self.identifier, self.store)

    def triple_count(self):
        """
        The number of triples in this context.
        """
        return Statement.objects.filter(store=self.store, context_refs=self).count() + \
               LiteralStatement.objects.filter(store=self.store, context_refs=self).count()


class AbstractStatement(models.Model):
    """
    Base class for statements.
    """

    id = UUIDField("ID", primary_key=True)
    store = models.ForeignKey(Store)

    subject = fields.URIField("Subject", db_index=True)
    predicate = fields.URIField("Predicate", db_index=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        """Returns the triple and its context"""
        return u"({0}, {1}, {2})".format(self.subject, self.predicate, getattr(self, 'object'))

    def as_triple(self):
        """
        Converts this statement back to a triple.
        """
        return self.subject, self.predicate, getattr(self, 'object')


class Statement(AbstractStatement):
    """
    A generic statement.
    """

    object = fields.URIField("Object", null=True, db_index=True)
    context_refs = models.ManyToManyField(ContextRef, verbose_name="Context(s)")

    class Meta:
        unique_together = ('store', 'subject', 'predicate', 'object')


class LiteralStatement(AbstractStatement):
    """
    A statement where the object is a literal.
    """

    object = fields.LiteralField("Object", null=True, db_index=True)
    context_refs = models.ManyToManyField(ContextRef, verbose_name="Context(s)")

    class Meta:
        unique_together = ('store', 'subject', 'predicate', 'object')
