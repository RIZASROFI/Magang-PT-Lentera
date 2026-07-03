"""
Inventory Serializers
"""

from rest_framework import serializers
from .models import (
    Category, Item, Supplier, 
    StockOut, StockOutItem, StockOpname, StockOpnameItem, StockAlert
)


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'description', 'parent', 'subcategories', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_subcategories(self, obj):
        subcategories = obj.subcategories.all()
        return CategorySerializer(subcategories, many=True).data if subcategories else []


class ItemListSerializer(serializers.ModelSerializer):
    """Serializer untuk list item"""
    category_name = serializers.ReadOnlyField(source='category.name')
    current_stock = serializers.ReadOnlyField()
    supplier_name = serializers.ReadOnlyField(source='default_supplier.name')
    
    class Meta:
        model = Item
        fields = [
            'id', 'name', 'sku', 'barcode', 'category', 'category_name',
            'brand', 'model', 'unit', 'current_stock', 'cost_price', 
            'sell_price', 'min_stock', 'warehouse_location', 'is_active',
            'supplier_name', 'image'
        ]


class ItemDetailSerializer(serializers.ModelSerializer):
    """Serializer untuk detail item"""
    category_name = serializers.ReadOnlyField(source='category.name')
    current_stock = serializers.ReadOnlyField()
    supplier_name = serializers.ReadOnlyField(source='default_supplier.name')
    
    class Meta:
        model = Item
        fields = [
            'id', 'name', 'sku', 'barcode', 'category', 'category_name',
            'brand', 'model', 'specs', 'unit', 'min_stock', 'max_stock',
            'cost_price', 'sell_price', 'warehouse_location', 'rack_location',
            'is_active', 'is_trackable', 'has_expiry', 'image', 'default_supplier',
            'supplier_name', 'created_by', 'created_at', 'updated_at', 'current_stock'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ItemCreateSerializer(serializers.ModelSerializer):
    """Serializer untuk membuat item"""
    
    class Meta:
        model = Item
        fields = [
            'name', 'sku', 'barcode', 'category', 'brand', 'model',
            'specs', 'unit', 'min_stock', 'max_stock', 'cost_price', 'sell_price',
            'warehouse_location', 'rack_location', 'is_active', 'is_trackable', 
            'has_expiry', 'image', 'default_supplier'
        ]
    
    def validate_sku(self, value):
        if Item.objects.filter(sku=value).exists():
            raise serializers.ValidationError('SKU sudah ada!')
        return value


class SupplierSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'code', 'contact_person', 'phone', 'email',
            'address', 'city', 'notes', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']




class StockOutItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    item_sku = serializers.ReadOnlyField(source='item.sku')
    
    class Meta:
        model = StockOutItem
        fields = [
            'id', 'item', 'item_name', 'item_sku', 'quantity', 
            'unit_price', 'total', 'notes'
        ]


class StockOutListSerializer(serializers.ModelSerializer):
    """Serializer untuk list stock out"""
    project_name = serializers.ReadOnlyField(source='project.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    items_list = serializers.SerializerMethodField()
    
    class Meta:
        model = StockOut
        fields = [
            'id', 'transaction_number', 'out_type', 'project', 'project_name',
            'reference_number', 'transaction_date', 'status', 'total_items',
            'total_amount', 'delivered_to', 'created_by_name', 'created_at',
            'items_list'
        ]
    
    def get_items_list(self, obj):
        items = obj.items.select_related('item').all()
        return [
            {
                'name': it.item.name if it.item else '(item dihapus)',
                'quantity': it.quantity
            }
            for it in items
        ]


class StockOutDetailSerializer(serializers.ModelSerializer):
    """Serializer untuk detail stock out"""
    project_name = serializers.ReadOnlyField(source='project.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    approved_by_name = serializers.ReadOnlyField(source='approved_by.email')
    items = StockOutItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = StockOut
        fields = [
            'id', 'transaction_number', 'out_type', 'project', 'project_name',
            'reference_number', 'transaction_date', 'delivered_date', 'status',
            'notes', 'total_items', 'total_amount', 'delivered_to', 'created_by',
            'created_by_name', 'approved_by', 'approved_by_name', 'is_completed',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockOutCreateSerializer(serializers.ModelSerializer):
    """Serializer untuk membuat stock out"""
    items = StockOutItemSerializer(many=True)
    
    class Meta:
        model = StockOut
        fields = [
            'out_type', 'project', 'reference_number', 'transaction_date',
            'delivered_to', 'notes', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        stock_out = StockOut.objects.create(**validated_data)
        
        total_items = 0
        total_amount = 0
        
        for item_data in items_data:
            item_data['stock_out'] = stock_out
            stock_item = StockOutItem.objects.create(**item_data)
            total_items += stock_item.quantity
            total_amount += stock_item.total
        
        stock_out.total_items = total_items
        stock_out.total_amount = total_amount
        stock_out.save()
        
        return stock_out


class StockOpnameItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    item_sku = serializers.ReadOnlyField(source='item.sku')
    
    class Meta:
        model = StockOpnameItem
        fields = [
            'id', 'item', 'item_name', 'item_sku', 'system_quantity',
            'actual_quantity', 'difference', 'notes'
        ]


class StockOpnameListSerializer(serializers.ModelSerializer):
    """Serializer untuk list stock opname"""
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = StockOpname
        fields = [
            'id', 'opname_number', 'start_date', 'end_date', 'status',
            'total_system', 'total_actual', 'difference', 'created_by_name', 'created_at'
        ]


class StockOpnameDetailSerializer(serializers.ModelSerializer):
    """Serializer untuk detail stock opname"""
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    items = StockOpnameItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = StockOpname
        fields = [
            'id', 'opname_number', 'start_date', 'end_date', 'status',
            'notes', 'total_system', 'total_actual', 'difference',
            'created_by', 'created_by_name', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockOpnameCreateSerializer(serializers.ModelSerializer):
    """Serializer untuk membuat stock opname"""
    items = StockOpnameItemSerializer(many=True)
    
    class Meta:
        model = StockOpname
        fields = ['start_date', 'end_date', 'notes', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        stock_opname = StockOpname.objects.create(**validated_data)
        
        for item_data in items_data:
            item_data['stock_opname'] = stock_opname
            item_data['difference'] = item_data.get('actual_quantity', 0) - item_data.get('system_quantity', 0)
            StockOpnameItem.objects.create(**item_data)
        
        return stock_opname


class StockAlertSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    item_sku = serializers.ReadOnlyField(source='item.sku')
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'item', 'item_name', 'item_sku', 'alert_type',
            'current_stock', 'threshold', 'is_active', 'created_at'
        ]


class StockOutCreateSerializer(serializers.ModelSerializer):
    """Serializer untuk membuat stock out"""
    items = StockOutItemSerializer(many=True)
    
    class Meta:
        model = StockOut
        fields = [
            'out_type', 'project', 'reference_number', 'transaction_date',
            'notes', 'delivered_to', 'items'
        ]
    
    def validate_items(self, items):
        """
        Validasi: pastikan stok setiap item mencukupi untuk transaksi barang keluar.
        """
        if not items:
            raise serializers.ValidationError('Minimal 1 item harus diisi.')
        
        errors = []
        for i, item_data in enumerate(items):
            item_obj = item_data.get('item')
            quantity = item_data.get('quantity', 0)
            
            if item_obj and quantity > 0:
                # Refresh item from DB to get latest stock
                item_from_db = Item.objects.get(pk=item_obj.id)
                if item_from_db.current_stock < quantity:
                    errors.append(f"{item_from_db.name}: stok tersedia {item_from_db.current_stock}, diminta {quantity}")
        
        if errors:
            raise serializers.ValidationError(
                {'items': errors}
            )
        
        return items
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        stock_out = StockOut.objects.create(**validated_data)
        
        total_items = 0
        total_amount = 0
        
        for item_data in items_data:
            item_data['stock_out'] = stock_out
            item = Item.objects.get(pk=item_data['item'].id)
            item_data['unit_price'] = item.cost_price
            stock_item = StockOutItem.objects.create(**item_data)
            
            # Kurangi stok barang secara otomatis
            item.current_stock -= stock_item.quantity
            item.save(update_fields=['current_stock'])
            
            total_items += stock_item.quantity
            total_amount += stock_item.total
        
        stock_out.total_items = total_items
        stock_out.total_amount = total_amount
        stock_out.save(update_fields=['total_items', 'total_amount'])
        
        return stock_out


class StockOpnameItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    item_sku = serializers.ReadOnlyField(source='item.sku')
    
    class Meta:
        model = StockOpnameItem
        fields = [
            'id', 'item', 'item_name', 'item_sku', 
            'system_quantity', 'actual_quantity', 'difference', 'notes'
        ]


class StockOpnameSerializer(serializers.ModelSerializer):
    items = StockOpnameItemSerializer(many=True, read_only=True)
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = StockOpname
        fields = [
            'id', 'opname_number', 'start_date', 'end_date', 'status',
            'notes', 'total_system', 'total_actual', 'difference',
            'created_by', 'created_by_name', 'created_at', 'items'
        ]
        read_only_fields = ['id', 'created_at']


class StockAlertSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    item_sku = serializers.ReadOnlyField(source='item.sku')
    resolved_by_name = serializers.ReadOnlyField(source='resolved_by.email')
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'item', 'item_name', 'item_sku', 'alert_type',
            'is_resolved', 'resolved_by', 'resolved_by_name', 'resolved_at',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StockReportSerializer(serializers.Serializer):
    """Serializer untuk laporan stok"""
    item = serializers.DictField()
    stock_in = serializers.IntegerField()
    stock_out = serializers.IntegerField()
    current_stock = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2)
