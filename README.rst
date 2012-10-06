rdflib-django
=============

A store implementation for `rdflib`_ that uses Django as its backend.

The current implementation is context-aware but not formula-aware.
Furthermore, performance has not yet been considered.

The implementation assumes that contexts are used for named graphs.

.. image:: https://secure.travis-ci.org/publysher/rdflib-django.png
   :target: https://travis-ci.org/#!/publysher/rdflib-django

Quick start
-----------

Install rdflib-django with your package manager:

::

    pip install rdflib-django

Add ``rdflib_django`` to your ``INSTALLED_APPS``:

::

    INSTALLED_APPS = (
        # other apps
        'rdflib_django'.
    )

You can now use the following examples to obtain a graph.

Getting a graph using rdflib's store API:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    from rdflib import Graph
    graph = Graph('Django')
    graph.open(create=True)

This example will give you a graph identified by a blank node within the
default store.

Getting a conjunctive graph using rdflib's store API:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    from rdflib import ConjunctiveGraph
    graph = ConjunctiveGraph('Django')

This example will give you a conjunctive graph in the default store.

Getting a named graph using rdflib-django's API:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    from rdflib_django import utils
    graph = utils.get_named_graph('http://example.com')

Getting the conjunctive graph using rdflib-django's API:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    from rdflib_django import utils
    graph = utils.get_conjunctive_graph()

Management commands
-------------------

``rdflib-django`` includes two management commands to import and export
RDF:

::

    $ python manage.py import_rdf --context=http://example.com my_file.rdf
    $ python manage.py export_rdf --context=http://example.com

License
-------

``rdflib-django`` is licensed under the `MIT license`_.

.. _rdflib: http://pypi.python.org/pypi/rdflib/
.. _MIT license: https://raw.github.com/publysher/rdflib-django/master/LICENSE

