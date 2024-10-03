from datetime import datetime
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Post, Category

@shared_task
def add_new_news(pk):
    post = Post.objects.get(pk=pk)
    categories = post.category_many_to_many.all()
    subscribers_list = []

    for c in categories:
        subscribers = c.subscribers.all()
        subscribers_list += [s for s in subscribers]

    for s in subscribers_list:
        sub_name = s.username
        sub_email = [s.email]

        html_content = render_to_string(
            'new_post.html',
            {
                'text': post.preview(),
                'link': f'http://127.0.0.1:8000/post/{pk}',
                'sub_name': sub_name
            }
        )
        msg = EmailMultiAlternatives(
            subject=post.title,
            body='',
            from_email='alisa2196@mail.ru',
            to=sub_email
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

@shared_task
def weekly_news():

    today = timezone.now()
    time_mail = today - datetime.timedelta(days=7)
    emails = set(Post.objects.filter(add_post__gte=time_mail).values_list('category_many_to_many__subscribers__email', flat=True))
    categories = set(Category.objects.values_list('name_category', flat=True))
    post = Post.objects.filter(add_post__gte=time_mail)

    html_content = render_to_string(
        'dailynews.html',
        {
            'categories': categories,
            'post':post,
            'link':'http://127.0.0.1:8000/post/',
         },
    )

    msg = EmailMultiAlternatives(
        subject='Еженедельная сводка',
        body='',
        from_email='alisa2196@mail.ru',
        to=emails
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()