"""
Finance Serializers
"""

from rest_framework import serializers
from .models import (
    Account, JournalEntry, JournalEntryItem, IncomeCategory, Income,
    ExpenseCategory, Expense, Invoice, InvoiceItem, Payment
)


class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.ReadOnlyField()
    subaccounts = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'code', 'name', 'account_type', 'parent', 'subaccounts',
            'description', 'is_active', 'is_cash', 'balance', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_subaccounts(self, obj):
        subaccounts = obj.subaccounts.all()
        return AccountSerializer(subaccounts, many=True).data if subaccounts else []


class JournalEntryItemSerializer(serializers.ModelSerializer):
    account_name = serializers.ReadOnlyField(source='account.name')
    
    class Meta:
        model = JournalEntryItem
        fields = ['id', 'account', 'account_name', 'description', 'debit', 'credit']


class JournalEntryListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = JournalEntry
        fields = [
            'id', 'entry_number', 'date', 'description', 'reference_number',
            'status', 'created_by_name', 'created_at'
        ]


class JournalEntryDetailSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    approved_by_name = serializers.ReadOnlyField(source='approved_by.email')
    items = JournalEntryItemSerializer(many=True)
    total_debit = serializers.ReadOnlyField()
    total_credit = serializers.ReadOnlyField()
    
    class Meta:
        model = JournalEntry
        fields = [
            'id', 'entry_number', 'date', 'description', 'reference_number',
            'reference_date', 'status', 'created_by', 'created_by_name', 
            'approved_by', 'approved_by_name', 'items', 'total_debit',
            'total_credit', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'entry_number': {'required': False},
        }
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        journal_entry = JournalEntry.objects.create(**validated_data)
        for item_data in items_data:
            JournalEntryItem.objects.create(journal_entry=journal_entry, **item_data)
        return journal_entry


class IncomeCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = IncomeCategory
        fields = ['id', 'name', 'code', 'account', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class IncomeSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    account_name = serializers.ReadOnlyField(source='account.name')
    customer_name = serializers.ReadOnlyField(source='customer.name')
    project_name = serializers.ReadOnlyField(source='project.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = Income
        fields = [
            'id', 'income_number', 'date', 'category', 'category_name', 'amount',
            'description', 'customer', 'customer_name', 'project', 'project_name',
            'account', 'account_name', 'cheque_number', 'cheque_date',
            'status', 'notes', 'created_by', 'created_by_name', 
            'is_completed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExpenseCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'code', 'account', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    account_name = serializers.ReadOnlyField(source='account.name')
    vendor_name = serializers.ReadOnlyField(source='vendor.name')
    project_name = serializers.ReadOnlyField(source='project.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = Expense
        fields = [
            'id', 'expense_number', 'date', 'category', 'category_name', 'amount',
            'description', 'vendor', 'vendor_name', 'project', 'project_name',
            'account', 'account_name', 'cheque_number', 'cheque_date',
            'status', 'notes', 'created_by', 'created_by_name',
            'is_completed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'total']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    customer_name = serializers.ReadOnlyField(source='customer.name')
    project_name = serializers.ReadOnlyField(source='project.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'customer', 'customer_name',
            'project', 'project_name', 'date', 'due_date',
            'subtotal', 'tax', 'discount', 'total',
            'amount_paid', 'amount_due', 'status', 'notes',
            'created_by', 'created_by_name', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)
        
        subtotal = 0
        for item_data in items_data:
            item_data['invoice'] = invoice
            InvoiceItem.objects.create(**item_data)
            subtotal += item_data['total']
        
        invoice.subtotal = subtotal
        invoice.save()
        
        return invoice


class InvoiceListSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.name')
    project_name = serializers.ReadOnlyField(source='project.name')
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'customer', 'customer_name',
            'project', 'project_name', 'date', 'due_date', 'total',
            'amount_paid', 'amount_due', 'status'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.name')
    invoice_number = serializers.ReadOnlyField(source='invoice.invoice_number')
    account_name = serializers.ReadOnlyField(source='account.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_number', 'payment_type', 'invoice', 'invoice_number',
            'customer', 'customer_name', 'date', 'amount',
            'account', 'account_name', 'cheque_number', 'cheque_date', 'bank',
            'notes', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FinanceReportSerializer(serializers.Serializer):
    """Serializer untuk Laporan Keuangan"""
    period = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    cash_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    receivables = serializers.DecimalField(max_digits=15, decimal_places=2)
    payables = serializers.DecimalField(max_digits=15, decimal_places=2)
