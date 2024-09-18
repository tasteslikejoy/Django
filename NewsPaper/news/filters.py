import django_filters
from django.forms import DateInput
from django_filters import FilterSet, DateFilter
from .models import Post

class NewFilter(FilterSet):
    add_post = DateFilter(
        field_name='add_post',
        widget=DateInput(attrs={'type': 'date'}),
        label='Date',
        lookup_expr='date__exact'
    )
    class Meta:
        model = Post
        fields = {
            'title_post': ['icontains'],
            'author_one_to_many': ['exact'],
        }
