import zipfile, os, re, fnmatch, subprocess, tempfile, shutil, urllib2
from django.db.models import Q
from itertools import islice, chain
from django.contrib.contenttypes.models import ContentType

from imp import load_source

from django.core import serializers

from django.conf import settings

from curricular.models import ActivityItem

import imp

human_size = lambda s:[(s%1024**i and "%.1f"%(s/1024.0**i) or str(s/1024**i))+x.strip() for i,x in enumerate(' KMGTPEZY') if s<1024**(i+1) or i==8][0]

keep_in_repo_after_install = getattr(settings, 'KEEP_IN_REPOSITORY_AFTER_INSTALL', True)

def find_program_path(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def getLength(filename, inseconds=True):
    '''get video legth'''
    extension_to_get_length = ('wmv', 'flv', 'avi', 'mov', 'mpg', 'mp4', 'vob', 'webm', 'mp3')
    if os.path.isfile(filename) and filename.split(".")[-1].lower() in extension_to_get_length:
        result = subprocess.Popen(["ffmpeg", '-i', filename],
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        duration = [x for x in result.stdout.readlines() if "Duration" in x]
        print "duration", duration
        d = duration[0].strip().split()[1]
        if inseconds:
            d = d.replace(".", ":").replace(",","").split(":")
            d = int(d[1])*60+int(d[2])
            return d
        else:
            return d

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    '''
    query_string = query_string.replace("'", '"')
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query | or_query
    return query
    
def zipdir(dir, zip_file):
    print "Zipping %s into %s" % (dir, zip_file)
    zip = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
    root_len = len(os.path.abspath(dir))
    for root, dirs, files in os.walk(dir):
        archive_root = os.path.abspath(root)[root_len:]
        for f in files:
            fullpath = os.path.join(root, f)
            archive_name = os.path.join(archive_root, f)
            print f
            zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
    zip.close()
    return zip_file
    

def folder_size(folder,inbytes=True):
    folder_size = 0
    for (path, dirs, files) in os.walk(folder):
      for file in files:
        filename = os.path.join(path, file)
        folder_size += os.path.getsize(filename)
    if inbytes:
        return folder_size
    else:
        return "%0.1f MB" % (folder_size/(1024*1024.0))

def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.
    from: http://code.activestate.com/recipes/499305-locating-files-throughout-a-directory-tree/
    '''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

def ImportItem(filepath, folder=settings.CONTENT_ROOT, delete_after=True, force=False):
    try:
        tmpfolder = tempfile.mkdtemp()
        #unzip
        unzipcommand = "unzip -o %s -d %s" % (filepath, tmpfolder)
        subprocess.call(unzipcommand, shell=True)
        # read json
        descriptor = "%s/descriptor.xml" % tmpfolder
        if os.path.isfile(descriptor):
            fl = open(descriptor)
            data = fl.read()
            #try:
            deserialized = serializers.deserialize("xml", data)
            a = []
            for r in deserialized: #its only one, but we need this
                r.object.pageviews = 0
                r.save()
                a.append(r)
            # content on db, copying
            dest = os.path.dirname(a[0].object.content_root())
            if not os.path.isdir(dest):
                try:
                    # trying to create
                    os.makedirs(dest)
                except OSError, err:
                    print "Dir exists or have no permission!"
                    # remove tmp
                    shutil.rmtree(tmpfolder)
                    raise
                    return False
            # copy from tmpfolder to dest
            copycommand = "cp -rvf %s/* %s" % (tmpfolder, dest)
            subprocess.call(copycommand, shell=True)
            # remove tmp
            shutil.rmtree(tmpfolder)
            if keep_in_repo_after_install:
                # keep/copy item into repository
                repo_path = os.path.dirname(a[0].object.repository_root())
                if not os.path.exists(repo_path):
                    subprocess.call("mkdir -vp %s" % repo_path, shell=True)
                cpcmd = "cp -rvf %s %s" % (filepath, repo_path)
                subprocess.call(cpcmd, shell=True)
            # remove installed file from installfolder ;)
            rmcommand = u"rm -v %s" % filepath
            subprocess.call(rmcommand, shell=True)
        return True
    except:
        raise
        return False

## labs ##
##
##  LABS LABS LABS
##

def text_sanitizer(value):
    value = value.replace("&#034;", '"').replace("&#039;", "'")
    return value

def activity_queued_item_delivery(queue, resource):
    '''this function receives a queue and a resource,
    finds related ActivityItem and change queueresource to resource'''
    # this resource belogs to this queue
    try:
        contenttype = ContentType.objects.get_for_model(queue)
        new_contenttype = ContentType.objects.get_for_model(resource)        
        # if there's a activity waiting for this resource...
        activity_items = ActivityItem.objects.filter(
            content_type=contenttype, object_id=queue.id
        )
        for activity_item in activity_items:
            activity_item.content_type = new_contenttype
            activity_item.object_id = resource.id
            activity_item.save()
        return True
    except ActivityItem.DoesNotExist:
        # activity doesnot exist, do nothing
        return False

def resource_identifier(url, plugin_slug=None, request=None):
    '''this function will rotate in all SOURCE_PLUGINS
    find a match and use the proper parser plugin'''
    try:
        plugin_module = __import__('source_plugins')
        if plugin_slug:
            available_plugins = (str(plugin_slug),)
        else:
            available_plugins = settings.SOURCE_PLUGINS
        print "PLUGINS:",settings.SOURCE_PLUGINS
        print "###" * 10
        print "URL: %s" % (url)
        for plugin_slug in available_plugins:
            print "---" * 10
            plugin_path = os.path.join(os.path.dirname(plugin_module.__file__), '%s.py' % plugin_slug)
            try:
                print plugin_path
                plugin_child = imp.load_source('source_plugins.%s' % plugin_slug, plugin_path)
                print "PLUGIN LOADED: %s" % plugin_slug
                parser = plugin_child.Parser()
                parser.has_internet = True
                parser.identify(url)
                if parser and parser.identified:
                    print "IDENTIFICADO: %s" % parser.identified
                    print "FULL URL: %s" % parser.full_url
                    parser.plugin_slug = plugin_slug
                    return parser
                    
            
            except urllib2.URLError:
                parser.has_internet = False
                print "NO INTERNET"

            except:
                print "Could not load %s" % parser.PLUGIN_NAME
                raise
                
    except:
        raise
        print "ERRO"
        