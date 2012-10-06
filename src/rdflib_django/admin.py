"""
Defines admin options for this RDFlib implementation.
"""
from django.contrib import admin
from rdflib_django import models, forms


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


class NamespaceAdmin(admin.ModelAdmin):
    """
    Admin module for managing namespaces.
    """
    list_display = ('prefix', 'uri', 'fixed')
    ordering = ('-fixed', 'prefix')
    search_fields = ('prefix', 'uri')
    form = forms.NamespaceForm

#    def get_readonly_fields(self, request, obj=None):
#        if obj and obj.fixed:
#            return 'prefix', 'uri', 'fixed'
#        else:
#            return 'fixed',

    def has_delete_permission(self, request, obj=None):
        """
        Default namespaces cannot be deleted.
        """
        if obj is not None and obj.fixed:
            return False
        return super(NamespaceAdmin, self).has_delete_permission(request, obj)

admin.site.register(models.ContextRef, ContextRefAdmin)
admin.site.register(models.Statement, StatementAdmin)
admin.site.register(models.LiteralStatement, LiteralStatementAdmin)
admin.site.register(models.Namespace, NamespaceAdmin)
