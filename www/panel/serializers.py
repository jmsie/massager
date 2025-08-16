from rest_framework import serializers
from .models import Therapist


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