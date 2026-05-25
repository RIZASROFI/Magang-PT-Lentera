"""
Frontend Views - HTML Pages
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime, timedelta
import json


def home(request):
    """Halaman Home"""
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    return render(request, 'frontend/home.html')


def login_page(request):
    """Halaman Login"""
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip() or request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Email dan password wajib diisi')
            return render(request, 'frontend/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_page = request.POST.get('next') or 'frontend:dashboard'
            return redirect(next_page)

        messages.error(request, 'Email atau password salah')

    return render(request, 'frontend/login.html')


def logout_page(request):
    """Logout"""
    logout(request)
    messages.success(request, 'Berhasil logout!')
    return redirect('frontend:login')


def register_page(request):
    """Halaman Registrasi"""
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')

    form_data = {}

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()

        form_data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        }

        errors = []

        if not username or len(username) < 3:
            errors.append('Username harus minimal 3 karakter')

        if not email or '@' not in email:
            errors.append('Email tidak valid')

        if not first_name:
            errors.append('Nama depan wajib diisi')

        if not last_name:
            errors.append('Nama belakang wajib diisi')

        if not password or len(password) < 8:
            errors.append('Password harus minimal 8 karakter')

        if password != password_confirm:
            errors.append('Password dan konfirmasi password tidak cocok')

        if errors:
            for error in errors:
                messages.error(request, error)
            context = {'form': form_data}
            return render(request, 'frontend/register.html', context)

        from django.contrib.auth import get_user_model
        User = get_user_model()

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah terdaftar')
            context = {'form': form_data}
            return render(request, 'frontend/register.html', context)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar')
            context = {'form': form_data}
            return render(request, 'frontend/register.html', context)

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        messages.success(request, f'Registrasi berhasil! Silakan login untuk melanjutkan.')
        return redirect('frontend:login')

    context = {'form': form_data}
    return render(request, 'frontend/register.html', context)


@login_required(login_url='frontend:login')
def dashboard(request):
    """Dashboard Utama"""
    from django.db.models import Sum
    from apps.projects.models import Project
    from apps.inventory.models import Item
    from apps.finance.models import Income
    from apps.hr.models import Employee
    from apps.core.models import ActivityLog, Notification
    from datetime import datetime, timedelta
    
    now = datetime.now()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        last_day = now.replace(year=now.year+1, month=1, day=1) - timedelta(seconds=1)
    else:
        last_day = now.replace(month=now.month+1, day=1) - timedelta(seconds=1)
    
    # Stats
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status__in=['progress', 'survey', 'pending', 'testing']).count()
    completed_projects = Project.objects.filter(status='completed').count()
    total_contract_value = Project.objects.aggregate(s=Sum('contract_value'))['s'] or 0
    
    total_items = Item.objects.count()
    # current_stock adalah @property, tidak bisa difilter di DB
    # Hitung jumlah item yang stok-nya mungkin rendah (min_stock > 0)
    low_stock_items = Item.objects.filter(min_stock__gt=0).count()
    
    monthly_income = Income.objects.filter(
        date__gte=first_day,
        date__lte=last_day
    ).aggregate(s=Sum('amount'))['s'] or 0
    
    total_employees = Employee.objects.filter(status__in=['permanent', 'contract', 'probation']).count()
    
    # Recent projects
    recent_projects = Project.objects.order_by('-created_at')[:5]
    
    # Recent activity logs
    recent_activities = ActivityLog.objects.order_by('-created_at')[:10]
    
    # Unread notifications
    unread_notifications = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'page_title': 'Dashboard',
        'username': request.user.get_full_name or request.user.username,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_contract_value': total_contract_value,
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'monthly_income': monthly_income,
        'total_employees': total_employees,
        'recent_projects': recent_projects,
        'recent_activities': recent_activities,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'frontend/dashboard.html', context)


@login_required(login_url='frontend:login')
def profile(request):
    """Profile Page"""
    from apps.core.models import UserProfile, ActivityLog
    
    profile_data = getattr(request.user, 'profile', None)
    recent_activities = ActivityLog.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'page_title': 'Profile',
        'username': request.user.get_full_name() if hasattr(request.user, 'get_full_name') else request.user.username,
        'profile': profile_data,
        'recent_activities': recent_activities,
    }
    return render(request, 'frontend/profile.html', context)


@login_required(login_url='frontend:login')
def profile_edit(request):
    """Edit Profile Page"""
    return render(request, 'frontend/profile_edit.html')


@login_required(login_url='frontend:login')
def notifications(request):
    """Notifications Page"""
    from apps.core.models import Notification
    
    notifications_qs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications_qs.filter(is_read=False).count()
    all_notifications = notifications_qs[:50]
    
    context = {
        'page_title': 'Notifikasi',
        'notifications': all_notifications,
        'unread_count': unread_count,
    }
    return render(request, 'frontend/notifications.html', context)


@login_required(login_url='frontend:login')
def projects_list(request):
    """Daftar Proyek"""
    from apps.projects.models import Project
    from django.db.models import Sum
    
    projects = Project.objects.all().order_by('-created_at')
    total = projects.count()
    active = projects.filter(status__in=['progress', 'survey', 'pending', 'testing']).count()
    completed = projects.filter(status='completed').count()
    total_value = projects.aggregate(s=Sum('contract_value'))['s'] or 0
    
    context = {
        'page_title': 'Daftar Proyek',
        'projects': projects,
        'total_projects': total,
        'active_projects': active,
        'completed_projects': completed,
        'total_value': total_value,
    }
    return render(request, 'frontend/projects/list.html', context)


@login_required(login_url='frontend:login')
def projects_form(request, id=None):
    """Form Proyek (Create/Edit)"""
    from apps.projects.models import Project, ProjectCategory
    
    project = None
    
    if id:
        try:
            project = Project.objects.get(id=id)
        except Project.DoesNotExist:
            pass
    
    categories = ProjectCategory.objects.filter(is_active=True)
    
    context = {
        'page_title': 'Edit Proyek' if project else 'Proyek Baru',
        'project': project,
        'categories': categories,
    }
    return render(request, 'frontend/projects/form.html', context)


@login_required(login_url='frontend:login')
def projects_progress(request):
    """Progress Proyek"""
    from apps.projects.models import Project, ProjectProgress
    
    projects = Project.objects.all().order_by('-created_at')
    
    context = {
        'page_title': 'Progress Proyek',
        'projects': projects,
    }
    return render(request, 'frontend/projects/progress.html', context)


# ===================== FINANCE VIEWS =====================

@login_required(login_url='frontend:login')
def finance_accounts(request):
    """Daftar Akun Keuangan"""
    context = {
        'page_title': 'Akun Keuangan',
    }
    return render(request, 'frontend/finance/accounts.html', context)


@login_required(login_url='frontend:login')
def finance_transactions(request):
    """Transaksi Keuangan (Income & Expense)"""
    context = {
        'page_title': 'Transaksi Keuangan',
    }
    return render(request, 'frontend/finance/transactions.html', context)


@login_required(login_url='frontend:login')
def finance_reports(request):
    """Laporan Keuangan"""
    context = {
        'page_title': 'Laporan Keuangan',
    }
    return render(request, 'frontend/finance/reports.html', context)


# ===================== SALES VIEWS =====================

@login_required(login_url='frontend:login')
def sales_customers(request):
    """Daftar Customer"""
    context = {
        'page_title': 'Data Customer',
    }
    return render(request, 'frontend/sales/customers.html', context)


@login_required(login_url='frontend:login')
def sales_quotations(request):
    """Daftar Quotation"""
    context = {
        'page_title': 'Quotation',
    }
    return render(request, 'frontend/sales/quotations.html', context)


@login_required(login_url='frontend:login')
def sales_orders(request):
    """Daftar Sales Order"""
    context = {
        'page_title': 'Sales Order',
    }
    return render(request, 'frontend/sales/orders.html', context)


@login_required(login_url='frontend:login')
def sales_vendors(request):
    """Daftar Vendor"""
    context = {
        'page_title': 'Data Vendor',
    }
    return render(request, 'frontend/sales/vendors.html', context)


@login_required(login_url='frontend:login')
def sales_purchase_orders(request):
    """Daftar Purchase Order"""
    context = {
        'page_title': 'Purchase Order',
    }
    return render(request, 'frontend/sales/purchase_orders.html', context)


# ===================== HR VIEWS =====================

@login_required(login_url='frontend:login')
def hr_attendances(request):
    """Absensi Karyawan"""
    context = {
        'page_title': 'Absensi Karyawan',
    }
    return render(request, 'frontend/hr/attendances.html', context)


@login_required(login_url='frontend:login')
def hr_salaries(request):
    """Gaji Karyawan"""
    context = {
        'page_title': 'Gaji Karyawan',
    }
    return render(request, 'frontend/hr/salaries.html', context)


@login_required(login_url='frontend:login')
def hr_leaves(request):
    """Cuti Karyawan"""
    context = {
        'page_title': 'Cuti Karyawan',
    }
    return render(request, 'frontend/hr/leaves.html', context)