"""
Inventory Models - Transaction Processing System
PT Lentera Anugerah Dimensi - Inventory Module
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    """Kategori Barang"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Item(models.Model):
    """Master Data Barang"""
    UNIT_CHOICES = [
        ('unit', 'Unit'),
        ('pcs', 'Pcs'),
        ('box', 'Box'),
        ('roll', 'Roll'),
        ('meter', 'Meter'),
        ('set', 'Set'),
    ]
    
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, help_text='Stock Keeping Unit')
    barcode = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='items')
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    specs = models.TextField(blank=True, help_text='Spesifikasi teknis')
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pcs')
    min_stock = models.IntegerField(default=0, help_text='Minimum stok')
    max_stock = models.IntegerField(default=0, help_text='Maximum stok')
    cost_price = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Harga beli')
    sell_price = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Harga jual')
    warehouse_location = models.CharField(max_length=100, blank=True)
    rack_location = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_trackable = models.BooleanField(default=True, help_text='Lacak serial number')
    has_expiry = models.BooleanField(default=False)
    image = models.ImageField(upload_to='inventory/items/', blank=True, null=True)
    default_supplier = models.ForeignKey('inventory.Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_items')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory_items'
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.sku} - {self.name}"
    
    @property
    def current_stock(self):
        """Hitung stok saat ini"""
        stock_in = StockIn.objects.filter(items__item=self, is_completed=True).aggregate(total=models.Sum('items__quantity'))['total'] or 0
        stock_out = StockOut.objects.filter(items__item=self, is_completed=True).aggregate(total=models.Sum('items__quantity'))['total'] or 0
        return stock_in - stock_out


class Supplier(models.Model):
    """Supplier/Vendor untuk Pembelian"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_suppliers'
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class StockIn(models.Model):
    """Transaksi Barang Masuk (Purchase/Receive)"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Menunggu Konfirmasi'),
        ('approved', 'Disetujui'),
        ('completed', 'Selesai'),
        ('canceled', 'Dibatalkan'),
    ]
    
    SOURCE_CHOICES = [
        ('purchase', 'Pembelian'),
        ('return', 'Retur'),
        ('adjustment', 'Penyesuaian'),
        ('transfer', 'Transfer'),
    ]
    
    transaction_number = models.CharField(max_length=50, unique=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='purchase')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_ins')
    reference_number = models.CharField(max_length=50, blank=True, help_text='No. PO/Terima')
    reference_date = models.DateField(blank=True, null=True)
    transaction_date = models.DateField()
    received_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    total_items = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stock_ins')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_stock_ins')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_ins'
        verbose_name = 'Stock In'
        verbose_name_plural = 'Stock Ins'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.transaction_number} - {self.get_source_display()}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = StockIn.objects.filter(transaction_number__startswith=f'SI{today}').count() + 1
            self.transaction_number = f'SI{today}{count:04d}'
        super().save(*args, **kwargs)


class StockInItem(models.Model):
    """Item dalam Stock In"""
    stock_in = models.ForeignKey(StockIn, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, related_name='stock_in_items')
    quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    batch_number = models.CharField(max_length=50, blank=True)
    expiry_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'stock_in_items'
    
    def __str__(self):
        item_name = self.item.name if self.item else '(item dihapus)'
        return f"{self.stock_in.transaction_number} - {item_name}"
    
    def save(self, *args, **kwargs):
        self.total = (self.quantity * self.unit_price) - self.discount
        super().save(*args, **kwargs)


class StockOut(models.Model):
    """Transaksi Barang Keluar (Delivery/Usage)"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Menunggu Konfirmasi'),
        ('approved', 'Disetujui'),
        ('completed', 'Selesai'),
        ('canceled', 'Dibatalkan'),
    ]
    
    OUT_TYPE_CHOICES = [
        ('project', 'Proyek'),
        ('sales', 'Penjualan'),
        ('return', 'Retur Supplier'),
        ('adjustment', 'Penyesuaian'),
        ('damaged', 'Barang Rusak'),
    ]
    
    transaction_number = models.CharField(max_length=50, unique=True)
    out_type = models.CharField(max_length=20, choices=OUT_TYPE_CHOICES, default='project')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_outs')
    reference_number = models.CharField(max_length=50, blank=True)
    transaction_date = models.DateField()
    delivered_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    total_items = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stock_outs')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_stock_outs')
    delivered_to = models.CharField(max_length=200, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_outs'
        verbose_name = 'Stock Out'
        verbose_name_plural = 'Stock Outs'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.transaction_number} - {self.get_out_type_display()}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = StockOut.objects.filter(transaction_number__startswith=f'SO{today}').count() + 1
            self.transaction_number = f'SO{today}{count:04d}'
        super().save(*args, **kwargs)


class StockOutItem(models.Model):
    """Item dalam Stock Out"""
    stock_out = models.ForeignKey(StockOut, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, related_name='stock_out_items')
    quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'stock_out_items'
    
    def __str__(self):
        item_name = self.item.name if self.item else '(item dihapus)'
        return f"{self.stock_out.transaction_number} - {item_name}"
    
    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class StockOpname(models.Model):
    """Stok Opname - Audit Stok"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('ongoing', 'Sedang Berlangsung'),
        ('completed', 'Selesai'),
        ('canceled', 'Dibatalkan'),
    ]
    
    opname_number = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    total_system = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_actual = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    difference = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stock_opnames')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_opnames'
        verbose_name = 'Stock Opname'
        verbose_name_plural = 'Stock Opnames'
        ordering = ['-start_date']
    
    def __str__(self):
        return self.opname_number
    
    def save(self, *args, **kwargs):
        if not self.opname_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = StockOpname.objects.filter(opname_number__startswith=f'SOP{today}').count() + 1
            self.opname_number = f'SOP{today}{count:04d}'
        super().save(*args, **kwargs)


class StockOpnameItem(models.Model):
    """Item dalam Stock Opname"""
    stock_opname = models.ForeignKey(StockOpname, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    system_quantity = models.IntegerField(default=0)
    actual_quantity = models.IntegerField(default=0)
    difference = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'stock_opname_items'
    
    def save(self, *args, **kwargs):
        self.difference = self.actual_quantity - self.system_quantity
        super().save(*args, **kwargs)


class StockAlert(models.Model):
    """Stock Alert untuk notifikasi"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_alerts'
        verbose_name = 'Stock Alert'
        verbose_name_plural = 'Stock Alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.item.name} - {self.alert_type}"
