from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_http_methods
import json

from ..models import Therapist, Store, ServiceSurvey


@ensure_csrf_cookie
def public_review_therapist(request, therapist_id):
    """客人評論師傅的公開頁面"""
    try:
        therapist = get_object_or_404(
            Therapist, 
            id=therapist_id, 
            is_deleted=False, 
            enabled=True
        )
        
        # 確保師傅所屬店家存在
        if not therapist.store:
            raise Http404("師傅所屬店家不存在")
            
    except Therapist.DoesNotExist:
        raise Http404("找不到指定的師傅")
    
    context = {
        'therapist': therapist,
        'store': therapist.store,
    }
    
    return render(request, 'panel/public_review.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def public_submit_review(request):
    """公開提交評論的 API 端點"""
    try:
        data = json.loads(request.body)
        
        # 驗證必要欄位
        therapist_id = data.get('therapist')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not therapist_id or not rating:
            return JsonResponse(
                {'error': '師傅 ID 和評分為必填欄位'}, 
                status=400
            )
        
        # 驗證評分範圍
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return JsonResponse(
                {'error': '評分必須是 1-5 之間的整數'}, 
                status=400
            )
        
        # 取得師傅
        try:
            therapist = Therapist.objects.get(
                id=therapist_id, 
                is_deleted=False, 
                enabled=True
            )
        except Therapist.DoesNotExist:
            return JsonResponse(
                {'error': '找不到指定的師傅或師傅已停用'}, 
                status=400
            )
        
        # 建立評論
        survey = ServiceSurvey.objects.create(
            therapist=therapist,
            rating=rating,
            comment=comment.strip()
        )
        
        return JsonResponse({
            'message': '評論提交成功',
            'data': {
                'id': survey.id,
                'therapist': survey.therapist.id,
                'therapist_name': survey.therapist.name,
                'rating': survey.rating,
                'comment': survey.comment,
                'created_at': survey.created_at.isoformat()
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': '無效的 JSON 格式'}, 
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {'error': f'伺服器錯誤: {str(e)}'}, 
            status=500
        )