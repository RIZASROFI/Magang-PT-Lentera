"""
HR Serializers - Human Resources Management
PT Lentera Anugerah Dimensi - HR Module
Complete CRUD Serializers
"""

from rest_framework import serializers
from .models import (
    Department, Position, Employee, Attendance, 
    Leave, Salary, Overtime
)


# ==================== DEPARTMENT ====================

class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer untuk Department - CRUD"""
    head_name = serializers.ReadOnlyField(source='head.get_full_name')
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'head', 'head_name', 
                  'employee_count', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_employee_count(self, obj):
        return obj.employees.filter(status__in=['permanent', 'contract', 'probation']).count()


# ==================== POSITION ====================

class PositionSerializer(serializers.ModelSerializer):
    """Serializer untuk Position - CRUD"""
    department_name = serializers.ReadOnlyField(source='department.name')
    
    class Meta:
        model = Position
        fields = ['id', 'name', 'code', 'department', 'department_name', 
                  'description', 'level', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


# ==================== EMPLOYEE ====================

class EmployeeListSerializer(serializers.ModelSerializer):
    """Serializer untuk list karyawan"""
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    user_email = serializers.ReadOnlyField(source='user.email')
    department_name = serializers.ReadOnlyField(source='department.name')
    position_name = serializers.ReadOnlyField(source='position.name')
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'nip', 'user', 'user_name', 'user_email',
            'department', 'department_name', 'position', 'position_name',
            'status', 'join_date', 'phone', 'photo', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'employee_id', 'created_at']


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Serializer untuk detail karyawan"""
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    user_email = serializers.ReadOnlyField(source='user.email')
    department_name = serializers.ReadOnlyField(source='department.name')
    position_name = serializers.ReadOnlyField(source='position.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'nip', 'user', 'user_name', 'user_email',
            'department', 'department_name', 'position', 'position_name',
            'status', 'join_date', 'resign_date', 'birth_date', 'birth_place',
            'gender', 'marital_status', 'religion', 'phone', 'emergency_contact',
            'emergency_phone', 'address', 'city', 'id_card', 'npwp', 
            'bpjs_ketenagakerjaan', 'bpjs_kesehatan', 'photo', 'notes',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.user.get_full_name')
    approved_by_name = serializers.ReadOnlyField(source='approved_by.email')
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'date', 'status',
            'check_in', 'check_out', 'overtime_hours', 'notes',
            'approved_by', 'approved_by_name', 'is_approved', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.user.get_full_name')
    approved_by_name = serializers.ReadOnlyField(source='approved_by.email')
    
    class Meta:
        model = Leave
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'start_date',
            'end_date', 'days', 'reason', 'notes', 'status',
            'approved_by', 'approved_by_name', 'approved_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.user.get_full_name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = Salary
        fields = [
            'id', 'employee', 'employee_name', 'period_month', 'period_year',
            'basic_salary', 'allowances', 'bonuses', 'overtime_pay',
            'deductions', 'tax', 'bpjs', 'gross_salary', 'net_salary',
            'status', 'payment_date', 'payment_method', 'payment_notes',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OvertimeSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.user.get_full_name')
    approved_by_name = serializers.ReadOnlyField(source='approved_by.email')
    
    class Meta:
        model = Overtime
        fields = [
            'id', 'employee', 'employee_name', 'date', 'start_time',
            'end_time', 'hours', 'reason', 'status',
            'approved_by', 'approved_by_name', 'approved_date',
            'rate', 'amount', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class HRReportSerializer(serializers.Serializer):
    """Serializer untuk laporan HR"""
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    departments = serializers.ListField()
    attendances_today = serializers.IntegerField()
    leaves_pending = serializers.IntegerField()
