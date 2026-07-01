"""
HR Serializers - Human Resources Management
PT Lentera Anugerah Dimensi - HR Module
Complete CRUD Serializers
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (
    Department, Position, Employee, Attendance, 
    Leave, Salary, Overtime
)

User = get_user_model()


# ==================== DEPARTMENT ====================

class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer untuk Department - CRUD"""
    head_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'head', 'head_name', 
                  'employee_count', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_head_name(self, obj):
        if obj.head:
            return obj.head.get_full_name or obj.head.email or '-'
        return '-'
    
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
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    department_name = serializers.ReadOnlyField(source='department.name')
    position_name = serializers.ReadOnlyField(source='position.name')
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'nip', 'user', 'user_name', 'user_email',
            'department', 'department_name', 'position', 'position_name',
            'status', 'join_date', 'phone', 'photo', 'created_at'
        ]
        read_only_fields = ['id', 'employee_id', 'created_at']
    
    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name or obj.user.email or str(obj.user)
        return '-'
    
    def get_user_email(self, obj):
        if obj.user:
            return obj.user.email or ''
        return ''


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Serializer untuk detail karyawan — support create via frontend (name, department code, position name)"""
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    user_email = serializers.ReadOnlyField(source='user.email')
    department_name = serializers.ReadOnlyField(source='department.name')
    position_name = serializers.ReadOnlyField(source='position.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.email')

    # Field bantuan dari frontend (write-only, di-resolve di create)
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    department_code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    position_input = serializers.CharField(write_only=True, required=False, allow_blank=True)

    # Buat department & position bisa null (karena kita resolve dari code/name)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True
    )
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'nip', 'user', 'user_name', 'user_email',
            'department', 'department_name', 'position', 'position_name',
            'status', 'join_date', 'resign_date', 'birth_date', 'birth_place',
            'gender', 'marital_status', 'religion', 'phone', 'emergency_contact',
            'emergency_phone', 'address', 'city', 'id_card', 'npwp',
            'bpjs_ketenagakerjaan', 'bpjs_kesehatan', 'photo', 'notes',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'name', 'department_code', 'position_input',
        ]
        read_only_fields = ['id', 'employee_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        name = validated_data.pop('name', '')
        dept_code = validated_data.pop('department_code', '')
        pos_name = validated_data.pop('position_input', '')

        # 1) Resolve department dari code
        if not validated_data.get('department') and dept_code:
            try:
                dept = Department.objects.get(code=dept_code)
                validated_data['department'] = dept
            except Department.DoesNotExist:
                raise serializers.ValidationError({'department': f'Departemen dengan code "{dept_code}" tidak ditemukan'})

        # 2) Resolve position dari nama (create if not exists)
        if not validated_data.get('position') and pos_name:
            dept = validated_data.get('department')
            if not dept:
                raise serializers.ValidationError({'position': 'Pilih departemen terlebih dahulu sebelum mengisi jabatan'})
            obj, _ = Position.objects.get_or_create(
                name__iexact=pos_name,
                defaults={
                    'name': pos_name,
                    'code': pos_name.upper().replace(' ', '_'),
                    'department': dept,
                }
            )
            validated_data['position'] = obj

        # 3) Jika user tidak dikirim, buat dari name
        if not validated_data.get('user'):
            if name:
                email_part = name.lower().replace(' ', '.')
                user, _ = User.objects.get_or_create(
                    username=email_part,
                    defaults={
                        'email': f'{email_part}@placeholder.com',
                        'first_name': name,
                    }
                )
                validated_data['user'] = user

        if not validated_data.get('department'):
            raise serializers.ValidationError({'department': 'Departemen harus diisi'})
        if not validated_data.get('position'):
            raise serializers.ValidationError({'position': 'Jabatan harus diisi'})
        if not validated_data.get('user'):
            raise serializers.ValidationError({'name': 'Nama karyawan harus diisi'})

        return super().create(validated_data)

    def update(self, instance, validated_data):
        name = validated_data.pop('name', '')
        dept_code = validated_data.pop('department_code', '')
        pos_name = validated_data.pop('position_input', '')

        # 1) Update nama user jika ada
        if name and instance.user:
            parts = name.split(' ', 1)
            instance.user.first_name = parts[0]
            if len(parts) > 1:
                instance.user.last_name = parts[1]
            else:
                instance.user.last_name = ''
            instance.user.save()

        # 2) Resolve department dari code
        if dept_code:
            try:
                dept = Department.objects.get(code=dept_code)
                validated_data['department'] = dept
            except Department.DoesNotExist:
                raise serializers.ValidationError({'department': f'Departemen dengan code "{dept_code}" tidak ditemukan'})

        # 3) Resolve position dari nama (create if not exists)
        if pos_name:
            dept = validated_data.get('department') or instance.department
            obj, _ = Position.objects.get_or_create(
                name__iexact=pos_name,
                defaults={
                    'name': pos_name,
                    'code': pos_name.upper().replace(' ', '_'),
                    'department': dept,
                }
            )
            validated_data['position'] = obj

        return super().update(instance, validated_data)


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
