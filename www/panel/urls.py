from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import from new locations
from .views import (login_view, logout_view, portal_home, manage_therapists, 
                   manage_surveys, manage_massage_plans, manage_reservations)
from .views.public_views import public_review_therapist
from .viewsets import TherapistViewSet, ServiceSurveyViewSet, MassagePlanViewSet, ReservationViewSet

# API Router
router = DefaultRouter()
router.register(r'therapists', TherapistViewSet)
router.register(r'service-surveys', ServiceSurveyViewSet)
router.register(r'massage-plans', MassagePlanViewSet)
router.register(r'reservations', ReservationViewSet)

urlpatterns = [
    # Web URLs
    path('', portal_home, name='portal_home'),
    path('manage-therapists/', manage_therapists, name='manage_therapists'),
    path('manage-surveys/', manage_surveys, name='manage_surveys'),
    path('manage-massage-plans/', manage_massage_plans, name='manage_massage_plans'),
    path('manage-reservations/', manage_reservations, name='manage_reservations'),  # 新增這行
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Public Review Page
    path('review/<int:therapist_id>/', public_review_therapist, name='public_review_therapist'),
    
    # API URLs
    path('api/', include((router.urls, 'api'))),
]