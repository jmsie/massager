from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta

from ..models import Reservation, MassagePlan, Therapist
from ..serializers import ReservationSerializer, SimpleReservationSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    """
    預約管理 ViewSet
    提供完整的 CRUD 功能
    """
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()

    def get_queryset(self):
        """只看自己店家的預約"""
        store = getattr(self.request.user, "store", None)
        if not store:
            return Reservation.objects.none()
        return Reservation.objects.filter(store=store).select_related(
            'massage_plan', 'therapist'
        ).order_by('-appointment_time')

    def get_serializer_class(self):
        """根據操作選擇序列化器"""
        if self.action == 'list':
            return SimpleReservationSerializer
        return ReservationSerializer

    def list(self, request, *args, **kwargs):
        """列出所有預約"""
        queryset = self.get_queryset()
        
        # 日期範圍過濾
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(appointment_time__gte=start_datetime)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                queryset = queryset.filter(appointment_time__lt=end_datetime)
            except ValueError:
                pass
        
        # 師傅過濾
        therapist_id = request.query_params.get('therapist_id')
        if therapist_id:
            queryset = queryset.filter(therapist_id=therapist_id)
        
        # 方案過濾
        massage_plan_id = request.query_params.get('massage_plan_id')
        if massage_plan_id:
            queryset = queryset.filter(massage_plan_id=massage_plan_id)
        
        # 客戶姓名搜尋
        customer_name = request.query_params.get('customer_name')
        if customer_name:
            queryset = queryset.filter(customer_name__icontains=customer_name)
        
        # 客戶電話搜尋
        customer_phone = request.query_params.get('customer_phone')
        if customer_phone:
            queryset = queryset.filter(customer_phone__icontains=customer_phone)
        
        # 時間狀態過濾（upcoming, past, today）
        time_filter = request.query_params.get('time_filter')
        now = timezone.now()
        
        if time_filter == 'upcoming':
            queryset = queryset.filter(appointment_time__gt=now)
        elif time_filter == 'past':
            queryset = queryset.filter(appointment_time__lt=now)
        elif time_filter == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            queryset = queryset.filter(
                appointment_time__gte=today_start,
                appointment_time__lt=today_end
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """取得單一預約"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """建立新預約"""
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
        """更新預約"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """刪除預約"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "預約取消成功"},
            status=status.HTTP_200_OK
        )

    def perform_create(self, serializer):
        """建立時關聯到當前使用者的店家"""
        store = getattr(self.request.user, "store", None)
        if store:
            serializer.save(store=store)
        else:
            raise ValueError("找不到使用者的店家資訊")

    def perform_update(self, serializer):
        """更新時不允許變更店家"""
        if 'store' in serializer.validated_data:
            raise ValueError("不允許變更預約所屬店家")
        serializer.save()

    def get_serializer_context(self):
        """傳遞 request 到 serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['get'])
    def today(self, request):
        """取得今日預約"""
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        queryset = self.get_queryset().filter(
            appointment_time__gte=today_start,
            appointment_time__lt=today_end
        )
        
        serializer = SimpleReservationSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """取得未來預約"""
        now = timezone.now()
        queryset = self.get_queryset().filter(appointment_time__gt=now)
        
        serializer = SimpleReservationSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """檢查指定日期的可用時段"""
        date_str = request.query_params.get('date')
        therapist_id = request.query_params.get('therapist_id')
        
        if not date_str:
            return Response(
                {"error": "請提供日期參數"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "日期格式錯誤，請使用 YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 生成該日期的時段（例如：09:00-21:00，每30分鐘一個時段）
        available_slots = []
        start_hour = 9
        end_hour = 21
        
        for hour in range(start_hour, end_hour):
            for minute in [0, 30]:
                slot_time = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
                slot_datetime = timezone.make_aware(slot_time)
                
                # 檢查這個時段是否已被預約
                if therapist_id:
                    existing_reservation = self.get_queryset().filter(
                        therapist_id=therapist_id,
                        appointment_time=slot_datetime
                    ).exists()
                else:
                    existing_reservation = self.get_queryset().filter(
                        appointment_time=slot_datetime
                    ).exists()
                
                available_slots.append({
                    'time': slot_datetime.strftime('%H:%M'),
                    'datetime': slot_datetime.isoformat(),
                    'available': not existing_reservation
                })
        
        return Response({
            'date': date_str,
            'therapist_id': therapist_id,
            'slots': available_slots
        })
