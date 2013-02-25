import datetime
from haystack import indexes
from haystack import site
from curricular.models import Activity

class ActivityIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    subject = indexes.CharField(model_attr='subject__title')
    description = indexes.CharField(model_attr='description')
    
    def get_model(self):
            return Activity
    
    def index_queryset(self):
            """Used when the entire index for model is updated."""
            return self.get_model().objects.filter(created__lte=datetime.datetime.now())

site.register(Activity, ActivityIndex)