from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.db.models import Q

from ..models import ServiceSurvey, Therapist
from ..serializers import ServiceSurveySerializer


class ServiceSurveyViewSet(viewsets.ModelViewSet):
    """
    服務問卷 ViewSet
    - GET: 需要登入，只能看自己店家的問卷
    - POST: 允許匿名，供客人評論
    """
    serializer_class = ServiceSurveySerializer
    queryset = ServiceSurvey.objects.all()
    http_method_names = ['get', 'post']

    def get_permissions(self):
        """
        根據操作類型設定權限
        - list, retrieve: 需要登入
        - create: 允許匿名
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """只看自己店家師傅的問卷 (僅用於 list 和 retrieve)"""
        # 如果是匿名用戶，回傳空查詢集
        if not self.request.user.is_authenticated:
            return ServiceSurvey.objects.none()
            
        store = getattr(self.request.user, "store", None)
        if not store:
            return ServiceSurvey.objects.none()
        
        # 取得該店家的所有師傅
        therapist_ids = Therapist.objects.filter(
            store=store, 
            is_deleted=False
        ).values_list('id', flat=True)
        
        return ServiceSurvey.objects.filter(
            therapist_id__in=therapist_ids
        ).select_related('therapist').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """列出所有問卷 (需要登入)"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        queryset = self.get_queryset()
        
        # 可以根據師傅過濾
        therapist_id = request.query_params.get('therapist_id')
        if therapist_id:
            queryset = queryset.filter(therapist_id=therapist_id)
        
        # 可以根據星級過濾
        rating = request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """取得單一問卷 (需要登入)"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """建立新問卷 (允許匿名)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 驗證師傅是否存在且啟用
        therapist = serializer.validated_data['therapist']
        if therapist.is_deleted or not therapist.enabled:
            return Response(
                {"error": "無法為此師傅評論"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 如果是已登入用戶，額外驗證師傅是否屬於該店家
        if request.user.is_authenticated:
            store = getattr(request.user, "store", None)
            if store and therapist.store != store:
                return Response(
                    {"error": "師傅不屬於您的店家"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 儲存問卷
        self.perform_create(serializer)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        """執行建立操作"""
        serializer.save()

    def get_serializer_context(self):
        """傳遞 request 到 serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    # 禁用其他 HTTP 方法
    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed"}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed"}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed"}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )