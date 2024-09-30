from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from .models import *
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def register_user(created, instance, **kwargs):
    if created:
        subject = f'{instance.username}'
        message = f'Добро пожаловать {instance.username}! Спасибо за регистрацию!'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]

        send_mail(subject, message, from_email, recipient_list)


# @receiver(m2m_changed, sender=CategoryUser)
# @receiver(m2m_changed, sender=PostCategory)