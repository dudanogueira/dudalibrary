from optparse import make_option

from django.core.management.base import BaseCommand

from dudalibrary.utils import resource_indexer

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--parse',
            action='store_true',
            dest='parse',
            default=False,
            help='Parse a set of OERs UIDs'),
        )

    def handle(self, *args, **options):
        if options['parse']:
            for arg in args:
                print "Analyzing %s" % arg
                parser = resource_indexer(arg)
                parser.index()
                parser.download()
                