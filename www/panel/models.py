from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from uuid import uuid4

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
    is_deleted = models.BooleanField(default=False, verbose_name="已刪除")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "按摩師"
        verbose_name_plural = "按摩師"
        ordering = ['-created_at']

    def __str__(self):
        return self.name
  
# 師傅服務問卷
class ServiceSurvey(models.Model):
    therapist = models.ForeignKey(
        'Therapist', on_delete=models.CASCADE, related_name='service_surveys'
    )
    RATING_CHOICES = [(i, f'{i} 星') for i in range(1, 6)]
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=5,
        verbose_name='星級'
    )
    comment = models.TextField(blank=True, verbose_name='備註')
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name='填寫時間'
    )

    class Meta:
        verbose_name = '服務問卷'
        verbose_name_plural = '服務問卷'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.therapist} - {self.rating} 星'

class MassagePlan(models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="massage_plans",
        verbose_name="店家"
    )
    name = models.CharField(max_length=255, verbose_name="方案名稱")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="方案價格"
    )
    duration = models.PositiveIntegerField(verbose_name="時間長度（分鐘）")
    notes = models.TextField(blank=True, null=True, verbose_name="備註")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "按摩方案"
        verbose_name_plural = "按摩方案"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.store.name})"

class Reservation(models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="店家"
    )
    customer_name = models.CharField(max_length=255, verbose_name="客戶姓名")
    customer_phone = models.CharField(max_length=20, verbose_name="客戶電話")
    appointment_time = models.DateTimeField(verbose_name="預約時間")
    massage_plan = models.ForeignKey(
        MassagePlan,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="預約的方案"
    )
    therapist = models.ForeignKey(
        Therapist,
        on_delete=models.SET_NULL,
        related_name="reservations",
        verbose_name="指定的師傅",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "預約"
        verbose_name_plural = "預約"
        ordering = ['-appointment_time']

    def __str__(self):
        return f"{self.customer_name} - {self.appointment_time} ({self.store.name})"

class MassageInvitation(models.Model):
    start_time = models.DateTimeField(verbose_name="開始時間")
    end_time = models.DateTimeField(verbose_name="結束時間")
    massage_plan = models.ForeignKey(
        MassagePlan,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name="按摩方案"
    )
    therapist = models.ForeignKey(
        Therapist,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name="師傅"
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="特價"
    )
    slug = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
        verbose_name="網址slug"
    )
    click_count = models.PositiveIntegerField(
        default=0,
        verbose_name="多少人點開"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="備註")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "按摩邀請"
        verbose_name_plural = "按摩邀請"
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.massage_plan.name} - {self.therapist.name} "
            f"({self.start_time} 至 {self.end_time})"
        )
