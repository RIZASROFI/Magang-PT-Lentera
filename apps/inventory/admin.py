"""
Inventory Admin
"""

from django.contrib import admin
from .models import (
    Category, Item, Supplier, StockIn, StockInItem,
    StockOut, StockOutItem, StockOpname, StockOpnameItem, StockAlert
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


class StockInItemInline(admin.TabularInline):
    model = StockInItem
    extra = 1


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'unit', 'cost_price', 'sell_price', 'is_active']
    list_filter = ['category', 'is_active', 'unit']
    search_fields = ['name', 'sku', 'barcode', 'brand', 'model']
    ordering = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'phone', 'city', 'is_active']
    list_filter = ['is_active', 'city']
    search_fields = ['name', 'code', 'phone', 'email']
    ordering = ['name']


@admin.register(StockIn)
class StockInAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'source', 'supplier', 'status', 'transaction_date', 'is_completed']
    list_filter = ['status', 'source', 'transaction_date']
    search_fields = ['transaction_number', 'reference_number']
    inlines = [StockInItemInline]
    date_hierarchy = 'transaction_date'


class StockOutItemInline(admin.TabularInline):
    model = StockOutItem
    extra = 1


@admin.register(StockOut)
class StockOutAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'out_type', 'project', 'status', 'transaction_date', 'is_completed']
    list_filter = ['status', 'out_type', 'transaction_date']
    search_fields = ['transaction_number', 'reference_number']
    inlines = [StockOutItemInline]
    date_hierarchy = 'transaction_date'


class StockOpnameItemInline(admin.TabularInline):
    model = StockOpnameItem
    extra = 1


@admin.register(StockOpname)
class StockOpnameAdmin(admin.ModelAdmin):
    list_display = ['opname_number', 'start_date', 'status', 'difference']
    list_filter = ['status']
    inlines = [StockOpnameItemInline]


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['item', 'alert_type', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'is_resolved']
    search_fields = ['item__name']
