from rest_framework import serializers
from .models import MassagePlan, Therapist, ServiceSurvey


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