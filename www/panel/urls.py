from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import from new locations
from .views.auth_views import login_view, logout_view
from .views.template_views import portal_home, manage_therapists
from .viewsets.therapist import TherapistViewSet

# API Router
router = DefaultRouter()
router.register(r'therapists', TherapistViewSet)

urlpatterns = [
    # Web URLs
    path('', portal_home, name='portal_home'),
    path('manage-therapists/', manage_therapists, name='manage_therapists'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # API URLs
    path('api/', include((router.urls, 'api'))),
]
