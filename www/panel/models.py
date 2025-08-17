from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Store(models.Model):
    # ⚠️ 改動：移除原本的 email/password 欄位，改用 OneToOne 綁 User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="store")
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    page_view_data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "店家"
        verbose_name_plural = "店家"

    def __str__(self):
        # 以店家名稱為主，沒有就退回 user.email/username
        return self.name or getattr(self.user, "email", self.user.username)



class Therapist(models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="therapists",
    )
    name = models.CharField(max_length=255, verbose_name="姓名")
    phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="電話"
    )
    line_id = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Line ID"
    )
    nick_name = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="暱稱"
    )
    bio = models.TextField(blank=True, null=True, verbose_name="介紹")
    enabled = models.BooleanField(default=True, verbose_name="啟用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "按摩師"
        verbose_name_plural = "按摩師"
        ordering = ['-created_at']

    def __str__(self):
        return self.name