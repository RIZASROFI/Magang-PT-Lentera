"""
Seed Data Lengkap SIMAN - Semua Model Database
PT Lentera Anugerah Dimensi
Usage: python manage.py seed_all

Membuat minimal 10 record per tabel untuk keperluan demo/pengembangan.
Data bersifat idempotent (dijalankan berulang aman).
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = "Seed semua data dummy untuk SIMAN (minimal 10 record per tabel)"

    def handle(self, *args, **options):
        # ============================================================
        # 1. CORE - USER
        # ============================================================
        self.stdout.write("Seeding Users...")
        User = get_user_model()

        users_data = [
            # (email, username, password, first_name, last_name, role, phone)
            ('admin@lentera.com', 'admin', 'admin123', 'Admin', 'Utama', 'admin', '081234567890'),
            ('manager1@lentera.com', 'manager1', 'manager123', 'Budi', 'Santoso', 'manager', '081234567891'),
            ('manager2@lentera.com', 'manager2', 'manager123', 'Siti', 'Rahmawati', 'manager', '081234567892'),
            ('staff1@lentera.com', 'staff1', 'staff123', 'Ahmad', 'Hidayat', 'staff', '081234567893'),
            ('staff2@lentera.com', 'staff2', 'staff123', 'Dewi', 'Kusuma', 'staff', '081234567894'),
            ('staff3@lentera.com', 'staff3', 'staff123', 'Rudi', 'Prasetyo', 'staff', '081234567895'),
            ('staff4@lentera.com', 'staff4', 'staff123', 'Maya', 'Anggraini', 'staff', '081234567896'),
            ('staff5@lentera.com', 'staff5', 'staff123', 'Hendra', 'Gunawan', 'staff', '081234567897'),
            ('staff6@lentera.com', 'staff6', 'staff123', 'Rina', 'Fitriani', 'staff', '081234567898'),
            ('staff7@lentera.com', 'staff7', 'staff123', 'Agus', 'Wijaya', 'staff', '081234567899'),
        ]

        users = {}
        for email, username, password, first_name, last_name, role, phone in users_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    'phone': phone,
                    'is_active': True,
                    'is_staff': True if role == 'admin' else False,
                }
            )
            if created:
                user.set_password(password)
                user.save()
            users[role + '_' + (first_name.lower() if role != 'admin' else 'utama')] = user

        self.stdout.write(f"  [OK] Users: {User.objects.count()}")

        # ============================================================
        # 2. CORE - USER PROFILE
        # ============================================================
        self.stdout.write("Seeding User Profiles...")
        from apps.core.models import UserProfile

        profiles_data = [
            (users['admin_utama'], 'IT', 'System Administrator', 'NIP-001', 'Jakarta', '1990-01-15', 'Laki-laki', 'Islam', 'Menikah'),
            (users['manager_budi'], 'IT', 'IT Manager', 'NIP-002', 'Bandung', '1988-05-20', 'Laki-laki', 'Islam', 'Menikah'),
            (users['manager_siti'], 'Finance', 'Finance Manager', 'NIP-003', 'Jakarta', '1992-03-10', 'Perempuan', 'Islam', 'Menikah'),
            (users['staff_ahmad'], 'IT', 'Teknisi', 'NIP-004', 'Surabaya', '1995-07-22', 'Laki-laki', 'Islam', 'Belum Menikah'),
            (users['staff_dewi'], 'Finance', 'Staff Finance', 'NIP-005', 'Jakarta', '1996-11-08', 'Perempuan', 'Islam', 'Belum Menikah'),
            (users['staff_rudi'], 'IT', 'Teknisi Senior', 'NIP-006', 'Semarang', '1991-09-15', 'Laki-laki', 'Islam', 'Menikah'),
            (users['staff_maya'], 'HR', 'Staff HR', 'NIP-007', 'Yogyakarta', '1997-02-28', 'Perempuan', 'Islam', 'Belum Menikah'),
            (users['staff_hendra'], 'IT', 'Teknisi', 'NIP-008', 'Medan', '1993-06-12', 'Laki-laki', 'Kristen', 'Menikah'),
            (users['staff_rina'], 'Sales', 'Staff Sales', 'NIP-009', 'Bali', '1998-04-05', 'Perempuan', 'Hindu', 'Belum Menikah'),
            (users['staff_agus'], 'IT', 'Teknisi Junior', 'NIP-010', 'Makassar', '1999-08-18', 'Laki-laki', 'Islam', 'Belum Menikah'),
        ]

        for user, dept, pos, nip, birth_place, birth_date, gender, religion, marital in profiles_data:
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'department': dept,
                    'position': pos,
                    'nip': nip,
                    'birth_place': birth_place,
                    'birth_date': date.fromisoformat(birth_date) if birth_date else None,
                    'gender': gender,
                    'religion': religion,
                    'marital_status': marital,
                    'emergency_contact': f'Ibu {user.first_name}',
                    'emergency_phone': user.phone,
                }
            )
        self.stdout.write(f"  [OK] User Profiles: {UserProfile.objects.count()}")

        # ============================================================
        # 3. CORE - SYSTEM SETTINGS
        # ============================================================
        self.stdout.write("Seeding System Settings...")
        from apps.core.models import SystemSetting

        settings_data = [
            ('company_name', 'PT Lentera Anugerah Dimensi', 'Nama Perusahaan'),
            ('company_address', 'Jl. Teknologi No. 123, Jakarta Selatan', 'Alamat Perusahaan'),
            ('company_phone', '021-12345678', 'Telepon Perusahaan'),
            ('company_email', 'info@lentera.com', 'Email Perusahaan'),
            ('company_website', 'www.lenteraanugerahdimensi.com', 'Website Perusahaan'),
            ('company_npwp', '01.234.567.8-999.000', 'NPWP Perusahaan'),
            ('ppn_rate', '11', 'Persentase PPN'),
            ('working_days_per_month', '22', 'Hari Kerja per Bulan'),
            ('max_leave_days', '12', 'Maksimal Cuti Tahunan'),
            ('overtime_rate', '1.5', 'Rate Lembur Standar'),
        ]

        for key, value, desc in settings_data:
            SystemSetting.objects.get_or_create(
                key=key,
                defaults={'value': value, 'description': desc, 'is_active': True}
            )
        self.stdout.write(f"  [OK] System Settings: {SystemSetting.objects.count()}")

        # ============================================================
        # 4. CORE - NOTIFICATIONS
        # ============================================================
        self.stdout.write("Seeding Notifications...")
        from apps.core.models import Notification

        notif_types = ['info', 'success', 'warning', 'error']
        notif_titles = [
            'Selamat Datang di SIMAN',
            'Proyek Baru Ditambahkan',
            'Stok Menipis',
            'Pembayaran Diterima',
            'Proyek Selesai',
            'Meeting Hari Ini',
            'Laporan Bulanan Tersedia',
            'Pengajuan Cuti Baru',
            'Invoice Jatuh Tempo',
            'Update Sistem',
        ]

        for i in range(10):
            recipient = random.choice(list(users.values()))
            sender = random.choice(list(users.values()))
            Notification.objects.get_or_create(
                title=notif_titles[i],
                recipient=recipient,
                defaults={
                    'sender': sender,
                    'message': f'Ini adalah notifikasi: {notif_titles[i]} untuk {recipient.get_full_name}',
                    'notification_type': random.choice(notif_types),
                    'is_read': random.choice([True, False]),
                    'link': '/dashboard/',
                }
            )
        self.stdout.write(f"  [OK] Notifications: {Notification.objects.count()}")

        # ============================================================
        # 5. CORE - ACTIVITY LOGS
        # ============================================================
        self.stdout.write("Seeding Activity Logs...")
        from apps.core.models import ActivityLog

        actions = ['create', 'update', 'delete', 'login', 'logout', 'view']
        models_list = ['User', 'Project', 'Item', 'Invoice', 'Employee']

        for i in range(10):
            user = random.choice(list(users.values()))
            ActivityLog.objects.create(
                user=user,
                action=random.choice(actions),
                model_name=random.choice(models_list),
                object_id=random.randint(1, 100),
                description=f'{user.get_full_name} melakukan aksi {actions[i % len(actions)]}',
                ip_address=f'192.168.1.{random.randint(1, 255)}',
            )
        self.stdout.write(f"  [OK] Activity Logs: {ActivityLog.objects.count()}")

        # ============================================================
        # 6. AUTH - USER SESSIONS
        # ============================================================
        self.stdout.write("Seeding User Sessions...")
        from apps.auth_app.models import UserSession

        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605',
            'Mozilla/5.0 (X11; Linux x86_64) Firefox/121',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) Mobile/15E148',
            'Mozilla/5.0 (Android 14; Mobile) Chrome/120',
        ]

        for i, user in enumerate(list(users.values())):
            UserSession.objects.get_or_create(
                user=user,
                token=f'token_dummy_{user.id}_{i}',
                defaults={
                    'ip_address': f'192.168.1.{random.randint(1, 255)}',
                    'user_agent': random.choice(user_agents),
                    'expires_at': timezone.now() + timedelta(days=7),
                    'is_active': True,
                }
            )
        self.stdout.write(f"  [OK] User Sessions: {UserSession.objects.count()}")

        # ============================================================
        # 7. HR - DEPARTMENTS
        # ============================================================
        self.stdout.write("Seeding HR Departments...")
        from apps.hr.models import Department

        departments_data = [
            ('IT', 'IT', users.get('admin_utama')),
            ('Finance', 'FIN', users.get('manager_siti')),
            ('HR', 'HRD', users.get('staff_maya')),
            ('Sales', 'SLS', users.get('staff_rina')),
            ('Operations', 'OPS', users.get('manager_budi')),
        ]

        departments = {}
        for name, code, head in departments_data:
            dept, _ = Department.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': f'Departemen {name}', 'head': head}
            )
            departments[code] = dept
        self.stdout.write(f"  [OK] Departments: {Department.objects.count()}")

        # ============================================================
        # 8. HR - POSITIONS
        # ============================================================
        self.stdout.write("Seeding HR Positions...")
        from apps.hr.models import Position

        positions_data = [
            ('Direktur', 'DIR', 'IT', 10),
            ('Manager IT', 'MGR-IT', 'IT', 8),
            ('Manager Finance', 'MGR-FIN', 'FIN', 8),
            ('Manager HR', 'MGR-HRD', 'HRD', 8),
            ('Senior Teknisi', 'SR-TEK', 'IT', 5),
            ('Teknisi', 'TEK', 'IT', 3),
            ('Staff Finance', 'STF-FIN', 'FIN', 3),
            ('Staff HR', 'STF-HRD', 'HRD', 3),
            ('Staff Sales', 'STF-SLS', 'SLS', 3),
            ('Admin', 'ADM', 'OPS', 2),
        ]

        positions = {}
        for name, code, dept_code, level in positions_data:
            pos, _ = Position.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'department': departments[dept_code],
                    'description': f'Jabatan {name}',
                    'level': level,
                }
            )
            positions[code] = pos
        self.stdout.write(f"  [OK] Positions: {Position.objects.count()}")

        # ============================================================
        # 9. HR - EMPLOYEES
        # ============================================================
        self.stdout.write("Seeding HR Employees...")
        from apps.hr.models import Employee

        employees_data = [
            (users['admin_utama'], 'IT', 'DIR', '1990-01-15', 'Laki-laki', 'Islam', 'Menikah', 'admin'),
            (users['manager_budi'], 'IT', 'MGR-IT', '1988-05-20', 'Laki-laki', 'Islam', 'Menikah', 'manager'),
            (users['manager_siti'], 'FIN', 'MGR-FIN', '1992-03-10', 'Perempuan', 'Islam', 'Menikah', 'manager'),
            (users['staff_ahmad'], 'IT', 'TEK', '1995-07-22', 'Laki-laki', 'Islam', 'Belum Menikah', 'staff'),
            (users['staff_dewi'], 'FIN', 'STF-FIN', '1996-11-08', 'Perempuan', 'Islam', 'Belum Menikah', 'staff'),
            (users['staff_rudi'], 'IT', 'SR-TEK', '1991-09-15', 'Laki-laki', 'Islam', 'Menikah', 'staff'),
            (users['staff_maya'], 'HRD', 'STF-HRD', '1997-02-28', 'Perempuan', 'Islam', 'Belum Menikah', 'staff'),
            (users['staff_hendra'], 'IT', 'TEK', '1993-06-12', 'Laki-laki', 'Kristen', 'Menikah', 'staff'),
            (users['staff_rina'], 'SLS', 'STF-SLS', '1998-04-05', 'Perempuan', 'Hindu', 'Belum Menikah', 'staff'),
            (users['staff_agus'], 'IT', 'TEK', '1999-08-18', 'Laki-laki', 'Islam', 'Belum Menikah', 'staff'),
        ]

        employees = {}
        for user, dept_code, pos_code, birth_date, gender, religion, marital, emp_type in employees_data:
            emp, _ = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'department': departments[dept_code],
                    'position': positions[pos_code],
                    'nip': f'NIP-{user.id:03d}',
                    'status': 'permanent' if emp_type in ['admin', 'manager'] else 'contract',
                    'join_date': date(2020, random.randint(1, 12), random.randint(1, 28)),
                    'birth_date': date.fromisoformat(birth_date),
                    'birth_place': 'Jakarta',
                    'gender': gender,
                    'religion': religion,
                    'marital_status': marital,
                    'phone': user.phone,
                    'address': f'Jl. Contoh No. {user.id}, Jakarta',
                    'city': 'Jakarta',
                    'id_card': f'3174{random.randint(100000, 999999)}',
                    'npwp': f'99.{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(1, 9)}.{random.randint(100, 999)}.000',
                    'bpjs_ketenagakerjaan': f'BK{random.randint(10000000, 99999999)}',
                    'bpjs_kesehatan': f'BK{random.randint(10000000, 99999999)}',
                    'notes': '',
                    'created_by': users['admin_utama'],
                }
            )
            employees[emp_type + '_' + user.first_name.lower()] = emp
        self.stdout.write(f"  [OK] Employees: {Employee.objects.count()}")

        # ============================================================
        # 10. HR - ATTENDANCES
        # ============================================================
        self.stdout.write("Seeding HR Attendances...")
        from apps.hr.models import Attendance

        statuses = ['present', 'present', 'present', 'present', 'late', 'present', 'present', 'absent', 'sick', 'permission']
        today = date.today()
        count = 0
        for emp in Employee.objects.all():
            for day_offset in range(5):  # 5 hari kerja per employee
                d = today - timedelta(days=day_offset)
                if d.weekday() < 6:  # Skip Minggu
                    Attendance.objects.get_or_create(
                        employee=emp,
                        date=d,
                        defaults={
                            'status': random.choice(statuses),
                            'check_in': timezone.now().replace(hour=8, minute=random.randint(0, 30)),
                            'check_out': timezone.now().replace(hour=17, minute=random.randint(0, 30)),
                            'is_approved': random.choice([True, False]),
                            'approved_by': users['manager_budi'] if random.random() > 0.3 else None,
                        }
                    )
                    count += 1
                    if count >= 15:
                        break
            if count >= 15:
                break
        self.stdout.write(f"  [OK] Attendances: {Attendance.objects.count()}")

        # ============================================================
        # 11. HR - LEAVES
        # ============================================================
        self.stdout.write("Seeding HR Leaves...")
        from apps.hr.models import Leave

        leave_types = ['annual', 'annual', 'sick', 'maternity', 'annual', 'sick', 'annual', 'paternity', 'annual', 'unpaid']
        leave_statuses = ['approved', 'approved', 'approved', 'pending', 'approved', 'rejected', 'approved', 'approved', 'pending', 'approved']

        for i in range(10):
            emp = random.choice(list(employees.values()))
            start = date.today() - timedelta(days=random.randint(30, 100))
            days_count = random.randint(1, 5)
            Leave.objects.get_or_create(
                employee=emp,
                start_date=start,
                leave_type=leave_types[i],
                defaults={
                    'end_date': start + timedelta(days=days_count),
                    'days': days_count,
                    'reason': f'Izin {leave_types[i]} karena keperluan keluarga/kesehatan',
                    'status': leave_statuses[i],
                    'approved_by': users.get('admin_utama') if leave_statuses[i] == 'approved' else None,
                }
            )
        self.stdout.write(f"  [OK] Leaves: {Leave.objects.count()}")

        # ============================================================
        # 12. HR - SALARIES
        # ============================================================
        self.stdout.write("Seeding HR Salaries...")
        from apps.hr.models import Salary

        for i, (emp_key, emp) in enumerate(list(employees.items())[:10]):
            for month_offset in range(2):  # 2 bulan terakhir
                month = (today.month - month_offset) or 12
                year = today.year if month <= today.month else today.year - 1
                if month == 0:
                    month = 12
                basic = random.choice([5000000, 7000000, 10000000, 15000000, 25000000])
                Salary.objects.get_or_create(
                    employee=emp,
                    period_month=month,
                    period_year=year,
                    defaults={
                        'basic_salary': basic,
                        'allowances': basic * 0.2,
                        'bonuses': random.choice([0, 500000, 1000000]),
                        'overtime_pay': random.choice([0, 250000, 500000]),
                        'deductions': basic * 0.05,
                        'tax': basic * 0.1,
                        'bpjs': basic * 0.04,
                        'status': random.choice(['calculated', 'approved', 'paid']),
                        'created_by': users['admin_utama'],
                    }
                )
        self.stdout.write(f"  [OK] Salaries: {Salary.objects.count()}")

        # ============================================================
        # 13. HR - OVERTIMES
        # ============================================================
        self.stdout.write("Seeding HR Overtimes...")
        from apps.hr.models import Overtime

        for i in range(10):
            emp = random.choice(list(employees.values()))
            d = date.today() - timedelta(days=random.randint(1, 30))
            Overtime.objects.get_or_create(
                employee=emp,
                date=d,
                defaults={
                    'start_time': timezone.now().replace(hour=17, minute=0),
                    'end_time': timezone.now().replace(hour=20, minute=0),
                    'hours': 3.0,
                    'reason': 'Pekerjaan tambahan / deadline proyek',
                    'status': random.choice(['pending', 'approved', 'rejected']),
                    'rate': 1.5,
                    'amount': 75000,
                    'approved_by': users.get('manager_budi') if random.random() > 0.3 else None,
                }
            )
        self.stdout.write(f"  [OK] Overtimes: {Overtime.objects.count()}")

        # ============================================================
        # 14. PROJECTS - CATEGORIES
        # ============================================================
        self.stdout.write("Seeding Project Categories...")
        from apps.projects.models import ProjectCategory

        project_cats_data = [
            'Instalasi CCTV',
            'Instalasi Jaringan',
            'Pemasangan Videotron',
            'Maintenance',
            'Konsultasi Teknis',
            'Instalasi Kabel',
            'Pengadaan Barang',
            'Upgrade Sistem',
            'Survey Lokasi',
            'Support Teknis',
        ]

        project_cats = {}
        for name in project_cats_data:
            cat, _ = ProjectCategory.objects.get_or_create(
                name=name,
                defaults={'description': f'Kategori {name}', 'is_active': True}
            )
            project_cats[name] = cat
        self.stdout.write(f"  [OK] Project Categories: {ProjectCategory.objects.count()}")

        # ============================================================
        # 15. INVENTORY - SUPPLIERS
        # ============================================================
        self.stdout.write("Seeding Inventory Suppliers...")
        from apps.inventory.models import Supplier

        suppliers_data = [
            ('SUP-HIK', 'PT Hikvision Indonesia', 'Bambang', '021-700001'),
            ('SUP-DAH', 'PT Dahua Technology', 'Susi', '021-700002'),
            ('SUP-LAN', 'CV LanPro Networking', 'Hendra', '021-700003'),
            ('SUP-VID', 'PT Videotron Solution', 'Rudi', '021-700004'),
            ('SUP-CAB', 'PT Kabelindo Utama', 'Ani', '021-700005'),
            ('SUP-UPS', 'PT UPS Solution', 'Doni', '021-700006'),
            ('SUP-ACC', 'CV Aksesoris Komputer', 'Lina', '021-700007'),
            ('SUP-TOO', 'PT Tools Indonesia', 'Rizky', '021-700008'),
            ('SUP-ELE', 'CV Elektronik Jaya', 'Sari', '021-700009'),
            ('SUP-GEN', 'PT General Suplai', 'Budi', '021-700010'),
        ]

        suppliers = {}
        for code, name, cp, phone in suppliers_data:
            sup, _ = Supplier.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'contact_person': cp,
                    'phone': phone,
                    'email': f'{name.lower().replace(" ", "")}@gmail.com',
                    'address': f'Jl. Industri No. {random.randint(1, 100)}, Jakarta',
                    'city': 'Jakarta',
                    'notes': '',
                    'is_active': True,
                }
            )
            suppliers[code] = sup
        self.stdout.write(f"  [OK] Suppliers: {Supplier.objects.count()}")

        # ============================================================
        # 16. INVENTORY - CATEGORIES
        # ============================================================
        self.stdout.write("Seeding Inventory Categories...")
        from apps.inventory.models import Category

        cat_data = [
            ('CAT-CCTV', 'CCTV', None, 'Kamera dan perangkat CCTV'),
            ('CAT-NET', 'Networking', None, 'Perangkat jaringan dan kabel'),
            ('CAT-VID', 'Videotron', None, 'Modul dan perangkat videotron'),
            ('CAT-ACC', 'Aksesoris', None, 'Aksesoris pendukung'),
            ('CAT-ELEC', 'Elektronik', None, 'Perangkat elektronik'),
            ('CAT-CBL', 'Kabel', None, 'Kabel dan konektor'),
            ('CAT-PWR', 'Power', None, 'Catu daya dan UPS'),
            ('CAT-TOOL', 'Tools', None, 'Alat kerja'),
            ('CAT-COMP', 'Komputer', None, 'Perangkat komputer dan laptop'),
            ('CAT-OTHR', 'Lainnya', None, 'Kategori lainnya'),
        ]

        categories = {}
        for code, name, parent, desc in cat_data:
            cat, _ = Category.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': desc,
                    'parent': parent,
                    'is_active': True,
                }
            )
            categories[code] = cat

        # Tambah sub-kategori untuk CCTV
        sub_cats = [
            ('CAT-CCTV-BUL', 'CCTV Bullet', 'CAT-CCTV', 'Kamera CCTV tipe bullet'),
            ('CAT-CCTV-DOM', 'CCTV Dome', 'CAT-CCTV', 'Kamera CCTV tipe dome'),
            ('CAT-CCTV-PTB', 'CCTV PTZ', 'CAT-CCTV', 'Kamera CCTV tipe PTZ'),
        ]
        for code, name, parent_code, desc in sub_cats:
            cat, _ = Category.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': desc,
                    'parent': categories[parent_code],
                    'is_active': True,
                }
            )
            categories[code] = cat
        self.stdout.write(f"  [OK] Inventory Categories: {Category.objects.count()}")

        # ============================================================
        # 17. INVENTORY - ITEMS
        # ============================================================
        self.stdout.write("Seeding Inventory Items...")
        from apps.inventory.models import Item

        items_data = [
            ('CCTV Bullet 2MP', 'CCTV-001', categories['CAT-CCTV-BUL'], 'Hikvision', 'DS-2CE16D0T', '2MP IR Bullet Camera', 150000, 275000),
            ('CCTV Dome 2MP', 'CCTV-002', categories['CAT-CCTV-DOM'], 'Dahua', 'DH-HAC-HDW1200', '2MP IR Dome Camera', 180000, 325000),
            ('CCTV PTZ 5MP', 'CCTV-003', categories['CAT-CCTV-PTB'], 'Hikvision', 'DS-2DE5225', '5MP PTZ Camera 25x', 2500000, 3750000),
            ('Kabel UTP Cat6', 'NET-001', categories['CAT-CBL'], 'LanPro', 'LP-CAT6-305', 'UTP Cat6 305m Roll', 350000, 550000),
            ('Kabel Coaxial RG59', 'NET-002', categories['CAT-CBL'], 'Belden', 'RG59-U', 'Coaxial RG59 100m', 200000, 350000),
            ('Module Videotron P8', 'VID-001', categories['CAT-VID'], 'Videotron', 'P8-SMD', 'Module LED P8 Outdoor', 750000, 1250000),
            ('Module Videotron P10', 'VID-002', categories['CAT-VID'], 'Videotron', 'P10-DIP', 'Module LED P10 Outdoor', 500000, 850000),
            ('Power Supply CCTV', 'PWR-001', categories['CAT-PWR'], 'Mean Well', 'MW-12V10A', 'PSU CCTV 12V 10A', 150000, 250000),
            ('UPS 600VA', 'PWR-002', categories['CAT-PWR'], 'APC', 'APC-BX600', 'UPS 600VA Backup Power', 800000, 1250000),
            ('Konektor BNC', 'ACC-001', categories['CAT-ACC'], 'Generic', 'BNC-CONN', 'Konektor BNC Male (10 pcs)', 15000, 35000),
            ('Switch 8 Port', 'NET-003', categories['CAT-NET'], 'TP-Link', 'TL-SG108', 'Switch Gigabit 8 Port', 350000, 550000),
            ('Router Mikrotik', 'NET-004', categories['CAT-NET'], 'Mikrotik', 'RB951Ui-2HnD', 'RouterBoard 2.4GHz', 600000, 950000),
            ('Hard DVR 4Ch', 'CCTV-004', categories['CAT-CCTV'], 'Hikvision', 'DS-7204HGHI', 'DVR 4 Channel 1080p', 1200000, 1850000),
            ('Hard DVR 8Ch', 'CCTV-005', categories['CAT-CCTV'], 'Dahua', 'DHI-XVR5108', 'XVR 8 Channel 1080p', 2000000, 3250000),
            ('Kabel Listrik NYM 2x1.5', 'CBL-002', categories['CAT-CBL'], 'Supreme', 'NYM-2x1.5', 'Kabel Listrik 2x1.5mm 50m', 250000, 400000),
        ]

        items = {}
        for name, sku, cat, brand, model, specs, cost, sell in items_data:
            item, _ = Item.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': cat,
                    'brand': brand,
                    'model': model,
                    'specs': specs,
                    'unit': 'pcs' if 'Kabel' not in name else 'roll',
                    'min_stock': 5,
                    'max_stock': 50,
                    'cost_price': cost,
                    'sell_price': sell,
                    'warehouse_location': f'WH-{random.choice(["A", "B", "C"])}',
                    'rack_location': f'RACK-{random.choice(["A", "B", "C", "D"])}{random.randint(1, 5)}',
                    'is_active': True,
                    'default_supplier': random.choice(list(suppliers.values())),
                    'created_by': users['admin_utama'],
                }
            )
            items[sku] = item
        self.stdout.write(f"  [OK] Items: {Item.objects.count()}")

        # ============================================================
        # 18. PROJECTS - PROJECTS (harus setelah User, ProjectCategory, Employee)
        # ============================================================
        self.stdout.write("Seeding Projects...")
        from apps.projects.models import Project

        projects_data = [
            ('PRJ-001', 'Instalasi CCTV Gedung A', 'Instalasi CCTV', 'PT Maju Jaya', 'Bambang', 'Jl. Merdeka No. 45', 'Jakarta', 'draft', 'medium', 150000000),
            ('PRJ-002', 'Pemasangan Videotron Mall', 'Pemasangan Videotron', 'PT Mall Indah', 'Siti', 'Jl. Sudirman No. 10', 'Jakarta', 'survey', 'high', 500000000),
            ('PRJ-003', 'Instalasi Jaringan Kantor', 'Instalasi Jaringan', 'PT Teknologi Maju', 'Doni', 'Jl. Gatot Subroto No. 88', 'Bandung', 'progress', 'medium', 75000000),
            ('PRJ-004', 'Upgrade CCTV Perumahan', 'Instalasi CCTV', 'Perumahan Griya Indah', 'RW 05', 'Jl. Flamboyan No. 1', 'Tangerang', 'progress', 'low', 250000000),
            ('PRJ-005', 'Maintenance Bulanan', 'Maintenance', 'PT Bank Sejahtera', 'Adi', 'Jl. Thamrin No. 1', 'Jakarta', 'testing', 'high', 25000000),
            ('PRJ-006', 'Instalasi Kabel Fiber Optik', 'Instalasi Kabel', 'PT Telkom Akses', 'Rudi', 'Jl. Asia Afrika No. 100', 'Bandung', 'completed', 'urgent', 350000000),
            ('PRJ-007', 'Pemasangan CCTV Gudang', 'Instalasi CCTV', 'PT Logistik Nusantara', 'Yanto', 'Jl. Pelabuhan No. 50', 'Surabaya', 'progress', 'medium', 85000000),
            ('PRJ-008', 'Instalasi Jaringan Sekolah', 'Instalasi Jaringan', 'Yayasan Pendidikan', 'Kepala Sekolah', 'Jl. Pendidikan No. 20', 'Yogyakarta', 'draft', 'high', 45000000),
            ('PRJ-009', 'Pengadaan Server & Rack', 'Pengadaan Barang', 'PT Asuransi Jiwa', 'Deni', 'Jl. Kuningan No. 5', 'Jakarta', 'pending', 'urgent', 200000000),
            ('PRJ-010', 'Support Teknis Tahunan', 'Support Teknis', 'PT Bank Sejahtera', 'Agus', 'Jl. Thamrin No. 1', 'Jakarta', 'progress', 'low', 120000000),
        ]

        projects = {}
        for code, name, cat_name, client, cp, addr, city, status, priority, value in projects_data:
            proj, _ = Project.objects.get_or_create(
                project_code=code,
                defaults={
                    'name': name,
                    'category': project_cats[cat_name],
                    'client_name': client,
                    'client_contact': cp,
                    'client_phone': f'0812{random.randint(1000000, 9999999)}',
                    'client_email': f'{client.lower().replace(" ", "")}@gmail.com',
                    'address': addr,
                    'city': city,
                    'province': 'DKI Jakarta' if city == 'Jakarta' else city,
                    'description': f'Proyek {name} untuk {client}',
                    'scope_of_work': f'Lingkup pekerjaan meliputi {name.lower()}',
                    'status': status,
                    'priority': priority,
                    'start_date': date.today() - timedelta(days=random.randint(30, 180)),
                    'end_date': date.today() + timedelta(days=random.randint(30, 180)) if status not in ['completed', 'canceled'] else date.today(),
                    'due_date': date.today() + timedelta(days=random.randint(30, 180)),
                    'contract_value': value,
                    'leader': random.choice([users['staff_rudi'], users['staff_ahmad'], users['staff_hendra']]),
                    'created_by': users['admin_utama'],
                    'is_active': status != 'canceled',
                }
            )
            projects[code] = proj
        self.stdout.write(f"  [OK] Projects: {Project.objects.count()}")

        # ============================================================
        # 19. PROJECTS - LOCATIONS
        # ============================================================
        self.stdout.write("Seeding Project Locations...")
        from apps.projects.models import ProjectLocation

        for i, (code, proj) in enumerate(list(projects.items())[:10]):
            for j in range(random.randint(1, 3)):
                ProjectLocation.objects.get_or_create(
                    project=proj,
                    location_name=f'Titik {j+1} - {proj.name}',
                    defaults={
                        'address': f'{proj.address}, Lantai {j+1}',
                        'city': proj.city,
                        'latitude': f'-6.{random.randint(100000, 999999)}',
                        'longitude': f'106.{random.randint(700000, 899999)}',
                        'notes': f'Lokasi titik ke-{j+1} dari proyek {proj.project_code}',
                    }
                )
        self.stdout.write(f"  [OK] Project Locations: {ProjectLocation.objects.count()}")

        # ============================================================
        # 20. PROJECTS - PROGRESS
        # ============================================================
        self.stdout.write("Seeding Project Progresses...")
        from apps.projects.models import ProjectProgress

        active_projects = Project.objects.filter(status__in=['progress', 'testing', 'pending'])
        for proj in active_projects:
            for day_offset in range(random.randint(3, 8)):
                d = date.today() - timedelta(days=day_offset * 3)
                ProjectProgress.objects.get_or_create(
                    project=proj,
                    date=d,
                    defaults={
                        'percentage': random.randint(5, 30),
                        'description': f'Progress hari ke-{(day_offset+1)*3}: Pekerjaan berjalan lancar',
                        'workers_count': random.randint(3, 15),
                        'status': 'progress',
                        'reported_by': proj.leader or users['staff_rudi'],
                    }
                )
        self.stdout.write(f"  [OK] Project Progresses: {ProjectProgress.objects.count()}")

        # ============================================================
        # 21. PROJECTS - TEAM ASSIGNMENTS
        # ============================================================
        self.stdout.write("Seeding Team Assignments...")
        from apps.projects.models import TeamAssignment

        team_roles = ['leader', 'technician', 'technician', 'helper', 'supervisor']
        all_staff = [u for k, u in users.items() if k.startswith('staff_')]
        for proj in Project.objects.all()[:8]:
            for role in team_roles:
                member = random.choice(all_staff)
                TeamAssignment.objects.get_or_create(
                    project=proj,
                    user=member,
                    defaults={
                        'role': role,
                        'is_active': True,
                        'notes': f'Anggota tim untuk proyek {proj.project_code}',
                    }
                )
        self.stdout.write(f"  [OK] Team Assignments: {TeamAssignment.objects.count()}")

        # ============================================================
        # 22. PROJECTS - MILESTONES
        # ============================================================
        self.stdout.write("Seeding Project Milestones...")
        from apps.projects.models import ProjectMilestone

        milestone_names = [
            'Survey Lokasi', 'Pengadaan Material', 'Instalasi', 'Testing',
            'Handover', 'Dokumentasi', 'Pembayaran DP', 'Pembayaran Pelunasan'
        ]
        for proj in active_projects[:6]:
            for m_name in milestone_names[:random.randint(3, 6)]:
                ProjectMilestone.objects.get_or_create(
                    project=proj,
                    title=m_name,
                    defaults={
                        'description': f'Milestone: {m_name} untuk proyek {proj.name}',
                        'due_date': date.today() + timedelta(days=random.randint(7, 90)),
                        'is_completed': random.choice([True, False]),
                        'completed_date': date.today() - timedelta(days=random.randint(1, 30)) if random.random() > 0.5 else None,
                    }
                )
        self.stdout.write(f"  [OK] Project Milestones: {ProjectMilestone.objects.count()}")

        # ============================================================
        # 23. PROJECTS - DOCUMENTS
        # ============================================================
        self.stdout.write("Seeding Project Documents...")
        from apps.projects.models import ProjectDocument

        doc_types = ['contract', 'survey', 'design', 'report', 'photo', 'other']
        for proj in Project.objects.all()[:8]:
            for doc_type in doc_types[:random.randint(3, 5)]:
                ProjectDocument.objects.get_or_create(
                    project=proj,
                    title=f'Dokumen {dict(ProjectDocument.DOC_TYPE_CHOICES).get(doc_type)} - {proj.project_code}',
                    doc_type=doc_type,
                    defaults={
                        'file': f'projects/documents/{proj.project_code}_{doc_type}.pdf',
                        'description': f'Dokumen {dict(ProjectDocument.DOC_TYPE_CHOICES).get(doc_type)} untuk proyek {proj.name}',
                        'uploaded_by': random.choice(all_staff),
                    }
                )
        self.stdout.write(f"  [OK] Project Documents: {ProjectDocument.objects.count()}")

        # ============================================================
        # 24. INVENTORY - STOCK IN
        # ============================================================
        self.stdout.write("Seeding Stock In...")
        from apps.inventory.models import StockIn, StockInItem

        for i in range(10):
            si, _ = StockIn.objects.get_or_create(
                transaction_number=f'SI-DUMMY-{202401:06d}{i+1:04d}',
                defaults={
                    'source': random.choice(['purchase', 'return', 'adjustment']),
                    'supplier': random.choice(list(suppliers.values())),
                    'transaction_date': date.today() - timedelta(days=random.randint(1, 60)),
                    'received_date': date.today() - timedelta(days=random.randint(1, 60)),
                    'reference_number': f'PO/{2024}/{random.randint(100, 999)}',
                    'status': 'completed' if i < 7 else 'pending',
                    'notes': f'Pembelian barang untuk stok gudang',
                    'total_items': random.randint(10, 100),
                    'total_amount': random.randint(5000000, 50000000),
                    'created_by': random.choice(all_staff),
                    'is_completed': i < 7,
                }
            )
            # Stock In Items
            for _ in range(random.randint(2, 5)):
                item = random.choice(list(items.values()))
                qty = random.randint(5, 50)
                StockInItem.objects.get_or_create(
                    stock_in=si,
                    item=item,
                    defaults={
                        'quantity': qty,
                        'unit_price': item.cost_price,
                        'discount': 0,
                        'total': qty * item.cost_price,
                        'batch_number': f'BATCH-{2024}{random.randint(100, 999)}',
                        'notes': '',
                    }
                )
        self.stdout.write(f"  [OK] Stock In: {StockIn.objects.count()}, Stock In Items: {StockInItem.objects.count()}")

        # ============================================================
        # 25. INVENTORY - STOCK OUT
        # ============================================================
        self.stdout.write("Seeding Stock Out...")
        from apps.inventory.models import StockOut, StockOutItem

        for i in range(10):
            proj = random.choice(list(projects.values())) if projects else None
            so, _ = StockOut.objects.get_or_create(
                transaction_number=f'SO-DUMMY-{202401:06d}{i+1:04d}',
                defaults={
                    'out_type': random.choice(['project', 'sales', 'adjustment']),
                    'project': proj,
                    'transaction_date': date.today() - timedelta(days=random.randint(1, 30)),
                    'delivered_date': date.today() - timedelta(days=random.randint(1, 30)),
                    'reference_number': f'SPK/{2024}/{random.randint(100, 999)}',
                    'status': 'completed' if i < 7 else 'approved',
                    'notes': f'Barang keluar untuk proyek' if proj else 'Barang keluar penjualan',
                    'total_items': random.randint(5, 50),
                    'total_amount': random.randint(2000000, 30000000),
                    'created_by': random.choice(all_staff),
                    'delivered_to': proj.client_name if proj else 'Customer Umum',
                    'is_completed': i < 7,
                }
            )
            # Stock Out Items
            for _ in range(random.randint(2, 4)):
                item = random.choice(list(items.values()))
                qty = random.randint(2, 20)
                StockOutItem.objects.get_or_create(
                    stock_out=so,
                    item=item,
                    defaults={
                        'quantity': qty,
                        'unit_price': item.sell_price,
                        'total': qty * item.sell_price,
                        'notes': '',
                    }
                )
        self.stdout.write(f"  [OK] Stock Out: {StockOut.objects.count()}, Stock Out Items: {StockOutItem.objects.count()}")

        # ============================================================
        # 26. INVENTORY - STOCK OPNAME
        # ============================================================
        self.stdout.write("Seeding Stock Opname...")
        from apps.inventory.models import StockOpname, StockOpnameItem

        for i in range(5):
            so, _ = StockOpname.objects.get_or_create(
                opname_number=f'SOP-DUMMY-{202401:06d}{i+1:04d}',
                defaults={
                    'start_date': date.today() - timedelta(days=random.randint(10, 60)),
                    'end_date': date.today() - timedelta(days=random.randint(5, 55)),
                    'status': 'completed',
                    'notes': f'Stok opname periode ke-{i+1}',
                    'total_system': random.randint(50000000, 500000000),
                    'total_actual': random.randint(50000000, 500000000),
                    'difference': 0,
                    'created_by': random.choice(all_staff),
                }
            )
            for _ in range(random.randint(5, 10)):
                item = random.choice(list(items.values()))
                sys_qty = random.randint(10, 100)
                StockOpnameItem.objects.get_or_create(
                    stock_opname=so,
                    item=item,
                    defaults={
                        'system_quantity': sys_qty,
                        'actual_quantity': sys_qty + random.randint(-5, 5),
                        'notes': '',
                    }
                )
        self.stdout.write(f"  [OK] Stock Opnames: {StockOpname.objects.count()}, Opname Items: {StockOpnameItem.objects.count()}")

        # ============================================================
        # 27. INVENTORY - STOCK ALERTS
        # ============================================================
        self.stdout.write("Seeding Stock Alerts...")
        from apps.inventory.models import StockAlert

        alert_types = ['stock_below_min', 'stock_above_max', 'expiry_warning', 'no_stock']
        for i in range(10):
            item = list(items.values())[i % len(items)]
            StockAlert.objects.get_or_create(
                item=item,
                alert_type=alert_types[i % len(alert_types)],
                defaults={
                    'is_resolved': random.choice([True, False]),
                    'resolved_by': random.choice(all_staff) if random.random() > 0.5 else None,
                    'notes': f'Peringatan untuk item {item.name}',
                }
            )
        self.stdout.write(f"  [OK] Stock Alerts: {StockAlert.objects.count()}")

        # ============================================================
        # 28. FINANCE - ACCOUNTS (COA)
        # ============================================================
        self.stdout.write("Seeding Finance Accounts...")
        from apps.finance.models import Account

        coa_data = [
            ('1-1000', 'Kas', 'asset', None, True),
            ('1-1100', 'Bank BCA', 'asset', None, True),
            ('1-2000', 'Piutang Usaha', 'asset', None, False),
            ('1-3000', 'Persediaan Barang', 'asset', None, False),
            ('2-1000', 'Hutang Usaha', 'liability', None, False),
            ('2-2000', 'Hutang Pajak', 'liability', None, False),
            ('3-1000', 'Modal', 'equity', None, False),
            ('4-1000', 'Pendapatan Jasa', 'revenue', None, False),
            ('5-1000', 'Beban Gaji', 'expense', None, False),
            ('5-2000', 'Beban Operasional', 'expense', None, False),
        ]

        accounts = {}
        for code, name, acc_type, parent, is_cash in coa_data:
            acc, _ = Account.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'account_type': acc_type,
                    'parent': parent,
                    'description': f'Akun {name}',
                    'is_active': True,
                    'is_cash': is_cash,
                }
            )
            accounts[code] = acc
        self.stdout.write(f"  [OK] Finance Accounts: {Account.objects.count()}")

        # ============================================================
        # 29. FINANCE - INCOME CATEGORIES
        # ============================================================
        self.stdout.write("Seeding Income Categories...")
        from apps.finance.models import IncomeCategory

        income_cats_data = [
            ('INC-CCTV', 'Pendapatan CCTV', '4-1000'),
            ('INC-NET', 'Pendapatan Jaringan', '4-1000'),
            ('INC-VID', 'Pendapatan Videotron', '4-1000'),
            ('INC-MNT', 'Pendapatan Maintenance', '4-1000'),
            ('INC-OTH', 'Pendapatan Lainnya', '4-1000'),
        ]

        income_cats = {}
        for code, name, acc_code in income_cats_data:
            cat, _ = IncomeCategory.objects.get_or_create(
                code=code,
                defaults={'name': name, 'account': accounts[acc_code]}
            )
            income_cats[code] = cat
        self.stdout.write(f"  [OK] Income Categories: {IncomeCategory.objects.count()}")

        # ============================================================
        # 30. FINANCE - EXPENSE CATEGORIES
        # ============================================================
        self.stdout.write("Seeding Expense Categories...")
        from apps.finance.models import ExpenseCategory

        expense_cats_data = [
            ('EXP-GAJI', 'Beban Gaji & Upah', '5-1000'),
            ('EXP-OPR', 'Beban Operasional', '5-2000'),
            ('EXP-TRAN', 'Beban Transportasi', '5-2000'),
            ('EXP-PEM', 'Beban Pembelian Barang', '5-2000'),
            ('EXP-OTH', 'Beban Lainnya', '5-2000'),
        ]

        expense_cats = {}
        for code, name, acc_code in expense_cats_data:
            cat, _ = ExpenseCategory.objects.get_or_create(
                code=code,
                defaults={'name': name, 'account': accounts[acc_code]}
            )
            expense_cats[code] = cat
        self.stdout.write(f"  [OK] Expense Categories: {ExpenseCategory.objects.count()}")

        # ============================================================
        # 31. SALES - CUSTOMERS
        # ============================================================
        self.stdout.write("Seeding Sales Customers...")
        from apps.sales.models import Customer

        customers_data = [
            ('CUST-001', 'PT Maju Jaya', 'Bambang', '08110000001', 'Jl. Merdeka No. 45', 'Jakarta', '01.234.567.8-001.000'),
            ('CUST-002', 'PT Mall Indah', 'Siti Rahayu', '08110000002', 'Jl. Sudirman No. 10', 'Jakarta', '01.234.567.8-002.000'),
            ('CUST-003', 'PT Teknologi Maju', 'Doni Prasetyo', '08110000003', 'Jl. Gatot Subroto No. 88', 'Bandung', '01.234.567.8-003.000'),
            ('CUST-004', 'PT Bank Sejahtera', 'Adi Nugroho', '08110000004', 'Jl. Thamrin No. 1', 'Jakarta', '01.234.567.8-004.000'),
            ('CUST-005', 'PT Telkom Akses', 'Rudi Hartono', '08110000005', 'Jl. Asia Afrika No. 100', 'Bandung', '01.234.567.8-005.000'),
            ('CUST-006', 'PT Logistik Nusantara', 'Yanto Susilo', '08110000006', 'Jl. Pelabuhan No. 50', 'Surabaya', '01.234.567.8-006.000'),
            ('CUST-007', 'Yayasan Pendidikan', 'Drs. H. Ahmad', '08110000007', 'Jl. Pendidikan No. 20', 'Yogyakarta', '01.234.567.8-007.000'),
            ('CUST-008', 'PT Asuransi Jiwa', 'Deni Hermawan', '08110000008', 'Jl. Kuningan No. 5', 'Jakarta', '01.234.567.8-008.000'),
            ('CUST-009', 'Perumahan Griya Indah', 'RW 05', '08110000009', 'Jl. Flamboyan No. 1', 'Tangerang', '01.234.567.8-009.000'),
            ('CUST-010', 'PT Anugerah Abadi', 'Hendra Gunawan', '08110000010', 'Jl. Raya No. 99', 'Jakarta', '01.234.567.8-010.000'),
        ]

        customers = {}
        for code, name, cp, phone, addr, city, npwp in customers_data:
            cust, _ = Customer.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'contact_person': cp,
                    'phone': phone,
                    'email': f'{name.lower().replace(" ", "")}@gmail.com',
                    'address': addr,
                    'city': city,
                    'province': 'DKI Jakarta' if city == 'Jakarta' else city,
                    'npwp': npwp,
                    'business_type': 'Perusahaan',
                    'is_active': True,
                }
            )
            customers[code] = cust
        self.stdout.write(f"  [OK] Customers: {Customer.objects.count()}")

        # ============================================================
        # 32. SALES - VENDORS
        # ============================================================
        self.stdout.write("Seeding Sales Vendors...")
        from apps.sales.models import Vendor

        vendors_data = [
            ('VEND-001', 'PT Hikvision Indonesia', 'Bambang Supomo'),
            ('VEND-002', 'PT Dahua Technology', 'Susi Susanti'),
            ('VEND-003', 'CV LanPro Networking', 'Hendra Kurniawan'),
            ('VEND-004', 'PT Videotron Solution', 'Rudi Hermawan'),
            ('VEND-005', 'PT Kabelindo Utama', 'Ani Lestari'),
            ('VEND-006', 'PT UPS Solution', 'Doni Firmansyah'),
            ('VEND-007', 'CV Aksesoris Komputer', 'Lina Marlina'),
            ('VEND-008', 'PT Tools Indonesia', 'Rizky Pratama'),
            ('VEND-009', 'CV Elektronik Jaya', 'Sari Wulandari'),
            ('VEND-010', 'PT General Suplai', 'Budi Hartono'),
        ]

        for code, name, cp in vendors_data:
            Vendor.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'contact_person': cp,
                    'phone': f'021-{random.randint(1000000, 9999999)}',
                    'email': f'{name.lower().replace(" ", "")}@gmail.com',
                    'address': f'Jl. Industri No. {random.randint(1, 100)}, Jakarta',
                    'city': 'Jakarta',
                    'is_active': True,
                }
            )
        self.stdout.write(f"  [OK] Sales Vendors: {Vendor.objects.count()}")

        # ============================================================
        # 33. FINANCE - INCOME
        # ============================================================
        self.stdout.write("Seeding Finance Income...")
        from apps.finance.models import Income

        for i in range(10):
            cust = random.choice(list(customers.values()))
            proj = random.choice(list(projects.values())) if projects else None
            amount = random.randint(5000000, 100000000)
            Income.objects.get_or_create(
                income_number=f'INC-DUMMY-{202401:06d}{i+1:04d}',
                defaults={
                    'date': date.today() - timedelta(days=random.randint(1, 60)),
                    'category': random.choice(list(income_cats.values())),
                    'amount': amount,
                    'description': f'Pendapatan dari {cust.name}' + (f' untuk proyek {proj.project_code}' if proj else ''),
                    'customer': cust,
                    'project': proj,
                    'account': accounts['1-1100'],
                    'status': random.choice(['confirmed', 'completed']),
                    'created_by': random.choice(all_staff),
                    'is_completed': True,
                }
            )
        self.stdout.write(f"  [OK] Incomes: {Income.objects.count()}")

        # ============================================================
        # 34. FINANCE - EXPENSE
        # ============================================================
        self.stdout.write("Seeding Finance Expenses...")
        from apps.finance.models import Expense

        supplier_list = list(suppliers.values())
        for i in range(10):
            sup = random.choice(supplier_list)
            proj = random.choice(list(projects.values())) if projects else None
            amount = random.randint(1000000, 50000000)
            Expense.objects.get_or_create(
                expense_number=f'EXP-DUMMY-{202401:06d}{i+1:04d}',
                defaults={
                    'date': date.today() - timedelta(days=random.randint(1, 60)),
                    'category': random.choice(list(expense_cats.values())),
                    'amount': amount,
                    'description': f'Pembayaran ke {sup.name}' + (f' untuk proyek {proj.project_code}' if proj else ''),
                    'vendor': sup,
                    'project': proj,
                    'account': accounts['1-1000'],
                    'status': random.choice(['confirmed', 'completed']),
                    'created_by': random.choice(all_staff),
                    'is_completed': True,
                }
            )
        self.stdout.write(f"  [OK] Expenses: {Expense.objects.count()}")

        # ============================================================
        # 35. FINANCE - JOURNAL ENTRIES
        # ============================================================
        self.stdout.write("Seeding Finance Journal Entries...")
        from apps.finance.models import JournalEntry, JournalEntryItem

        for i in range(10):
            je, _ = JournalEntry.objects.get_or_create(
                entry_number=f'JE-DUMMY-{202401:06d}{i+1:04d}',
                defaults={
                    'date': date.today() - timedelta(days=random.randint(1, 30)),
                    'description': f'Jurnal transaksi ke-{i+1}',
                    'status': 'posted',
                    'created_by': random.choice(all_staff),
                }
            )
            # Debit
            JournalEntryItem.objects.get_or_create(
                journal_entry=je,
                account=accounts['4-1000'],
                defaults={'description': 'Pendapatan jasa', 'debit': random.randint(5000000, 50000000), 'credit': 0}
            )
            # Credit
            JournalEntryItem.objects.get_or_create(
                journal_entry=je,
                account=accounts['1-1100'],
                defaults={'description': 'Kas masuk', 'debit': 0, 'credit': random.randint(5000000, 50000000)}
            )
        self.stdout.write(f"  [OK] Journal Entries: {JournalEntry.objects.count()}, Journal Items: {JournalEntryItem.objects.count()}")

        # ============================================================
        # 36. FINANCE - INVOICES
        # ============================================================
        self.stdout.write("Seeding Finance Invoices...")
        from apps.finance.models import Invoice, InvoiceItem

        for i in range(10):
            cust = random.choice(list(customers.values()))
            proj = random.choice(list(projects.values())) if projects else None
            total = random.randint(10000000, 200000000)
            status_list = ['sent', 'paid', 'partial', 'overdue']
            inv, _ = Invoice.objects.get_or_create(
                invoice_number=f'INV-DUMMY-{202401:06d}{i+1:04d}',
                defaults={
                    'invoice_type': 'invoice',
                    'customer': cust,
                    'project': proj,
                    'date': date.today() - timedelta(days=random.randint(10, 90)),
                    'due_date': date.today() - timedelta(days=random.randint(5, 30)),
                    'subtotal': total,
                    'tax': total * 11 // 100,
                    'discount': 0,
                    'total': total + (total * 11 // 100),
                    'amount_paid': (total + (total * 11 // 100)) if status_list[i % 4] == 'paid' else total // 2,
                    'amount_due': 0 if status_list[i % 4] == 'paid' else total // 2,
                    'status': status_list[i % 4],
                    'created_by': random.choice(all_staff),
                }
            )
            # Invoice Items
            for _ in range(random.randint(2, 4)):
                item = random.choice(list(items.values())) if items else None
                InvoiceItem.objects.get_or_create(
                    invoice=inv,
                    description=f'{item.name} x {random.randint(2, 10)} unit' if item else f'Jasa ke-{_}',
                    defaults={
                        'quantity': random.randint(1, 10),
                        'unit_price': random.randint(100000, 5000000),
                        'total': random.randint(1000000, 10000000),
                    }
                )
        self.stdout.write(f"  [OK] Invoices: {Invoice.objects.count()}, Invoice Items: {InvoiceItem.objects.count()}")

        # ============================================================
        # 37. FINANCE - PAYMENTS
        # ============================================================
        self.stdout.write("Seeding Finance Payments...")
        from apps.finance.models import Payment

        invoices = Invoice.objects.filter(status__in=['paid', 'partial'])
        for i, inv in enumerate(invoices[:10]):
            Payment.objects.get_or_create(
                payment_number=f'PAY-DUMMY-{202401:06d}{i+1:04d}',
                defaults={
                    'payment_type': 'invoice',
                    'invoice': inv,
                    'customer': inv.customer,
                    'date': inv.due_date - timedelta(days=random.randint(0, 5)),
                    'amount': inv.amount_paid,
                    'account': accounts['1-1100'],
                    'bank': 'Bank BCA',
                    'notes': f'Pembayaran untuk {inv.invoice_number}',
                    'created_by': random.choice(all_staff),
                }
            )
        self.stdout.write(f"  [OK] Payments: {Payment.objects.count()}")

        # ============================================================
        # 38. SALES - QUOTATIONS
        # ============================================================
        self.stdout.write("Seeding Sales Quotations...")
        from apps.sales.models import Quotation, QuotationItem

        for i in range(10):
            cust = random.choice(list(customers.values()))
            proj = random.choice(list(projects.values())) if projects else None
            total = random.randint(10000000, 150000000)
            qt, _ = Quotation.objects.get_or_create(
                quotation_number=f'QT-DUMMY-{202401:06d}{i+1:04d}',
                defaults={
                    'customer': cust,
                    'project': proj,
                    'date': date.today() - timedelta(days=random.randint(10, 60)),
                    'valid_until': date.today() + timedelta(days=30),
                    'subtotal': total,
                    'tax': total * 11 // 100,
                    'discount': 0,
                    'total': total + (total * 11 // 100),
                    'payment_terms': 'Net 30',
                    'delivery_terms': 'FOB Jakarta',
                    'status': random.choice(['draft', 'sent', 'accepted', 'expired']),
                    'created_by': random.choice(all_staff),
                }
            )
            for _ in range(random.randint(2, 5)):
                item = random.choice(list(items.values())) if items else None
                if item:
                    qty = random.randint(2, 20)
                    QuotationItem.objects.get_or_create(
                        quotation=qt,
                        item=item,
                        defaults={
                            'description': item.name,
                            'quantity': qty,
                            'unit_price': item.sell_price,
                            'discount': 0,
                            'total': qty * item.sell_price,
                        }
                    )
        self.stdout.write(f"  [OK] Quotations: {Quotation.objects.count()}, Quotation Items: {QuotationItem.objects.count()}")

        # ============================================================
        # 39. SALES - SALES ORDERS
        # ============================================================
        self.stdout.write("Seeding Sales Orders...")
        from apps.sales.models import SalesOrder, SalesOrderItem

        quotations = Quotation.objects.filter(status='accepted')[:5]
        for i in range(10):
            cust = random.choice(list(customers.values()))
            proj = random.choice(list(projects.values())) if projects else None
            qt = random.choice(quotations) if quotations else None
            total = random.randint(10000000, 150000000)
            so, _ = SalesOrder.objects.get_or_create(
                sales_order_number=f'SO-DUMMY-{202401:06d}{i+1:04d}',
                defaults={
                    'quotation': qt if random.random() > 0.5 else None,
                    'customer': cust,
                    'project': proj,
                    'date': date.today() - timedelta(days=random.randint(5, 30)),
                    'delivery_date': date.today() + timedelta(days=random.randint(7, 30)),
                    'subtotal': total,
                    'tax': total * 11 // 100,
                    'discount': 0,
                    'total': total + (total * 11 // 100),
                    'status': random.choice(['draft', 'confirmed', 'in_progress', 'completed']),
                    'created_by': random.choice(all_staff),
                }
            )
            for _ in range(random.randint(2, 4)):
                item = random.choice(list(items.values())) if items else None
                if item:
                    qty = random.randint(2, 15)
                    SalesOrderItem.objects.get_or_create(
                        sales_order=so,
                        item=item,
                        defaults={
                            'description': item.name,
                            'quantity': qty,
                            'unit_price': item.sell_price,
                            'discount': 0,
                            'total': qty * item.sell_price,
                        }
                    )
        self.stdout.write(f"  [OK] Sales Orders: {SalesOrder.objects.count()}, SO Items: {SalesOrderItem.objects.count()}")

        # ============================================================
        # 40. SALES - PURCHASE ORDERS
        # ============================================================
        self.stdout.write("Seeding Purchase Orders...")
        from apps.sales.models import PurchaseOrder, PurchaseOrderItem

        for i in range(10):
            vendor_sup = random.choice(list(suppliers.values()))
            total = random.randint(5000000, 100000000)
            po, _ = PurchaseOrder.objects.get_or_create(
                purchase_order_number=f'PO-DUMMY-{202401:06d}{i+1:04d}',
                defaults={
                    'vendor': vendor_sup,
                    'date': date.today() - timedelta(days=random.randint(5, 45)),
                    'delivery_date': date.today() + timedelta(days=random.randint(7, 30)),
                    'subtotal': total,
                    'tax': total * 11 // 100,
                    'discount': 0,
                    'total': total + (total * 11 // 100),
                    'status': random.choice(['draft', 'sent', 'confirmed', 'received', 'completed']),
                    'created_by': random.choice(all_staff),
                }
            )
            for _ in range(random.randint(2, 5)):
                item = random.choice(list(items.values())) if items else None
                if item:
                    qty = random.randint(5, 50)
                    PurchaseOrderItem.objects.get_or_create(
                        purchase_order=po,
                        item=item,
                        defaults={
                            'quantity': qty,
                            'unit_price': item.cost_price,
                            'discount': 0,
                            'total': qty * item.cost_price,
                        }
                    )
        self.stdout.write(f"  [OK] Purchase Orders: {PurchaseOrder.objects.count()}, PO Items: {PurchaseOrderItem.objects.count()}")

        # ============================================================
        # SELESAI
        # ============================================================
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('  SEED DATA BERHASIL! Semua tabel telah diisi.'))
        self.stdout.write(self.style.SUCCESS('=' * 60 + '\n'))
