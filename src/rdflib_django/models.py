"""
The rdflib_django implementation uses Django models to store its triples. It provides the following models:

Statement - A generic triple
LiteralStatement - A triple where the object is a literal.
ContextRef - A context. Every triple is contained in zero or more contexts.
Namespace - A namespace binding

"""
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import UUIDField
from rdflib_django import fields


class ContextRef(models.Model):
    """
    Models a reference to a single context within a store.
    """

    identifier = fields.GraphReferenceField(max_length=200, unique=True, primary_key=True)

    class Meta:
        verbose_name = "Context"
        verbose_name_plural = "Contexts"

    def __unicode__(self):
        return u"{0}".format(self.identifier)

    def triple_count(self):
        """
        The number of triples in this context.
        """
        return self.statement_set.count() + self.literalstatement_set.count()   # pylint: disable=E1101


class Resource(models.Model):
    """
    The subject part of a triple.
    """

    id = UUIDField(verbose_name="ID", primary_key=True)
    identifier = fields.URIField(max_length=500)
    context = models.ForeignKey(ContextRef, verbose_name="Context", null=True)

    class Meta:
        unique_together = ('identifier', 'context')

    def __unicode__(self):
        return u"{0}".format(self.identifier)


class URIPredicate(models.Model):
    """
    Base class for resource predicates with a URI value.
    """

    id = UUIDField("ID", primary_key=True)
    subject = models.ForeignKey(Resource, verbose_name="Subject", db_index=True)
    predicate = fields.URIField("Predicate", db_index=True)
    object = fields.URIField("Object", db_index=True)

    class Meta:
        unique_together = ('subject', 'predicate', 'object')

    def __unicode__(self):
        return u"{0}, {1}".format(self.as_triple(), self.subject.context_id)    # pylint: disable=E1101

    def as_triple(self):
        """
        Converts this predicate to a triple.
        """
        return self.subject.identifier, self.predicate, self.object


class LiteralPredicate(models.Model):
    """
    Base class for resource predicates with a literal value.
    """

    id = UUIDField("ID", primary_key=True)
    subject = models.ForeignKey(Resource, verbose_name="Subject", db_index=True)
    predicate = fields.URIField("Predicate", db_index=True)
    object = fields.LiteralField("Object", db_index=True)

    class Meta:
        unique_together = ('subject', 'predicate', 'object')

    def __unicode__(self):
        return u"{0}, {1}".format(self.as_triple(), self.subject.context_id)    # pylint: disable=E1101

    def as_triple(self):
        """
        Converts this predicate to a triple.
        """
        return self.subject.identifier, self.predicate, self.object


class NamespaceModel(models.Model):
    """
    A namespace definition.

    In essence, a namespace consists of a prefix and a URI. However, the namespaces in rdflib_django
    also have an extra field called '`fixed`' - this is used to mark namespaces that cannot be
    remapped such as ``xml``, ``rdf`` and ``rdfs``.
    """

    prefix = models.CharField(max_length=50, verbose_name="Prefix", primary_key=True)
    uri = models.CharField(max_length=500, verbose_name="URI", db_index=True, unique=True)
    fixed = models.BooleanField(verbose_name="Fixed", editable=False, default=False)

    class Meta:
        verbose_name = _("namespace")
        verbose_name_plural = _("namespaces")

    def __unicode__(self):
        return "@prefix {0}: <{1}>".format(self.prefix, self.uri)
