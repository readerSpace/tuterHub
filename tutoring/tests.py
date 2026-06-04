import datetime as dt
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from tutoring.models import Assignment, Invoice, Lesson, Student


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def teacher():
    return User.objects.create_user(username='teacher', password='secret', role=User.Role.TEACHER)


@pytest.fixture
def other_teacher():
    return User.objects.create_user(username='other-teacher', password='secret', role=User.Role.TEACHER)


@pytest.fixture
def parent_user():
    return User.objects.create_user(username='parent', password='secret', role=User.Role.PARENT)


@pytest.fixture
def student_user():
    return User.objects.create_user(username='student', password='secret', role=User.Role.STUDENT)


@pytest.fixture
def student(teacher, parent_user, student_user):
    return Student.objects.create(
        user=student_user,
        full_name='Taro Test',
        grade='中3',
        school='Test Junior High',
        target_school='Science High',
        weak_subjects='Mathematics',
        teacher=teacher,
        parent=parent_user,
        guardian_contact='parent@example.com',
        notes='Needs weekly review.',
    )


def make_lesson(student, teacher, start_time, status):
    return Lesson.objects.create(
        student=student,
        teacher=teacher,
		subject='数学',
        start_time=start_time,
        end_time=start_time + dt.timedelta(hours=2),
        lesson_format=Lesson.Format.IN_PERSON,
        status=status,
    )


def test_teacher_only_sees_assigned_students(api_client, teacher, other_teacher, parent_user):
    Student.objects.create(
        full_name='Owned Student',
        grade='高1',
        school='North High',
        target_school='National University',
        weak_subjects='Physics',
        teacher=teacher,
        parent=parent_user,
        guardian_contact='owned@example.com',
        notes='',
    )
    Student.objects.create(
        full_name='Other Student',
        grade='高2',
        school='South High',
        target_school='City University',
        weak_subjects='Chemistry',
        teacher=other_teacher,
        parent=parent_user,
        guardian_contact='other@example.com',
        notes='',
    )

    api_client.force_authenticate(user=teacher)
    response = api_client.get('/api/students/')

    assert response.status_code == 200
    payload = response.json()
    assert payload['count'] == 1
    assert payload['results'][0]['full_name'] == 'Owned Student'


def test_student_cannot_create_student_record(api_client, student_user, teacher, parent_user):
    api_client.force_authenticate(user=student_user)
    response = api_client.post(
        '/api/students/',
        {
            'full_name': 'Blocked Student',
            'grade': '中2',
            'school': 'Central Junior High',
            'target_school': 'STEM High',
            'weak_subjects': 'English',
            'teacher': teacher.id,
            'parent': parent_user.id,
            'guardian_contact': 'blocked@example.com',
            'notes': 'Should not be created.',
        },
        format='json',
    )

    assert response.status_code == 403


def test_teacher_can_create_student_without_teacher_field(api_client, teacher):
    api_client.force_authenticate(user=teacher)
    response = api_client.post(
        '/api/students/',
        {
            'full_name': 'Teacher Owned Student',
            'grade': '高1',
            'school': 'North High',
            'target_school': 'National University',
            'weak_subjects': 'Physics',
            'guardian_contact': 'owner@example.com',
            'notes': 'Created without explicit teacher field.',
        },
        format='json',
    )

    assert response.status_code == 201
    assert response.json()['teacher'] == teacher.id
    assert Student.objects.get(id=response.json()['id']).teacher == teacher


def test_teacher_can_create_lesson_without_teacher_field(api_client, teacher, student):
    api_client.force_authenticate(user=teacher)
    start_time = timezone.make_aware(dt.datetime(2026, 6, 12, 18, 0))
    end_time = start_time + dt.timedelta(hours=2)

    response = api_client.post(
        '/api/lessons/',
        {
            'student': student.id,
            'subject': '英語',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'lesson_format': Lesson.Format.ONLINE,
            'status': Lesson.Status.SCHEDULED,
        },
        format='json',
    )

    assert response.status_code == 201
    assert response.json()['teacher'] == teacher.id
    assert Lesson.objects.get(id=response.json()['id']).teacher == teacher


def test_teacher_can_create_assignment_without_teacher_field(api_client, teacher, student):
    api_client.force_authenticate(user=teacher)
    response = api_client.post(
        '/api/assignments/',
        {
            'student': student.id,
            'title': 'Worksheet review',
            'description': 'Review the previous lesson exercises.',
            'due_date': '2026-06-20',
            'status': 'pending',
            'teacher_comment': 'Focus on the weak areas first.',
        },
        format='json',
    )

    assert response.status_code == 201
    assert response.json()['teacher'] == teacher.id
    assert Assignment.objects.get(id=response.json()['id']).teacher == teacher


def test_invoice_auto_calculates_completed_lessons(student, teacher):
    completed_1 = timezone.make_aware(dt.datetime(2026, 6, 3, 18, 0))
    completed_2 = timezone.make_aware(dt.datetime(2026, 6, 10, 18, 0))
    scheduled = timezone.make_aware(dt.datetime(2026, 6, 17, 18, 0))

    make_lesson(student, teacher, completed_1, Lesson.Status.COMPLETED)
    make_lesson(student, teacher, completed_2, Lesson.Status.COMPLETED)
    make_lesson(student, teacher, scheduled, Lesson.Status.SCHEDULED)

    invoice = Invoice.objects.create(
        student=student,
        month=dt.date(2026, 6, 15),
        unit_price=Decimal('3500.00'),
    )

    assert invoice.month == dt.date(2026, 6, 1)
    assert invoice.lesson_count == 2
    assert invoice.total_amount == Decimal('7000.00')


def test_dashboard_summary_returns_teacher_scoped_counts(api_client, teacher, other_teacher, parent_user):
    owned_student = Student.objects.create(
        full_name='Owned Student',
        grade='高1',
        school='North High',
        target_school='National University',
        weak_subjects='Physics',
        teacher=teacher,
        parent=parent_user,
        guardian_contact='owned@example.com',
        notes='',
    )
    other_student = Student.objects.create(
        full_name='Other Student',
        grade='高2',
        school='South High',
        target_school='City University',
        weak_subjects='Chemistry',
        teacher=other_teacher,
        parent=parent_user,
        guardian_contact='other@example.com',
        notes='',
    )

    this_month = timezone.make_aware(dt.datetime(2026, 6, 8, 18, 0))
    last_month = timezone.make_aware(dt.datetime(2026, 5, 20, 18, 0))
    make_lesson(owned_student, teacher, this_month, Lesson.Status.COMPLETED)
    make_lesson(owned_student, teacher, last_month, Lesson.Status.COMPLETED)
    make_lesson(other_student, other_teacher, this_month, Lesson.Status.COMPLETED)

    api_client.force_authenticate(user=teacher)
    response = api_client.get('/api/dashboard-summary/')

    assert response.status_code == 200
    assert response.json() == {
        'students_count': 1,
        'current_month_lessons_count': 1,
        'pending_assignments_count': 0,
    }
