from datetime import date

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from tutoring.access import (
    filter_assignments_for_user,
    filter_lessons_for_user,
    filter_students_for_user,
)
from tutoring.models import Assignment, Lesson, Student


@api_view(['GET'])
@permission_classes([AllowAny])
def api_index(request):
    return Response(
        {
            'name': 'TutorHub API',
            'docs': request.build_absolute_uri('/api/docs/'),
            'schema': request.build_absolute_uri('/api/schema/'),
            'auth': {
                'token_obtain': request.build_absolute_uri('/api/auth/token/'),
                'token_refresh': request.build_absolute_uri('/api/auth/token/refresh/'),
                'me': request.build_absolute_uri('/api/auth/me/'),
            },
        }
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    if month_start.month == 12:
        next_month = date(month_start.year + 1, 1, 1)
    else:
        next_month = date(month_start.year, month_start.month + 1, 1)

    students_count = filter_students_for_user(Student.objects.all(), request.user).count()
    current_month_lessons_count = filter_lessons_for_user(Lesson.objects.all(), request.user).filter(
        start_time__date__gte=month_start,
        start_time__date__lt=next_month,
    ).count()
    pending_assignments_count = filter_assignments_for_user(Assignment.objects.all(), request.user).filter(
        status=Assignment.Status.PENDING
    ).count()

    return Response(
        {
            'students_count': students_count,
            'current_month_lessons_count': current_month_lessons_count,
            'pending_assignments_count': pending_assignments_count,
        }
    )