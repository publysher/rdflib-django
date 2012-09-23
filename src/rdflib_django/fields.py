"""
Custom fields for storing RDF primitives.

Based on http://blog.elsdoerfer.name/2008/01/08/fuzzydates-or-one-django-model-field-multiple-database-columns/
"""
from django.db import models
from rdflib.graph import Graph
from rdflib.term import BNode, URIRef, Literal

TYPE_BNODE = 1
TYPE_URIREF = 0
TYPE_GRAPH = 2


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
        uri_type = getattr(obj, self.type_name)

        if uri_type == TYPE_BNODE:
            if identifier:
                return BNode(identifier)
            else:
                return BNode()

        if uri_type == TYPE_URIREF:
            return URIRef(identifier)

        if uri_type == TYPE_GRAPH:
            return Graph('Django', identifier=URIRef(identifier))

        raise ValueError("Unknown type {0} for identifier {1}".format(uri_type, identifier))

    def __set__(self, obj, value):
        if isinstance(value, URIRef):
            setattr(obj, self.type_name, TYPE_URIREF)
            obj.__dict__[self.field.name] = value
        elif isinstance(value, BNode):
            setattr(obj, self.type_name, TYPE_BNODE)
            obj.__dict__[self.field.name] = value
        elif isinstance(value, Graph):
            setattr(obj, self.type_name, TYPE_GRAPH)
            obj.__dict__[self.field.name] = value.identifier
        elif value is None:
            setattr(obj, self.type_name, None)
            obj.__dict__[self.field.name] = None
        elif isinstance(value, basestring):
            obj.__dict__[self.field.name] = value
        else:
            raise TypeError("Cannot set URI to value {0} of type {1}".format(value, value.__class__))


class URIField(models.CharField):
    """
    Field for storing either URIRefs or BNodes.
    """

    description = "Stores URIs, blank nodes and graph references."

    def __init__(self, *args, **kwargs):
        if not 'max_length' in kwargs:
            kwargs['max_length'] = 1024
        super(URIField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        type_field = models.SmallIntegerField(
            choices=((TYPE_URIREF, "URI"), (TYPE_BNODE, "Blank Node"), (TYPE_GRAPH, "Graph")),
            null=False,
        )
        type_field.creation_counter = self.creation_counter

        if _type_name(name) not in cls._meta.get_all_field_names():  # pylint: disable=W0212
            cls.add_to_class(_type_name(name), type_field)

        super(URIField, self).contribute_to_class(cls, name)

        setattr(cls, self.name, URIFieldCreator(self))

    def get_db_prep_save(self, value, connection):
        if isinstance(value, Graph):
            return value.identifier

        return super(URIField, self).get_db_prep_save(value, connection)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'isnull':
            return None

        if lookup_type == 'exact':
            if isinstance(value, Graph):
                return value.identifier

            if isinstance(value, URIRef):
                return value

            if isinstance(value, BNode):
                return value

            if isinstance(value, basestring):
                return unicode(value)

        raise ValueError(self, lookup_type, value)
#        return super(URIField, self).get_prep_lookup(lookup_type, value)


class LiteralField(models.TextField):
    """
    Custom field for storing literals.
    """

    __metaclass__ = models.SubfieldBase
    description = "Field for storing Literals, including their type and language"

    def to_python(self, value):
        if isinstance(value, Literal):
            return value

        parts = value.split('^^')
        if len(parts) != 3:
            raise ValueError("Wrong value: {0}".format(value))
        return Literal(parts[0], parts[1] or None, parts[2] or None)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def get_prep_value(self, value):
        if not isinstance(value, Literal):
            raise TypeError("Value {0} has the wrong type: {1}".format(value, value.__class__))

        return unicode(value) + "^^" + (value.language or '') + "^^" + (value.datatype or '')
