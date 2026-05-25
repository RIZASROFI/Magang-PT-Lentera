"""
Project Management Admin
"""

from django.contrib import admin
from .models import (
    ProjectCategory, Project, ProjectLocation, ProjectProgress,
    TeamAssignment, ProjectMilestone, ProjectDocument
)


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


class ProjectLocationInline(admin.TabularInline):
    model = ProjectLocation
    extra = 1


class ProjectProgressInline(admin.TabularInline):
    model = ProjectProgress
    extra = 0
    readonly_fields = ['created_at']


class TeamAssignmentInline(admin.TabularInline):
    model = TeamAssignment
    extra = 1


class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_code', 'name', 'client_name', 'status', 'priority', 'city', 'start_date', 'created_at']
    list_filter = ['status', 'priority', 'category', 'city', 'is_active']
    search_fields = ['project_code', 'name', 'client_name', 'address', 'city']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    inlines = [ProjectLocationInline, ProjectProgressInline, TeamAssignmentInline, ProjectMilestoneInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProjectLocation)
class ProjectLocationAdmin(admin.ModelAdmin):
    list_display = ['project', 'location_name', 'city']
    search_fields = ['location_name', 'project__name']
    list_filter = ['city']


@admin.register(ProjectProgress)
class ProjectProgressAdmin(admin.ModelAdmin):
    list_display = ['project', 'date', 'percentage', 'workers_count', 'reported_by']
    list_filter = ['date', 'status']
    search_fields = ['project__name', 'description']
    date_hierarchy = 'date'


@admin.register(TeamAssignment)
class TeamAssignmentAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'role', 'is_active', 'assigned_date']
    list_filter = ['role', 'is_active']
    search_fields = ['project__name', 'user__email']


@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'due_date', 'is_completed']
    list_filter = ['is_completed', 'due_date']
    search_fields = ['title', 'project__name']


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'doc_type', 'uploaded_by', 'created_at']
    list_filter = ['doc_type']
    search_fields = ['title', 'project__name']
    date_hierarchy = 'created_at'
