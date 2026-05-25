"""Frontend URL Patterns for Inventory.

Catatan: proyek ini memakai DRF untuk API (di apps/inventory/urls.py).
Untuk UI halaman tertentu (template), kita mapping di apps/inventory/frontend_urls.py.
"""

from django.urls import path

from . import frontend_views as views

app_name = 'inventory_frontend'

urlpatterns = [
    path('stock-in/', views.stock_in_page, name='stock_in'),
]

