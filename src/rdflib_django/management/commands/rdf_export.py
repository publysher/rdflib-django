"""
Management command for exporting RDF from the store.
"""
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
import sys
from rdflib.term import URIRef
from rdflib_django import utils


class Command(BaseCommand):
    """
    Command object for exporting RDF.
    """

    option_list = BaseCommand.option_list + (
        make_option('--context', '-c', type='string', dest='context',
            help='Only RDF data from the context with this identifier will be exported. If not specified, a new blank ' +
                 'context is created.'),

        make_option('--store', '-s', type='string', dest='store',
            help='RDF data will be exported from the store with this identifier. If not specified, the default store ' +
                 'is used.'),

        make_option('--format', '-f', type='string', dest='format', default='xml',
            help='Format of the RDF data. This option accepts all formats allowed by rdflib. Defaults to xml.')
    )

    help = """Exports an RDF resource.

Examples:
    {0} rdf_export my_file.rdf
    {0} rdf_export --format n3 my_file.n3
    {0} rdf_export --context http://example.com/context
    """.format(sys.argv[0])
    args = 'file'

    def handle(self, *args, **options):
        store_id = options.get('store')
        context_id = options.get('context')
        target = args[0] if args else sys.stdout

        if context_id:
            graph = utils.get_named_graph(URIRef(context_id), store_id=store_id)
        else:
            graph = utils.get_conjunctive_graph(store_id)

        #noinspection PyUnresolvedReferences
        graph.serialize(target, format=options.get('format'))
