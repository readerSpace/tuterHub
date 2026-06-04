from accounts.models import User


def filter_students_for_user(queryset, user):
    if user.is_superuser or user.role == User.Role.ADMIN:
        return queryset
    if user.role == User.Role.TEACHER:
        return queryset.filter(teacher=user)
    if user.role == User.Role.STUDENT:
        return queryset.filter(user=user)
    if user.role == User.Role.PARENT:
        return queryset.filter(parent=user)
    return queryset.none()


def filter_lessons_for_user(queryset, user):
    if user.is_superuser or user.role == User.Role.ADMIN:
        return queryset
    if user.role == User.Role.TEACHER:
        return queryset.filter(teacher=user)
    if user.role == User.Role.STUDENT:
        return queryset.filter(student__user=user)
    if user.role == User.Role.PARENT:
        return queryset.filter(student__parent=user)
    return queryset.none()


def filter_reports_for_user(queryset, user):
    if user.is_superuser or user.role == User.Role.ADMIN:
        return queryset
    if user.role == User.Role.TEACHER:
        return queryset.filter(lesson__teacher=user)
    if user.role == User.Role.STUDENT:
        return queryset.filter(lesson__student__user=user)
    if user.role == User.Role.PARENT:
        return queryset.filter(lesson__student__parent=user)
    return queryset.none()


def filter_assignments_for_user(queryset, user):
    if user.is_superuser or user.role == User.Role.ADMIN:
        return queryset
    if user.role == User.Role.TEACHER:
        return queryset.filter(teacher=user)
    if user.role == User.Role.STUDENT:
        return queryset.filter(student__user=user)
    if user.role == User.Role.PARENT:
        return queryset.filter(student__parent=user)
    return queryset.none()


def filter_scores_for_user(queryset, user):
    if user.is_superuser or user.role == User.Role.ADMIN:
        return queryset
    if user.role == User.Role.TEACHER:
        return queryset.filter(student__teacher=user)
    if user.role == User.Role.STUDENT:
        return queryset.filter(student__user=user)
    if user.role == User.Role.PARENT:
        return queryset.filter(student__parent=user)
    return queryset.none()


def filter_invoices_for_user(queryset, user):
    if user.is_superuser or user.role == User.Role.ADMIN:
        return queryset
    if user.role == User.Role.TEACHER:
        return queryset.filter(student__teacher=user)
    if user.role == User.Role.STUDENT:
        return queryset.filter(student__user=user)
    if user.role == User.Role.PARENT:
        return queryset.filter(student__parent=user)
    return queryset.none()