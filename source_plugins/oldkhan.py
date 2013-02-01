# -*- coding: utf-8 -*-
import urllib2, json

import urlparse

SOURCE_ID = 10
SOURCE_URL = "youtube.com/user/KhanAcademyPortugues/"
SOURCE_SLUG = "youtube.com"
SOURCE_NAME = "Khan Academy Português"

class Parser(object):
    '''
    Duda Library Plugin to parse and index Open Educational Resources (OERs)
    stored at youtube under the user of KhanAcademyPortuguese.
    '''
    def identify(self, url):
        '''return True if the url belongs to this Parser'''
        self.url = url
        try:
            if url.find('youtube.com'):
                query = urlparse.parse_qs(self.url) 
                self.video_id = str(query["v"][0])
                self.identified = True
            else:
                self.identified = False
        except:
            self.identified = False
    
    def parse(self, url):
        if(self.identify(url)):
            json_url = "http://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=jsonc" % self.video_id
            request = urllib2.urlopen(json_url)
            json_data = json.load(request)
            self.title = json_data['data'].get('khan')
            print "KHAN %s" % str(self.title)
            
            
            