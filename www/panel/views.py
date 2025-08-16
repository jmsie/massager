from rest_framework import viewsets
from django.shortcuts import render

from .models import Therapist
from .serializers import TherapistSerializer


class TherapistViewSet(viewsets.ModelViewSet):
    queryset = Therapist.objects.all()
    serializer_class = TherapistSerializer


def index(request):
    return render(request, 'panel/index.html')


def manage_therapists(request):
    therapists = Therapist.objects.all()
    return render(
        request, 'panel/manage_therapists.html', {'therapists': therapists}
    )