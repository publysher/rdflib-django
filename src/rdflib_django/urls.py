"""
The application provides no URLs of its own.
In development mode, this will include the admin package.
"""
from django.conf import settings
from django.conf.urls import patterns, include

if hasattr(settings, 'DJANGO_RDFLIB_DEVELOP') and getattr(settings, 'DJANGO_RDFLIB_DEVELOP'):
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns = patterns('',
        (r'^admin/doc/', include('django.contrib.admindocs.urls')),
        (r'^admin/', include(admin.site.urls)),
    )
