"""
Defines admin options for this RDFlib implementation.
"""
from django.contrib import admin
from rdflib_django import models

admin.site.register(models.Store)
admin.site.register(models.ContextRef)
admin.site.register(models.Statement)
admin.site.register(models.LiteralStatement)
