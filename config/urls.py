from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import CurrentUserAPIView
from config.views import api_index, dashboard_summary

urlpatterns = [
    path('', api_index, name='api-index'),
    path('admin/', admin.site.urls),
    path('api/', include('tutoring.urls')),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/auth/me/', CurrentUserAPIView.as_view(), name='current-user'),
    path('api/dashboard-summary/', dashboard_summary, name='dashboard-summary'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
