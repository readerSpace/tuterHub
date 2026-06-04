from rest_framework import serializers

from accounts.models import User
from tutoring.models import Assignment, Invoice, Lesson, LessonReport, Score, Student


class StudentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            'id',
            'user',
            'user_name',
            'parent',
            'parent_name',
            'teacher',
            'teacher_name',
            'full_name',
            'grade',
            'school',
            'target_school',
            'weak_subjects',
            'guardian_contact',
            'notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'teacher': {'required': False},
        }

    def get_teacher_name(self, obj):
        return str(obj.teacher) if obj.teacher else ''

    def get_parent_name(self, obj):
        return str(obj.parent) if obj.parent else ''

    def get_user_name(self, obj):
        return obj.user.username if obj.user else ''

    def validate(self, attrs):
        request = self.context.get('request')
        user = attrs.get('user', getattr(self.instance, 'user', None))
        parent = attrs.get('parent', getattr(self.instance, 'parent', None))
        teacher = attrs.get('teacher', getattr(self.instance, 'teacher', None))

        if request and request.user.role == User.Role.TEACHER and not teacher:
            attrs['teacher'] = request.user
            teacher = request.user

        if user and user.role != User.Role.STUDENT:
            raise serializers.ValidationError({'user': 'Linked user must have the student role.'})
        if parent and parent.role != User.Role.PARENT:
            raise serializers.ValidationError({'parent': 'Linked parent must have the parent role.'})
        if teacher and teacher.role != User.Role.TEACHER:
            raise serializers.ValidationError({'teacher': 'Assigned teacher must have the teacher role.'})
        if request and request.user.role == User.Role.TEACHER and teacher and teacher != request.user:
            raise serializers.ValidationError({'teacher': 'Teachers can only manage their own students.'})
        return attrs


class LessonSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            'id',
            'student',
            'student_name',
            'teacher',
            'teacher_name',
            'subject',
            'start_time',
            'end_time',
            'lesson_format',
            'status',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'teacher': {'required': False},
        }

    def get_teacher_name(self, obj):
        return str(obj.teacher) if obj.teacher else ''

    def validate(self, attrs):
        request = self.context.get('request')
        student = attrs.get('student', getattr(self.instance, 'student', None))
        teacher = attrs.get('teacher', getattr(self.instance, 'teacher', None))
        start_time = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))

        if request and request.user.role == User.Role.TEACHER and not teacher:
            attrs['teacher'] = request.user
            teacher = request.user

        if teacher and teacher.role != User.Role.TEACHER:
            raise serializers.ValidationError({'teacher': 'Assigned teacher must have the teacher role.'})
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({'end_time': 'End time must be after start time.'})
        if student and teacher and student.teacher and student.teacher != teacher:
            raise serializers.ValidationError({'teacher': 'Assigned teacher must match the student owner.'})
        if request and request.user.role == User.Role.TEACHER and student and student.teacher and student.teacher != request.user:
            raise serializers.ValidationError({'student': 'Teachers can only manage their own students.'})
        return attrs


class LessonReportSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='lesson.student.full_name', read_only=True)
    subject = serializers.CharField(source='lesson.subject', read_only=True)

    class Meta:
        model = LessonReport
        fields = (
            'id',
            'lesson',
            'student_name',
            'subject',
            'content',
            'understanding_level',
            'homework',
            'next_plan',
            'parent_comment',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, attrs):
        request = self.context.get('request')
        lesson = attrs.get('lesson', getattr(self.instance, 'lesson', None))
        if request and request.user.role == User.Role.TEACHER and lesson and lesson.teacher != request.user:
            raise serializers.ValidationError({'lesson': 'Teachers can only manage reports for their own lessons.'})
        return attrs


class AssignmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = (
            'id',
            'student',
            'student_name',
            'teacher',
            'teacher_name',
            'title',
            'description',
            'due_date',
            'status',
            'teacher_comment',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'teacher': {'required': False},
        }

    def get_teacher_name(self, obj):
        return str(obj.teacher) if obj.teacher else ''

    def validate(self, attrs):
        request = self.context.get('request')
        student = attrs.get('student', getattr(self.instance, 'student', None))
        teacher = attrs.get('teacher', getattr(self.instance, 'teacher', None))

        if request and request.user.role == User.Role.TEACHER and not teacher:
            attrs['teacher'] = request.user
            teacher = request.user

        if teacher and teacher.role != User.Role.TEACHER:
            raise serializers.ValidationError({'teacher': 'Assigned teacher must have the teacher role.'})
        if student and teacher and student.teacher and student.teacher != teacher:
            raise serializers.ValidationError({'teacher': 'Assigned teacher must match the student owner.'})
        if request and request.user.role == User.Role.TEACHER and student and student.teacher and student.teacher != request.user:
            raise serializers.ValidationError({'student': 'Teachers can only manage their own students.'})
        return attrs


class ScoreSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = Score
        fields = (
            'id',
            'student',
            'student_name',
            'subject',
            'score',
            'max_score',
            'percentage',
            'exam_date',
            'exam_type',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at', 'percentage')

    def get_percentage(self, obj):
        if not obj.max_score:
            return 0
        return round((obj.score / obj.max_score) * 100, 2)

    def validate(self, attrs):
        request = self.context.get('request')
        student = attrs.get('student', getattr(self.instance, 'student', None))
        score = attrs.get('score', getattr(self.instance, 'score', None))
        max_score = attrs.get('max_score', getattr(self.instance, 'max_score', None))

        if score is not None and max_score is not None and score > max_score:
            raise serializers.ValidationError({'score': 'Score cannot exceed max score.'})
        if request and request.user.role == User.Role.TEACHER and student and student.teacher and student.teacher != request.user:
            raise serializers.ValidationError({'student': 'Teachers can only manage scores for their own students.'})
        return attrs


class InvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = Invoice
        fields = (
            'id',
            'student',
            'student_name',
            'month',
            'lesson_count',
            'unit_price',
            'total_amount',
            'payment_status',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at', 'lesson_count', 'total_amount')

    def validate(self, attrs):
        request = self.context.get('request')
        student = attrs.get('student', getattr(self.instance, 'student', None))
        unit_price = attrs.get('unit_price', getattr(self.instance, 'unit_price', None))

        if unit_price is not None and unit_price < 0:
            raise serializers.ValidationError({'unit_price': 'Unit price cannot be negative.'})
        if request and request.user.role == User.Role.TEACHER and student and student.teacher and student.teacher != request.user:
            raise serializers.ValidationError({'student': 'Teachers can only manage invoices for their own students.'})
        return attrs