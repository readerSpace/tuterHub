from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from tutoring.models import LessonReport
from tutoring.tasks import send_lesson_report_notification


@receiver(post_save, sender=LessonReport)
def notify_parent_on_new_report(sender, instance, created, **kwargs):
    if created and settings.ENABLE_ASYNC_NOTIFICATIONS:
        send_lesson_report_notification.delay(instance.pk)