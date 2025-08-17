from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import TherapistViewSet

router = DefaultRouter()
router.register(r'therapists', TherapistViewSet)

urlpatterns = [
    path('', views.portal_home, name='portal_home'),
    path(
        'manage-therapists/', views.manage_therapists, name='manage_therapists'
    ),
    path('api/', include((router.urls, 'api'))),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
