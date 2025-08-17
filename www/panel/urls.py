from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import from new locations
from .views import login_view, logout_view, portal_home, manage_therapists, manage_surveys
from .views.public_views import public_review_therapist, public_submit_review
from .viewsets import TherapistViewSet, ServiceSurveyViewSet

# API Router
router = DefaultRouter()
router.register(r'therapists', TherapistViewSet)
router.register(r'service-surveys', ServiceSurveyViewSet)

urlpatterns = [
    # Web URLs
    path('', portal_home, name='portal_home'),
    path('manage-therapists/', manage_therapists, name='manage_therapists'),
    path('manage-surveys/', manage_surveys, name='manage_surveys'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Public Review Page
    path('review/<int:therapist_id>/', public_review_therapist, name='public_review_therapist'),
    
    # Public API (CSRF exempt)
    path('api/public-review/', public_submit_review, name='public_submit_review'),
    
    # API URLs
    path('api/', include((router.urls, 'api'))),
]