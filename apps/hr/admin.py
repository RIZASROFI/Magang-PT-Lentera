"""
HR Admin
"""

from django.contrib import admin
from .models import (
    Department, Position, Employee, Attendance,
    Leave, Salary, Overtime
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'level']
    list_filter = ['department', 'level']
    search_fields = ['name', 'code']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'position', 'status', 'join_date']
    list_filter = ['status', 'department', 'position']
    search_fields = ['employee_id', 'nip', 'user__email']
    ordering = ['employee_id']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'check_in', 'check_out', 'is_approved']
    list_filter = ['status', 'date', 'is_approved']
    search_fields = ['employee__user__email']
    date_hierarchy = 'date'


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['leave_type', 'status']
    search_fields = ['employee__user__email']


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'period_month', 'period_year', 'net_salary', 'status']
    list_filter = ['status', 'period_month', 'period_year']
    search_fields = ['employee__employee_id']


@admin.register(Overtime)
class OvertimeAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'hours', 'rate', 'amount', 'status']
    list_filter = ['status', 'date']
    search_fields = ['employee__user__email']
    date_hierarchy = 'date'
