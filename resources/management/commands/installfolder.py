# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode

import datetime, settings, os, subprocess, utils

from optparse import make_option

class Command(BaseCommand):
    help = "Read and Install Resources from Install Folder: %s" % settings.INSTALL_FOLDER
    args = "install"
    option_list = BaseCommand.option_list + (
    make_option('--force',
        action='store_true',
        dest='force',
        help='Force installing a already installed resources.'),
    )

    def handle(self, *args, **options):
        '''Read the Install Folder, and install its contents'''
        force = options.get('force')
        if args:
            if args[0] == "install":
                print "Installing resources from %s" % settings.INSTALL_FOLDER
                if not os.path.exists(settings.INSTALL_FOLDER):
                    subprocess.call("mkdir -vp %s" % settings.INSTALL_FOLDER, shell=True)
                for resource_pack in utils.locate('*.zip', settings.INSTALL_FOLDER):
                    print "######" * 5
                    print "INSTALLING: %s" % resource_pack
                    if utils.ImportItem(resource_pack):
                        print "INSTALLED: %s" % resource_pack
                    else:
                        print "ERROR: %s" % resource_pack
            else:
                pass
        else:
            print "You must provide at least 'install' as argument"
