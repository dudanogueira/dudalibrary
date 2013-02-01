# -*- coding: utf-8 -*-
# TODO: better logger
import sys, time, urllib, random, subprocess, os, settings
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from optparse import make_option
from options.models import Source, Category, Language
from BeautifulSoup import BeautifulSoup
from resources.models import Resource
from utils import folder_size, getLength, find_program_path

SOURCE_ID = 2
SOURCE_URL = "http://portaldoprofessor.mec.gov.br/"
SOURCE_SLUG = "portaldoprofessor.mec.gov.br"
SOURCE_NAME = "Portal do Professor (MEC)"
SOURCE_KNOWN_TOTAL = 11126
SOURCE_ITEMS_PER_PAGE = 100
SOURCE_TOTAL_PAGES = SOURCE_KNOWN_TOTAL / SOURCE_ITEMS_PER_PAGE


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
logger = logging.getLogger('portaldoprofessor.py')
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

print #*10
print "LOG FILE", LOG_FILE
print #*10

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

def text_sanitizer(value):
    value = value.replace("&#034;", '"').replace("&#039;", "'")
    return value

def downloader(urltodownload, basetarget, filename):
    '''download file to basefolder/downloaded_source if packed, and unpack to basefolder'''
    packed = False
    option_str = ''
    DOWNLOAD_LIMIT_RATE = getattr(settings, 'DOWNLOAD_LIMIT_RATE', None)
    if DOWNLOAD_LIMIT_RATE:
        option_str = "--limit-rate=%s" % DOWNLOAD_LIMIT_RATE
    if 'zip' in filename or 'rar' in filename:
        packed = True
        #created downloaded_source dir in filetarget folder
        download_source_folder = "%s/downloaded_source" % basetarget
        subprocess.call("mkdir -vp %s" % download_source_folder, shell=True)
        dlcmd = 'wget -c %s "%s" -O "%s/%s"' % (option_str, urltodownload, download_source_folder, filename)
    else:
        dlcmd = 'wget -c %s "%s" -O "%s/%s"' % (option_str, urltodownload, basetarget, filename)

    logger.info(">>>> %s" % dlcmd)
    
    subprocess.call(dlcmd, shell=True)
    if packed:
        if 'zip' in filename:
            if find_program_path('unzip'):
                cmd = "unzip -o '%s/%s' -d %s" % (download_source_folder, filename, basetarget)
            else:
                logger.error("No Unzip tools found (unzip)")
        elif 'rar' in filename:
            if find_program_path('unrar'):
                cmd = "unrar e -o+ '%s/%s' %s" % (download_source_folder, filename, basetarget)
            elif find_program_path('rar'):
                cmd = "rar e -o+ '%s/%s' %s" % (download_source_folder, filename, basetarget)
            else:
                logger.error("No Rar tools found (rar nor unrar)")
        logger.info("unpacking... %s" % cmd)
        #unpack, keeping the pack for reference
        subprocess.call(cmd, shell=True)

class PortalDoProfessorItem:
    def __init__(self, resource, created=False):
        logger.info("fetching individual... %s" % resource.resource_url)
        f = urllib.urlopen(resource.resource_url)
        s = f.read()
        f.close()
        logger.info("parsing...")
        soup = BeautifulSoup(s)
        self.soup = soup
        self.resource = resource
        self.title = resource.title
        self.structure = resource.structure
        self.objective = resource.objective
        self.language = resource.language
        self.category = resource.category
        self.resource_url = resource.resource_url

    def parse(self):
        self.status = 'processing...'
        ficha = self.soup.find('div', id="ficha_recurso")
        link = self.soup.find('a', id="link_visualizar_recurso")
        try:
            trigger = link.attrs[2][1].split("/")[-1].split("?")[0]
            trigger_extension = trigger.rsplit('.')[-1]
        except:
            trigger = ''
            trigger_extension = ''            
        try:
            language_listed = ficha.table.contents[3].contents[1].text.lower()
        except:
            language_listed = ''
        self.resource_language = language_listed
        # TODO: needs improvement
        if language_listed.find("port") == 0:
            language,created = Language.objects.get_or_create(code='pt-br')
        elif language_listed.find("ingl") == 0:
            language,created = Language.objects.get_or_create(code='en')
        elif language_listed.find("espa") == 0:
            language,created = Language.objects.get_or_create(code='es')
        else:
            language,created = Language.objects.get_or_create(code='na')
        try:
            direct_link = self.soup("a", {'class': 'download_recurso'})[0].attrs[2][1]
            filename = urllib.unquote(str(direct_link.split('?')[0].split('/')[-1]))
        except:
            direct_link = ''
            filename = ''
        z = {}
        ref = 'data'
        structure = []
        estrutura = ''
        authors = []
        autors = ''
        if ficha and ficha.contents:
            for i in ficha.contents:
                if i != '\n' and '[if IE]' not in i:
                    if i.name == 'h5' or i.name == 'p' or i.name == 'a':  
                        if i.name == 'h5':
                            ref = i.text
                        else:
                            if ref == 'Estrutura curricular':
                                structure.append("%s\n" % i.text)
                            if ref == 'Autor' or ref =='Autores':
                                authors.append("%s\n" % i.text)
                            z[ref] = i.text

        for es in structure:
            estrutura += es
        estrutura = estrutura.strip()
        authors = ''.join(authors).strip()
        try:
            notes = z['Observa&ccedil;&atilde;o']
        except:
            notes = ''
        try:
            source = z['Fonte do recurso']
        except:
            source = ''
        try:
            origin = z['Origem']
        except:
            origin = ''
        try:
            resource_size = ficha.table.contents[3].td.next.next.next.text
        except:
            resource_size = ''
        try:
            resource_pageviews =  int(ficha.table.contents[3].contents[5].text)
        except:
            resource_pageviews = ''
        try:
            license = z['Licen&ccedil;a']
        except:
            license = ''
        try:
            a = z['data'].split()
            data = "%s/%s/%s" % (a[2],a[1],a[-1])
            c = time.strptime(data,"%d/%b/%Y")
            published = time.strftime("%Y-%m-%d",c)
        except:
            published = ''
        # get tags from structure
        tags = estrutura.strip()
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
        # mount class
        try:
            self.title = self.soup.h3.text
        except:
            self.title = ''
        self.structure = estrutura
        self.tags = tags
        self.objective = z['Objetivo']
        self.description = z['Descri&ccedil;&atilde;o']
        self.author = authors
        self.notes = notes
        self.content_source = source
        self.license = license
        self.published = published
        # will be get after download and unzip
        self.size = 0
        self.trigger = trigger
        self.trigger_extension = trigger_extension
        self.language = language
        self.resource_download_url = direct_link
        self.resource_downloaded_file = filename
        self.resource_size = resource_size
        self.resource_pageviews = resource_pageviews
        self.language = language
        
    def download(self):
        r = self.resource
        work_folder = os.path.dirname(smart_str(r.content_root()))
        logger.info("creating dir")
        subprocess.call("mkdir -vp %s" % work_folder, shell=True)
        # run downloader
        urltodownload = str(r.resource_download_url)
        basetarget = str(work_folder)
        downloader(urltodownload, basetarget, str(r.resource_downloaded_file))
        # try to create
        if r.category.filter(code='video'):
            try:
                r.generate_thumb()
            except:
                pass
        elif r.category.filter(code='audio'):
            try:
                seconds = getLength(r.content_root())
                r.duration = seconds
            except:
                pass
        else:
            pass

    def save(self):
        self.resource.title = self.title
        self.resource.structure = self.structure
        self.resource.objective = self.objective
        self.resource.description = text_sanitizer(self.description)
        self.resource.language = self.language
        self.resource.resource_language = self.resource_language
        self.resource.author = self.author
        self.resource.notes = self.notes
        self.resource.content_source = self.content_source
        self.resource.license = self.license
        self.resource.published = self.published
        self.resource.trigger = self.trigger
        self.resource.trigger_extension = self.trigger_extension
        self.resource.resource_url = self.resource_url
        self.resource.resource_download_url = self.resource_download_url
        self.resource.resource_downloaded_file = self.resource_downloaded_file
        self.resource.resource_size = self.resource_size
        self.resource.resource_pageviews = self.resource_pageviews
        # gently fail
        try:
            self.resource.tags = self.tags
            self.resource.save()
        except:
            try:
                self.resource.force_tags(self.tags)
                self.resource.save()
            except:
                self.resource.tags = ''
                self.resource.save()

    def finish(self):
        self.resource.enabled = True
        self.resource.status = 'installed'
        self.resource.save()
        self.resource.check_files()

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
        if args:
            try:
                start,finish = args[0].split(',')
            except:
                pass
        else:
            start,finish = 1,SOURCE_TOTAL_PAGES
        sync = options.get('sync')
        get = options.get('get')
        nodownload = options.get('nodownload')
        force_download = options.get('force_download')
        range_values = options.get('range_values')
        if get:
            grids = get[0].split(",")
            for grid in grids:
                print "GRID:",grid
                resource = Resource.objects.get(pk=grid)
                resourceitem = PortalDoProfessorItem(resource, False)
                print "GRID TITLE: %s" % resourceitem.title
                resourceitem.download()                
        if sync:
            # try to get the source from database
            source, created = Source.objects.get_or_create(pk=SOURCE_ID, url=SOURCE_URL, slug=SOURCE_SLUG, name=SOURCE_NAME)
            logger.info("Source created? %s" %created)
            print "TOTAL PAGES: %s" % SOURCE_TOTAL_PAGES
            all_pages = range(SOURCE_TOTAL_PAGES)
            #all_pages.reverse()
            for page in all_pages[int(start):int(finish)]:
                logger.info("PAGE %s" % page)
                url = "http://portaldoprofessor.mec.gov.br/recursos.html?pagina=%s&tamanhoPagina=%s&ajax" % (page, SOURCE_ITEMS_PER_PAGE)
                logger.info("hitting %s" % url)
                f = urllib.urlopen(url)
                s = f.read()
                f.close()
                logger.info("parsing...")
                print "parsing..."
                soup = BeautifulSoup(s)
                in_page_items = len(soup.findAll('tr'))
                logger.info("IN_PAGE_ITEMS: %s" % in_page_items)
                # for each individual resource
                i = 0
                for resource_item in range(1,in_page_items):
                    logger.info("#######"*4)
                    try:
                        id = soup('tr')[resource_item].first('a').attrs[0][1].split('=')[1]
                        cat = soup('tr')[resource_item].findAll('img')[0].attrs[0][1].split("/")[1].split("_")[1].split(".")[0]
                    except:
                        id = "error%s" % i
                        i += 1
                        cat = ''
                    # resource informations
                    resource_url = "%sfichaTecnica.html?id=%s" % (SOURCE_URL, id)
                    resource,created = Resource.objects.get_or_create(
                        resource_reference_string=id, source=source, resource_url=resource_url
                    )
                    first_status = resource.status
                    logger.info("Created? %s" % created)
                    logger.info("DBITEM? %s" % resource.pk)
                    logger.info("PAGE? %s" % page)
                    logger.info("FIRST STATUS: %s" % first_status)
                    try:
                        category_object = Category.objects.get(pk=CATEGORY_DICT[cat])
                    except:
                        category_object = ""
                    if resource.status != 'installed' and resource.status != 'downloaded' and resource.status != 'error':
                        resource.status = "processing"
                    # START CLASS
                    r = PortalDoProfessorItem(resource, created)
                    r.parse()
                    logger.info("TITLE: %s" % r.title)
                    try:
                        r.resource.category.add(category_object)
                    except:
                        pass
                    try:
                        r.save()
                    except Exception, e:
                        logger.error('ERROR PARSING ID: %d', r.resource.pk)
                        r.resource.status = 'error'
                        logger.error('EXCEPTION: %s', e)
                        # even here the tag field can be truncated
                        # and break the save
                        try:
                            r.save()
                        except Exception, e:
                            logger.error('EXCEPTION: %s', e)
                            r.resource.tags = ''
                            try:
                                r.resource.save()
                            except:
                                pass
                    if nodownload:
                        logger.info("NOT DOWNLOADING! STATUS: %s" % r.resource.status)
                    else:
                        if force_download or first_status != 'downloaded' and first_status != 'installed' and first_status != 'error':
                            try:
                                logger.info("FORCING DOWNLOAD? %s, FIRST STATUS: %s" % (force_download, first_status))
                                r.download()
                                r.resource.status = 'downloaded'
                                r.resource.save()
                                r.finish()
                            except Exception, e:
                                logger.error("ERROR DOWNLOADING")
                                logger.error('EXCEPTION: %s', e)
                                r.resource.status = 'error'
                                try:
                                    r.resource.save()
                                except Exception, e:
                                    logger.error('EXCEPTION: %s', e)
                                    logger.error("DEAD END")
                                    pass
                        else:
                            logger.info("-- CONTENT ALREADY MARKED AS DOWNLOADED")
                            r.size = folder_size(r.resource.content_root())
                            try:
                                r.save()
                            except: 
                                pass