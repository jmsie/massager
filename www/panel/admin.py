from django.contrib import admin
from .models import Therapist, Specialization, Store, MassagePlan, ServiceSurvey, Reservation, MassageInvitation

# Register your models here.
admin.site.register(Therapist)
admin.site.register(Specialization)
admin.site.register(Store)
admin.site.register(MassagePlan)
admin.site.register(ServiceSurvey)
admin.site.register(Reservation)
admin.site.register(MassageInvitation)