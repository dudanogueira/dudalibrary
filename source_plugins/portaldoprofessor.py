# -*- coding: utf-8 -*-
from options.models import Source, Category, Language
import urllib, os, subprocess
from BeautifulSoup import BeautifulSoup

from resources.models import Resource
from dudalibrary import utils

from django.conf import settings
from django.utils.encoding import smart_str, smart_unicode

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


class Parser:
    '''
    Duda Library Plugin to parse and index Open Educational Resources (OERs)
    stored at the Portal do Professor - Ministério da Educação do Brasil.
    '''
    def __init__(self):
        # metas
        self.PLUGIN_NAME = u'Plugin Portal do Professor - Ministério da Educação'
        self.PLUGIN_SLUG = u'portaldoprofessor'
        self.AUTHOR = u'Duda Nogueira'
        self.EMAIL = u'dudanogueira@gmail.com'
        self.VERSION = 0.1
        # source infos
        self.SOURCE_URL = u"http://portaldoprofessor.mec.gov.br/"
        self.SOURCE_SLUG = u"portaldoprofessor.mec.gov.br"
        self.SOURCE_NAME = u"Portal do Professor (Ministério da Educação)"
        self.SOURCE_KNOWN_TOTAL = 11126
        self.SOURCE_ITEMS_PER_PAGE = 100
        self.SOURCE_TOTAL_PAGES = self.SOURCE_KNOWN_TOTAL / self.SOURCE_ITEMS_PER_PAGE
        self.BASE_URL = u'http://portaldoprofessor.mec.gov.br/fichaTecnica.html?id='
        self.resource = None
    
    def text_sanitizer(self, value):
        value = value.replace("&#034;", '"').replace("&#039;", "'")
        return value
    
    
    def identify(self, url):
        '''return True if the url belongs to this Parser
        considering this Source (Portal do Professor), the url can be both:
        38294@portaldoprofessor.mec.gov.br
        or
        http://portaldoprofessor.mec.gov.br/fichaTecnica.html?id=38294    
        '''
        # define infos for testing
        # test 1234@source.org
        self.url = url
        if self.url.find('@') != -1:
            bits = self.url.split('@')
            try:
                # its a valid integer
                self.reference_id = int(bits[0])
                # second part of @ matches with source_slug
                if bits[1] == self.SOURCE_SLUG:
                    self.resource_slug = bits[1]
                    self.identifier_id = '%s@%s' % (self.reference_id, self.resource_slug)
                    self.identified = True
                    self.full_url = "%s%s" % (self.BASE_URL, self.reference_id)
            except:
                self.identified = False
        # test the others
        else:
            try:
                bits = self.url.split(self.BASE_URL)
                self.resource_slug = self.SOURCE_SLUG
                self.reference_id = int(bits[1])
                self.identifier_id = '%s@%s' % (self.reference_id, self.resource_slug)
                self.identified = True
                self.full_url = "%s%s" % (self.BASE_URL, self.reference_id)
            except:
                self.identified = False
    
    def parse(self, url=None):
        '''identify and parse the url into a registered Resource Object'''
        if url:
            self.url = url
        # parse already try to identify
        self.identify(url)
        if(self.identified):
            f = urllib.urlopen(self.full_url)
            s = f.read()
            f.close()
            self.soup = BeautifulSoup(s)
            # identifiers
            self.resource_reference_string = self.identifier_id
            # rejected resource. Not parsing
            try:
                # some preparing
                self.ficha = self.soup.find('div', id="ficha_recurso")
                self.link = self.soup.find('a', id="link_visualizar_recurso")
                #
                # TITLE
                #
                try:
                    self.title = self.soup.h3.text
                except:
                    self.title = ''
                self.title = self.text_sanitizer(self.title)
                #
                # TRIGGER
                #
                try:
                    self.trigger = self.link.attrs[2][1].split("/")[-1].split("?")[0]
                    self.trigger_extension = self.trigger.rsplit('.')[-1]
                except:
                    self.trigger = ''
                    self.trigger_extension = ''            
                #
                # LANGUAGE
                #
                try:
                    self.language_listed = self.ficha.table.contents[3].contents[1].text.lower()
                except:
                    self.language_listed = ''
                self.resource_language = self.language_listed
                if self.language_listed.find("port") == 0:
                    self.language,self.language_created = Language.objects.get_or_create(code='pt-br')
                elif self.language_listed.find("ingl") == 0:
                    self.language,self.language_created = Language.objects.get_or_create(code='en')
                elif self.language_listed.find("espa") == 0:
                    self.language,self.language_created = Language.objects.get_or_create(code='es')
                else:
                    self.language,self.language_created = Language.objects.get_or_create(code='na')
                #
                # FILENAME
                # 
                try:
                    self.direct_link = self.soup("a", {'class': 'download_recurso'})[0].attrs[2][1]
                    self.filename = urllib.unquote(str(self.direct_link.split('?')[0].split('/')[-1]))
                except:
                    self.direct_link = ''
                    self.filename = ''
                # category
                self.imgs = self.soup.findAll('img')
                for img in self.imgs:
                    if img['src'].find('img/ico_') != -1:
                        self.img = img
                        self.cat = img['src'].split('img/ico_')[1].split('.')[0]
                        try:
                            self.category = Category.objects.get(pk=CATEGORY_DICT[self.cat])
                        except:
                            raise
                            self.category = ""
                    
                # other stuff
                z = {}
                ref = 'data'
                self.structure = []
                self.estrutura = ''
                self.authors = []
                self.autors = ''
                if self.ficha and self.ficha.contents:
                    for i in self.ficha.contents:
                        if i != '\n' and '[if IE]' not in i:
                            if i.name == 'h5' or i.name == 'p' or i.name == 'a':  
                                if i.name == 'h5':
                                    ref = i.text
                                else:
                                    if ref == 'Estrutura curricular':
                                        self.structure.append("%s\n" % i.text)
                                    if ref == 'Autor' or ref =='Autores':
                                        self.authors.append("%s\n" % i.text)
                                    z[ref] = i.text
                for es in self.structure:
                    self.estrutura += es
                self.estrutura = self.estrutura.strip()
                self.authors = ''.join(self.authors).strip()
                self.objective = z['Objetivo']
                self.description = z['Descri&ccedil;&atilde;o']
                try:
                    self.notes = z['Observa&ccedil;&atilde;o']
                except:
                    self.notes = ''
                try:
                    self.source = z['Fonte do recurso']
                except:
                    self.source = ''
                try:
                    self.origin = z['Origem']
                except:
                    self.origin = ''
                try:
                    self.resource_size = self.ficha.table.contents[3].td.next.next.next.text
                except:
                    self.resource_size = ''
                try:
                    self.resource_pageviews =  int(self.ficha.table.contents[3].contents[5].text)
                except:
                    self.resource_pageviews = ''
                try:
                    self.license = z['Licen&ccedil;a']
                except:
                    self.license = ''
                try:
                    a = z['data'].split()
                    data = "%s/%s/%s" % (a[2],a[1],a[-1])
                    c = time.strptime(data,"%d/%b/%Y")
                    self.published = time.strftime("%Y-%m-%d",c)
                except:
                    self.published = ''
                # get tags from structure
                tags = self.estrutura.strip()
                tags = tags.replace('|', ',').replace('::', ',').replace(':', ','
                    ).replace('/', ',').replace('\n', ',').replace(" e ", ',').replace(" e da ", ',').lower()
                tags = tags.split(',')
                tags = [t.strip() for t in tags]
                # some weird problems with big tags
                tags_short = []
                for tag in tags:
                    if len(tag) < 40:
                        tags_short.append(tag)
                # enJOIN them ;)
                tags = ",".join(tags)
                self.tags = tags
                self.parsed = True
                return self


            except:
                raise
                # error. Mark the resource with error
                self.parsed = False
                self.resource.status = 'error'
                self.resource.save()
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
            # identifier
            self.resource.reference_string = self.identifier_id
            self.resource.title = self.text_sanitizer(self.title)
            self.resource.structure = self.estrutura
            self.resource.tags = self.tags
            self.resource.objective = self.objective
            self.resource.description = self.text_sanitizer(self.description)
            self.resource.author = self.authors
            self.resource.notes = self.text_sanitizer(self.notes)
            self.resource.trigger = self.trigger
            self.resource.trigger_extension = self.trigger_extension
            self.resource.language = self.language
            self.resource.resource_download_url = self.direct_link
            self.resource.resource_downloaded_file = self.filename
            self.resource.resource_size = self.resource_size
            self.resource.resource_pageviews = self.resource_pageviews
            self.resource.language = self.language
            self.resource.license = self.license
            self.resource.content_source = self.resource.source.__unicode__()
            self.resource_language = self.language_listed
            self.resource.category.add(self.category)
            # save
            self.indexed = True
            self.resource.status = "installed"
            self.resource.enabled = True
            self.resource.save()
        else:
            print "ERROR. Not parsed"
    
    def download(self):
        if not self.resource:
            print "Error. Can't download. No Resource found. Try parsing and saving first."
        else:
            work_folder = os.path.dirname(smart_str(self.resource.content_root()))
            subprocess.call("mkdir -vp %s" % work_folder, shell=True)
            self.packed = False
            self.filename = urllib.unquote(str(self.resource.resource_download_url.split('?')[0].split('/')[-1]))
            self.basetarget = os.path.dirname(smart_str(self.resource.content_root()))
            self.wget_option_str = ''
            self.DOWNLOAD_LIMIT_RATE = getattr(settings, 'DOWNLOAD_LIMIT_RATE', None)
            if self.DOWNLOAD_LIMIT_RATE:
                self.wget_option_str = "--limit-rate=%s" % self.DOWNLOAD_LIMIT_RATE
            if 'zip' in self.filename or 'rar' in self.filename:
                self.packed = True
                self.download_source_folder = "%s/downloaded_source" % self.basetarget
                subprocess.call("mkdir -vp %s" % self.download_source_folder, shell=True)
                self.download_command = u'wget -c %s "%s" -O "%s/%s"' % (unicode(self.wget_option_str), unicode(self.resource.resource_download_url), unicode(self.download_source_folder), unicode(self.filename))
            else:
                self.download_command = u'wget -c %s "%s" -O "%s/%s"' % (smart_unicode(self.wget_option_str), smart_unicode(self.resource.resource_download_url), smart_unicode(self.basetarget), smart_unicode(self.filename))
            subprocess.call(self.download_command, shell=True)
            # if packed, unpack
            if self.packed:
                if 'zip' in self.filename:
                    if utils.find_program_path('unzip'):
                        self.unpack_command = "unzip -o '%s/%s' -d %s" % (self.download_source_folder, self.filename, self.basetarget)
                    else:
                        print "No Unzip tools found (unzip)"
                elif 'rar' in self.filename:
                    if utils.find_program_path('unrar'):
                        self.unpack_command = "unrar e -o+ '%s/%s' %s" % (self.download_source_folder, self.filename, self.basetarget)
                    elif utils.find_program_path('rar'):
                        self.unpack_command = "rar e -o+ '%s/%s' %s" % (self.download_source_folder, self.filename, self.basetarget)
                    else:
                        print "No Rar tools found (rar nor unrar)"
                #unpack, keeping the pack for reference
                subprocess.call(self.unpack_command, shell=True)
            # check files, paths, thumbnails, etc
            self.resource.check_files()
            self.resource.generate_thumb()

            
            