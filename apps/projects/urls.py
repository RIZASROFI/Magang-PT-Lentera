"""
Project Management URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectCategoryViewSet, ProjectViewSet, ProjectLocationViewSet,
    ProjectProgressViewSet, TeamAssignmentViewSet, ProjectMilestoneViewSet,
    ProjectDocumentViewSet
)

router = DefaultRouter()
router.register(r'categories', ProjectCategoryViewSet, basename='project-category')
router.register(r'', ProjectViewSet, basename='project')

# Nested routes for project-related data
project_nested_router = DefaultRouter()
project_nested_router.register(r'locations', ProjectLocationViewSet, basename='project-location')
project_nested_router.register(r'progress', ProjectProgressViewSet, basename='project-progress')
project_nested_router.register(r'team', TeamAssignmentViewSet, basename='team-assignment')
project_nested_router.register(r'milestones', ProjectMilestoneViewSet, basename='project-milestone')
project_nested_router.register(r'documents', ProjectDocumentViewSet, basename='project-document')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:project_pk>/', include(project_nested_router.urls)),
]
