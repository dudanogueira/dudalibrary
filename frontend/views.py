# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.shortcuts import render_to_response, get_object_or_404, redirect

from django.template import RequestContext, loader, Context
from django.views.generic import ListView, DetailView

from django.utils.translation import ugettext_lazy as _

from resources.models import Resource, CustomResource
from queue.models import ResourceQueue
from queue.tasks import add_resource_to_queue
from django import forms
import django_filters
from dudalibrary.utils import get_query, resource_identifier
from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud, LOGARITHMIC
from ratings.forms.widgets import StarWidget
from ratings.forms import StarVoteForm
from ratings.handlers import ratings
from hitcount.models import HitCount
from curricular.models import CurricularGrade, Activity, ActivityItem, SubjectClass, Subject

from django.conf import settings

CONTENT_PER_PAGE = getattr(settings, 'CONTENT_PER_PAGE', 10)
TAGGING_RELATED_RESOURCE_LIST_NUM = getattr(settings, 'TAGGING_RELATED_RESOURCE_LIST_NUM', 10)

search_fields = ['description', 'title']

class AddCurricularClassForm(forms.ModelForm):
    class Meta:
        model = SubjectClass
        fields = ('title', 'description')

class AddSubjectClassForm(forms.ModelForm):
    class Meta:
        model = SubjectClass
        fields = ('title', 'description')

class AddSubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ('title', 'description')

class AddActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ('title', 'description')

class SearchForm(forms.Form):
    q = forms.CharField(max_length=300, label="", required=False)

class ResourcetFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super(ResourcetFilter, self).__init__(*args, **kwargs)
        self.filters['source'].extra.update(
            {'empty_label': u'All Sources'})
        self.filters['language'].extra.update(
            {'empty_label': u'All Languages'})            
    class Meta:
        model = Resource
        fields = ['source', 'category', 'language',]

def search_query_set(q):
    if q != '' and q != None:
        output = get_query(q, ['description', 'title'])
        return output
    else:
        return q

def tag_details(request, pk):
    tag = Tag.objects.get(pk=pk)
    qs = TaggedItem.objects.get_by_model(Resource, tag)
    qs = qs.filter(enabled=True).exclude(status='rejected')
    related_tags = Tag.objects.related_for_model(
        tag, Resource, counts=True)[0:20]
    # sort by ocurrence
    related_tags = sorted(related_tags, key=lambda tag: tag.count)
    related_tags.reverse()
    paginator = Paginator(qs, CONTENT_PER_PAGE)
    searchform = SearchForm(request.GET)
    pageid = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(pageid)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)
    object_list = page_obj.object_list
    return render_to_response('tag_details.html', locals(),
        context_instance=RequestContext(request),)
            
def resource_details(request, object_id):
    querystring = request.META.get('QUERY_STRING')
    try:
        query = request.GET['q']
    except:
        query = ''
    resource = get_object_or_404(Resource, id=object_id)
    related_resources = TaggedItem.objects.get_related(resource, Resource, num=TAGGING_RELATED_RESOURCE_LIST_NUM)
    module_name = resource._meta.module_name
    test = StarVoteForm(resource, 'main', score_range=(0,10), score_step=1)
    handler = ratings.get_handler(Resource)
    score = handler.get_score(resource, 'main')
    try:
        resource_actual_score = int(round(score.average, 0))
    except:
        resource_actual_score = 0
    app_label = resource._meta.app_label
    return render_to_response('resource_details.html', locals(),
        context_instance=RequestContext(request),)

@staff_member_required
def activity_details_request_resource(request, object_id):
    if request.POST:
        activity = Activity.objects.get(pk=object_id)
        raw_data = request.POST.get('resources_to_process', None)
        data = raw_data.splitlines()
        for line in data:
            item = resource_identifier(line)
            # check if item is identified
            if item and item.identified:
                # set order in activity
                try:
                    order = activity.activityitem_set.order_by('-order')[0].order + 1
                except:
                    order = 1
                # check if resource already exists
                try:
                    resource = Resource.objects.get(
                        resource_reference_string=item.identifier_id
                    )
                    # resource is installed, lets add to the activity
                    if resource.status == "installed":
                        contenttype = ContentType.objects.get_for_model(resource)
                        activity_item = ActivityItem.objects.create(
                            order=order,
                            content_type_id=contenttype.id,
                            object_id=resource.id,
                            activity=activity,
                        )
                        messages.success(request, u'O Recurso %s (ID: %s) Foi adicionado à atividade %s!' % (resource, item.identifier_id, activity))
                    elif resource.status == "rejected":
                        messages.error(request, u'<b>Error!</b> Rejected Resource!')
                except Resource.DoesNotExist:
                    # no resource found with this identifier,
                    # lets add to the queue                
                    # get or create a queue item
                    queue,created = ResourceQueue.objects.get_or_create(
                        identifier_id=item.identifier_id,
                        plugin_name=item.PLUGIN_NAME,
                        plugin_slug=item.PLUGIN_SLUG,
                        request_user=request.user,
                        full_url=item.full_url,
                    )
                    if created:
                        # create celery queue too
                        if getattr(settings, 'USE_CELERY', False):
                            add_resource_to_queue.delay(queue.id)
                        contenttype = ContentType.objects.get_for_model(queue)
                        # add activity item first
                        activity_item = ActivityItem.objects.create(
                            order=order,
                            content_type_id=contenttype.id,
                            object_id=queue.id,
                            activity=activity,
                        )
                        messages.info(request, u'<b>%s</b> foi identificado como pertencendo ao %s e Adicionado à Lista de Downloads' % (item.identifier_id, item.SOURCE_NAME))
                    else:
                        messages.info(request, u'<b>Informação!</b>! %s Já está na Lista de Download' % item.identifier_id)                
            else:
                messages.warning(request, u'<b>Atenção!</b>! %s Não identificado!' % (line))
    return redirect(reverse("activity_details", args=[object_id]))

def index(request):
    searchform = SearchForm(request.GET)
    tagcloud = Tag.objects.cloud_for_model(Resource)
    qs = Resource.objects.filter(enabled=True).exclude(status='rejected')
    query = request.GET.get('q', None)
    if  query != None:
        if query != '':
            qs = qs.filter(
                search_query_set(query)
            )
        else:
            blankquery = True
        qsfiltered = ResourcetFilter(request.GET, queryset=qs)
        filter_form = qsfiltered.form
        objects = []
        [objects.append(item) for item in qsfiltered]
        # treat querystring, remove page
        querystring = QueryDict(request.META.get('QUERY_STRING'))
        # handle pagination
        if 'page' in request.GET:
            pageid = request.GET.get('page')
            if pageid:
                querystring._mutable = True
                del querystring['page']
            querystring_nopage = querystring.urlencode()
        else:
            pageid = 1
            querystring_nopage = request.META.get('QUERY_STRING')

        paginator = Paginator(objects, CONTENT_PER_PAGE)

        try:
            page_obj = paginator.page(pageid)
        except TypeError:
            page_obj = paginator.page(1)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        object_list = page_obj.object_list
        return render_to_response('index.html', locals(),
            context_instance=RequestContext(request),)
        
    else:
        # browse mode
        # featured list
        curricular_grades = CurricularGrade.objects.filter(parent=None)
        featured_list = qs.filter(
                #category__code='video', thumbnails__gt=0
            ).order_by("?").all()[0:1]
        if featured_list.count() > 0:
            featured_list = featured_list.all()
        qsfiltered = ResourcetFilter(request.GET, queryset=qs)
        filter_form = qsfiltered.form
        # top pageviews
        resource_type = ContentType.objects.get(app_label="resources", model="resource")
        hit_list = HitCount.objects.filter(content_type=resource_type)[0:7]
        # top rated
        handler = ratings.get_handler(qs.model)
        top_qs = handler.annotate_scores(qs, 'main', 
                average='average', num_votes='num_votes').order_by('-average')[0:7]
        top_qs_list = []
        for resource_listed in top_qs:
            if resource_listed.average:
                top_qs_list.append(resource_listed)
        # tags
        tags_to_cloud = Tag.objects.usage_for_queryset(qs, counts=True,)#[0:20]
        calculate_cloud(tags_to_cloud, steps=5, distribution=LOGARITHMIC)
        query = ''
        # latest additions
        latest_additions = Resource.objects.filter(status="installed").order_by('-created')[0:5]
        return render_to_response('index.html', locals(),
            context_instance=RequestContext(request),)

def get_random_resource(request):
    try:
        r = Resource.objects.filter(enabled=True).exclude(
            status='rejected').order_by("?")[0]
        return redirect(r)
    except:
        return redirect(index)


class TopHitsView(ListView):
    template_name = "tophit_list.html"
    paginate_by = CONTENT_PER_PAGE*2    
    
    def get_queryset(self):
        resource_type = ContentType.objects.get(app_label="resources", model="resource")
        hit_objects = HitCount.objects.filter(content_type=resource_type)
        return hit_objects
    
    def get_context_data(self, **kwargs):
        context = super(TopHitsView, self).get_context_data(**kwargs)
        featured_list = Resource.objects.filter(
                enabled=True, featured=True
            ).exclude(status='rejected')
        context['featured_list'] = featured_list
        context['searchform'] = SearchForm()
        return context

class TopVotesView(TopHitsView):
    template_name = "topvoted_list.html"
    paginate_by = CONTENT_PER_PAGE*2

    def get_queryset(self):
        qs = Resource.objects.filter(enabled=True).exclude(status='rejected')
        handler = ratings.get_handler(Resource)
        top_qs = handler.annotate_scores(qs, 'main', 
                average='average', num_votes='num_votes').order_by('-average')
        objects = []
        for i in top_qs:
            if i.average != None and i.average != "":
                objects.append(i)
        return objects

def add_custom(request):
    ''' this is a admin view'''
    if request.GET:
        urls = request.GET.get('urls', '')
        analyze_items = urls.splitlines()
        report = []
        for url in analyze_items:
            cr = CustomResource(url)
            cr.get_model_object()
            cr.download()
            cr.intake()
            report.append(cr)
    return render_to_response('add_custom_resource.html', locals(),
        context_instance=RequestContext(request),)

def activity_details(request, object_id):
    activity = get_object_or_404(Activity, id=object_id)
    curricular_grades = CurricularGrade.objects.filter(parent=None)
    return render_to_response('activity_details.html', locals(),
        context_instance=RequestContext(request),)

def curricular_add_activity(request, curricular_id, class_id, subject_id):
    curricular_grade = get_object_or_404(CurricularGrade, id=curricular_id)
    curricular_class = get_object_or_404(SubjectClass, id=class_id)
    curricular_subject = get_object_or_404(Subject, id=subject_id)

    if request.POST:
        form = AddActivityForm(request.POST)
        if form.is_valid():
            new_activity = form.save(commit=False)
            new_activity.subject = curricular_subject
            new_activity.save()
            return redirect(reverse("activity_details", args=[new_activity.id]))
        
    else:
        form = AddActivityForm()
    return render_to_response('curricular_add_activity.html', locals(),
        context_instance=RequestContext(request),)

def curricular_activity_select_add_subject(request, curricular_id, class_id):
    curricular_grade = get_object_or_404(CurricularGrade, id=curricular_id)
    curricular_class = get_object_or_404(SubjectClass, id=class_id)
    subjects = Subject.objects.filter(subject_class=curricular_class)
    form = AddSubjectClassForm()
    if request.POST:
        form = AddSubjectForm(request.POST)
        if form.is_valid():
            new_subject = form.save(commit=False)
            new_subject.curricular_grade = curricular_grade
            new_subject.subject_class = curricular_class
            new_subject.save()
            return redirect(reverse('curricular_add_activity', args=[curricular_grade.id, curricular_class.id, new_subject.id]))

    return render_to_response('curricular_activity_select_add_subject.html', locals(),
        context_instance=RequestContext(request),)
    

def get_curricular_grade(request, object_id):
    curricular_grade = get_object_or_404(CurricularGrade, id=object_id)
    add_curricular_class_form = AddCurricularClassForm()
    if request.POST:
        form_class = AddCurricularClassForm(request.POST)
        if form_class.is_valid():
            new_curricular_class = form_class.save(commit=False)
            new_curricular_class.curricular_grade = curricular_grade
            new_curricular_class.user = request.user
            new_curricular_class.save()
            messages.success(request, _(u'<b>Success!</b> Curricular Class %s Added' % new_curricular_class.title))
        else:
            messages.error(request, _(u'<b>Error!</b> Curricular Class NOT Added'))
            
    return render_to_response('curricular_grade_details.html', locals(),
        context_instance=RequestContext(request),)
