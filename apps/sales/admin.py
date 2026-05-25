"""
Sales Admin
"""

from django.contrib import admin
from .models import (
    Customer, Vendor, Quotation, QuotationItem,
    SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'phone', 'city', 'is_active']
    list_filter = ['is_active', 'city']
    search_fields = ['name', 'code', 'phone', 'email']


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'phone', 'city', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quotation_number', 'customer', 'date', 'total', 'status']
    list_filter = ['status', 'date']
    search_fields = ['quotation_number', 'customer__name']
    inlines = [QuotationItemInline]


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['sales_order_number', 'customer', 'date', 'total', 'status']
    list_filter = ['status', 'date']
    search_fields = ['sales_order_number', 'customer__name']
    inlines = [SalesOrderItemInline]


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['purchase_order_number', 'vendor', 'date', 'total', 'status']
    list_filter = ['status', 'date']
    search_fields = ['purchase_order_number', 'vendor__name']
    inlines = [PurchaseOrderItemInline]
