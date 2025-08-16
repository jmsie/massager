from django.db import models


class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Therapist(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.ManyToManyField(
        Specialization, related_name="therapists"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    line_id = models.CharField(max_length=50, null=True, blank=True)
    nick_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
