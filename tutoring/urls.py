from rest_framework.routers import DefaultRouter

from tutoring.views import (
    AssignmentViewSet,
    InvoiceViewSet,
    LessonReportViewSet,
    LessonViewSet,
    ScoreViewSet,
    StudentViewSet,
)


router = DefaultRouter()
router.register('students', StudentViewSet, basename='student')
router.register('lessons', LessonViewSet, basename='lesson')
router.register('reports', LessonReportViewSet, basename='report')
router.register('assignments', AssignmentViewSet, basename='assignment')
router.register('scores', ScoreViewSet, basename='score')
router.register('invoices', InvoiceViewSet, basename='invoice')

urlpatterns = router.urls