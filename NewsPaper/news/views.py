
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .filters import *
from .forms import *
from django.contrib.auth.mixins import PermissionRequiredMixin


class CategoryList(ListView):
    # модель, которую мы будем выводить
    model = Category
    # Поле для сортировки
    ordering = 'name_category'
    # Шаблон html
    template_name = 'categories.html'
    # Как обращаться в html
    context_object_name = 'categories'


class CategoryDetail(DetailView):
    model = Category
    template_name = 'post.html'
    context_object_name = 'post'
    # pk_url_kwarg = 'id' меняет название pk на id в файле news\urls.py


class NewsPost(ListView):
    model = Post
    ordering ='add_post'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10


class NewsDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'


def create_post(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/create/')

    return render(request, 'post_edit.html', {'form': form})


class PostCreate(PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == 'post/create':
            post.post_choice = 'post'
        else:
            post.post_choice = 'news'
        post.author_one_to_many = self.request.user.author
        post.save()
        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_update.html'


class PostDelete(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class PostSearch(ListView):
    model = Post
    template_name = 'post_search.html'
    paginate_by = 10
    context_object_name = 'news'
    ordering = '-add_post'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        if self.request.GET:
            context['has_results'] = self.filterset.qs.exists()
        else:
            context['has_results'] = False
        return context


