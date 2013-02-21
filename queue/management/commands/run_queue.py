from django.core.management.base import BaseCommand

from optparse import make_option

from django.conf import settings

from dudalibrary import utils

from queue.models import ResourceQueue

class Command(BaseCommand):
    help = "Enqueue items to download."
    def handle(self, *args, **kwargs):
        queues = ResourceQueue.objects.all().exclude(status='done')
        for queue in queues:
            queue.run()