from django import forms
from .models import *


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title_post',
            'text_post',
            'category_many_to_many',
        ]

