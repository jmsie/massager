from rest_framework import viewsets, status
from rest_framework.response import Response
from decimal import Decimal

from ..models import MassagePlan, Store
from ..serializers import MassagePlanSerializer


class MassagePlanViewSet(viewsets.ModelViewSet):
    """
    按摩方案 ViewSet
    提供完整的 CRUD 功能
    """
    serializer_class = MassagePlanSerializer
    queryset = MassagePlan.objects.all()

    def get_queryset(self):
        """只看自己店家的方案"""
        store = getattr(self.request.user, "store", None)
        if not store:
            return MassagePlan.objects.none()
        return MassagePlan.objects.filter(store=store).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """列出所有方案"""
        queryset = self.get_queryset()
        
        # 可以根據價格範圍過濾
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        
        if min_price:
            try:
                queryset = queryset.filter(price__gte=Decimal(min_price))
            except (ValueError, TypeError):
                pass
                
        if max_price:
            try:
                queryset = queryset.filter(price__lte=Decimal(max_price))
            except (ValueError, TypeError):
                pass
        
        # 可以根據時間長度過濾
        min_duration = request.query_params.get('min_duration')
        max_duration = request.query_params.get('max_duration')
        
        if min_duration:
            try:
                queryset = queryset.filter(duration__gte=int(min_duration))
            except (ValueError, TypeError):
                pass
                
        if max_duration:
            try:
                queryset = queryset.filter(duration__lte=int(max_duration))
            except (ValueError, TypeError):
                pass
        
        # 搜尋方案名稱
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """取得單一方案"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """建立新方案"""
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
        """更新方案"""
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
        """刪除方案"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "方案刪除成功"},
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
            raise ValueError("不允許變更方案所屬店家")
        serializer.save()

    def get_serializer_context(self):
        """傳遞 request 到 serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
