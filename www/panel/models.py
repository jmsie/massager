from django.db import models
from django.utils import timezone


class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Therapist(models.Model):
    name = models.CharField(max_length=100, verbose_name="姓名")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="電話")
    line_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Line ID")
    nick_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="暱稱")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "按摩師"
        verbose_name_plural = "按摩師"
        ordering = ['-created_at']

    def __str__(self):
        return self.name