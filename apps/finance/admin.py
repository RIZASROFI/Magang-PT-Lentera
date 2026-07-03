"""
Finance Admin
"""

from django.contrib import admin
from .models import (
    Account, JournalEntry, JournalEntryItem, IncomeCategory, Income,
    ExpenseCategory, Expense, Invoice, InvoiceItem, Payment
)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'is_cash', 'is_active']
    list_filter = ['account_type', 'is_cash', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['code']


class JournalEntryItemInline(admin.TabularInline):
    model = JournalEntryItem
    extra = 1


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_number', 'date', 'description', 'status', 'created_by']
    list_filter = ['status', 'date']
    search_fields = ['entry_number', 'description']
    inlines = [JournalEntryItemInline]
    date_hierarchy = 'date'


@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'account', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['income_number', 'date', 'category', 'amount', 'status']
    list_filter = ['status', 'category', 'date']
    search_fields = ['income_number', 'description']
    date_hierarchy = 'date'


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'account', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['expense_number', 'date', 'category', 'amount', 'vendor', 'status']
    list_filter = ['status', 'category', 'date']
    search_fields = ['expense_number', 'description']
    date_hierarchy = 'date'


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'date', 'total', 'status']
    list_filter = ['status', 'invoice_type', 'date']
    search_fields = ['invoice_number']
    inlines = [InvoiceItemInline]
    date_hierarchy = 'date'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'date', 'amount', 'account']
    list_filter = ['date', 'payment_type']
    search_fields = ['payment_number']
    date_hierarchy = 'date'
