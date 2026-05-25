# 📚 DOKUMENTASI API LENGKAP - SIMAN

## ✅ STATUS IMPLEMENTASI CRUD

### Modul yang Sudah Complete:
- ✅ **HR Module** - Semua CRUD endpoints dan custom actions
- ✅ **Inventory Serializers** - Lengkap dengan nested items
- ✅ **Projects Models** - Semua models defined

### Modul yang Perlu Dilengkapi:
- [ ] Finance ViewSets (gunakan pattern HR module)
- [ ] Sales ViewSets (gunakan pattern HR module)
- [ ] Inventory ViewSets (gunakan pattern HR module)
- [ ] Projects ViewSets (update dengan nested routes lengkap)

---

## 🚀 QUICK START - TESTING CRUD OPERATIONS

### 1. Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create database
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### 2. Test dengan Postman/cURL

#### LOGIN - Get JWT Token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Response:
# {
#   "access": "eyJhbGc...",
#   "refresh": "eyJhbGc..."
# }
```

#### CREATE DEPARTMENT
```bash
curl -X POST http://127.0.0.1:8000/api/hr/departments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "IT Department",
    "code": "IT001",
    "description": "Information Technology Department"
  }'
```

#### LIST DEPARTMENTS
```bash
curl -X GET http://127.0.0.1:8000/api/hr/departments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### GET DEPARTMENT DETAIL
```bash
curl -X GET http://127.0.0.1:8000/api/hr/departments/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### UPDATE DEPARTMENT
```bash
curl -X PUT http://127.0.0.1:8000/api/hr/departments/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "IT Department - Updated",
    "code": "IT001"
  }'
```

#### DELETE DEPARTMENT
```bash
curl -X DELETE http://127.0.0.1:8000/api/hr/departments/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📋 API ENDPOINTS REFERENCE

### HR Module - Complete
```
/api/hr/departments/          - CRUD + stats
/api/hr/positions/            - CRUD
/api/hr/employees/            - CRUD + stats + salary
/api/hr/attendances/          - CRUD + report + approve
/api/hr/leaves/               - CRUD + approve + reject
/api/hr/salaries/             - CRUD + approve + pay
/api/hr/overtimes/            - CRUD + approve
```

### Inventory Module - Needs Implementation
```
/api/inventory/items/         - CRUD + low_stock
/api/inventory/categories/    - CRUD
/api/inventory/suppliers/     - CRUD
/api/inventory/stock-in/      - CRUD + approve
/api/inventory/stock-out/     - CRUD + approve + deliver
/api/inventory/stock-opname/  - CRUD
```

### Projects Module - Needs Implementation
```
/api/projects/                - CRUD
/api/projects/{id}/locations/ - Nested CRUD
/api/projects/{id}/progress/  - Nested CRUD + update_progress
/api/projects/{id}/team/      - Nested CRUD
/api/projects/{id}/milestones/ - Nested CRUD
/api/projects/{id}/documents/ - Nested CRUD
```

### Finance Module - Needs Implementation
```
/api/finance/accounts/        - CRUD + cash_accounts + stats
/api/finance/journal-entries/ - CRUD + post
/api/finance/invoices/        - CRUD + send + payment
/api/finance/payments/        - CRUD
/api/finance/income/          - CRUD
/api/finance/expenses/        - CRUD
/api/finance/reports/         - Financial reports endpoints
```

### Sales Module - Needs Implementation
```
/api/sales/customers/         - CRUD + total_sales + receivables
/api/sales/vendors/           - CRUD
/api/sales/quotations/        - CRUD + convert_to_sales_order
/api/sales/sales-orders/      - CRUD + confirm + complete
/api/sales/purchase-orders/   - CRUD + approve + receive
```

---

## 🔐 AUTHENTICATION ENDPOINTS

```
POST   /api/auth/login/              - User login
POST   /api/auth/logout/             - User logout
GET    /api/auth/me/                 - Get current user profile
POST   /api/auth/token/refresh/      - Refresh access token
POST   /api/auth/change-password/    - Change password
POST   /api/auth/register/           - User registration
```

---

## ✨ RESPONSE FORMAT

### Success Response
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Item Name",
    "created_at": "2024-04-30T10:00:00Z"
  }
}
```

### List Response with Pagination
```json
{
  "status": "success",
  "count": 100,
  "next": "http://api.example.com/api/module/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Item 1"
    }
  ]
}
```

### Error Response
```json
{
  "status": "error",
  "error": "ValidationError",
  "message": "Field 'name' is required",
  "details": {
    "name": ["This field is required."]
  }
}
```

---

## 📊 FIELD VALIDATION RULES

### Department
- `name` (string, required): Max 100 characters
- `code` (string, required, unique): Max 20 characters
- `description` (text, optional)
- `head` (integer, optional): FK to User
- `is_active` (boolean): Default True

### Employee
- `employee_id` (auto-generated): Format EMPYY#### (auto)
- `user` (ForeignKey, required): User model
- `nip` (string, optional): National ID
- `department` (ForeignKey, required)
- `position` (ForeignKey, required)
- `status` (choice): probation|contract|permanent|resigned|fired
- `join_date` (date, required)
- `resign_date` (date, optional)
- Personal info fields: birth_date, gender, marital_status, religion, etc.

### Attendance
- `employee` (ForeignKey, required)
- `date` (date, required): Unique per employee
- `status` (choice): present|absent|sick|permission|leave|late
- `check_in` (time, optional)
- `check_out` (time, optional)
- `overtime_hours` (decimal): 0-99.99 hours
- `notes` (text, optional)

### Leave
- `employee` (ForeignKey, required)
- `leave_type` (choice): annual|sick|maternity|paternity|unpaid|other
- `start_date` (date, required): Must be < end_date
- `end_date` (date, required)
- `reason` (text, required)
- `status` (choice): pending|approved|rejected|canceled

### Salary
- `employee` (ForeignKey, required)
- `period_month` (integer, required): 1-12
- `period_year` (integer, required)
- `basic_salary` (decimal): Harga beli base gaji
- `allowances` (decimal): Tunjangan
- `bonuses` (decimal): Bonus tambahan
- `deductions` (decimal): Potongan lainnya
- `tax` (decimal): PPh
- `bpjs` (decimal): Iuran BPJS
- Status: draft|calculated|approved|paid|canceled
- `payment_date` (date, optional)

---

## 🧪 TESTING EXAMPLES

### Scenario 1: Create Employee & Assign to Department
```bash
# 1. Create Department
POST /api/hr/departments/
{
  "name": "Sales Department",
  "code": "SALES001",
  "description": "Sales team"
}

# 2. Create Position
POST /api/hr/positions/
{
  "name": "Sales Manager",
  "code": "SM001",
  "department": 1,
  "level": 1
}

# 3. Create Employee
POST /api/hr/employees/
{
  "user": 5,  # ID user yang sudah ada
  "department": 1,
  "position": 1,
  "join_date": "2024-01-01",
  "gender": "male",
  "phone": "08123456789"
}
```

### Scenario 2: Record Attendance & Create Leave
```bash
# 1. Record Attendance
POST /api/hr/attendances/
{
  "employee": 1,
  "date": "2024-04-30",
  "status": "present",
  "check_in": "08:00:00",
  "check_out": "17:00:00"
}

# 2. Approve Attendance
POST /api/hr/attendances/1/approve/

# 3. Request Leave
POST /api/hr/leaves/
{
  "employee": 1,
  "leave_type": "annual",
  "start_date": "2024-05-01",
  "end_date": "2024-05-03",
  "reason": "Personal holiday"
}

# 4. Approve Leave
POST /api/hr/leaves/1/approve/
```

### Scenario 3: Calculate & Process Salary
```bash
# 1. Create Salary
POST /api/hr/salaries/
{
  "employee": 1,
  "period_month": 5,
  "period_year": 2024,
  "basic_salary": 5000000,
  "allowances": 500000,
  "bonuses": 200000,
  "overtime_pay": 100000,
  "deductions": 50000,
  "tax": 250000,
  "bpjs": 100000
}

# 2. Approve Salary
POST /api/hr/salaries/1/approve/

# 3. Mark as Paid
POST /api/hr/salaries/1/pay/
```

---

## 🛠️ TEMPLATE UNTUK MODULE LAIN

Setiap module harus mengikuti pattern yang sama:

1. **Serializers** (`apps/module/serializers.py`):
   - ListSerializer (untuk GET list)
   - DetailSerializer (untuk GET detail)
   - CreateUpdateSerializer (untuk POST/PUT)

2. **ViewSets** (`apps/module/views.py`):
   - Extend `viewsets.ModelViewSet`
   - Setup queryset, permissions, filters, search
   - Override `get_serializer_class()` per action
   - Add custom actions dengan `@action` decorator

3. **URLs** (`apps/module/urls.py`):
   - Register viewsets ke router
   - router akan auto-generate CRUD endpoints
   - Custom actions akan tersedia sebagai sub-routes

4. **Main URLs** (`siman/urls.py`):
   - Sudah ada: `path('api/module/', include('apps.module.urls'))`

---

## ✅ CHECKLIST IMPLEMENTASI

### [ ] Complete semua Module:
- [x] HR Module - Done!
- [ ] Inventory Module
  - [ ] Lengkapi Views (copy pattern dari HR)
  - [ ] Lengkapi URLs
  - [ ] Add custom actions (approve, receive, low_stock)
- [ ] Finance Module
  - [ ] Buat missing models (Invoice, Payment)
  - [ ] Buat Serializers lengkap
  - [ ] Buat Views lengkap
  - [ ] Buat URLs lengkap
- [ ] Projects Module
  - [ ] Buat nested Routes
  - [ ] Buat Views lengkap
  - [ ] Buat URLs dengan nested routing
- [ ] Sales Module
  - [ ] Buat missing models (PurchaseOrder)
  - [ ] Buat Serializers lengkap
  - [ ] Buat Views lengkap
  - [ ] Buat URLs lengkap

### [ ] Setup Security:
- [ ] Implement Custom Permissions (IsAdmin, IsManager, IsStaff)
- [ ] Setup RBAC (Role-Based Access Control)
- [ ] Add rate limiting
- [ ] Add request/response validation

### [ ] Setup Admin:
- [ ] Configure Django Admin untuk semua models
- [ ] Add inline admins untuk related objects
- [ ] Setup list_display, search_fields, filters

### [ ] Testing:
- [ ] Write unit tests untuk setiap ViewSet
- [ ] Write integration tests untuk complex workflows
- [ ] Test authentication & permissions
- [ ] Test validation & error handling

### [ ] Documentation:
- [ ] Setup Swagger/Redoc API documentation
- [ ] Write endpoint descriptions
- [ ] Document all query parameters
- [ ] Document authentication flow

---

## 💡 NEXT STEPS (URUTAN PRIORITAS)

1. **Copy HR pattern ke Inventory module** (paling besar manfaatnya)
   - Copy ViewSets pattern
   - Copy URLs pattern
   - Update serializers

2. **Copy HR pattern ke Finance module**
   - Tapi perlu tambah custom actions (post journal, approve invoice)

3. **Setup Projects nested routing** (lebih kompleks)

4. **Setup Sales module** dengan integrasi ke Inventory & Finance

5. **Implement Permissions & RBAC**

6. **Setup Admin interface**

7. **Write tests**

8. **Setup API documentation**

---

## 📞 SUPPORT & ISSUES

Jika ada yang error atau tidak jelas, langkah debugging:

1. Check error message di response
2. Verify JWT token masih valid
3. Check permissions (user role vs endpoint requirements)
4. Check field validation (required fields, format, uniqueness)
5. Check database constraints (foreign key relationships)
6. Check query parameters (spelling, type conversion)
7. Check server logs: `python manage.py runserver`

---

## 🎉 CONCLUSION

Dengan mengikuti pattern yang sudah dibuat (terutama HR module), Anda bisa dengan mudah:
- Membuat CRUD endpoint untuk setiap model
- Implement filtering, searching, ordering
- Add custom business logic actions
- Setup proper authentication & permissions
- Handle nested resources

**Happy Coding!** 🚀
