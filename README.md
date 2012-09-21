zoowizard-rdf
=============

Manages the RDF repositories for [Zoo Wizard](http://zoowizard.eu).

The current version creates an initial RDF datasource for the http://www.zoochat.com/zoos/ list of zoos.

For more information, read [My Blog](http://blog.publysher.nl/2012/08/using-rdf-to-populate-zoowizard-case.html)


Setup
-----

Bootstrap the project with 

	python bootstrap.py && ./bin/buildout

Then, use the following Makefile targets:

    make all        # create a fully published dataset archive
    make dataclean  # remove all generated files

