"""
Project Management Views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from .models import (
    ProjectCategory, Project, ProjectLocation, ProjectProgress,
    TeamAssignment, ProjectMilestone, ProjectDocument
)
from .serializers import (
    ProjectCategorySerializer, ProjectListSerializer, ProjectDetailSerializer,
    ProjectCreateSerializer, ProjectUpdateSerializer,
    ProjectLocationSerializer, ProjectProgressSerializer,
    TeamAssignmentSerializer, ProjectMilestoneSerializer,
    ProjectDocumentSerializer
)


class ProjectFilter(filters.FilterSet):
    """Filter for Project"""
    status = filters.ChoiceFilter(choices=Project.STATUS_CHOICES)
    priority = filters.ChoiceFilter(choices=Project.PRIORITY_CHOICES)
    category = filters.NumberFilter(field_name='category_id')
    leader = filters.NumberFilter(field_name='leader_id')
    start_date_from = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    due_date_from = filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_date_to = filters.DateFilter(field_name='due_date', lookup_expr='lte')
    city = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Project
        fields = ['status', 'priority', 'category', 'leader', 'city']


class ProjectCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Project Category"""
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Project Management"""
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_class = ProjectFilter
    search_fields = ['project_code', 'name', 'client_name', 'address', 'city']
    ordering_fields = ['created_at', 'start_date', 'due_date', 'contract_value']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectUpdateSerializer
        return ProjectDetailSerializer
    
    def get_queryset(self):
        queryset = Project.objects.select_related(
            'category', 'leader', 'created_by'
        ).prefetch_related(
            'locations', 'progresses', 'team_assignments', 
            'milestones', 'documents'
        )
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by active
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update progress proyek"""
        project = self.get_object()
        serializer = ProjectProgressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project, reported_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign_team(self, request, pk=None):
        """Assign team to project"""
        project = self.get_object()
        user_id = request.data.get('user')
        role = request.data.get('role', 'technician')
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            assignment, created = TeamAssignment.objects.update_or_create(
                project=project,
                user=user,
                defaults={'role': role}
            )
            return Response({'message': 'Tim ditambahkan!'})
        except User.DoesNotExist:
            return Response({'error': 'User tidak ditemukan!'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unassign_team(self, request, pk=None):
        """Unassign team from project"""
        project = self.get_object()
        user_id = request.data.get('user')
        
        try:
            assignment = TeamAssignment.objects.get(project=project, user_id=user_id)
            assignment.delete()
            return Response({'message': 'Tim dihapus dari proyek!'})
        except TeamAssignment.DoesNotExist:
            return Response({'error': 'Assignment tidak ditemukan!'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Project statistics"""
        total = Project.objects.count()
        draft = Project.objects.filter(status='draft').count()
        survey = Project.objects.filter(status='survey').count()
        progress = Project.objects.filter(status='progress').count()
        pending = Project.objects.filter(status='pending').count()
        testing = Project.objects.filter(status='testing').count()
        completed = Project.objects.filter(status='completed').count()
        canceled = Project.objects.filter(status='canceled').count()
        
        # Priority stats
        urgent = Project.objects.filter(priority='urgent').count()
        high = Project.objects.filter(priority='high').count()
        
        # Total nilai kontrak
        total_value = sum(p.contract_value for p in Project.objects.all())
        
        # Recent projects
        recent = Project.objects.order_by('-created_at')[:5]
        
        return Response({
            'total': total,
            'by_status': {
                'draft': draft,
                'survey': survey,
                'progress': progress,
                'pending': pending,
                'testing': testing,
                'completed': completed,
                'canceled': canceled
            },
            'by_priority': {
                'urgent': urgent,
                'high': high
            },
            'total_value': total_value,
            'recent_projects': ProjectListSerializer(recent, many=True).data
        })


class ProjectLocationViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Project Location"""
    serializer_class = ProjectLocationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProjectLocation.objects.filter(project_id=self.kwargs['project_pk'])
    
    def perform_create(self, serializer):
        from .models import Project
        project = Project.objects.get(pk=self.kwargs['project_pk'])
        serializer.save(project=project)


class ProjectProgressViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Project Progress"""
    serializer_class = ProjectProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProjectProgress.objects.filter(project_id=self.kwargs['project_pk'])
    
    def perform_create(self, serializer):
        from .models import Project
        project = Project.objects.get(pk=self.kwargs['project_pk'])
        serializer.save(project=project, reported_by=self.request.user)


class TeamAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Team Assignment"""
    serializer_class = TeamAssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TeamAssignment.objects.filter(project_id=self.kwargs['project_pk'])
    
    def perform_create(self, serializer):
        from .models import Project
        project = Project.objects.get(pk=self.kwargs['project_pk'])
        serializer.save(project=project)


class ProjectMilestoneViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Project Milestone"""
    serializer_class = ProjectMilestoneSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProjectMilestone.objects.filter(project_id=self.kwargs['project_pk'])
    
    def perform_create(self, serializer):
        from .models import Project
        project = Project.objects.get(pk=self.kwargs['project_pk'])
        serializer.save(project=project)


class ProjectDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Project Document"""
    serializer_class = ProjectDocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProjectDocument.objects.filter(project_id=self.kwargs['project_pk'])
    
    def perform_create(self, serializer):
        from .models import Project
        project = Project.objects.get(pk=self.kwargs['project_pk'])
        serializer.save(project=project, uploaded_by=self.request.user)
