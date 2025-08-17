from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

from ..models import Therapist


@ensure_csrf_cookie
@login_required
def manage_therapists(request):
    therapists = Therapist.objects.all().order_by('-created_at').filter(is_deleted=False)
    return render(request, 'panel/manage_therapists.html', {'therapists': therapists})


@login_required
def portal_home(request):
    ctx = {"store_name": request.session.get("store_name", "店家名稱")}
    return render(request, "panel/portal_home.html", ctx)
