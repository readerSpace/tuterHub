from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from tutoring.ai_client import AIServiceError, call_ai_lesson_feedback
from tutoring.models import LessonReport


def build_parent_comment(report):
    if report.parent_comment:
        return report.parent_comment

    if not settings.ENABLE_AI_PARENT_COMMENT:
        return 'None'

    try:
        payload = {
            'student_name': report.lesson.student.full_name,
            'subject': report.lesson.subject,
            'lesson_content': report.content,
            'understanding_level': report.understanding_level,
            'teacher_note': report.next_plan or '次回の学習計画を継続して進めます。',
        }
        response = call_ai_lesson_feedback(payload)
        return response.get('feedback') or 'None'
    except AIServiceError:
        return 'None'


@shared_task
def send_lesson_report_notification(report_id):
    report = LessonReport.objects.select_related('lesson__student__parent').get(pk=report_id)
    parent = report.lesson.student.parent
    parent_comment = build_parent_comment(report)

    if not parent or not parent.email:
        return 'skipped'

    subject = f'TutorHub lesson report: {report.lesson.student.full_name}'
    message = (
        f'Student: {report.lesson.student.full_name}\n'
        f'Subject: {report.lesson.subject}\n'
        f'Understanding: {report.understanding_level}/5\n\n'
        f'Lesson content:\n{report.content}\n\n'
        f'Homework:\n{report.homework or "None"}\n\n'
        f'Next lesson plan:\n{report.next_plan or "None"}\n\n'
        f'Comment to parent:\n{parent_comment}'
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[parent.email],
        fail_silently=True,
    )
    return parent.email