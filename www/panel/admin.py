from django.contrib import admin
from .models import Therapist, Specialization, Store

# Register your models here.
admin.site.register(Therapist)
admin.site.register(Specialization)
admin.site.register(Store)