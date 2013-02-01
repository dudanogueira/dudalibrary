# -*- coding: utf-8 -*-
# TODO: better logger
import sys, time, urllib2, random, subprocess, os, settings
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from optparse import make_option
from options.models import Source, Category, Language
from BeautifulSoup import BeautifulSoup
from resources.models import Resource
from utils import folder_size


# "youtube.py, youtube-dl"
downloader = "youtube-dl"

try:
    import json
except ImportError:
    import simplejson as json

from xml.dom.minidom import parseString

from youtube import youtube

SOURCE_ID = 10
SOURCE_URL = "http://khanacademy.org/"
SOURCE_SLUG = "khanacademy.org"
SOURCE_NAME = "Khan Academy"

# This is a set of youtube users.

YOUTUBE_USERS = {
    'khanacademy': 'en',
    'KhanAcademyPortugues': 'pt-br',
}


# login 
# log tests
import logging

LOG_DIR = getattr(settings, 'LOGDIR', '%slogs' % settings.INSTANCE(''))
if not os.path.isdir(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except:
        print "ERROR! no log!"
        raise

LOG_FILE = '%s/downloader-%s.log' % (LOG_DIR, SOURCE_SLUG)

# Setup logging
logger = logging.getLogger('khan.py')
logger.setLevel(logging.DEBUG)
# Use file output for production logging:
filelog = logging.FileHandler(LOG_FILE, 'w')
filelog.setLevel(logging.INFO)
# Use console for development logging:
conlog = logging.StreamHandler()
conlog.setLevel(logging.DEBUG)
# Specify log formatting:
formatter = logging.Formatter("%(asctime)s L%(lineno)s \
%(levelname)s: %(message)s", "%Y-%m-%d %H:%M")
conlog.setFormatter(formatter)
filelog.setFormatter(formatter)
# Add console log to logger
logger.addHandler(conlog)
logger.addHandler(filelog)

# YOUTUBE INSTANVE
youtube.YouTube()

def downloader(urltodownload, basetarget, filename):
    '''download file at urltodownload to basetarget/downloaded_source if packed, and unpack to basetarget'''
    # here you will download the file, observing above
    pass

class KhanAcademyItem:
    def __init__(self, resource, created=False):
        pass
        # create a class that will receive the resource object, with it's the url to be parsed.

class Command(BaseCommand):
    help = "Sync Resources from Resource N: SOME GOOD CONTENT"
    args = "--sync, --get GRID,GRID,GRID, --nowdownload"
    option_list = BaseCommand.option_list + (
    make_option('--sync',
        action='store_true',
        dest='sync',
        help='Sync Resources with Source.'),
    make_option('--nodownload',
        action='store_true',
        dest='nodownload',
        help='Only get informations. Do not download'),
    make_option('--force-download',
        action='store_true',
        dest='force_download',
        help='Force download even if already downloaded.'),
    )

    def handle(self, *args, **options):
        # REGISTERING SOURCE
        source, created = Source.objects.get_or_create(pk=SOURCE_ID, url=SOURCE_URL, slug=SOURCE_SLUG, name=SOURCE_NAME)
        logger.info("SOURCE: %s, Created: %s " % (source, created))
        # pagesets as arguments
        sync = options.get('sync')
        get = options.get('get')
        nodownload = options.get('nodownload')
        force_download = options.get('force_download')
        range_values = options.get('range_values')
        # GET SPECIFIC ITEMS, AND DO SOMETHING
        if sync:
            if args:
                print "ARGS:",args
                user = args[0]
                language_code = YOUTUBE_USERS[user]
                language,created = Language.objects.get_or_create(code=language_code)
            # try to get the source from database. this will create
            source, created = Source.objects.get_or_create(pk=SOURCE_ID, url=SOURCE_URL, slug=SOURCE_SLUG, name=SOURCE_NAME)
            print "Source created?",created
            # get total of videos per user:
            try:
                logger.info("USER: %s, LANGUAGE: %s" % (user, language))
                print "GETTING TOTAL OF VIDEOS..."
                BASE_URL = "https://gdata.youtube.com/feeds/api/users/%s/uploads" % user
                f = urllib2.urlopen(BASE_URL)
                data = f.read()
                f.close()
                p = parseString(data)
                a = p.getElementsByTagName('openSearch:totalResults')
                try:
                    total_items = int(a[0].childNodes[0].data)
                    logger.info("TOTAL VIDEOS: %d" % total_items)
                    # loop in all items
                    for index in range(1,total_items,50):#[0:1]:
                        logger.info("ITEM INDEX ID: %d" % index)
                        MOD_URL = BASE_URL + "?start-index=" + str(index) + "&max-results=50"
                        logger.info("HITTING: %s" % MOD_URL)
                        f = urllib2.urlopen(MOD_URL)
                        data = f.read()
                        f.close()
                        p = parseString(data)
                        urls = []
                        # debug
                        print "URLS"
                        for entry in p.getElementsByTagName("entry"):
                            print entry.getElementsByTagName('id')[0].childNodes[0].data
                        for entry in p.getElementsByTagName("entry"):
                            url = entry.getElementsByTagName('id')[0].childNodes[0].data
                            title = entry.getElementsByTagName('title')[0].childNodes[0].data
                            youtubeid = url.split("/")[-1]
                            youtube_url = "http://www.youtube.com/watch?v=%s" % youtubeid
                            logger.info("URL to HIT: %s" % youtube_url)
                            # get or create resource
                            resource,created = Resource.objects.get_or_create(
                                resource_reference_string=youtubeid, source=source, resource_url=youtube_url, language=language
                            )
                            resource.category = Category.objects.filter(code__in=['video', 'video-class'])
                            if not os.path.isdir(resource.content_root_path()):
                                try:
                                    os.makedirs(resource.content_root_path())
                                except:
                                    print "ERROR! CANT CREATE %s!" %  resource.content_root_path()
                                    raise

                            logger.info("GRID: %s, CREATED: %s STATUS: %s" % (resource.id, created, resource.status))
                            if resource.status == "installed":
                                logger.info("installed. passing")
                            else:                                
                                #get more data from youtube
                                json_url = "http://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=jsonc" % youtubeid
                                request = urllib2.urlopen(json_url)
                                json_data = json.load(request)
                                description = json_data['data'].get('description')
                                duration = json_data['data'].get('duration')
                                resource_pageviews = json_data['data'].get('viewCount')
                                #tags = ', '.join(json_data['data'].get('tags'))
                                tags = ''
                                # download using : https://github.com/NFicano/python-youtube-download
                                if downloader == "youtube.py":
                                    yt = youtube.YouTube()
                                    yt.url = youtube_url
                                    print "URL",yt.url
                                    yt.filename = youtubeid
                                    yt.filter("mp4")[0].download(resource.content_root_path(), youtubeid)
                                    resource.trigger = "%s.mp4" % yt.filename
                                    reload(youtube)
                                else:
                                    dlcmd = 'python %s/youtube-dl.py -c --write-info-json --write-description -f 18 %s' % (settings.INSTANCE(), youtube_url)
                                    logger.info("COMMAND: %s" % dlcmd)
                                    resource.create_content_root()
                                    os.chdir(resource.content_root_path())
                                    try:
                                        p = subprocess.call(dlcmd, shell=True)
                                        resource.status = "installed"
                                        resource.enabled = True
                                        resource.trigger = "%s.%s" % (youtubeid, "mp4")
                                    except:
                                        resource.enabled = False
                                        resource.status = "error"
                                resource.tags = tags
                                resource.title = title
                                resource.author = "http://www.youtube.com/user/%s" % user
                                resource.duration = duration
                                resource.size = folder_size(resource.content_root_path())
                                resource.resource_pageviews = resource_pageviews
                                resource.save()
                                # generate thumbs
                                resource.generate_thumb()
                except:
                    print "ERROR!"
                    raise

            except:
                raise
                print "ERROR, USER NOT LISTED ON SCRIPT"
                print "OPTIONS ARE --sync: %s" % ", ".join(YOUTUBE_USERS)
        else:
            print "OPTIONS ARE --sync: %s" % ", ".join(YOUTUBE_USERS) 
            
            
            