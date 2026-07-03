"""
URL Configuration for SIMAN project.
PT Lentera Anugerah Dimensi
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/', include('apps.core.urls')),
    path('api/auth/', include('apps.auth_app.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/hr/', include('apps.hr.urls')),
    
    # Frontend URLs
    path('', include(('apps.core.frontend_urls', 'frontend'))),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
