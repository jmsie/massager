from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Therapist, Store
from .serializers import TherapistSerializer


class TherapistViewSet(viewsets.ModelViewSet):
    serializer_class = TherapistSerializer
    queryset = Therapist.objects.none()  # Default queryset to avoid errors

    def get_queryset(self):
        # 只看自己店、且未刪
        store = getattr(self.request.user, "store", None)
        if not store:
            return Therapist.objects.none()
        return Therapist.objects.filter(store=store, is_deleted=False)

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
        return Response({"detail": "Therapist soft deleted successfully."},
                        status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        # Associate the therapist with the currently logged-in user's store
        store_name = self.request.session.get('store_name')
        store = Store.objects.filter(name=store_name).first()
        if store:
            therapist_store = serializer.validated_data.get('store')
            if therapist_store and therapist_store != store:
                raise ValueError(
                    "You do not have permission to add a therapist "
                    "to this store."
                )
            serializer.save(store=store)
        else:
            raise ValueError("Store not found for the current session.")

    def perform_update(self, serializer):
        # Prevent changing the store during updates
        if 'store' in serializer.validated_data:
            raise ValueError("Changing the store is not allowed.")
        serializer.save()
