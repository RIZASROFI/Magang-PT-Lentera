# 🚀 PANDUAN IMPLEMENTASI FITUR CRUD LENGKAP

## 📋 STRUKTUR STANDAR CRUD DI SETIAP MODULE

Setiap module apps (projects, inventory, finance, hr, sales) harus memiliki:

```
apps/module_name/
├── models.py          # Definisi model dengan fields lengkap
├── serializers.py     # Serializers untuk CRUD operations
├── views.py           # ViewSets dengan CRUD operations
├── urls.py            # URL routing & nested routes
├── admin.py           # Django admin configuration
├── apps.py            # App configuration
└── permissions.py     # Custom permissions (optional)
```

---

## 📝 POLA STANDARD UNTUK SERIALIZERS

### 1. Buatkan 3 tipe serializer untuk setiap model:

#### a) ListSerializer (untuk GET list dengan pagination)
```python
class ItemListSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    
    class Meta:
        model = Item
        fields = ['id', 'name', 'category', 'category_name', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']
```

#### b) DetailSerializer (untuk GET detail, mencakup semua fields)
```python
class ItemDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    
    class Meta:
        model = Item
        fields = [... semua fields ...]
        read_only_fields = ['id', 'created_at', 'updated_at']
```

#### c) CreateUpdateSerializer (untuk POST & PUT, minimal fields)
```python
class ItemCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Item
        fields = ['name', 'category', 'status', 'description']
    
    def validate(self):
        # Add custom validation here
        pass
```

---

## 🎯 POLA STANDARD UNTUK VIEWSETS

Setiap ViewSet harus mengimplementasikan:

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters

class ItemViewSet(viewsets.ModelViewSet):
    """Complete CRUD ViewSet untuk Item"""
    
    # 1. Setup queryset & permissions
    queryset = Item.objects.all()
    permission_classes = [IsAuthenticated]
    
    # 2. Setup filtering, searching, ordering
    filterset_fields = ['category', 'status', 'is_active']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'created_at', 'price']
    ordering = ['-created_at']
    
    # 3. Select appropriate serializer per action
    def get_serializer_class(self):
        if self.action == 'list':
            return ItemListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ItemCreateUpdateSerializer
        return ItemDetailSerializer
    
    # 4. Optimize queries dengan select_related & prefetch_related
    def get_queryset(self):
        queryset = Item.objects.select_related('category', 'created_by')
        
        # Add custom filtering if needed
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        return queryset
    
    # 5. Handle create/update dengan proper context
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    # 6. Add custom actions if needed
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics"""
        return Response({
            'total': Item.objects.count(),
            'active': Item.objects.filter(is_active=True).count(),
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate item"""
        item = self.get_object()
        item.is_active = True
        item.save()
        return Response({'message': 'Item activated'}, status=status.HTTP_200_OK)
```

---

## 🔗 POLA STANDARD UNTUK URLS

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, CategoryViewSet

# Main router untuk top-level resources
router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='item')
router.register(r'categories', CategoryViewSet, basename='category')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
```

### Nested Routes (untuk related resources)
```python
from rest_framework.routers import DefaultRouter, SimpleRouter

# Jika ada nested URL seperti /projects/{id}/team/
# Gunakan custom nesting di urls.py

urlpatterns = [
    # Main resource
    path('projects/', ProjectViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-list'),
    path('projects/<int:pk>/', ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='project-detail'),
    
    # Nested resources
    path('projects/<int:project_pk>/team/', TeamAssignmentViewSet.as_view({'get': 'list', 'post': 'create'}), name='team-list'),
    path('projects/<int:project_pk>/team/<int:pk>/', TeamAssignmentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='team-detail'),
]
```

---

## ✅ CHECKLIST IMPLEMENTASI CRUD PER MODULE

### [ ] Projects Module
- [x] Models: Complete
- [ ] Serializers: Complete CRUD (List, Detail, Create)
- [ ] ViewSets: Complete dengan nested routes
  - [ ] ProjectViewSet (CRUD + custom actions)
  - [ ] ProjectLocationViewSet (nested under project)
  - [ ] ProjectProgressViewSet (nested under project)
  - [ ] TeamAssignmentViewSet (nested under project)
- [ ] URLs: Complete routing dengan nested
- [ ] Permissions: Is owner atau IsManager
- [ ] Tests: Basic CRUD operations

### [ ] Inventory Module
- [x] Models: Complete
- [ ] Serializers: Complete CRUD
  - [ ] CategorySerializer
  - [ ] ItemSerializer (List, Detail, Create)
  - [ ] SupplierSerializer
  - [ ] StockInSerializer (nested items)
  - [ ] StockOutSerializer (nested items)
  - [ ] StockOpnameSerializer (nested items)
- [ ] ViewSets: Complete dengan actions
  - [ ] CategoryViewSet
  - [ ] ItemViewSet (+ low_stock, stock_history actions)
  - [ ] SupplierViewSet
  - [ ] StockInViewSet (+ approve action)
  - [ ] StockOutViewSet (+ approve, deliver actions)
  - [ ] StockOpnameViewSet
- [ ] URLs: Complete routing
- [ ] Permissions: IsStaff untuk create, IsManager untuk approve
- [ ] Tests: CRUD + stock calculations

### [ ] Finance Module
- [ ] Models: Complete (Invoice, Payment missing)
- [ ] Serializers: Complete CRUD
  - [ ] AccountSerializer
  - [ ] JournalEntrySerializer (nested items)
  - [ ] InvoiceSerializer
  - [ ] PaymentSerializer
  - [ ] IncomeSerializer
  - [ ] ExpenseSerializer
- [ ] ViewSets: Complete
  - [ ] AccountViewSet (+ balance action)
  - [ ] JournalEntryViewSet (+ post action)
  - [ ] InvoiceViewSet (+ send, payment actions)
  - [ ] PaymentViewSet
  - [ ] IncomeViewSet
  - [ ] ExpenseViewSet
  - [ ] ReportViewSet (+ report endpoints)
- [ ] URLs: Complete routing
- [ ] Permissions: Only Manager dapat post journal
- [ ] Tests: CRUD + balance calculations

### [ ] HR Module
- [x] Models: Complete
- [ ] Serializers: Complete CRUD
  - [x] DepartmentSerializer
  - [x] PositionSerializer
  - [x] EmployeeSerializer (List, Detail, Create)
  - [ ] AttendanceSerializer (List, Detail, Create, Approve)
  - [ ] LeaveSerializer (List, Detail, Create, Approve)
  - [ ] SalarySerializer (List, Detail, Create, Pay)
  - [ ] OvertimeSerializer (List, Detail, Create, Approve)
- [ ] ViewSets: Complete
  - [x] DepartmentViewSet
  - [x] PositionViewSet
  - [x] EmployeeViewSet (+ filter, search)
  - [ ] AttendanceViewSet (+ monthly_report action)
  - [ ] LeaveViewSet (+ approve action)
  - [ ] SalaryViewSet (+ calculate, pay actions)
  - [ ] OvertimeViewSet (+ approve action)
  - [ ] HRReportViewSet (salary, attendance reports)
- [ ] URLs: Complete routing
- [ ] Permissions: IsStaff untuk input, IsManager untuk approve
- [ ] Tests: CRUD + salary calculations

### [ ] Sales Module
- [ ] Models: Complete (SalesOrder complete, PurchaseOrder missing)
- [ ] Serializers: Complete CRUD
  - [ ] CustomerSerializer
  - [ ] VendorSerializer
  - [ ] QuotationSerializer (nested items)
  - [ ] SalesOrderSerializer (nested items)
  - [ ] PurchaseOrderSerializer (nested items)
- [ ] ViewSets: Complete
  - [ ] CustomerViewSet (+ total_sales, receivables actions)
  - [ ] VendorViewSet
  - [ ] QuotationViewSet (+ convert_to_sales_order action)
  - [ ] SalesOrderViewSet (+ confirm, complete actions)
  - [ ] PurchaseOrderViewSet (+ approve, receive actions)
- [ ] URLs: Complete routing
- [ ] Permissions: IsStaff untuk create, IsManager untuk convert/confirm
- [ ] Tests: CRUD + integration dengan inventory & finance

### [ ] Auth Module
- [ ] Models: Custom User dengan role
- [ ] Serializers:
  - [ ] UserRegisterSerializer
  - [ ] UserLoginSerializer
  - [ ] UserProfileSerializer
  - [ ] ChangePasswordSerializer
- [ ] ViewSets:
  - [ ] AuthenticationViewSet (register, login, logout, token_refresh)
  - [ ] UserViewSet (list, detail, update, change_password)
  - [ ] ProfileViewSet (my_profile, update_profile)
- [ ] Permissions: IsAuthenticated, IsAdmin, IsManager, IsStaff
- [ ] Tests: Auth flow

---

## 🧪 TEMPLATE TEST FILE

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class ItemCRUDTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Setup test data
    
    def test_create_item(self):
        """Test POST /api/inventory/items/"""
        response = self.client.post('/api/inventory/items/', data={
            'name': 'Test Item',
            'sku': 'TEST-001',
            'category_id': 1,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_items(self):
        """Test GET /api/inventory/items/"""
        response = self.client.get('/api/inventory/items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_detail_item(self):
        """Test GET /api/inventory/items/1/"""
        response = self.client.get('/api/inventory/items/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_item(self):
        """Test PUT /api/inventory/items/1/"""
        response = self.client.put('/api/inventory/items/1/', data={
            'name': 'Updated Item',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_item(self):
        """Test DELETE /api/inventory/items/1/"""
        response = self.client.delete('/api/inventory/items/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
```

---

## 📚 API ENDPOINT OVERVIEW

### Standard CRUD Endpoints
```
LIST:   GET    /api/module/resource/
CREATE: POST   /api/module/resource/
DETAIL: GET    /api/module/resource/{id}/
UPDATE: PUT    /api/module/resource/{id}/
PATCH:  PATCH  /api/module/resource/{id}/
DELETE: DELETE /api/module/resource/{id}/
```

### Nested Endpoints (Example)
```
LIST:   GET    /api/projects/{project_id}/team/
CREATE: POST   /api/projects/{project_id}/team/
DETAIL: GET    /api/projects/{project_id}/team/{id}/
UPDATE: PUT    /api/projects/{project_id}/team/{id}/
DELETE: DELETE /api/projects/{project_id}/team/{id}/
```

### Custom Actions
```
CUSTOM: POST   /api/module/resource/{id}/custom_action/
CUSTOM: GET    /api/module/resource/stats/
```

---

## 🎁 NEXT STEPS

1. **Lengkapi Missing Models**
   - Finance: Invoice, Payment models
   - Sales: PurchaseOrder complete

2. **Implementasikan Serializers** sesuai dengan template di atas

3. **Implementasikan ViewSets** dengan:
   - Proper queryset optimization
   - Filtering & Searching
   - Custom actions untuk business logic
   - Status code yang tepat

4. **Setup URLs** dengan nested routing yang benar

5. **Implement Permissions** untuk RBAC

6. **Add Validation & Error Handling**

7. **Write Tests** untuk setiap endpoint

---

## 💡 PRO TIPS

1. **Selalu gunakan `select_related()` & `prefetch_related()`** untuk optimize queries
2. **Validasi data di serializer**, bukan di view
3. **Gunakan transaction** untuk operasi yang complex & critical
4. **Implement proper error handling** dengan custom exception handlers
5. **Document API** menggunakan Django REST Swagger
6. **Test semua endpoint** sebelum production
7. **Gunakan permission classes** untuk security
