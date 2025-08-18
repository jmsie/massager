from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import from new locations
from .views import (login_view, logout_view, portal_home, manage_therapists, 
                   manage_surveys, manage_massage_plans, manage_reservations, manage_invitations)
from .views.public_views import public_review_therapist, public_massage_invitation, public_submit_review
from .viewsets import (TherapistViewSet, ServiceSurveyViewSet, MassagePlanViewSet, 
                      ReservationViewSet, MassageInvitationViewSet, PublicMassageInvitationViewSet)

# API Router
router = DefaultRouter()
router.register(r'therapists', TherapistViewSet)
router.register(r'service-surveys', ServiceSurveyViewSet)
router.register(r'massage-plans', MassagePlanViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'massage-invitations', MassageInvitationViewSet)
# 為 PublicMassageInvitationViewSet 指定唯一的 basename
router.register(r'public-invitations', PublicMassageInvitationViewSet, basename='public-invitation')

urlpatterns = [
    # Web URLs
    path('', portal_home, name='portal_home'),
    path('manage-therapists/', manage_therapists, name='manage_therapists'),
    path('manage-surveys/', manage_surveys, name='manage_surveys'),
    path('manage-massage-plans/', manage_massage_plans, name='manage_massage_plans'),
    path('manage-reservations/', manage_reservations, name='manage_reservations'),
    path('manage-invitations/', manage_invitations, name='manage_invitations'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Public Pages
    path('review/<int:therapist_id>/', public_review_therapist, name='public_review_therapist'),
    path('invitation/<uuid:slug>/', public_massage_invitation, name='public_massage_invitation'),

 # Public API (CSRF exempt)
    path('api/public-reviews/', public_submit_review, name='public_submit_review'),

    # API URLs
    path('api/', include((router.urls, 'api'))),


]