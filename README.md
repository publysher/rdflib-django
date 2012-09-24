rdflib-django
=============

A store implementation for [rdflib](http://pypi.python.org/pypi/rdflib/) that uses Django as its backend. 

The current implementation is context-aware but not formula-aware. Furthermore, performance 
has not yet been considered. 

The implementation assumes that contexts are used for named graphs. 

Quick start
-----------

Add the `rdflib-django` sources to your project, and add `rdflib_django` to your `INSTALLED_APPS` in `settings.py`. 

You can now use the following examples to obtain a graph. 

Getting a graph using rdflib's store API:

	from rdflib import Graph
	graph = Graph('Django')

This example will give you a graph identified by a blank node within the default store. 

Getting a conjunctive graph using rdflib's store API:

	from rdflib import ConjunctiveGraph
	graph = ConjunctiveGraph('Django')

This example will give you a conjunctive graph in the default store.

Getting a named graph using `django_rdflib`'s API:

	from django_rdflib import utils
	graph = utils.get_named_graph('http://example.com')

License
-------

`rdflib-django` is licensed under the [MIT license](https://raw.github.com/publysher/rdflib-django/master/LICENSE). 
