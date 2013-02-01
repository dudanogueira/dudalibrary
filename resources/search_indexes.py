import datetime
from haystack import indexes
from haystack import site
from resources.models import Resource

class ResourceIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    objectives = indexes.CharField(model_attr='objective')
    author = indexes.CharField(model_attr='author')
    
    def get_model(self):
            return Resource
    
    
    def index_queryset(self):
            """Used when the entire index for model is updated."""
            return self.get_model().objects.filter(created__lte=datetime.datetime.now())

site.register(Resource, ResourceIndex)