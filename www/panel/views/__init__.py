from .auth_views import login_view, logout_view
from .template_views import (manage_therapists, portal_home, manage_surveys, 
                           manage_massage_plans, manage_reservations)

__all__ = [
    'login_view', 
    'logout_view', 
    'manage_therapists', 
    'portal_home',
    'manage_surveys',
    'manage_massage_plans',
    'manage_reservations'
]