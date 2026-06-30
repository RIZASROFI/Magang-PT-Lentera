"""
HR Models - Human Resources Management
PT Lentera Anugerah Dimensi - HR Module
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Department(models.Model):
    """Departemen"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hr_departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Position(models.Model):
    """Jabatan"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True)
    level = models.IntegerField(default=1, help_text='Level jabatan')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hr_positions'
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        ordering = ['department', 'level']
    
    def __str__(self):
        return f"{self.department.name} - {self.name}"


class Employee(models.Model):
    """
    Data Karyawan
    MIS - Management Information System
    """
    GENDER_CHOICES = [
        ('male', 'Laki-laki'),
        ('female', 'Perempuan'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Belum Menikah'),
        ('married', 'Menikah'),
        ('divorced', 'Cerai'),
        ('widowed', 'Janda/Duda'),
    ]
    
    STATUS_CHOICES = [
        ('probation', 'Probation'),
        ('contract', 'Kontrak'),
        ('permanent', 'Tetap'),
        ('resigned', 'Resign'),
        ('fired', 'PHK'),
    ]
    
    # User reference (optional — bisa diisi nanti)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee', null=True, blank=True)
    
    # Personal Info
    employee_id = models.CharField(max_length=50, unique=True)
    nip = models.CharField(max_length=50, blank=True)
    
    # Department & Position
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name='employees')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='probation')
    
    # Tanggal
    join_date = models.DateField()
    resign_date = models.DateField(blank=True, null=True)
    
    # Personal Details
    birth_date = models.DateField(blank=True, null=True)
    birth_place = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)
    religion = models.CharField(max_length=20, blank=True)
    
    # Kontak
    phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    
    # Alamat
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Dokumen
    id_card = models.CharField(max_length=50, blank=True)
    npwp = models.CharField(max_length=50, blank=True)
    bpjs_ketenagakerjaan = models.CharField(max_length=50, blank=True)
    bpjs_kesehatan = models.CharField(max_length=50, blank=True)
    
    # Foto
    photo = models.ImageField(upload_to='hr/employees/', blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_employees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hr_employees'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['employee_id']
    
    def __str__(self):
        user_name = self.user.get_full_name if self.user else '(tanpa akun)'
        return f"{self.employee_id} - {user_name}"
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            year = timezone.now().strftime('%y')
            count = Employee.objects.filter(employee_id__startswith=f'EMP{year}').count() + 1
            self.employee_id = f'EMP{year}{count:04d}'
        super().save(*args, **kwargs)


class Attendance(models.Model):
    """
    Absensi Karyawan
    TPS - Transaction Processing System
    """
    STATUS_CHOICES = [
        ('present', 'Hadir'),
        ('absent', 'Tidak Hadir'),
        ('sick', 'Sakit'),
        ('permission', 'Izin'),
        ('leave', 'Cuti'),
        ('late', 'Terlambat'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    
    # Waktu
    check_in = models.TimeField(blank=True, null=True)
    check_out = models.TimeField(blank=True, null=True)
    
    # Lembur
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    
    # Keterangan
    notes = models.TextField(blank=True)
    
    # Approve
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_attendances')
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hr_attendances'
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        ordering = ['-date', 'employee']
        unique_together = ['employee', 'date']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name} - {self.date}"


class Leave(models.Model):
    """
    Cuti Karyawan
    """
    LEAVE_TYPE_CHOICES = [
        ('annual', 'Cuti Tahunan'),
        ('sick', 'Cuti Sakit'),
        ('maternity', 'Cuti Melahirkan'),
        ('paternity', 'Cuti Ayah'),
        ('unpaid', 'Cuti Tanpa Gaji'),
        ('other', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('canceled', 'Dibatalkan'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.IntegerField(default=0)
    
    reason = models.TextField()
    notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hr_leaves'
        verbose_name = 'Leave'
        verbose_name_plural = 'Leaves'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name} - {self.get_leave_type_display()}"


class Salary(models.Model):
    """
    Gaji Karyawan
    MIS - Management Information System
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('calculated', 'Dihitung'),
        ('approved', 'Disetujui'),
        ('paid', 'Dibayar'),
        ('canceled', 'Dibatalkan'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salaries')
    period_month = models.IntegerField()
    period_year = models.IntegerField()
    
    # Komponen Gaji
    basic_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Potongan
    deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    bpjs = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Total
    gross_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_salaries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hr_salaries'
        verbose_name = 'Salary'
        verbose_name_plural = 'Salaries'
        ordering = ['-period_year', '-period_month']
        unique_together = ['employee', 'period_month', 'period_year']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.period_month}/{self.period_year}"
    
    def save(self, *args, **kwargs):
        self.gross_salary = self.basic_salary + self.allowances + self.bonuses + self.overtime_pay
        self.net_salary = self.gross_salary - self.deductions - self.tax - self.bpjs
        super().save(*args, **kwargs)


class Overtime(models.Model):
    """
    Lembur Karyawan
    """
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtimes')
    date = models.DateField()
    
    start_time = models.TimeField()
    end_time = models.TimeField()
    hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=1.5, help_text='Rate lembur (1.5, 2, dll)')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hr_overtimes'
        verbose_name = 'Overtime'
        verbose_name_plural = 'Overtimes'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name} - {self.date}"
