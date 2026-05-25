"""
Core API URLs - User Management & Authentication
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet, UserViewSet, NotificationViewSet, 
    SystemSettingViewSet, ActivityLogViewSet, RegisterView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='user')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'settings', SystemSettingViewSet, basename='setting')
router.register(r'activity-log', ActivityLogViewSet, basename='activity-log')

urlpatterns = [
    path('', include(router.urls)),
    
    # JWT Auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Register API
    path('register/', RegisterView.as_view(), name='api_register'),
]
