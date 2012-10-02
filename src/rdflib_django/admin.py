"""
Defines admin options for this RDFlib implementation.
"""
from django.contrib import admin
from rdflib_django import models


class ContextRefAdmin(admin.ModelAdmin):
    """
    Admin module for Contexts.
    """

    list_display = ('identifier', 'triple_count')


class StatementAdmin(admin.ModelAdmin):
    """
    Admin module for Statements.
    """

    list_display = ('subject', 'predicate', 'object')
    list_filter = ('context_refs', 'predicate')


class LiteralStatementAdmin(admin.ModelAdmin):
    """
    Admin module for Literal statements.
    """

    list_display = ('subject', 'predicate', 'object')
    list_filter = ('context_refs', 'predicate')


admin.site.register(models.ContextRef, ContextRefAdmin)
admin.site.register(models.Statement, StatementAdmin)
admin.site.register(models.LiteralStatement, LiteralStatementAdmin)
