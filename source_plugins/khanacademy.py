# -*- coding: utf-8 -*-
from options.models import Source, Category, Language
import os, subprocess, urllib2, json
from BeautifulSoup import BeautifulSoup

from xml.dom.minidom import parseString

from resources.models import Resource
from dudalibrary import utils

from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.utils.encoding import smart_str

from youtube import Parser as YoutubeParser

class Parser(YoutubeParser):
    '''
    Duda Library Plugin to parse and index Open Educational Resources (OERs)
    stored at Youtube under KhanAcademy user.
    '''
    def __init__(self):
        YoutubeParser.__init__(self)
        # initials
        self.parsed = False
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
    
    def get_all_identifiers(self, youtubeuser=None):
        '''return a list of all identifiers that this source can provide'''
        print "GETTING TOTAL OF VIDEOS..."
        if youtubeuser:
            BASE_URL = "https://gdata.youtube.com/feeds/api/users/%s/uploads" % youtubeuser
            f = urllib2.urlopen(BASE_URL)
            data = f.read()
            f.close()
            p = parseString(data)
            a = p.getElementsByTagName('openSearch:totalResults')
            try:
                total_items = int(a[0].childNodes[0].data)
                urls = []
                for index in range(1,total_items,50):#[0:1]:
                    MOD_URL = BASE_URL + "?start-index=" + str(index) + "&max-results=50"
                    f = urllib2.urlopen(MOD_URL)
                    data = f.read()
                    f.close()
                    p = parseString(data)
                    for entry in p.getElementsByTagName("entry"):
                        url = entry.getElementsByTagName('id')[0].childNodes[0].data
                        youtubeid = url.split("/")[-1]
                        urls.append("%s@youtube.com" % youtubeid)
                return urls
            except:
                pass    

        else:
            print "Need the youtubeuser"
        
    
    
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
            
