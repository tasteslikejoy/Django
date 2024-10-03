import datetime
from django.utils import timezone
import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import EmailMultiAlternatives
from news.models import Category, Post


logger = logging.getLogger(__name__)


def my_job():

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
            'link':settings.SITE_ID,
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


def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(
                day_of_week="sat", hour="10", minute="00"
            ),
            id = "my_job",
            max_instances = 1,
            replace_existing = True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="sat", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")