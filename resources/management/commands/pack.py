# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode

from optparse import make_option

from resources.models import Resource
from utils import folder_size

class Command(BaseCommand):
    help = "Pack Resources"
    args = "all, GRID,GRID,GRID"
    option_list = BaseCommand.option_list + (
    make_option('--force',
        action='store_true',
        dest='force',
        help='Force packaging already packed resources.'),
    )

    def handle(self, *args, **options):
        '''Pack the content. First generate the descriptor, then zipping to the expected location'''
        force = options.get('force')
        print force
        if args:
            if args[0] == "all":
                items = Resource.objects.filter(status="installed")
            else:
                if len(args[0].split('-')) == 2:
                    items_id = range(int(args[0].split('-')[0]),int(args[0].split('-')[1])+1)
                else:
                    items_id = args[0].split(',')
                items = Resource.objects.filter(id__in=items_id)
            for item in items:
                # generate descritors and
                # generate pack
                item.generate_pack(force)
            if force:
                print "with force", args
            else:
                print "no force", args
        else:
            print "USAGE: manage.py pack all"
            print "OPTIONS: --force : Force packaging."
