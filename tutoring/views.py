import csv

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from tutoring.access import (
    filter_assignments_for_user,
    filter_invoices_for_user,
    filter_lessons_for_user,
    filter_reports_for_user,
    filter_scores_for_user,
    filter_students_for_user,
)
from tutoring.models import Assignment, Invoice, Lesson, LessonReport, Score, Student
from tutoring.permissions import RoleBasedWritePermission
from tutoring.serializers import (
    AssignmentSerializer,
    InvoiceSerializer,
    LessonReportSerializer,
    LessonSerializer,
    ScoreSerializer,
    StudentSerializer,
)


def display_user(user):
    if not user:
        return ''
    return user.get_full_name() or user.username


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'parent', 'teacher')
    serializer_class = StudentSerializer
    permission_classes = [RoleBasedWritePermission]
    filterset_fields = ['grade', 'school', 'teacher', 'parent']
    search_fields = ['full_name', 'school', 'target_school', 'weak_subjects', 'guardian_contact']
    ordering_fields = ['full_name', 'grade', 'created_at']

    def get_queryset(self):
        return filter_students_for_user(super().get_queryset(), self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role == User.Role.TEACHER:
            serializer.save(teacher=self.request.user)
            return
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role == User.Role.TEACHER:
            serializer.save(teacher=self.request.user)
            return
        serializer.save()

    @action(detail=False, methods=['get'], url_path='export_csv')
    def export_csv(self, request):
        if not (request.user.is_superuser or request.user.role in {User.Role.ADMIN, User.Role.TEACHER}):
            raise PermissionDenied('Only admins and teachers can export student data.')

        queryset = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        writer = csv.writer(response)
        writer.writerow(['id', 'name', 'grade', 'school', 'target_school', 'teacher', 'parent'])

        for student in queryset:
            writer.writerow(
                [
                    student.id,
                    student.full_name,
                    student.grade,
                    student.school,
                    student.target_school,
                    display_user(student.teacher),
                    display_user(student.parent),
                ]
            )
        return response


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('student', 'teacher', 'student__teacher', 'student__parent', 'student__user')
    serializer_class = LessonSerializer
    permission_classes = [RoleBasedWritePermission]
    filterset_fields = ['student', 'teacher', 'subject', 'status', 'lesson_format']
    search_fields = ['student__full_name', 'subject']
    ordering_fields = ['start_time', 'end_time', 'created_at']

    def get_queryset(self):
        return filter_lessons_for_user(super().get_queryset(), self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role == User.Role.TEACHER:
            serializer.save(teacher=self.request.user)
            return
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role == User.Role.TEACHER:
            serializer.save(teacher=self.request.user)
            return
        serializer.save()


class LessonReportViewSet(viewsets.ModelViewSet):
    queryset = LessonReport.objects.select_related('lesson', 'lesson__student', 'lesson__teacher')
    serializer_class = LessonReportSerializer
    permission_classes = [RoleBasedWritePermission]
    filterset_fields = ['lesson__student', 'lesson__teacher']
    search_fields = ['lesson__student__full_name', 'lesson__subject', 'content', 'parent_comment']
    ordering_fields = ['lesson__start_time', 'created_at']

    def get_queryset(self):
        return filter_reports_for_user(super().get_queryset(), self.request.user)


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('student', 'teacher', 'student__teacher', 'student__parent', 'student__user')
    serializer_class = AssignmentSerializer
    permission_classes = [RoleBasedWritePermission]
    filterset_fields = ['student', 'teacher', 'status', 'due_date']
    search_fields = ['title', 'student__full_name', 'description', 'teacher_comment']
    ordering_fields = ['due_date', 'created_at']

    def get_queryset(self):
        return filter_assignments_for_user(super().get_queryset(), self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role == User.Role.TEACHER:
            serializer.save(teacher=self.request.user)
            return
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role == User.Role.TEACHER:
            serializer.save(teacher=self.request.user)
            return
        serializer.save()


class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.select_related('student', 'student__teacher', 'student__parent', 'student__user')
    serializer_class = ScoreSerializer
    permission_classes = [RoleBasedWritePermission]
    filterset_fields = ['student', 'subject', 'exam_type', 'exam_date']
    search_fields = ['student__full_name', 'subject', 'exam_type']
    ordering_fields = ['exam_date', 'created_at', 'score']

    def get_queryset(self):
        return filter_scores_for_user(super().get_queryset(), self.request.user)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('student', 'student__teacher', 'student__parent', 'student__user')
    serializer_class = InvoiceSerializer
    permission_classes = [RoleBasedWritePermission]
    filterset_fields = ['student', 'payment_status', 'month']
    search_fields = ['student__full_name']
    ordering_fields = ['month', 'created_at', 'total_amount']

    def get_queryset(self):
        return filter_invoices_for_user(super().get_queryset(), self.request.user)
