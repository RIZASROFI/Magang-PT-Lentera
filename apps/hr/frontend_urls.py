from django.urls import path
from . import frontend_views

app_name = 'hr_frontend'

urlpatterns = [
    path('employees/', frontend_views.employees_page, name='employees'),
]

