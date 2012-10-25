"""
Base forms for editing the models in this module. You can use or extend these forms in your
project to ensure that all validation is correct.
"""
from django import forms
from rdflib_django import models
from rdflib import namespace


class NamespaceForm(forms.ModelForm):
    """
    Form for editing namespaces.
    """

    class Meta:
        model = models.NamespaceModel
        fields = ('prefix', 'uri')

    def __init__(self, *args, **kwargs):
        super(NamespaceForm, self).__init__(*args, **kwargs)

        if self.instance.fixed:
            self.fields['prefix'].widget.attrs['readonly'] = True
            self.fields['uri'].widget.attrs['readonly'] = True

    def clean_prefix(self):
        """
        Validates the prefix
        """
        if self.instance.fixed:
            return self.instance.prefix

        prefix = self.cleaned_data['prefix']
        if not namespace.is_ncname(prefix):
            raise forms.ValidationError("This is an invalid prefix")

        return prefix

    def clean_uri(self):
        """
        Validates the URI
        """
        if self.instance.fixed:
            return self.instance.uri

        uri = self.cleaned_data['uri']
        # todo: URI validation
        return uri
