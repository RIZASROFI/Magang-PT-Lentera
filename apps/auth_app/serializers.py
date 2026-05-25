"""
Auth App Serializers
"""

from rest_framework import serializers


class LoginResponseSerializer(serializers.Serializer):
    """Standard login response"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.DictField()
    message = serializers.CharField(required=False)
