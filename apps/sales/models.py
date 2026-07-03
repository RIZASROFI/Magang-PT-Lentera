"""
Sales & Purchase Models - ERP Module
PT Lentera Anugerah Dimensi - Sales & Purchase Module
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Customer(models.Model):
    """
    Customer Management - ERP
    """
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    
    # Kontak
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Alamat
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    
    # NPWP
    npwp = models.CharField(max_length=50, blank=True)
    npwp_address = models.TextField(blank=True)
    
    # Info Bisnis
    business_type = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales_customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_sales(self):
        """Total penjualan ke customer"""
        from apps.finance.models import Invoice
        return Invoice.objects.filter(
            customer=self,
            status__in=['paid', 'partial']
        ).aggregate(total=models.Sum('total'))['total'] or 0
    
    @property
    def receivables(self):
        """Piutang belum lunas"""
        from apps.finance.models import Invoice
        return Invoice.objects.filter(
            customer=self
        ).exclude(status='paid').aggregate(total=models.Sum('amount_due'))['total'] or 0


class Vendor(models.Model):
    """
    Vendor/Supplier Management - ERP (Reference from Inventory)
    """
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
        db_table = 'sales_vendors'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Quotation(models.Model):
    """
    Penawaran Harga
    ERP - Transaction Processing
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Terkirim'),
        ('accepted', 'Diterima'),
        ('rejected', 'Ditolak'),
        ('expired', 'Kedaluwarsa'),
        ('converted', 'Diubah ke Sales Order'),
    ]
    
    quotation_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='quotations')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='quotations')
    
    date = models.DateField()
    valid_until = models.DateField()
    
    # Nilai
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Terms
    payment_terms = models.TextField(blank=True)
    delivery_terms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='quotations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quotations'
        verbose_name = 'Quotation'
        verbose_name_plural = 'Quotations'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.quotation_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.quotation_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = Quotation.objects.filter(quotation_number__startswith=f'QT{today}').count() + 1
            self.quotation_number = f'QT{today}{count:04d}'
        
        self.total = self.subtotal + self.tax - self.discount
        super().save(*args, **kwargs)


class QuotationItem(models.Model):
    """Item dalam Quotation"""
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey('inventory.Item', on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=200, blank=True)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        db_table = 'quotation_items'

    def save(self, *args, **kwargs):
        self.total = (self.quantity * self.unit_price) - self.discount
        super().save(*args, **kwargs)


class SalesOrder(models.Model):
    """
    Sales Order
    ERP - Transaction Processing
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Dikonfirmasi'),
        ('in_progress', 'Sedang Dikerjakan'),
        ('completed', 'Selesai'),
        ('canceled', 'Dibatalkan'),
    ]
    
    sales_order_number = models.CharField(max_length=50, unique=True)
    quotation = models.ForeignKey(Quotation, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_orders')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales_orders')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_orders')
    
    date = models.DateField()
    delivery_date = models.DateField(blank=True, null=True)
    
    # Nilai
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Terms
    terms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales_orders'
        verbose_name = 'Sales Order'
        verbose_name_plural = 'Sales Orders'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.sales_order_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.sales_order_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = SalesOrder.objects.filter(sales_order_number__startswith=f'SO{today}').count() + 1
            self.sales_order_number = f'SO{today}{count:04d}'
        
        self.total = self.subtotal + self.tax - self.discount
        super().save(*args, **kwargs)


class SalesOrderItem(models.Model):
    """Item dalam Sales Order"""
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey('inventory.Item', on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=200, blank=True)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        db_table = 'sales_order_items'

    def save(self, *args, **kwargs):
        self.total = (self.quantity * self.unit_price) - self.discount
        super().save(*args, **kwargs)


class PurchaseOrder(models.Model):
    """
    Purchase Order
    ERP - Transaction Processing
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Terkirim ke Vendor'),
        ('confirmed', 'Dikonfirmasi Vendor'),
        ('received', 'Diterima'),
        ('completed', 'Selesai'),
        ('canceled', 'Dibatalkan'),
    ]
    
    purchase_order_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey('inventory.Supplier', on_delete=models.PROTECT, related_name='purchase_orders')
    
    date = models.DateField()
    delivery_date = models.DateField(blank=True, null=True)
    
    # Nilai
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Terms
    notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='purchase_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchase_orders'
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.purchase_order_number} - {self.vendor.name}"
    
    def save(self, *args, **kwargs):
        if not self.purchase_order_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = PurchaseOrder.objects.filter(purchase_order_number__startswith=f'PO{today}').count() + 1
            self.purchase_order_number = f'PO{today}{count:04d}'
        
        self.total = self.subtotal + self.tax - self.discount
        super().save(*args, **kwargs)


class PurchaseOrderItem(models.Model):
    """Item dalam Purchase Order"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey('inventory.Item', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        db_table = 'purchase_order_items'

    def save(self, *args, **kwargs):
        self.total = (self.quantity * self.unit_price) - self.discount
        super().save(*args, **kwargs)
