from rest_framework import serializers
from .models import MassagePlan, Therapist, ServiceSurvey, Reservation, MassageInvitation
from django.utils import timezone


class TherapistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Therapist
        fields = ['id', 'name', 'phone', 'line_id', 'nick_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        """Validate that name is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("姓名不能為空")
        return value.strip()

    def validate_phone(self, value):
        """Clean phone number"""
        if value:
            return value.strip()
        return value

    def validate_line_id(self, value):
        """Clean Line ID"""
        if value:
            return value.strip()
        return value

    def validate_nick_name(self, value):
        """Clean nick name"""
        if value:
            return value.strip()
        return value
    
class ServiceSurveySerializer(serializers.ModelSerializer):
    therapist_name = serializers.CharField(source='therapist.name', read_only=True)
    
    class Meta:
        model = ServiceSurvey
        fields = ['id', 'therapist', 'therapist_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at', 'therapist_name']

    def validate_rating(self, value):
        """驗證星級範圍"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("星級必須在 1-5 之間")
        return value

    def validate_therapist(self, value):
        """驗證師傅狀態"""
        if value.is_deleted:
            raise serializers.ValidationError("師傅已被刪除")
        if not value.enabled:
            raise serializers.ValidationError("師傅未啟用")
            
        # 如果是已登入用戶，驗證師傅是否屬於當前店家
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            store = getattr(request.user, "store", None)
            if store and value.store != store:
                raise serializers.ValidationError("師傅不屬於您的店家")
                
        return value
    
class MassagePlanSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = MassagePlan
        fields = ['id', 'name', 'price', 'duration', 'notes', 'store', 'store_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'store', 'store_name', 'created_at', 'updated_at']

    def validate_name(self, value):
        """驗證方案名稱不能為空"""
        if not value or not value.strip():
            raise serializers.ValidationError("方案名稱不能為空")
        return value.strip()

    def validate_price(self, value):
        """驗證價格必須大於 0"""
        if value <= 0:
            raise serializers.ValidationError("價格必須大於 0")
        return value

    def validate_duration(self, value):
        """驗證時間長度必須大於 0"""
        if value <= 0:
            raise serializers.ValidationError("時間長度必須大於 0 分鐘")
        return value

    def validate(self, data):
        """額外的跨欄位驗證"""
        # 檢查同一店家是否已有相同名稱的方案
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            store = getattr(request.user, "store", None)
            if store:
                name = data.get('name')
                existing_plan = MassagePlan.objects.filter(
                    store=store, 
                    name=name
                ).exclude(id=self.instance.id if self.instance else None)
                
                if existing_plan.exists():
                    raise serializers.ValidationError({
                        'name': '該店家已存在相同名稱的方案'
                    })
        
        return data    
    
class ReservationSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    massage_plan_name = serializers.CharField(source='massage_plan.name', read_only=True)
    massage_plan_price = serializers.DecimalField(source='massage_plan.price', max_digits=10, decimal_places=2, read_only=True)
    massage_plan_duration = serializers.IntegerField(source='massage_plan.duration', read_only=True)
    therapist_name = serializers.CharField(source='therapist.name', read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'customer_name', 'customer_phone', 'appointment_time',
            'massage_plan', 'massage_plan_name', 'massage_plan_price', 'massage_plan_duration',
            'therapist', 'therapist_name', 'store', 'store_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'store', 'store_name', 'created_at', 'updated_at']

    def validate_customer_name(self, value):
        """驗證客戶姓名不能為空"""
        if not value or not value.strip():
            raise serializers.ValidationError("客戶姓名不能為空")
        return value.strip()

    def validate_customer_phone(self, value):
        """驗證客戶電話格式"""
        if not value or not value.strip():
            raise serializers.ValidationError("客戶電話不能為空")
        
        # 簡單的電話號碼驗證（移除空格和符號後至少8位數字）
        phone_digits = ''.join(filter(str.isdigit, value))
        if len(phone_digits) < 8:
            raise serializers.ValidationError("請輸入有效的電話號碼")
        
        return value.strip()

    def validate_appointment_time(self, value):
        """驗證預約時間"""
        if value <= timezone.now():
            raise serializers.ValidationError("預約時間必須是未來時間")
        return value

    def validate_massage_plan(self, value):
        """驗證按摩方案是否屬於當前店家"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            store = getattr(request.user, "store", None)
            if store and value.store != store:
                raise serializers.ValidationError("所選方案不屬於您的店家")
        return value

    def validate_therapist(self, value):
        """驗證師傅是否屬於當前店家且可用"""
        if value is None:
            return value  # 允許不指定師傅
            
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            store = getattr(request.user, "store", None)
            if store:
                if value.store != store:
                    raise serializers.ValidationError("所選師傅不屬於您的店家")
                if value.is_deleted or not value.enabled:
                    raise serializers.ValidationError("所選師傅不可用")
        return value

    def validate(self, data):
        """跨欄位驗證"""
        massage_plan = data.get('massage_plan')
        therapist = data.get('therapist')
        appointment_time = data.get('appointment_time')

        # 檢查師傅和方案是否屬於同一店家
        if massage_plan and therapist:
            if massage_plan.store != therapist.store:
                raise serializers.ValidationError({
                    'therapist': '師傅和方案必須屬於同一店家'
                })

        # 檢查師傅在該時間段是否已有預約（如果指定了師傅）
        if therapist and appointment_time:
            massage_duration = massage_plan.duration if massage_plan else 60
            start_time = appointment_time
            end_time = appointment_time + timezone.timedelta(minutes=massage_duration)
            
            # 檢查是否有重疊的預約
            overlapping_reservations = Reservation.objects.filter(
                therapist=therapist,
                appointment_time__lt=end_time,
                appointment_time__gt=start_time - timezone.timedelta(minutes=120)  # 假設最長2小時
            ).exclude(id=self.instance.id if self.instance else None)
            
            if overlapping_reservations.exists():
                raise serializers.ValidationError({
                    'appointment_time': '該師傅在此時間段已有其他預約'
                })

        return data


class SimpleReservationSerializer(serializers.ModelSerializer):
    """簡化版預約序列化器，用於列表顯示"""
    massage_plan_name = serializers.CharField(source='massage_plan.name', read_only=True)
    therapist_name = serializers.CharField(source='therapist.name', read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'customer_name', 'customer_phone', 'appointment_time',
            'massage_plan_name', 'therapist_name'
        ]


class MassageInvitationSerializer(serializers.ModelSerializer):
    massage_plan_name = serializers.CharField(source='massage_plan.name', read_only=True)
    massage_plan_duration = serializers.IntegerField(source='massage_plan.duration', read_only=True)
    massage_plan_original_price = serializers.DecimalField(source='massage_plan.price', max_digits=10, decimal_places=2, read_only=True)
    therapist_name = serializers.CharField(source='therapist.name', read_only=True)
    store_name = serializers.CharField(source='massage_plan.store.name', read_only=True)
    invitation_url = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = MassageInvitation
        fields = [
            'id', 'start_time', 'end_time', 'massage_plan', 'massage_plan_name', 
            'massage_plan_duration', 'massage_plan_original_price', 'therapist', 
            'therapist_name', 'discount_price', 'discount_amount', 'slug', 
            'click_count', 'notes', 'store_name', 'invitation_url', 'is_active',
            'time_remaining', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'click_count', 'created_at', 'updated_at']

    def get_invitation_url(self, obj):
        """生成完整的邀請連結"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/invitation/{obj.slug}/')
        return f'/invitation/{obj.slug}/'

    def get_discount_amount(self, obj):
        """計算折扣金額"""
        if obj.massage_plan:
            return float(obj.massage_plan.price - obj.discount_price)
        return 0

    def get_is_active(self, obj):
        """檢查邀請是否仍然有效"""
        now = timezone.now()
        return obj.start_time <= now <= obj.end_time

    def get_time_remaining(self, obj):
        """計算剩餘時間（分鐘）"""
        now = timezone.now()
        if now > obj.end_time:
            return 0
        elif now < obj.start_time:
            return int((obj.start_time - now).total_seconds() / 60)
        else:
            return int((obj.end_time - now).total_seconds() / 60)

    def validate_start_time(self, value):
        """驗證開始時間"""
        if value <= timezone.now():
            raise serializers.ValidationError("開始時間必須是未來時間")
        return value

    def validate_end_time(self, value):
        """驗證結束時間"""
        if value <= timezone.now():
            raise serializers.ValidationError("結束時間必須是未來時間")
        return value

    def validate_discount_price(self, value):
        """驗證特價必須大於 0"""
        if value <= 0:
            raise serializers.ValidationError("特價必須大於 0")
        return value

    def validate_massage_plan(self, value):
        """驗證按摩方案是否屬於當前店家"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            store = getattr(request.user, "store", None)
            if store and value.store != store:
                raise serializers.ValidationError("所選方案不屬於您的店家")
        return value

    def validate_therapist(self, value):
        """驗證師傅是否屬於當前店家且可用"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            store = getattr(request.user, "store", None)
            if store:
                if value.store != store:
                    raise serializers.ValidationError("所選師傅不屬於您的店家")
                if value.is_deleted or not value.enabled:
                    raise serializers.ValidationError("所選師傅不可用")
        return value

    def validate(self, data):
        """跨欄位驗證"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        discount_price = data.get('discount_price')
        massage_plan = data.get('massage_plan')
        therapist = data.get('therapist')

        # 檢查結束時間是否在開始時間之後
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': '結束時間必須在開始時間之後'
            })

        # 檢查特價是否不超過原價
        if discount_price and massage_plan and discount_price >= massage_plan.price:
            raise serializers.ValidationError({
                'discount_price': '特價必須低於原價'
            })

        # 檢查師傅和方案是否屬於同一店家
        if massage_plan and therapist:
            if massage_plan.store != therapist.store:
                raise serializers.ValidationError({
                    'therapist': '師傅和方案必須屬於同一店家'
                })

        # 檢查師傅在該時間段是否已有其他邀請或預約
        if therapist and start_time and end_time:
            # 檢查邀請衝突
            overlapping_invitations = MassageInvitation.objects.filter(
                therapist=therapist,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(id=self.instance.id if self.instance else None)
            
            if overlapping_invitations.exists():
                raise serializers.ValidationError({
                    'start_time': '該師傅在此時間段已有其他邀請'
                })

            # 檢查預約衝突
            overlapping_reservations = Reservation.objects.filter(
                therapist=therapist,
                appointment_time__gte=start_time,
                appointment_time__lt=end_time
            )
            
            if overlapping_reservations.exists():
                raise serializers.ValidationError({
                    'start_time': '該師傅在此時間段已有預約'
                })

        return data


class PublicMassageInvitationSerializer(serializers.ModelSerializer):
    """公開邀請序列化器，用於客人查看邀請詳情"""
    massage_plan_name = serializers.CharField(source='massage_plan.name', read_only=True)
    massage_plan_duration = serializers.IntegerField(source='massage_plan.duration', read_only=True)
    massage_plan_original_price = serializers.DecimalField(source='massage_plan.price', max_digits=10, decimal_places=2, read_only=True)
    therapist_name = serializers.CharField(source='therapist.name', read_only=True)
    store_name = serializers.CharField(source='massage_plan.store.name', read_only=True)
    store_address = serializers.CharField(source='massage_plan.store.address', read_only=True)
    store_phone = serializers.CharField(source='massage_plan.store.phone', read_only=True)
    discount_amount = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = MassageInvitation
        fields = [
            'start_time', 'end_time', 'massage_plan_name', 'massage_plan_duration', 
            'massage_plan_original_price', 'therapist_name', 'discount_price', 
            'discount_amount', 'notes', 'store_name', 'store_address', 'store_phone',
            'is_active', 'time_remaining'
        ]

    def get_discount_amount(self, obj):
        """計算折扣金額"""
        if obj.massage_plan:
            return float(obj.massage_plan.price - obj.discount_price)
        return 0

    def get_is_active(self, obj):
        """檢查邀請是否仍然有效"""
        now = timezone.now()
        return obj.start_time <= now <= obj.end_time

    def get_time_remaining(self, obj):
        """計算剩餘時間（分鐘）"""
        now = timezone.now()
        if now > obj.end_time:
            return 0
        elif now < obj.start_time:
            return int((obj.start_time - now).total_seconds() / 60)
        else:
            return int((obj.end_time - now).total_seconds() / 60)        