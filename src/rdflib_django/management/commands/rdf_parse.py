"""
Management command for parsing RDF into the store.
"""
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
import sys
from django.db import transaction
from rdflib.graph import Graph
from rdflib.term import URIRef
from rdflib_django.store import DjangoStore


class Command(BaseCommand):
    """
    The actual command.
    """

    option_list = BaseCommand.option_list + (
        make_option('--store', '-s', type='string', dest='store',
            help='RDF data will be imported into the store with this identifier. If not specified, the default store ' +
                 'is used.'),

        make_option('--context', '-c', type='string', dest='context',
            help='RDF data will be imported into a context with this identifier. If not specified, a new blank ' +
                 'context is created.'),

        make_option('--format', '-f', type='string', dest='format', default='xml',
            help='Format of the RDF data. This option accepts all formats allowed by rdflib. Defaults to xml.')
    )

    help = """Imports an RDF resource.

Examples:
    {0} rdf_parse my_file.rdf
    {0} rdf_parse --format n3 my_file.n3
    {0} rdf_parse --context http://zoowizard.eu http://zoowizard.eu/datasource/zoochat/294
    """.format(sys.argv[0])
    args = 'file-or-resource'

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if not args:
            raise CommandError("No file or resource specified.")

        if options.get('store'):
            store = DjangoStore(configuration=None, identifier=options.get('store'))
        else:
            store = DjangoStore(configuration=None)

        if options.get('context'):
            graph = Graph(store=store, identifier=URIRef(options.get('context')))
        else:
            graph = Graph(store=store)

        graph.open(configuration=None)
        graph.parse(args[0], format=options.get('format'))
