import datetime
import logging
from datetime import timezone, timedelta
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail, EmailMultiAlternatives
from news.models import Category, Post



logger = logging.getLogger(__name__)


def my_job():
    # send_mail(
    #     'Job mail',
    #     'hello from job!',
    #     from_email='alisa2196@mail.ru',
    #     recipient_list=['ru00012r@gmail.com'],
    # )

    today = datetime.datetime.now()
    time_mail = today - datetime.timedelta(days=7)

    post = Post.objects.filter(add_post__gte=time_mail)
    categories = list(Category.objects.values('name_category'))
    subscribers = list(Category.objects.filter(subscribers__in=categories).values_list('subscribers__email')) # related_name

    html_content = render_to_string(
        'dailynews.html',
        {
            'post':post,
            'link':settings.SITE_ID,
         }
    )

    msg = EmailMultiAlternatives(
        subject='Еженедельная сводка',
        body='',
        from_email='alisa2196@mail.ru',
        to=subscribers
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
            trigger=CronTrigger(second="*/10"),
            # trigger=CronTrigger(
            #     day_of_week="sat", hour="10", minute="00"
            # ),
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