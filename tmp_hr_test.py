import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siman.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.hr.models import Department
import json

User = get_user_model()

# cleanup test user
User.objects.filter(username='testerapi').delete()
User.objects.filter(username='testerapi2').delete()

u = User.objects.create_user(username='testerapi', password='123456', email='testerapi@example.com')

c = Client()
logged = c.login(username='testerapi', password='123456')

dept, created = Department.objects.get_or_create(code='ITAPI', defaults={'name':'ITAPI', 'description':'x'})

payload = {'name': 'Alice', 'department_code': 'ITAPI', 'position_input': 'Developer', 'status': 'permanent', 'join_date': '2026-06-30'}
response = c.post('/api/hr/employees/', data=json.dumps(payload), content_type='application/json')

print('logged', logged)
print('status', response.status_code)
print('content', response.content.decode('utf-8'))
