from django.core.management.base import BaseCommand

from optparse import make_option

from django.conf import settings

from dudalibrary import utils

from queue.models import ResourceQueue

class Command(BaseCommand):
    help = "Enqueue items to download."
    def handle(self, *args, **kwargs):
        print args
        for identifier in args:
            # identify this identifier_id
            item = utils.resource_identifier(identifier)
            if item and item.identified:
                queue,created = ResourceQueue.objects.get_or_create(
                    identifier_id=item.identifier_id,
                    plugin_name=item.PLUGIN_NAME,
                    plugin_slug=item.PLUGIN_SLUG,
                    full_url=item.full_url,
                    priority=1,
                )
                if created:
                    print "QUEUE for IDENTIFIER: %s CREATED" % identifier
            else:
                print "IDENTIFIER %s NOT IDENTIFIED. IGNORING" % identifier
