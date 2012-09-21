"""
Custom fields for storing RDF primitives.

Based on http://blog.elsdoerfer.name/2008/01/08/fuzzydates-or-one-django-model-field-multiple-database-columns/
"""
from django.db import models
from rdflib.term import BNode, URIRef

TYPE_BNODE = 1
TYPE_URIREF = 0


def _type_name(name):
    """Column name for the type field"""
    return "{0}_type".format(name)


class URIFieldCreator(object):
    """
    Special descriptor that keeps the type field in sync with the values passed
    to the URIField.
    """

    def __init__(self, field):
        self.field = field
        self.type_name = _type_name(field.name)

    def __get__(self, obj, type=None):  # pylint: disable=W0622
        assert obj is not None

        identifier = obj.__dict__[self.field.name]
        if not identifier:
            return None

        uri_type = getattr(obj, self.type_name)
        if uri_type == TYPE_BNODE:
            return BNode(identifier)

        if uri_type == TYPE_URIREF:
            return URIRef(identifier)

        raise ValueError("Unknown type: {0}".format(uri_type))

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = value
        if isinstance(value, URIRef):
            setattr(obj, self.type_name, TYPE_URIREF)
        elif isinstance(value, BNode):
            setattr(obj, self.type_name, TYPE_BNODE)


class URIField(models.TextField):
    """
    Field for storing either URIRefs or BNodes.
    """

    def contribute_to_class(self, cls, name):
        type_field = models.IntegerField(
            choices=((TYPE_URIREF, "URI"), (TYPE_BNODE, "Blank Node")),
            editable=False,
            null=True,
            blank=True
        )
        type_field.creation_counter = self.creation_counter

        if _type_name(name) not in cls._meta.get_all_field_names():  # pylint: disable=W0212
            cls.add_to_class(_type_name(name), type_field)

        super(URIField, self).contribute_to_class(cls, name)

        setattr(cls, self.name, URIFieldCreator(self))
