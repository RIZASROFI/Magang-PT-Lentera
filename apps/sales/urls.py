"""
Sales URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet, VendorViewSet, QuotationViewSet,
    SalesOrderViewSet, PurchaseOrderViewSet, SalesReportViewSet
)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'vendors', VendorViewSet, basename='vendor')
router.register(r'quotations', QuotationViewSet, basename='quotation')
router.register(r'sales-orders', SalesOrderViewSet, basename='sales-order')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'reports', SalesReportViewSet, basename='sales-report')

urlpatterns = [
    path('', include(router.urls)),
]
