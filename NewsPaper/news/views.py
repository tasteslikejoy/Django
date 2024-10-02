import random
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.core.mail import send_mail, EmailMultiAlternatives, mail_admins
from datetime import datetime
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import PermissionRequiredMixin
from .filters import *
from .forms import *
from .models import *



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
    template_name = 'categorydetail.html'
    context_object_name = 'categorydetail'
    # pk_url_kwarg = 'id' меняет название pk на id в файле news\urls.py

    def get_queryset(self):
        return Category.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['news_list'] = Post.objects.filter(category_many_to_many=category)
        return context


class NewsPost(ListView):
    model = Post
    ordering ='add_post'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 5


class NewsDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        category = post.category_many_to_many.all()
        if post.category_many_to_many:
            context['category_name'] = category
        else:
            context['category_name'] = None
        return context

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

        if self.request.path == '/post/post/create/':
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
    permission_required = ('news.add_post',)

class PostDelete(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    permission_required = ('news.add_post',)

class PostSearch(ListView):
    model = Post
    template_name = 'post_search.html'
    paginate_by = 5
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


class AppointmentView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'appointment/make_appointment.html', {})

    def post(self, request, *args, **kwargs):
        appointment = Appointment(
            appointment_date=datetime.strptime(request.POST['appointment_date'], '%Y-%m-%d'),
            appointment_name=request.POST['appointment_name'],
            appointment_message=request.POST['appointment_message']
            )
        appointment.save()

        # получаем html
        html_content = render_to_string (
            'appointment/appointment_created.html',
            {'appointment':appointment},
        )

        # отправляем сообщение
        msg = EmailMultiAlternatives(
            subject=f'{appointment.appointment_name} '
                    f'{appointment.appointment_date.strftime('%Y-%M-%d')}',
            body=appointment.appointment_message,
            from_email='alisa2196@mail.ru',
            to=['ru00012r@gmail.com',]
        )

        msg.attach_alternative(html_content, 'text/html')
        msg.send()

        # отправляет сообщение всем админам, получателя указывать не нужно, это будут все админы
        # из settings
        # mail_admins(
        #     subject=f'{appointment.appointment_name}'
        #             f'{appointment.appointment_date.strftime('%d %m %Y')}',
        #     message=appointment.appointment_message,
        # )

        # отправляем письмо
        # send_mail(
        #     subject=f'{appointment.appointment_name}'
        #             f'{appointment.appointment_date.strftime('%Y-%M-%d')}',
        #     message=appointment.appointment_message,
        #     from_email='alisa2196@mail.ru',
        #     recipient_list=['ru00012r@gmail.com',
        #                     'dastlerz2405@gmail.com', ],
        #     fail_silently=True
        # )

        return redirect('appointment_form:appointment_form')


class NewsPostRandom(ListView):
    model = Post
    ordering ='add_post'
    template_name = 'flatpages/inc.html'
    context_object_name = 'news'

    def get_queryset(self):
        return  list(Post.objects.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news_list = self.get_queryset()

        if news_list:
            context['random_news'] = random.choice(news_list)
        else:
            context['random_news'] = None
        return context


@login_required
def add_subscribers(request, pk):
    user = request.user
    category = get_object_or_404(Category, id=pk)

    if user in category.subscribers.all():
        message = 'Вы уже подписаны на эту категорию: '
    else:
        category.subscribers.add(user)
        message = 'Вы подписались на рассылку новостей: '

    return render(request, 'subscribe.html', {'category': category, 'message': message})





