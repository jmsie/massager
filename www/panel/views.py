from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Therapist
from .serializers import TherapistSerializer


class TherapistViewSet(viewsets.ModelViewSet):
    queryset = Therapist.objects.all()
    serializer_class = TherapistSerializer
    
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
        self.perform_destroy(instance)
        return Response(
            {'detail': 'Therapist deleted successfully.'}, 
            status=status.HTTP_200_OK
        )


def index(request):
    return render(request, 'panel/index.html')


@ensure_csrf_cookie
def manage_therapists(request):
    therapists = Therapist.objects.all().order_by('-created_at')
    return render(
        request, 
        'panel/manage_therapists.html', 
        {'therapists': therapists}
    )