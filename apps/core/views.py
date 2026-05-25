"""
Core Views - User Management & Authentication Views
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model, login as auth_login, logout as auth_logout
from .models import User, Notification, SystemSetting, ActivityLog
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, LoginSerializer, NotificationSerializer,
    ActivityLogSerializer, SystemSettingSerializer
)
from .permissions import IsAdminOrReadOnly, IsAdmin

User = get_user_model()


class AuthViewSet(viewsets.ViewSet):
    """ViewSet untuk Authentication"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login endpoint"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Create Django session for frontend
            auth_login(request, user)
            
            # Update last login IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            user.last_login_ip = ip
            user.save(update_fields=['last_login_ip'])
            
            # Log activity
            ActivityLog.objects.create(
                user=user,
                action='login',
                model_name='auth',
                description=f'User {user.email} login from {ip}',
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
            )
            
            # Return user info only; session cookie set by auth_login
            return Response({
                'message': 'Login berhasil',
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout endpoint"""
        try:
            # Destroy Django session
            if request.user.is_authenticated:
                ActivityLog.objects.create(
                    user=request.user,
                    action='logout',
                    model_name='auth',
                    description=f'User {request.user.email} logout'
                )
            auth_logout(request)
            return Response({'message': 'Logout berhasil!'})
        except Exception as e:
            return Response({'message': 'Logout gagal!'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user info"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh(self, request):
        """Refresh access token"""
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token diperlukan'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            return Response({'access': str(token.access_token)})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet untuk manajemen User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Ubah password user"""
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'Password lama salah!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            ActivityLog.objects.create(
                user=user,
                action='update',
                model_name='User',
                object_id=user.id,
                description='Password changed',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return Response({'message': 'Password berhasil diubah!'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """User statistics"""
        total = User.objects.count()
        active = User.objects.filter(is_active=True).count()
        admin = User.objects.filter(role='admin').count()
        manager = User.objects.filter(role='manager').count()
        staff = User.objects.filter(role='staff').count()
        
        return Response({
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_role': {
                'admin': admin,
                'manager': manager,
                'staff': staff
            }
        })


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Notification"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Tandai semua notifikasi sebagai sudah dibaca"""
        self.get_queryset().update(is_read=True, read_at=timezone.now())
        return Response({'message': 'Semua notifikasi ditandai sudah dibaca!'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Jumlah notifikasi yang belum dibaca"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})


from django.utils import timezone


class SystemSettingViewSet(viewsets.ModelViewSet):
    """ViewSet untuk System Settings"""
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['key', 'is_active']
    search_fields = ['key', 'description']


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet untuk Activity Log (Read Only)"""
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['user', 'action', 'model_name']
    search_fields = ['description']
    
    def get_queryset(self):
        queryset = ActivityLog.objects.all()
        
        # Filter by user
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by model
        model_name = self.request.query_params.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        return queryset


class RegisterView(generics.CreateAPIView):
    """View untuk Registrasi User baru"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=user,
            action='create',
            model_name='User',
            object_id=user.id,
            description=f'User {user.email} registered'
        )
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
