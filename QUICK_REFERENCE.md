# ⚡ QUICK REFERENCE - SIMAN CRUD IMPLEMENTATION

## 🚀 QUICK START

```bash
# 1. Setup
python manage.py migrate
python manage.py runserver

# 2. In Postman:
# Set Authorization type: Bearer Token
# Paste access token from login
```

---

## 📝 MINIMUM CODE NEEDED FOR NEW ENDPOINT

### 1. Model (in models.py)
```python
class Item(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
```

### 2. Serializer (in serializers.py)
```python
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'code', 'created_at']
        read_only_fields = ['id', 'created_at']
```

### 3. ViewSet (in views.py)
```python
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
```

### 4. URL (in urls.py)
```python
router = DefaultRouter()
router.register(r'items', ItemViewSet)
urlpatterns = [path('', include(router.urls))]
```

**That's it!** 4 endpoints auto-generated:
- GET    /api/module/items/
- POST   /api/module/items/
- GET    /api/module/items/{id}/
- PUT    /api/module/items/{id}/
- DELETE /api/module/items/{id}/

---

## 🔧 COMMON PATTERNS

### Filter & Search
```python
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    filterset_fields = ['status', 'category']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
```

### Custom Serializer per Action
```python
def get_serializer_class(self):
    if self.action == 'list':
        return ItemListSerializer
    elif self.action == 'create':
        return ItemCreateSerializer
    return ItemDetailSerializer
```

### Custom Action
```python
@action(detail=False, methods=['get'])
def stats(self, request):
    return Response({'total': Item.objects.count()})

@action(detail=True, methods=['post'])
def approve(self, request, pk=None):
    obj = self.get_object()
    obj.is_approved = True
    obj.save()
    return Response({'status': 'approved'})
```

### Query Optimization
```python
def get_queryset(self):
    queryset = Item.objects.select_related('category', 'created_by')
    queryset = queryset.prefetch_related('related_items')
    return queryset
```

### Nested Resources
```python
# URL pattern
path('items/<int:item_id>/details/', DetailViewSet.as_view({
    'get': 'list',
    'post': 'create'
}))

# ViewSet with lookup
class DetailViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        item_id = self.kwargs.get('item_id')
        return Detail.objects.filter(item_id=item_id)
```

---

## 🧪 TESTING QUICK SNIPPETS

### Using cURL
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "pass"}'

# Extract token and save to variable
TOKEN="eyJ..."

# List
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/module/items/

# Create
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Item"}' \
  http://localhost:8000/api/module/items/

# Get one
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/module/items/1/

# Update
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated"}' \
  http://localhost:8000/api/module/items/1/

# Delete
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/module/items/1/

# Custom action
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/module/items/1/approve/
```

### Using Python/Requests
```python
import requests

BASE_URL = "http://localhost:8000/api"

# Login
response = requests.post(f"{BASE_URL}/auth/login/", json={
    "email": "user@example.com",
    "password": "pass"
})
token = response.json()['access']

headers = {"Authorization": f"Bearer {token}"}

# List
response = requests.get(f"{BASE_URL}/module/items/", headers=headers)
print(response.json())

# Create
response = requests.post(f"{BASE_URL}/module/items/", 
    headers=headers,
    json={"name": "Item", "code": "001"}
)
print(response.json())

# Get one
response = requests.get(f"{BASE_URL}/module/items/1/", headers=headers)

# Update
response = requests.put(f"{BASE_URL}/module/items/1/",
    headers=headers,
    json={"name": "Updated"}
)

# Delete
response = requests.delete(f"{BASE_URL}/module/items/1/", headers=headers)

# Custom action
response = requests.post(f"{BASE_URL}/module/items/1/approve/", 
    headers=headers
)
```

---

## 📦 RESPONSE FORMATS

### Success Response
```json
{
  "id": 1,
  "name": "Item Name",
  "created_at": "2024-04-30T10:00:00Z"
}
```

### List Response
```json
{
  "count": 10,
  "next": "http://api.example.com/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response
```json
{
  "field_name": ["Error message"]
}
```

### Custom Response (in action)
```python
return Response(
    {"message": "Success", "data": {...}},
    status=status.HTTP_200_OK
)
```

---

## ⚡ VALIDATION SHORTCUTS

```python
# In serializer
class ItemSerializer(serializers.ModelSerializer):
    
    def validate_code(self, value):
        if Item.objects.filter(code=value).exists():
            raise serializers.ValidationError("Code already exists!")
        return value
    
    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("Start must be before end!")
        return data
```

---

## 🔐 PERMISSIONS QUICK

```python
# In ViewSet
permission_classes = [IsAuthenticated]

# For specific actions
def get_permissions(self):
    if self.action in ['create', 'update']:
        permission_classes = [IsAuthenticated, IsAdmin]
    else:
        permission_classes = [IsAuthenticated]
    return [permission() for permission in permission_classes]

# Or per action
@action(detail=True, permission_classes=[IsManager])
def approve(self, request):
    ...
```

---

## 🎯 COMMON STATUS CODES

| Code | Meaning | Use |
|------|---------|-----|
| 200 | OK | GET, PUT, PATCH, DELETE success |
| 201 | Created | POST success |
| 204 | No Content | DELETE (no response body) |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Unexpected error |

---

## 🛠️ DEBUGGING CHECKLIST

- [ ] Is endpoint URL correct? `GET /api/module/items/`
- [ ] Is HTTP method correct? (GET, POST, PUT, DELETE, PATCH)
- [ ] Is authorization header present? `Authorization: Bearer token`
- [ ] Is token valid & not expired?
- [ ] Is JSON data valid? (check Content-Type header)
- [ ] Are required fields present in POST/PUT?
- [ ] Do field values match expected types?
- [ ] Is database migration done? `python manage.py migrate`
- [ ] Are models imported in admin.py?
- [ ] Is app added to INSTALLED_APPS in settings.py?

---

## 📊 QUERY PARAMETER EXAMPLES

```bash
# Search
GET /api/items/?search=laptop

# Filter
GET /api/items/?category=1&status=active

# Ordering (- for desc)
GET /api/items/?ordering=-created_at

# Pagination
GET /api/items/?page=1&page_size=50

# Combined
GET /api/items/?search=laptop&category=1&status=active&ordering=-price&page=1&page_size=20
```

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] Debug = False in settings
- [ ] SECRET_KEY is secure
- [ ] Database configured (MySQL for production)
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Media files have proper permissions
- [ ] CORS_ALLOWED_ORIGINS configured
- [ ] ALLOWED_HOSTS configured
- [ ] Migrations applied: `python manage.py migrate`
- [ ] Superuser created: `python manage.py createsuperuser`
- [ ] Tests passing: `python manage.py test`
- [ ] Error logging configured
- [ ] Backup strategy in place
- [ ] SSL/HTTPS enabled
- [ ] Rate limiting enabled
- [ ] CSRF tokens verified

---

## 💾 USEFUL DJANGO COMMANDS

```bash
# Database
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
python manage.py sqlmigrate app_name 0001

# Admin
python manage.py createsuperuser
python manage.py changepassword username

# Data
python manage.py dumpdata > data.json
python manage.py loaddata data.json

# Development
python manage.py runserver
python manage.py shell
python manage.py check

# Testing
python manage.py test
python manage.py test apps.module
python manage.py test apps.module.tests.ItemTest.test_create

# Utilities
python manage.py flush           # Delete all data
python manage.py collectstatic   # Collect static files
python manage.py clearsessions   # Clear expired sessions
```

---

## 📚 DOCUMENTATION LINKS

- Django REST Framework: https://www.django-rest-framework.org/
- Django Docs: https://docs.djangoproject.com/
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- DRF ViewSets: https://www.django-rest-framework.org/api-guide/viewsets/
- DRF Permissions: https://www.django-rest-framework.org/api-guide/permissions/
- DRF Filtering: https://www.django-rest-framework.org/api-guide/filtering/
- DRF Pagination: https://www.django-rest-framework.org/api-guide/pagination/

---

## 🆘 COMMON ERRORS & FIXES

### Error: "No 'Access-Control-Allow-Origin' header"
```python
# Fix in settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]
```

### Error: "Authentication credentials were not provided"
```python
# Add token to header
Authorization: Bearer {token}
```

### Error: "JSON parse error"
```python
# Check Content-Type header is application/json
# Check JSON is valid (no trailing commas)
```

### Error: "Field X is required"
```python
# Add the field in POST/PUT request body
```

### Error: "Duplicate key value violates unique constraint"
```python
# The value already exists in database
# Use different value or check for uniqueness
```

---

## ✨ PRO TIPS

1. **Always use `select_related()` & `prefetch_related()`** for queries
2. **Test locally before pushing** to avoid breaking production
3. **Use meaningful variable names** for readability
4. **Write docstrings** for all classes & methods
5. **Use transactions** for critical operations
6. **Implement pagination** for large datasets
7. **Add logging** for debugging
8. **Version your API** for backward compatibility
9. **Document breaking changes**
10. **Use git commits** frequently

---

## 🎉 YOU'RE READY!

Sekarang Anda sudah punya:
- ✅ Complete HR module dengan semua CRUD
- ✅ Template pattern untuk module lain
- ✅ Dokumentasi lengkap & examples
- ✅ Quick reference ini

**Happy coding!** 🚀
