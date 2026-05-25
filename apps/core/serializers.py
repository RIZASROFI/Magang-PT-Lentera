"""
Core Serializers - User Management Serializers
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, Notification, SystemSetting, ActivityLog


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer untuk UserProfile"""
    
    class Meta:
        model = UserProfile
        fields = [
            'department', 'position', 'employee_id', 'nip', 
            'birth_date', 'birth_place', 'gender', 'religion', 
            'marital_status', 'emergency_contact', 'emergency_phone', 'bio'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer untuk User dengan Profile"""
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField(source='get_full_name')
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'role', 'phone', 'address', 'photo', 
            'is_active', 'profile', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer untuk membuat User baru"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'phone', 'address'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Password tidak cocok!'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer untuk update User"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'address', 'photo', 'role', 'is_active'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer untuk mengubah password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Password tidak cocok!'})
        return attrs


class LoginSerializer(serializers.Serializer):
    """Serializer untuk Login"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                user_obj = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=email).first()
                if user_obj:
                    user = authenticate(username=user_obj.get_username(), password=password)

            if not user:
                raise serializers.ValidationError('Email atau password salah!')
            if not user.is_active:
                raise serializers.ValidationError('Akun dinonaktifkan!')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Email dan password wajib diisi!')
        
        return attrs


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer untuk Notification"""
    sender_name = serializers.ReadOnlyField(source='sender.get_full_name')
    
    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'sender_name', 'title', 'message', 
            'notification_type', 'link', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer untuk Activity Log"""
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'user_name', 'action', 'model_name', 
            'object_id', 'description', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SystemSettingSerializer(serializers.ModelSerializer):
    """Serializer untuk System Settings"""
    
    class Meta:
        model = SystemSetting
        fields = ['id', 'key', 'value', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
