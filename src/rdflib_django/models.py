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


class AbstractStatement(models.Model):
    """
    Base class for statements.
    """

    id = UUIDField("ID", primary_key=True)
    store = models.ForeignKey(Store)

    subject = fields.URIField("Subject")
    predicate = fields.URIField("Predicate")
    context = fields.URIField("Context", null=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        """Returns the triple and its context"""
        return u"{0}".format(self.as_triple())

    def as_triple(self):
        """
        Converts this statement back to a triple.

        :return - tuple ((subject, predicate, object), context)
        """
        return (self.subject, self.predicate, getattr(self, 'object')), self.context


class Statement(AbstractStatement):
    """
    A generic statement.
    """

    object = fields.URIField("Object", null=True)

    class Meta:
        unique_together = ('store', 'subject', 'predicate', 'object', 'context')


class LiteralStatement(AbstractStatement):
    """
    A statement where the object is a literal.
    """

    object = fields.LiteralField("Object", null=True)

    class Meta:
        unique_together = ('store', 'subject', 'predicate', 'object', 'context')
