"""
RDFlib Store implementation for Django, providing lots of extra goodies.

Use this application by just including it in your INSTALLED_APPS. After this,
you can create a new Graph using:

>>> import rdflib
>>> g = rdflib.Graph('Django')

"""
from rdflib.plugin import register
from rdflib.store import Store

register('Django', Store, 'rdflib_django.store', 'DjangoStore')
