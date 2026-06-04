from django.contrib import admin

from tutoring.models import Assignment, Invoice, Lesson, LessonReport, Score, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'grade', 'school', 'teacher', 'parent')
	list_filter = ('grade', 'school', 'teacher')
	search_fields = ('full_name', 'school', 'target_school', 'weak_subjects', 'guardian_contact')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
	list_display = ('student', 'subject', 'teacher', 'start_time', 'status', 'lesson_format')
	list_filter = ('status', 'lesson_format', 'teacher', 'subject')
	search_fields = ('student__full_name', 'subject')


@admin.register(LessonReport)
class LessonReportAdmin(admin.ModelAdmin):
	list_display = ('lesson', 'understanding_level', 'created_at')
	search_fields = ('lesson__student__full_name', 'lesson__subject', 'content', 'parent_comment')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
	list_display = ('title', 'student', 'teacher', 'due_date', 'status')
	list_filter = ('status', 'teacher', 'due_date')
	search_fields = ('title', 'student__full_name', 'description', 'teacher_comment')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
	list_display = ('student', 'subject', 'score', 'max_score', 'exam_date', 'exam_type')
	list_filter = ('subject', 'exam_type', 'exam_date')
	search_fields = ('student__full_name', 'subject', 'exam_type')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
	list_display = ('student', 'month', 'lesson_count', 'unit_price', 'total_amount', 'payment_status')
	list_filter = ('payment_status', 'month')
	search_fields = ('student__full_name',)
	readonly_fields = ('lesson_count', 'total_amount')
