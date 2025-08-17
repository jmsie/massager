from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status


class SoftDeleteViewSetMixin:
    """提供軟刪除功能的 Mixin"""
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
        model_name = self.__class__.__name__.replace('ViewSet', '')
        return Response(
            {"detail": f"{model_name} soft deleted successfully."},
            status=status.HTTP_200_OK
        )


class StoreFilteredViewSetMixin:
    """根據使用者所屬店家過濾資料的 Mixin"""
    
    def get_queryset(self):
        """覆寫 get_queryset 來過濾店家資料"""
        store = getattr(self.request.user, "store", None)
        if not store:
            return self.queryset.none()
        return self.queryset.filter(store=store, is_deleted=False)
