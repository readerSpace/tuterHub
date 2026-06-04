from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	class Role(models.TextChoices):
		ADMIN = 'admin', '管理者'
		TEACHER = 'teacher', '講師'
		STUDENT = 'student', '生徒'
		PARENT = 'parent', '保護者'

	role = models.CharField(max_length=20, choices=Role.choices, default=Role.TEACHER)

	def save(self, *args, **kwargs):
		if self.is_superuser:
			self.role = self.Role.ADMIN
		super().save(*args, **kwargs)

	def __str__(self):
		return self.get_full_name() or self.username
