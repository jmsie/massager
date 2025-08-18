from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

from ..models import Therapist, ServiceSurvey, MassagePlan, Reservation


@ensure_csrf_cookie
@login_required
def manage_therapists(request):
    therapists = Therapist.objects.all().order_by('-created_at').filter(is_deleted=False)
    return render(request, 'panel/manage_therapists.html', {'therapists': therapists})


@login_required
def portal_home(request):
    ctx = {"store_name": request.session.get("store_name", "店家名稱")}
    return render(request, "panel/portal_home.html", ctx)

@ensure_csrf_cookie
@login_required
def manage_surveys(request):
    """師傅評論管理頁面"""
    store = getattr(request.user, "store", None)
    if store:
        # 取得該店家的所有師傅
        therapist_ids = Therapist.objects.filter(
            store=store, 
            is_deleted=False
        ).values_list('id', flat=True)
        
        # 取得評論，並包含師傅資訊
        surveys = ServiceSurvey.objects.filter(
            therapist_id__in=therapist_ids
        ).select_related('therapist').order_by('-created_at')
        
        # 取得師傅列表供過濾使用
        therapists = Therapist.objects.filter(
            store=store, 
            is_deleted=False
        ).order_by('name')
    else:
        surveys = ServiceSurvey.objects.none()
        therapists = Therapist.objects.none()
    
    return render(
        request,
        'panel/manage_surveys.html',
        {
            'surveys': surveys,
            'therapists': therapists
        }
    )

@ensure_csrf_cookie
@login_required
def manage_massage_plans(request):
    """按摩方案管理頁面"""
    store = getattr(request.user, "store", None)
    if store:
        massage_plans = MassagePlan.objects.filter(
            store=store
        ).order_by('-created_at')
    else:
        massage_plans = MassagePlan.objects.none()
    
    return render(
        request,
        'panel/manage_massage_plans.html',
        {'massage_plans': massage_plans}
    )


@ensure_csrf_cookie
@login_required
def manage_reservations(request):
    """預約管理頁面"""
    store = getattr(request.user, "store", None)
    if store:
        reservations = Reservation.objects.filter(
            store=store
        ).select_related('massage_plan', 'therapist').order_by('-appointment_time')
        
        # 取得師傅和方案列表供篩選使用
        therapists = Therapist.objects.filter(
            store=store, 
            is_deleted=False
        ).order_by('name')
        
        massage_plans = MassagePlan.objects.filter(
            store=store
        ).order_by('name')
    else:
        reservations = Reservation.objects.none()
        therapists = Therapist.objects.none()
        massage_plans = MassagePlan.objects.none()
    
    return render(
        request,
        'panel/manage_reservations.html',
        {
            'reservations': reservations,
            'therapists': therapists,
            'massage_plans': massage_plans
        }
    )
