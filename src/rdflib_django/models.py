"""
The rdflib_django implementation uses Django models to store its triples.

The underlying models are Resource centric, because rdflib-django is intended
to be used for publishing resources.
"""
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import UUIDField
from rdflib_django import fields


class NamedGraph(models.Model):
    """
    Models a context which represents a named graph.
    """

    id = UUIDField(verbose_name=_("ID"), primary_key=True)
    identifier = fields.URIField(verbose_name=_("Identifier"), unique=True)

    class Meta:
        verbose_name = _("named graph")
        verbose_name_plural = _("named graphs")

    def __unicode__(self):
        return u"{0}".format(self.identifier, "identifier")


class Resource(models.Model):
    """
    The subject part of a triple.
    """

    id = UUIDField(verbose_name="ID", primary_key=True)
    identifier = fields.URIField(max_length=500)
    context = models.ForeignKey(NamedGraph, verbose_name="Context", null=True)

    class Meta:
        unique_together = ('identifier', 'context')

    def __unicode__(self):
        return u"{0}".format(self.identifier)


class URIPredicate(models.Model):
    """
    Base class for resource predicates with a URI value.
    """

    id = UUIDField("ID", primary_key=True)
    subject = models.ForeignKey(Resource, verbose_name=_("Subject"), db_index=True)
    predicate = fields.URIField(_("Predicate"), db_index=True)
    object = fields.URIField(_("Object"), db_index=True)

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
    subject = models.ForeignKey(Resource, verbose_name=_("Subject"), db_index=True)
    predicate = fields.URIField(_("Predicate"), db_index=True)
    object = fields.LiteralField(_("Object"), db_index=True)

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

    id = UUIDField(_("ID"), primary_key=True)
    prefix = models.CharField(max_length=50, verbose_name=_("Prefix"), unique=True)
    uri = models.CharField(max_length=500, verbose_name=_("URI"), db_index=True, unique=True)
    fixed = models.BooleanField(verbose_name=_("Fixed"), editable=False, default=False)

    class Meta:
        verbose_name = _("namespace")
        verbose_name_plural = _("namespaces")

    def __unicode__(self):
        return "@prefix {0}: <{1}>".format(self.prefix, self.uri)
