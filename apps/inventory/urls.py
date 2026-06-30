"""
Inventory URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ItemViewSet, SupplierViewSet, 
    StockOutViewSet, StockOpnameViewSet,
    StockAlertViewSet, InventoryReportViewSet,
    item_create_view, item_edit_view
)

urlpatterns_forms = [
    path('items/create/', item_create_view, name='inventory_item_create'),
    path('items/<int:id>/edit/', item_edit_view, name='inventory_item_edit'),
]


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'stock-out', StockOutViewSet, basename='stock-out')
router.register(r'stock-opname', StockOpnameViewSet, basename='stock-opname')
router.register(r'alerts', StockAlertViewSet, basename='alert')
router.register(r'reports', InventoryReportViewSet, basename='inventory-report')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(urlpatterns_forms)),

]

