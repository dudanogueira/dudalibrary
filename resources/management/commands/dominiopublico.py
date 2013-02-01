# -*- coding: utf-8 -*-
# TODO: better logger
import sys, time, urllib, random, subprocess, os, cookielib, urllib2
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from optparse import make_option
from options.models import Source, Category, Language
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from utils import folder_size

from resources.models import Resource
from utils import folder_size

SOURCE_ID = 3
SOURCE_URL = "http://http://www.dominiopublico.gov.br/"
SOURCE_SLUG = "dominiopublico.gov.br"
SOURCE_NAME = "Domínio Público Brasileiro"
TOTAL_DOWNLOAD = 100#2000


CATEGORY_DICT = {
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

def downloader(urltodownload, basetarget):
    '''download file to basefolder/downloaded_source if packed, and unpack to basefolder'''
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    response = opener.open(urltodownload)
    url_to_download = response.geturl()
    filename = url_to_download.split("/")[-1]
    fileresponse = opener.open(urltodownload)
    try:
        target = open("%s/%s" % (basetarget, filename), "w")
        print "GETTING n WRITTING FILE..."
        target.write(fileresponse.read())
        target.close()
    except:
        print "ERROR downloader"
        raise

class DominioPublicoItem:
    def __init__(self, resource, created=False):
        self.resource = resource
        print "fetching individual... %s" % resource.resource_url
        f = urllib.urlopen(resource.resource_url)
        s = f.read()
        soup = BeautifulSoup(s)
        self.soup = soup
        self.notes = ''
        self.language_s = ''
        self.structure = ''

    def parse(self):
        if self.resource.status != 'downloaded':
            self.resource.status = "processing"
            self.status = 'processing...'
        
        self.declared_cat = self.soup("td", {"class": "detalhe2"})[5].text
        self.structure = self.declared_cat
        # if it falls below, should be marked as excluded
        if self.declared_cat == u'Teses e Dissertações':
            print "WARNING! This content was marked as excluded"
            self.resource.status = 'rejected'
            self.resource.enabled = False
            self.resource.save()
        else:
            # LANGUAGE DEFS
            self.language_s = self.soup("td", {"class": "detalhe2"})[6].text.strip()
            print "LANGUAGE", self.language_s
            language_listed = self.language_s.lower()
            if language_listed.find("port") == 0:
                self.language,created = Language.objects.get_or_create(code='pt-br')
            elif language_listed.find("ingl") == 0:
                self.language,created = Language.objects.get_or_create(code='en')
            elif language_listed.find("espa") == 0:
                self.language,created = Language.objects.get_or_create(code='es')
            else:
                self.language,created = Language.objects.get_or_create(code='na')
            self.resource.language = self.language
            self.notes = ' '.join(self.soup("td", {"class": "detalhe2"})[7].text.strip().split())
            print "NOTES",self.notes.strip()

    def download(self):
        work_folder = os.path.dirname(smart_str(self.resource.content_root()))
        print "- CREATING DIR..."
        subprocess.call("mkdir -vp %s" % work_folder, shell=True)
        # run downloader
        urltodownload = str(self.resource.resource_download_url)
        basetarget = str(work_folder)
        try:
            downloader(urltodownload, basetarget)
            self.resource.status = 'downloaded'
            size = folder_size(work_folder)
            self.resource.size = size
            contents = os.listdir(work_folder)
            if contents:
                self.resource.trigger = contents[0]
                self.resource.trigger_extensions = self.resource.trigger.rsplit('.')[-1]
                self.resource.resource_downloaded_file = self.resource.trigger
        except:
            self.resource.status = 'error'
            self.resource.save()
            raise
        
    def save(self):
        self.resource.notes = self.notes
        self.resource.structure = self.structure
        self.resource.resource_language = self.language_s
        self.resource.save()

class Command(BaseCommand):
    help = "Sync Resources from Resource 1: Portal do Professor"
    args = "--sync, --get GRID,GRID,GRID, --nowdownload"
    option_list = BaseCommand.option_list + (
    make_option('--sync',
        action='store_true',
        dest='sync',
        help='Sync Resources with Source. You'),
    make_option('--nodownload',
        action='store_true',
        dest='nodownload',
        help='Only get informations. Do not download'),
    make_option('--get',
        action='append',
        dest='get',
        help='Get specific GRIDS for debug.'),
    make_option('--force-download',
        action='store_true',
        dest='force_download',
        help='Force download even if already downloaded.'),
    )

    def handle(self, *args, **options):
        # pagesets as arguments
        sync = options.get('sync')
        get = options.get('get')
        nodownload = options.get('nodownload')
        force_download = options.get('force_download')
        range_values = options.get('range_values')
        if get:
            grids = get[0].split(",")
            for grid in grids:
                print "GRID:",grid
                try:
                    resource = Resource.objects.get(pk=grid)
                except DoesNotExist:
                    raise                
        if sync:
            # try to get the source from database
            source, created = Source.objects.get_or_create(pk=SOURCE_ID, url=SOURCE_URL, slug=SOURCE_SLUG, name=SOURCE_NAME)
            print "Source created?",created
            print "processing..."
            url = "http://www.dominiopublico.gov.br/pesquisa/ResultadoPesquisaObraForm.do?first=%d&skip=0&ds_titulo=&co_autor=&no_autor=&co_categoria=&pagina=1&select_action=Submit&co_midia=2&co_obra=&co_idioma=&colunaOrdenar=NU_PAGE_HITS&ordem=desc" % TOTAL_DOWNLOAD
            print "fetching ...%s..." % url
            f = urllib.urlopen(url)
            s = f.read()
            f.close()
            print "parsing..."
            soup = BeautifulSoup(s)
            units = soup("table", {'class': 'displaytagTable'})[0].tbody.contents
            controller = 0
            for i in units:
                if i != '\n':
                    print "#####" * 10
                    controller += 1
                    print "CONTROLLER",controller
                    id = int(i.contents[3].a.attrs[0][1].split("=")[-1])
                    print "ID:",id
                    title = i.contents[5].text
                    title=unicode(BeautifulStoneSoup(title,convertEntities=BeautifulStoneSoup.HTML_ENTITIES ))
                    resource_size = ''.join(i.contents[13].text.strip().split())
                    resource_download_url = "http://www.dominiopublico.gov.br/pesquisa/DetalheObraDownload.do?select_action=&co_obra=%d&co_midia=2" % id
                    resource_url = "http://www.dominiopublico.gov.br/pesquisa/DetalheObraForm.do?select_action=&co_obra=%d" % int(id)
                    file_name = ''
                    resource_pageviews =  i.contents[15].text.replace(".",'')
                    author = i.contents[7].text.strip()
                    author=unicode(BeautifulStoneSoup(author,convertEntities=BeautifulStoneSoup.HTML_ENTITIES ))
                    content_source = i.contents[9].text.strip()
                    content_source=unicode(BeautifulStoneSoup(content_source,convertEntities=BeautifulStoneSoup.HTML_ENTITIES ))
                    license = u'Domínio Público / Public Domain'
                    resource_extension = i.contents[11].text.strip()
                    category = Category.objects.get(code='ebook')
                    print "TITLE:",title
                    print "AUTHOR:",author
                    print "CONTENT_SOURCE:",content_source
                    print "FORMAT:",resource_extension
                    print "R_SIZE:",resource_size
                    print "PGVIEWS:",resource_pageviews
                    print "R_LINK:",resource_url
                    print "R_DL_LINK:",resource_download_url
                    print "LICENSE:",license
                    resource,created = Resource.objects.get_or_create(
                        resource_reference_string=str(id), source=source, resource_url=resource_url
                    )
                    
                    print "GRID:",resource.pk
                    if resource.status != 'rejected':
                        resource.title = title
                        resource.author = author
                        resource.content_source = content_source
                        resource.resource_size = resource_size
                        resource.resource_pageviews = resource_pageviews
                        resource.resource_url = resource_url
                        resource.resource_download_url = resource_download_url
                        resource.license = license
                        resource.category.add(category)
                        resource.save()
                        r = DominioPublicoItem(resource, created)
                        if force_download or resource.status != 'downloaded':
                            try:
                                print "--DOWNLOADING...FORCED?",force_download
                                print "--STATUS:",resource.status
                                r.parse()
                                if nodownload:
                                    print "NOT DOWNLOADING!"
                                    print "STATUS",r.resource.status
                                else:
                                    r.download()
                                r.save()
                            except:
                                print "ERROR DOWNLOADING"
                                r.resource.status = 'error'
                                r.resource.save()
                                raise
                        else:
                            print "-- CONTENT ALREADY MARKED AS DOWNLOADED"
                            r.save()
                    else:
                        print "######" * 10
                        print "######" * 10
                        print "WARNING! THIS RESOURCE WAS MARKED AS REJECTED"
                        print "######" * 10
                        print "######" * 10