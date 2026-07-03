"""
Finance Models - Management Information System
PT Lentera Anugerah Dimensi - Finance Module
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Account(models.Model):
    """
    Chart of Accounts (COA)
    """
    ACCOUNT_TYPE_CHOICES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subaccounts')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_cash = models.BooleanField(default=False, help_text='Kas/Bank')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'finance_accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def balance(self):
        """Hitung saldo"""
        debits = self.debits.aggregate(total=models.Sum('debit'))['total'] or 0
        credits = self.credits.aggregate(total=models.Sum('credit'))['total'] or 0
        
        if self.account_type in ['asset', 'expense']:
            return debits - credits
        else:
            return credits - debits


class JournalEntry(models.Model):
    """
    Jurnal Umum
    """
    entry_number = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    description = models.TextField()
    
    # Referensi
    reference_number = models.CharField(max_length=50, blank=True)
    reference_date = models.DateField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('canceled', 'Canceled'),
    ], default='draft')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='journal_entries')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_journals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'journal_entries'
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'
        ordering = ['-date', '-entry_number']
    
    def __str__(self):
        return f"{self.entry_number} - {self.description}"
    
    def save(self, *args, **kwargs):
        if not self.entry_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = JournalEntry.objects.filter(entry_number__startswith=f'JE{today}').count() + 1
            self.entry_number = f'JE{today}{count:04d}'
        super().save(*args, **kwargs)
    
    @property
    def total_debit(self):
        return sum(item.debit for item in self.items.all())
    
    @property
    def total_credit(self):
        return sum(item.credit for item in self.items.all())


class JournalEntryItem(models.Model):
    """Item dalam Journal Entry"""
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='items')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='journal_items')
    description = models.CharField(max_length=200, blank=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'journal_entry_items'
    
    def __str__(self):
        return f"{self.journal_entry.entry_number} - {self.account.name}"


class IncomeCategory(models.Model):
    """Kategori Pendapatan"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='income_categories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'income_categories'
        verbose_name = 'Income Category'
        verbose_name_plural = 'Income Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Income(models.Model):
    """
    Pendapatan/Income
    MIS - Management Information System
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Menunggu Konfirmasi'),
        ('confirmed', 'Dikonfirmasi'),
        ('completed', 'Selesai'),
        ('canceled', 'Dibatalkan'),
    ]
    
    income_number = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    category = models.ForeignKey(IncomeCategory, on_delete=models.PROTECT, related_name='incomes')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='incomes')
    
    # Pembayaran
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='incomes', help_text='Akun Kas/Bank')
    cheque_number = models.CharField(max_length=50, blank=True)
    cheque_date = models.DateField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='incomes')
    is_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'incomes'
        verbose_name = 'Income'
        verbose_name_plural = 'Incomes'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.income_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.income_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = Income.objects.filter(income_number__startswith=f'INC{today}').count() + 1
            self.income_number = f'INC{today}{count:04d}'
        super().save(*args, **kwargs)


class ExpenseCategory(models.Model):
    """Kategori Pengeluaran"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='expense_categories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'expense_categories'
        verbose_name = 'Expense Category'
        verbose_name_plural = 'Expense Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Expense(models.Model):
    """
    Pengeluaran/Expense
    MIS - Management Information System
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Menunggu Konfirmasi'),
        ('confirmed', 'Dikonfirmasi'),
        ('completed', 'Selesai'),
        ('canceled', 'Dibatalkan'),
    ]
    
    expense_number = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    
    # referensi
    vendor = models.ForeignKey('inventory.Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    
    # Pembayaran
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='expenses', help_text='Akun Kas/Bank')
    cheque_number = models.CharField(max_length=50, blank=True)
    cheque_date = models.DateField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_expenses')
    is_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'expenses'
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.expense_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.expense_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = Expense.objects.filter(expense_number__startswith=f'EXP{today}').count() + 1
            self.expense_number = f'EXP{today}{count:04d}'
        super().save(*args, **kwargs)


class Invoice(models.Model):
    """
    Invoice untuk Pelanggan
    """
    INVOICE_TYPE_CHOICES = [
        ('invoice', 'Invoice'),
        ('tax_invoice', 'Faktur Pajak'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Terkirim'),
        ('paid', 'Lunas'),
        ('partial', 'Sebagian'),
        ('overdue', 'Jatuh Tempo'),
        ('canceled', 'Dibatalkan'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES, default='invoice')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    
    date = models.DateField()
    due_date = models.DateField()
    
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount_due = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invoices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.invoice_number}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = Invoice.objects.filter(invoice_number__startswith=f'INV{today}').count() + 1
            self.invoice_number = f'INV{today}{count:04d}'
        
        self.total = self.subtotal + self.tax - self.discount
        self.amount_due = self.total - self.amount_paid
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """Item dalam Invoice"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'invoice_items'
    
    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Pembayaran dari Pelanggan
    """
    PAYMENT_TYPE_CHOICES = [
        ('invoice', 'Invoice'),
        ('direct', 'Direct Payment'),
    ]
    
    payment_number = models.CharField(max_length=50, unique=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='invoice')
    
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='payments')
    
    cheque_number = models.CharField(max_length=50, blank=True)
    cheque_date = models.DateField(blank=True, null=True)
    bank = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.payment_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = Payment.objects.filter(payment_number__startswith=f'PAY{today}').count() + 1
            self.payment_number = f'PAY{today}{count:04d}'
        super().save(*args, **kwargs)
