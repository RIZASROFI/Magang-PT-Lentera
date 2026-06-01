"""
Project Management Models
PT Lentera Anugerah Dimensi - Project Management Module
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class ProjectCategory(models.Model):
    """Kategori Proyek"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_categories'
        verbose_name = 'Project Category'
        verbose_name_plural = 'Project Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Project(models.Model):
    """
    Master Data Proyek
    """
    STATUS_CHOICES = [
        ('draft', 'Rencana/Draft'),
        ('survey', 'Survei'),
        ('progress', 'Sedang Berjalan'),
        ('pending', 'Menunggu Material'),
        ('testing', 'Testing/QC'),
        ('completed', 'Selesai'),
        ('canceled', 'Dibatalkan'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Rendah'),
        ('medium', 'Sedang'),
        ('high', 'Tinggi'),
        ('urgent', 'Mendesak'),
    ]
    
    project_code = models.CharField(max_length=50, unique=True, default=None, null=True, blank=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, null=True, related_name='projects')
    client_name = models.CharField(max_length=200)
    client_contact = models.CharField(max_length=100, blank=True)
    client_phone = models.CharField(max_length=20, blank=True)
    client_email = models.EmailField(blank=True)
    
    # Lokasi
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100, blank=True)
    
    # Detail
    description = models.TextField(blank=True)
    scope_of_work = models.TextField(blank=True)
    
    # Status & Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Tanggal
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    
    # Nilai Kontrak
    contract_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Lead & Team
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='led_projects')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project_code} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.project_code:
            self.project_code = f"PRJ-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def progress_percentage(self):
        """Hitung progress persen berdasarkan tracker"""
        trackers = self.progresses.all()
        if not trackers.exists():
            return 0
        total = sum(t.percentage for t in trackers)
        return min(total, 100)


class ProjectLocation(models.Model):
    """
    Detail Lokasi Proyek
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='locations')
    location_name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'project_locations'
        verbose_name = 'Project Location'
        verbose_name_plural = 'Project Locations'
    
    def __str__(self):
        return f"{self.project.project_code} - {self.location_name}"


class ProjectProgress(models.Model):
    """
    Tracking Progress Proyek Harian
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='progresses')
    date = models.DateField(default=timezone.now)
    percentage = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    #Foto dokumentasi
    photo = models.ImageField(upload_to='projects/progress/', blank=True, null=True)
    
    # Worker count
    workers_count = models.IntegerField(default=0)
    
    # Status update
    status = models.CharField(max_length=20, choices=Project.STATUS_CHOICES, blank=True)
    
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_progresses')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_progresses'
        verbose_name = 'Project Progress'
        verbose_name_plural = 'Project Progresses'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.project.project_code} - {self.date} ({self.percentage}%)"


class TeamAssignment(models.Model):
    """
    Penugasan Tim Proyek
    """
    ROLE_CHOICES = [
        ('leader', 'Leader'),
        ('technician', 'Technician'),
        ('helper', 'Helper'),
        ('supervisor', 'Supervisor'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='team_assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_assignments')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='technician')
    assigned_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'team_assignments'
        verbose_name = 'Team Assignment'
        verbose_name_plural = 'Team Assignments'
        unique_together = ['project', 'user']
    
    def __str__(self):
        return f"{self.project.project_code} - {self.user.email}"


class ProjectMilestone(models.Model):
    """
    Milestone Proyek
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    completed_date = models.DateField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_milestones'
        verbose_name = 'Project Milestone'
        verbose_name_plural = 'Project Milestones'
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.project.project_code} - {self.title}"


class ProjectDocument(models.Model):
    """
    Dokumen Proyek (Kontrak, Gambar, dll)
    """
    DOC_TYPE_CHOICES = [
        ('contract', 'Kontrak'),
        ('survey', 'Survei'),
        ('design', 'Desain'),
        ('report', 'Laporan'),
        ('photo', 'Foto'),
        ('other', 'Lainnya'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    file = models.FileField(upload_to='projects/documents/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_documents'
        verbose_name = 'Project Document'
        verbose_name_plural = 'Project Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.project_code} - {self.title}"
