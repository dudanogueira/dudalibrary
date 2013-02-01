# -*- coding: utf-8 -*-
from options.models import Source, Category, Language
import os, subprocess, urllib2, json
from BeautifulSoup import BeautifulSoup

from resources.models import Resource
from dudalibrary import utils

from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.utils.encoding import smart_str

from youtube import Parser as YoutubeParser

class Parser(YoutubeParser):
    '''
    Duda Library Plugin to parse and index Open Educational Resources (OERs)
    stored at Youtube under KhanAcademyPortugues user.
    '''
    def __init__(self):
        YoutubeParser.__init__(self)
        # metas
        self.PLUGIN_NAME = u'Plugin Khan Academy'
        self.YOUTUBE_USERS = {
            "khanacademy": { "language_code": "en", },
            "khanacademyportugues": { "language_code": "pt-br", },
        }
        self.PLUGIN_SLUG = u'khanacademy'
        self.EMAIL = u'dudanogueira@gmail.com'
        self.VERSION = 0.1
        # source infos
        self.SOURCE_URL = u"http://www.youtube.com/user/KhanAcademyLanguages/"
        self.SOURCE_SLUG_FULL = u"youtube.com/user/KhanAcademyLanguages/"
        self.SOURCE_SLUG = u"youtube.com"
        self.SOURCE_NAME = u"Khan Academy"
        self.BASE_URL = u'http://www.youtube.com/watch?v='
        self.resource = None
    
    def identify(self, url):
        YoutubeParser.identify(self, url)
        # identified already as youtube 
        if self.identified:
            # check if the user of this youtube video is from self.YOUTUBE_USERS
            request = urllib2.urlopen(self.json_url)
            self.json_data = json.load(request)
            try:
                self.youtube_user = self.json_data['data']['uploader']
                self.language_code = self.YOUTUBE_USERS[self.youtube_user]['language_code']
                self.language_name = dict(LANGUAGES)[self.language_code]
                self.SOURCE_NAME = "%s (%s)" % (self.PLUGIN_NAME, self.language_name)
                self.identified = True
            except:
                self.identified = False
    
    def parse(self, url=None):
        '''identify and parse the url into a registered Resource Object'''
        if url:
            self.url = url
        
        try:
            return self
        except:
            raise
            # error. Mark the resource with error
            self.parsed = False
            self.resource.status = 'error'
            self.resource.save()
    
    def index(self):
        '''Index the resource with the parsed infos'''
        if self.parsed:
            # check files, paths, thumbnails, etc
            print "INDEX!"
            self.resource.check_files()
            self.resource.generate_thumb()

            
            
