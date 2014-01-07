# -*- coding: utf-8 -*-
from options.models import Source, Category, Language
import urllib2, os, subprocess, json
from BeautifulSoup import BeautifulSoup

from resources.models import Resource
from dudalibrary import utils

import urlparse

from youtube_downloader import youtube as youtube_downloader

from django.conf import settings
from django.utils.encoding import smart_str

class Parser(object):
    '''
    Duda Library Plugin to parse and index Open Educational Resources (OERs)
    stored at Youtube under KhanAcademyPortugues user.
    '''
    def __init__(self):
        # metas
        self.CATEGORY_DICT = {
            "audio": 9,
            "imagem": 2,
            "mapa": 7,
            "experimento": 3,
            "software": 8,
            "animacao": 5,
            "ebook": 10,
            "hipertexto": 6,
            "video-class": 4,
            "video": 1,
        }
        
        self.PLUGIN_NAME = u'Youtube'
        self.PLUGIN_SLUG = u'youtube'
        self.AUTHOR = u'Duda Nogueira'
        self.EMAIL = u'dudanogueira@gmail.com'
        self.VERSION = 0.1
        # source infos
        self.SOURCE_URL = u"http://www.youtube.com/"
        self.SOURCE_SLUG_FULL = u"youtube.com"
        self.SOURCE_SLUG = u"youtube.com"
        self.SOURCE_NAME = u"Youtube"
        self.BASE_URL = u'http://www.youtube.com/watch?v='
        self.resource = None
        self.json_url_raw = "http://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=jsonc"


    def identify(self, url):
        '''return True if the url belongs to this Parser
        considering this Source (Youtube), the url can be both:
        M960P77pvbQ@youtube.com
        or
        http://www.youtube.com/watch?v=M960P77pvbQ    
        '''
        # define infos for testing
        # test 1234@source.org
        self.identified = False
        self.url = url
        if self.url.find('@') != -1:
            bits = url.split('@')
            try:
                # its a valid integer
                self.reference_id = str(bits[0])
                
                # second part of @ matches with source_slug
                if bits[1] == self.SOURCE_SLUG:
                    self.resource_slug = bits[1]
                    self.json_url = self.json_url_raw % self.reference_id
                    self.identifier_id = '%s@%s' % (self.reference_id, self.resource_slug)
                    self.resource_reference_string = self.identifier_id
                    self.full_url = "%s%s" % (self.BASE_URL, self.reference_id)
                    self.identified = True
                else:
                    self.identified = False
            except:
                raise
                self.identified = False
        # test the others
        else:
            try:
                if self.url.find("youtube.com") != -1:
                    self.query = urlparse.parse_qs(self.url.split('?')[1]) 
                    self.video_id = str(self.query["v"][0])
                    self.resource_slug = self.SOURCE_SLUG
                    self.reference_id = self.video_id
                    self.json_url = self.json_url_raw % self.reference_id
                    self.identifier_id = '%s@%s' % (self.reference_id, self.resource_slug)
                    self.resource_reference_string = self.identifier_id
                    self.identified = True
                    self.full_url = "%s%s" % (self.BASE_URL, self.reference_id)
                else:
                    self.identified = False
            except:
                self.identified = False
    
    def parse(self, url=None):
        '''identify and parse the url into a registered Object'''
        self.parsed = False
        if url:
            self.url = url
        # parse already try to identify
        self.identify(self.url)
        if self.identified:
            try:
                request = urllib2.urlopen(self.json_url)
                self.json_data = json.load(request)
                self.description = self.json_data['data'].get('description')
                self.duration = self.json_data['data'].get('duration')
                self.resource_pageviews = self.json_data['data'].get('viewCount')
                self.title = self.json_data['data'].get('title')
                self.youtube_user = self.json_data['data'].get('uploader')
                self.parsed = True
                return True
            except:
                # error. Mark the resource with error
                self.parsed = False
                return False
    
    def index(self):
        '''Index the resource with the parsed infos'''
        if self.parsed:
            # get source
            source, created = Source.objects.get_or_create(url=self.SOURCE_URL, slug=self.SOURCE_SLUG, name=self.SOURCE_NAME)
            # get resource
            self.resource,self.resource_created = Resource.objects.get_or_create(
                resource_reference_string=self.resource_reference_string, source=source, resource_url=self.full_url
            )
            self.resource.title = self.title
            self.resource.author = "http://www.youtube.com/user/%s" % self.youtube_user
            self.resource.duration = self.duration
            self.resource.description = self.description
            self.resource.save()
            self.parsed = True

        else:
            self.parsed = False
            print "ERROR. Not parsed"
    
    def download(self, download_method=None):
        if self.parsed:
            if not download_method:
                download_method = getattr(settings, 'YOUTUBE_DOWNLOAD_METHOD', None)
            if download_method == 'youtube_downloader' or None:
                print "METHOD: %s" % download_method
                # check files, paths, thumbnails, etc
                yt = youtube_downloader.YouTube()
                yt.url = self.full_url
                video = yt.filter("mp4")[0]
                video.filename = self.reference_id + '.mp4'
                # create folder
                work_folder = os.path.dirname(smart_str(self.resource.content_root()))
                subprocess.call("mkdir -vp %s" % work_folder, shell=True)
                # download
                video.download(self.resource.content_root_path())
                #reload(youtube)
                self.resource.trigger = video.filename
                self.resource.enabled = True
                self.resource.size = utils.folder_size(self.resource.content_root_path())
                self.resource.check_files()
                self.resource.generate_thumb()
            elif download_method == 'youtube-dl':
                print "METHOD: %s" % download_method
                dlcmd = 'python %s/youtube-dl.py -c --write-info-json --write-description -f 18 %s' % (settings.INSTANCE(), self.full_url)
                print "COMMAND: %s" % dlcmd
                self.resource.create_content_root()
                os.chdir(self.resource.content_root_path())
                print self.resource.content_root_path()
                try:
                    p = subprocess.call(dlcmd, shell=True)
                    self.resource.status = "installed"
                    self.resource.enabled = True
                    self.resource.trigger = "%s.%s" % (self.reference_id, "mp4")
                except:
                    raise
                    self.resource.enabled = False
                    self.resource.status = "error"
            

            
            
