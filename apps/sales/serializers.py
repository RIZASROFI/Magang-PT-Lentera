"""
Sales & Purchase Serializers
"""

from rest_framework import serializers
from .models import (
    Customer, Vendor, Quotation, QuotationItem,
    SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem
)


class CustomerSerializer(serializers.ModelSerializer):
    total_sales = serializers.ReadOnlyField()
    receivables = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'code', 'contact_person', 'phone', 'email',
            'address', 'city', 'province', 'npwp', 'npwp_address',
            'business_type', 'notes', 'is_active', 'total_sales',
            'receivables', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VendorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Vendor
        fields = [
            'id', 'name', 'code', 'contact_person', 'phone', 'email',
            'address', 'city', 'notes', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class QuotationItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    
    class Meta:
        model = QuotationItem
        fields = ['id', 'item', 'item_name', 'description', 'quantity', 'unit_price', 'discount', 'total']


class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True)
    customer_name = serializers.ReadOnlyField(source='customer.name')
    project_name = serializers.ReadOnlyField(source='project.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = Quotation
        fields = [
            'id', 'quotation_number', 'customer', 'customer_name',
            'project', 'project_name', 'date', 'valid_until',
            'subtotal', 'tax', 'discount', 'total',
            'payment_terms', 'delivery_terms', 'notes', 'status',
            'created_by', 'created_by_name', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        quotation = Quotation.objects.create(**validated_data)
        
        subtotal = 0
        for item_data in items_data:
            item_data['quotation'] = quotation
            QuotationItem.objects.create(**item_data)
            subtotal += item_data['total']
        
        quotation.subtotal = subtotal
        quotation.save()
        
        return quotation


class SalesOrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    
    class Meta:
        model = SalesOrderItem
        fields = ['id', 'item', 'item_name', 'description', 'quantity', 'unit_price', 'discount', 'total']


class SalesOrderSerializer(serializers.ModelSerializer):
    items = SalesOrderItemSerializer(many=True)
    customer_name = serializers.ReadOnlyField(source='customer.name')
    project_name = serializers.ReadOnlyField(source='project.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = SalesOrder
        fields = [
            'id', 'sales_order_number', 'quotation', 'customer', 'customer_name',
            'project', 'project_name', 'date', 'delivery_date',
            'subtotal', 'tax', 'discount', 'total',
            'terms', 'notes', 'status',
            'created_by', 'created_by_name', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sales_order = SalesOrder.objects.create(**validated_data)
        
        subtotal = 0
        for item_data in items_data:
            item_data['sales_order'] = sales_order
            SalesOrderItem.objects.create(**item_data)
            subtotal += item_data['total']
        
        sales_order.subtotal = subtotal
        sales_order.save()
        
        return sales_order


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'item', 'item_name', 'quantity', 'unit_price', 'discount', 'total']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)
    vendor_name = serializers.ReadOnlyField(source='vendor.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'purchase_order_number', 'vendor', 'vendor_name',
            'date', 'delivery_date', 'subtotal', 'tax', 'discount', 'total',
            'notes', 'status', 'created_by', 'created_by_name',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        
        subtotal = 0
        for item_data in items_data:
            item_data['purchase_order'] = purchase_order
            PurchaseOrderItem.objects.create(**item_data)
            subtotal += item_data['total']
        
        purchase_order.subtotal = subtotal
        purchase_order.save()
        
        return purchase_order
