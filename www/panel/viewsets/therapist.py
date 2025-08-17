from rest_framework import viewsets, status
from rest_framework.response import Response

from ..models import Therapist, Store
from ..serializers import TherapistSerializer
from .base import SoftDeleteViewSetMixin, StoreFilteredViewSetMixin


class TherapistViewSet(SoftDeleteViewSetMixin, StoreFilteredViewSetMixin, viewsets.ModelViewSet):
    serializer_class = TherapistSerializer
    queryset = Therapist.objects.all()  # 基礎 queryset，會被 get_queryset 過濾

    # 移除原本的 get_queryset，因為已經在 StoreFilteredViewSetMixin 中實作了

    def create(self, request, *args, **kwargs):
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

    def perform_create(self, serializer):
        """建立時關聯到當前使用者的店家"""
        store_name = self.request.session.get('store_name')
        store = Store.objects.filter(name=store_name).first()
        if store:
            serializer.save(store=store)
        else:
            raise ValueError("Store not found for the current session.")

    def perform_update(self, serializer):
        """更新時不允許變更店家"""
        if 'store' in serializer.validated_data:
            raise ValueError("Changing the store is not allowed.")
        serializer.save()
