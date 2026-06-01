"""
Project Management Serializers
"""

from rest_framework import serializers
from .models import (
    ProjectCategory, Project, ProjectLocation, ProjectProgress,
    TeamAssignment, ProjectMilestone, ProjectDocument
)


class ProjectCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProjectCategory
        fields = ['id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjectLocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProjectLocation
        fields = ['id', 'location_name', 'address', 'latitude', 'longitude', 'notes']
        read_only_fields = ['id']


class TeamAssignmentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    user_email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = TeamAssignment
        fields = [
            'id', 'user', 'user_name', 'user_email', 'role', 
            'assigned_date', 'is_active', 'notes'
        ]
        read_only_fields = ['id', 'assigned_date']


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProjectMilestone
        fields = [
            'id', 'title', 'description', 'due_date', 
            'completed_date', 'is_completed', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProjectDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.get_full_name')
    
    class Meta:
        model = ProjectDocument
        fields = [
            'id', 'title', 'doc_type', 'file', 'description', 
            'uploaded_by', 'uploaded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProjectProgressSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.ReadOnlyField(source='reported_by.get_full_name')
    
    class Meta:
        model = ProjectProgress
        fields = [
            'id', 'date', 'percentage', 'description', 'notes', 
            'photo', 'workers_count', 'status', 'reported_by', 
            'reported_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('Persentase harus antara 0-100!')
        return value


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer untuk list proyek"""
    category_name = serializers.ReadOnlyField(source='category.name')
    leader_name = serializers.ReadOnlyField(source='leader.get_full_name')
    progress_percentage = serializers.ReadOnlyField()
    assigned_teams = TeamAssignmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'project_code', 'name', 'category', 'category_name',
            'client_name', 'city', 'status', 'priority',
            'start_date', 'end_date', 'due_date', 'contract_value',
            'leader', 'leader_name', 'progress_percentage',
            'assigned_teams', 'is_active', 'created_at'
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer untuk detail proyek"""
    category_name = serializers.ReadOnlyField(source='category.name')
    leader_name = serializers.ReadOnlyField(source='leader.get_full_name')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    progress_percentage = serializers.ReadOnlyField()
    
    locations = ProjectLocationSerializer(many=True, read_only=True)
    progresses = ProjectProgressSerializer(many=True, read_only=True)
    team_assignments = TeamAssignmentSerializer(many=True, read_only=True)
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)
    documents = ProjectDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'project_code', 'name', 'category', 'category_name',
            'client_name', 'client_contact', 'client_phone', 'client_email',
            'address', 'city', 'province', 'description', 'scope_of_work',
            'status', 'priority', 'start_date', 'end_date', 'due_date',
            'contract_value', 'leader', 'leader_name', 'created_by', 'created_by_name',
            'progress_percentage', 'locations', 'progresses', 'team_assignments',
            'milestones', 'documents', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer untuk membuat proyek baru"""
    
    class Meta:
        model = Project
        fields = [
            'name', 'category', 'client_name',
            'client_contact', 'client_phone', 'client_email',
            'address', 'city', 'province', 'description', 'scope_of_work',
            'status', 'priority', 'start_date', 'end_date', 'due_date',
            'contract_value', 'leader'
        ]


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Serializer untuk update proyek"""
    
    class Meta:
        model = Project
        fields = [
            'name', 'category', 'client_name', 'client_contact',
            'client_phone', 'client_email', 'address', 'city', 'province',
            'description', 'scope_of_work', 'status', 'priority',
            'start_date', 'end_date', 'due_date', 'contract_value', 'leader', 'is_active'
        ]
