"""
Defines admin options for this RDFlib implementation.
"""
from django.contrib import admin
from rdflib_django import models


class StoreAdmin(admin.ModelAdmin):
    """
    Admin module for Stores.
    """

    list_display = ('identifier', 'triple_count')


class ContextRefAdmin(admin.ModelAdmin):
    """
    Admin module for Contexts.
    """

    list_display = ('identifier', 'store', 'triple_count')
    list_filter = ('store', )


class StatementAdmin(admin.ModelAdmin):
    """
    Admin module for Statements.
    """

    list_display = ('subject', 'object', 'predicate', 'store')
    list_filter = ('store', 'context_refs')


class LiteralStatementAdmin(admin.ModelAdmin):
    """
    Admin module for Literal statements.
    """

    list_display = ('subject', 'object', 'predicate', 'store')
    list_filter = ('store', 'context_refs')


admin.site.register(models.Store, StoreAdmin)
admin.site.register(models.ContextRef, ContextRefAdmin)
admin.site.register(models.Statement, StatementAdmin)
admin.site.register(models.LiteralStatement, LiteralStatementAdmin)
