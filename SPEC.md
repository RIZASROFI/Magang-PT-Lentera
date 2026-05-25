# Sistem Informasi Manajemen PT Lentera Anugerah Dimensi

## 1. Project Overview

**Nama Aplikasi:** SIMAN - Sistem Informasi Manajemen  
**Perusahaan:** PT Lentera Anugerah Dimensi  
**Bidang:** IT Networking (CCTV, Videotron, Server)  
**Tipe:** Enterprise Resource Planning (ERP), Transaction Processing System (TPS), Management Information System (MIS)

### Teknologi Stack
- **Backend:** Django 4.2 + Django REST Framework
- **Database:** MySQL 8.0
- **Frontend:** HTML5, CSS3, JavaScript (SPA dengan Fetch API)
- **Authentication:** JWT Token-based

---

## 2. Modul & Fitur

### 2.1 Modul Project Management
**TPS Module**
- Lokasi proyek (alamat, client, kontak)
- Progress pekerjaan (status: rencana, berjalan, selesai)
- Penugasan tim proyek
- Timeline & milestones
- Monitoring harian

### 2.2 Modul Inventory (TPS)
**Transaksi Processing**
- Barang masuk (purchase/terima dari vendor)
- Barang keluar (pengirman ke proyek)
- Stok-opname
- Kategori barang (CCTV, Videotron, Server, Accessories)
- Laporan stok

### 2.3 Modul Keuangan (MIS)
**Management Information**
- Income (penjualan, penerimaan)
- Expense (pembelian, operasional)
- Laporan keuangan (rugi-laba)
- Pengaturan akunCOA (Chart of Accounts)
- Transaksi bank

### 2.4 Modul HR (MIS)
**Employee Management**
- Data karyawan
- Jabatan & departemen
- Absensi
- Slip gaji
- Kontrak kerja

### 2.5 Modul Penjualan & Pembelian (ERP)
**Integrated Transactions**
- Quotations & Sales Orders
- Purchase Orders
- Customer Management
- Vendor Management
- Integrasi dengan Inventory & Keuangan

---

## 3. Fitur Sistem

### 3.1 Autentikasi & Otorisasi
- Role-based Access Control (RBAC)
- Role: Admin, Manager, Staff
- JWT Authentication
- Session management

### 3.2 Dashboard
- Widgets interaktif
- Grafik (Chart.js)
- Ringkasan data penting
- Notifikasi terbaru

### 3.3 Monitoring
- Project progress real-time
- Inventory alerts
- Financial summary

### 3.4 Notifikasi
- Email notifications
- In-app notifications
- Sistem notifikasi terpusat

### 3.5 Integrasi Antar Modul
- Project → Inventory (barang keluar proyek)
- Penjualan → Inventory (kurangi stok)
- Penjualan → Keuangan (income)
- Pembelian → Inventory (barang masuk)
- Pembelian → Keuangan (expense)

---

## 4. Struktur Database

### Users & Auth
- `users` - Extended User model
- `userprofiles` - Profile dengan role

### Project Module
- `projects` - Master proyek
- `projectlocations` - Lokasi detail
- `progresstracker` - Tracking progress
- `teamassignments` - Penugasan tim

### Inventory Module
- `inventoryitems` - Master barang
- `inventorycategories` - Kategori
- `stockin` - Barang masuk
- `stockout` - Barang keluar
- `stockopname` - Stok opname

### Finance Module
- `accounts` - COA
- `transactions` - Jurnal umum
- `incomes` - Income records
- `expenses` - Expense records

### HR Module
- `employees` - Data karyawan
- `departments` - Departemen
- `positions` - Jabatan
- `attendances` - Absensi
- `salaries` - Gaji

### Sales & Purchase
- `customers` - Master customer
- `vendors` - Master vendor
- `quotations` - Penawaran
- `salesorders` - Sales order
- `purchaseorders` - Purchase order

---

## 5. REST API Endpoints

### Auth
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`

### Projects
- `GET/POST /api/projects/`
- `GET/PUT/DELETE /api/projects/{id}/`
- `GET/POST /api/progress/`

### Inventory
- `GET/POST /api/inventory/`
- `GET/POST /api/stock-in/`
- `GET/POST /api/stock-out/`

### Finance
- `GET/POST /api/accounts/`
- `GET/POST /api/transactions/`
- `GET /api/reports/finance/`

### HR
- `GET/POST /api/employees/`
- `GET/POST /api/attendances/`

### Sales & Purchase
- `GET/POST /api/customers/`
- `GET/POST /api/sales-orders/`
- `GET/POST /api/purchase-orders/`

---

## 6. File Structure

```
siman/
├── manage.py
├── requirements.txt
├── siman/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── auth/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── projects/
│   ├── inventory/
│   ├── finance/
│   ├── hr/
│   └── sales/
├── templates/
│   ├── base.html
│   ├── login.html
│   └── dashboard.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/
```

---

## 7. Implementation Steps

### Phase 1: Project Setup
1. Setup virtual environment
2. Install Django & dependencies
3. Configure MySQL database
4. Create Django project structure

### Phase 2: Core Development
1. Create custom user model
2. Implement authentication
3. Create base templates

### Phase 3: Module Development
1. Project Management module
2. Inventory module
3. Finance module
4. HR module
5. Sales & Purchase module

### Phase 4: Integration
1. Connect modules
2. Create dashboard
3. Implement notifications
4. Testing

### Phase 5: Deployment
1. Final testing
2. Documentation
3. Deployment preparation
