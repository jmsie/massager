from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import from new locations
from .views import login_view, logout_view, portal_home, manage_therapists, manage_surveys
from .viewsets import TherapistViewSet, ServiceSurveyViewSet

# API Router
router = DefaultRouter()
router.register(r'therapists', TherapistViewSet)
router.register(r'service-surveys', ServiceSurveyViewSet)

urlpatterns = [
    # Web URLs
    path('', portal_home, name='portal_home'),
    path('manage-therapists/', manage_therapists, name='manage_therapists'),
    path('manage-surveys/', manage_surveys, name='manage_surveys'),  # 新增這行
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # API URLs
    path('api/', include((router.urls, 'api'))),
]
