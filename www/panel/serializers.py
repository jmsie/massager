from rest_framework import serializers
from .models import Therapist, ServiceSurvey


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