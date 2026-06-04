from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Student(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		related_name='student_profile',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)
	full_name = models.CharField(max_length=255)
	grade = models.CharField(max_length=50)
	school = models.CharField(max_length=255, blank=True)
	target_school = models.CharField(max_length=255, blank=True)
	weak_subjects = models.CharField(max_length=255, blank=True)
	teacher = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name='assigned_students',
		on_delete=models.PROTECT,
	)
	parent = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name='children',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)
	guardian_contact = models.CharField(max_length=255, blank=True)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('full_name',)

	def __str__(self):
		return self.full_name


class Lesson(models.Model):
	class Format(models.TextChoices):
		IN_PERSON = 'in_person', '対面'
		ONLINE = 'online', 'オンライン'

	class Status(models.TextChoices):
		SCHEDULED = 'scheduled', '予定'
		COMPLETED = 'completed', '実施済み'
		ABSENT = 'absent', '欠席'
		RESCHEDULED = 'rescheduled', '振替'

	student = models.ForeignKey(Student, related_name='lessons', on_delete=models.CASCADE)
	teacher = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name='lessons',
		on_delete=models.PROTECT,
	)
	subject = models.CharField(max_length=100)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	lesson_format = models.CharField(max_length=20, choices=Format.choices)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-start_time',)

	def clean(self):
		errors = {}
		if self.start_time and self.end_time and self.start_time >= self.end_time:
			errors['end_time'] = '終了時刻は開始時刻より後である必要があります。'
		if self.student_id and self.teacher_id and self.student.teacher_id != self.teacher_id:
			errors['teacher'] = '授業の講師は担当講師と一致する必要があります。'
		if errors:
			raise ValidationError(errors)

	def __str__(self):
		return f'{self.student.full_name} - {self.subject}'


class LessonReport(models.Model):
	lesson = models.OneToOneField(Lesson, related_name='report', on_delete=models.CASCADE)
	content = models.TextField()
	understanding_level = models.PositiveSmallIntegerField(
		validators=[MinValueValidator(1), MaxValueValidator(5)]
	)
	homework = models.TextField(blank=True)
	next_plan = models.TextField(blank=True)
	parent_comment = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-created_at',)

	def __str__(self):
		return f'{self.lesson} report'


class Assignment(models.Model):
	class Status(models.TextChoices):
		PENDING = 'pending', '未着手'
		SUBMITTED = 'submitted', '提出済み'
		REVIEWED = 'reviewed', '確認済み'

	student = models.ForeignKey(Student, related_name='assignments', on_delete=models.CASCADE)
	teacher = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name='assignments',
		on_delete=models.PROTECT,
	)
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	due_date = models.DateField()
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	teacher_comment = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('due_date', 'title')

	def __str__(self):
		return self.title


class Score(models.Model):
	student = models.ForeignKey(Student, related_name='scores', on_delete=models.CASCADE)
	subject = models.CharField(max_length=100)
	score = models.PositiveIntegerField()
	max_score = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	exam_date = models.DateField()
	exam_type = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-exam_date',)

	def clean(self):
		if self.score > self.max_score:
			raise ValidationError({'score': '得点は満点以下である必要があります。'})

	def __str__(self):
		return f'{self.student.full_name} - {self.subject} ({self.score}/{self.max_score})'


class Invoice(models.Model):
	class PaymentStatus(models.TextChoices):
		UNPAID = 'unpaid', '未払い'
		PAID = 'paid', '支払い済み'
		OVERDUE = 'overdue', '期限超過'

	student = models.ForeignKey(Student, related_name='invoices', on_delete=models.CASCADE)
	month = models.DateField(help_text='請求対象月の1日を指定します。')
	lesson_count = models.PositiveIntegerField(default=0, editable=False)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
	payment_status = models.CharField(
		max_length=20,
		choices=PaymentStatus.choices,
		default=PaymentStatus.UNPAID,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-month', 'student__full_name')
		constraints = [
			models.UniqueConstraint(fields=('student', 'month'), name='unique_student_invoice_month')
		]

	def sync_totals(self):
		month_start = self.month.replace(day=1)
		if month_start.month == 12:
			next_month = month_start.replace(year=month_start.year + 1, month=1)
		else:
			next_month = month_start.replace(month=month_start.month + 1)

		lesson_total = self.student.lessons.filter(
			status=Lesson.Status.COMPLETED,
			start_time__date__gte=month_start,
			start_time__date__lt=next_month,
		).count()
		self.lesson_count = lesson_total
		self.total_amount = Decimal(lesson_total) * self.unit_price

	def save(self, *args, **kwargs):
		if self.month:
			self.month = self.month.replace(day=1)
		self.sync_totals()
		super().save(*args, **kwargs)

	def __str__(self):
		return f'{self.student.full_name} {self.month:%Y-%m}'
