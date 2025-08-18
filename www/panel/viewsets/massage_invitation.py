from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta

from ..models import MassageInvitation, Reservation
from ..serializers import MassageInvitationSerializer, PublicMassageInvitationSerializer


class MassageInvitationViewSet(viewsets.ModelViewSet):
    """
    按摩邀請管理 ViewSet
    提供完整的 CRUD 功能
    """
    serializer_class = MassageInvitationSerializer
    queryset = MassageInvitation.objects.all()

    def get_queryset(self):
        """只看自己店家的邀請"""
        store = getattr(self.request.user, "store", None)
        if not store:
            return MassageInvitation.objects.none()
        
        return MassageInvitation.objects.filter(
            massage_plan__store=store
        ).select_related('massage_plan', 'therapist').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """列出所有邀請"""
        queryset = self.get_queryset()
        
        # 狀態過濾
        status_filter = request.query_params.get('status')
        now = timezone.now()
        
        if status_filter == 'active':
            queryset = queryset.filter(start_time__lte=now, end_time__gte=now)
        elif status_filter == 'upcoming':
            queryset = queryset.filter(start_time__gt=now)
        elif status_filter == 'expired':
            queryset = queryset.filter(end_time__lt=now)
        
        # 師傅過濾
        therapist_id = request.query_params.get('therapist_id')
        if therapist_id:
            queryset = queryset.filter(therapist_id=therapist_id)
        
        # 方案過濾
        massage_plan_id = request.query_params.get('massage_plan_id')
        if massage_plan_id:
            queryset = queryset.filter(massage_plan_id=massage_plan_id)
        
        # 日期範圍過濾
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(start_time__gte=start_datetime)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                queryset = queryset.filter(end_time__lt=end_datetime)
            except ValueError:
                pass
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """取得單一邀請"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """建立新邀請"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        """更新邀請"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # 檢查邀請是否已經開始
        now = timezone.now()
        if instance.start_time <= now:
            return Response(
                {"error": "邀請已經開始，無法修改"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """刪除邀請"""
        instance = self.get_object()
        
        # 檢查邀請是否已經開始
        now = timezone.now()
        if instance.start_time <= now <= instance.end_time:
            return Response(
                {"error": "邀請正在進行中，無法刪除"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(
            {"detail": "邀請刪除成功"},
            status=status.HTTP_200_OK
        )

    def get_serializer_context(self):
        """傳遞 request 到 serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['get'])
    def active(self, request):
        """取得目前有效的邀請"""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            start_time__lte=now,
            end_time__gte=now
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """取得即將開始的邀請"""
        now = timezone.now()
        queryset = self.get_queryset().filter(start_time__gt=now)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """複製邀請"""
        instance = self.get_object()
        
        # 創建新的邀請副本
        new_invitation = MassageInvitation(
            start_time=instance.start_time,
            end_time=instance.end_time,
            massage_plan=instance.massage_plan,
            therapist=instance.therapist,
            discount_price=instance.discount_price,
            notes=instance.notes
        )
        
        # 如果提供了新的時間，則使用新時間
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        
        if start_time:
            new_invitation.start_time = timezone.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if end_time:
            new_invitation.end_time = timezone.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        new_invitation.save()
        
        serializer = self.get_serializer(new_invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class PublicMassageInvitationViewSet(viewsets.GenericViewSet):
    """
    公開邀請 ViewSet
    供客人查看和預約邀請
    """
    permission_classes = [AllowAny]
    serializer_class = PublicMassageInvitationSerializer
    queryset = MassageInvitation.objects.all()
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def view(self, request, slug=None):
        """查看邀請詳情並增加點擊次數"""
        try:
            invitation = get_object_or_404(MassageInvitation, slug=slug)
            
            # 增加點擊次數
            invitation.click_count += 1
            invitation.save(update_fields=['click_count'])
            
            # 檢查是否已被預約（一個邀請只能有一個預約）
            has_reservation = Reservation.objects.filter(
                massage_plan=invitation.massage_plan,
                therapist=invitation.therapist,
                appointment_time__gte=invitation.start_time,
                appointment_time__lte=invitation.end_time,
                # 可以加入其他條件來識別是透過這個邀請預約的
            ).exists()
            
            serializer = self.get_serializer(invitation)
            response_data = serializer.data
            response_data['is_booked'] = has_reservation
            response_data['click_count'] = invitation.click_count
            
            return Response(response_data)
            
        except MassageInvitation.DoesNotExist:
            return Response(
                {"error": "邀請不存在"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    @method_decorator(csrf_exempt)
    def book(self, request, slug=None):
        """預約邀請"""
        try:
            invitation = get_object_or_404(MassageInvitation, slug=slug)
            
            # 檢查是否已經有人預約了（先搶先贏）
            existing_reservation = Reservation.objects.filter(
                massage_plan=invitation.massage_plan,
                therapist=invitation.therapist,
                appointment_time__gte=invitation.start_time,
                appointment_time__lte=invitation.end_time,
            ).exists()
            
            if existing_reservation:
                return Response(
                    {"error": "此優惠已被預約"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 檢查必要欄位
            customer_name = request.data.get('customer_name')
            customer_phone = request.data.get('customer_phone')
            appointment_time = request.data.get('appointment_time')
            
            if not all([customer_name, customer_phone, appointment_time]):
                return Response(
                    {"error": "請提供客戶姓名、電話和預約時間"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 驗證預約時間是否在邀請時間範圍內
            try:
                appointment_datetime = timezone.datetime.fromisoformat(
                    appointment_time.replace('Z', '+00:00')
                )
            except ValueError:
                return Response(
                    {"error": "預約時間格式錯誤"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 檢查預約時間是否在可預約範圍內
            if not (invitation.start_time <= appointment_datetime <= invitation.end_time):
                return Response(
                    {"error": "預約時間必須在可預約時段內"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 檢查是否有足夠時間完成服務
            service_end_time = appointment_datetime + timedelta(minutes=invitation.massage_plan.duration)
            if service_end_time > invitation.end_time:
                return Response(
                    {"error": "預約時間加上服務時長超出可預約時段"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 檢查現在時間是否已經過了可預約時間
            now = timezone.now()
            last_bookable_time = invitation.end_time - timedelta(minutes=invitation.massage_plan.duration)
            if now > last_bookable_time:
                return Response(
                    {"error": "優惠已過期，無法預約"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 檢查預約時間是否在未來
            if appointment_datetime <= now:
                return Response(
                    {"error": "預約時間必須是未來時間"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 再次檢查是否有衝突（防止同時預約）
            existing_conflict = Reservation.objects.filter(
                therapist=invitation.therapist,
                appointment_time=appointment_datetime
            ).exists()
            
            if existing_conflict:
                return Response(
                    {"error": "該時段已被預約"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 創建預約
            reservation = Reservation.objects.create(
                store=invitation.massage_plan.store,
                customer_name=customer_name.strip(),
                customer_phone=customer_phone.strip(),
                appointment_time=appointment_datetime,
                massage_plan=invitation.massage_plan,
                therapist=invitation.therapist,
                # 可以加入關聯到邀請的欄位
                notes=f"透過優惠邀請預約 (原價: {invitation.massage_plan.price}, 優惠價: {invitation.discount_price})"
            )
            
            # 回傳預約資訊
            return Response({
                "message": "預約成功",
                "reservation_id": reservation.id,
                "customer_name": reservation.customer_name,
                "appointment_time": reservation.appointment_time.isoformat(),
                "massage_plan": reservation.massage_plan.name,
                "therapist": reservation.therapist.name,
                "original_price": float(invitation.massage_plan.price),
                "discount_price": float(invitation.discount_price),
                "savings": float(invitation.massage_plan.price - invitation.discount_price)
            }, status=status.HTTP_201_CREATED)
            
        except MassageInvitation.DoesNotExist:
            return Response(
                {"error": "邀請不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"預約失敗: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )