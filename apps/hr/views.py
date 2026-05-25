"""
HR Views - Human Resources Management
PT Lentera Anugerah Dimensi - HR Module
Complete CRUD ViewSets with all operations
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Department, Position, Employee, Attendance,
    Leave, Salary, Overtime
)
from .serializers import (
    DepartmentSerializer, PositionSerializer, EmployeeListSerializer,
    EmployeeDetailSerializer, AttendanceSerializer, LeaveSerializer,
    SalarySerializer, OvertimeSerializer
)


# ==================== DEPARTMENT ====================

class DepartmentFilter(filters.FilterSet):
    is_active = filters.BooleanFilter()
    
    class Meta:
        model = Department
        fields = ['is_active']


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk Department - CRUD Operations
    
    GET    /api/hr/departments/           - List all departments
    POST   /api/hr/departments/           - Create new department
    GET    /api/hr/departments/{id}/      - Get department detail
    PUT    /api/hr/departments/{id}/      - Update department
    DELETE /api/hr/departments/{id}/      - Delete department
    GET    /api/hr/departments/stats/     - Get department statistics
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = DepartmentFilter
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = Department.objects.select_related('head').prefetch_related('employees')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def perform_create(self, serializer):
        """Create new department"""
        serializer.save()
    
    def perform_update(self, serializer):
        """Update department"""
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get department statistics"""
        total = Department.objects.count()
        active = Department.objects.filter(is_active=True).count()
        inactive = total - active
        
        departments_stats = Department.objects.annotate(
            employee_count=Count('employees')
        ).values('name', 'code', 'employee_count').order_by('name')
        
        return Response({
            'summary': {
                'total': total,
                'active': active,
                'inactive': inactive
            },
            'departments': list(departments_stats)
        }, status=status.HTTP_200_OK)


# ==================== POSITION ====================

class PositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk Position - CRUD Operations
    
    GET    /api/hr/positions/             - List all positions
    POST   /api/hr/positions/             - Create new position
    GET    /api/hr/positions/{id}/        - Get position detail
    PUT    /api/hr/positions/{id}/        - Update position
    DELETE /api/hr/positions/{id}/        - Delete position
    """
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['department', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'level', 'created_at']
    ordering = ['department', 'level']
    
    def get_queryset(self):
        queryset = Position.objects.select_related('department').prefetch_related('employees')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


# ==================== EMPLOYEE ====================

class EmployeeFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    status = filters.ChoiceFilter(choices=Employee.STATUS_CHOICES)
    
    class Meta:
        model = Employee
        fields = ['department', 'status']


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk Employee - CRUD Operations
    
    GET    /api/hr/employees/             - List all employees
    POST   /api/hr/employees/             - Create new employee
    GET    /api/hr/employees/{id}/        - Get employee detail
    PUT    /api/hr/employees/{id}/        - Update employee
    DELETE /api/hr/employees/{id}/        - Delete employee
    GET    /api/hr/employees/stats/       - Get employee statistics
    GET    /api/hr/employees/{id}/salary/ - Get employee salary info
    """
    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_class = EmployeeFilter
    search_fields = ['employee_id', 'nip', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['employee_id', 'join_date', 'created_at']
    ordering = ['employee_id']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeDetailSerializer
        return EmployeeDetailSerializer
    
    def get_queryset(self):
        queryset = Employee.objects.select_related(
            'user', 'department', 'position', 'created_by'
        ).prefetch_related('attendances', 'leaves', 'salaries', 'overtimes')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(user__is_active=is_active.lower() == 'true')
        
        return queryset
    
    def perform_create(self, serializer):
        """Create new employee"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Update employee"""
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get employee statistics"""
        total = Employee.objects.count()
        active = Employee.objects.filter(status='permanent').count()
        contract = Employee.objects.filter(status='contract').count()
        probation = Employee.objects.filter(status='probation').count()
        
        by_department = Employee.objects.values('department__name').annotate(
            count=Count('id')
        ).order_by('department__name')
        
        return Response({
            'summary': {
                'total': total,
                'active': active,
                'contract': contract,
                'probation': probation
            },
            'by_department': list(by_department)
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def salary(self, request, pk=None):
        """Get employee salary information"""
        employee = self.get_object()
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        current_salary = employee.salaries.filter(
            period_month=current_month,
            period_year=current_year
        ).first()
        
        if current_salary:
            serializer = SalarySerializer(current_salary)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(
            {'message': 'No salary record for current month'},
            status=status.HTTP_404_NOT_FOUND
        )


# ==================== ATTENDANCE ====================

class AttendanceFilter(filters.FilterSet):
    employee = filters.NumberFilter(field_name='employee_id')
    status = filters.ChoiceFilter(choices=Attendance.STATUS_CHOICES)
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')
    
    class Meta:
        model = Attendance
        fields = ['employee', 'status']


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk Attendance - CRUD Operations
    
    GET    /api/hr/attendances/           - List all attendances
    POST   /api/hr/attendances/           - Create new attendance record
    GET    /api/hr/attendances/{id}/      - Get attendance detail
    PUT    /api/hr/attendances/{id}/      - Update attendance record
    DELETE /api/hr/attendances/{id}/      - Delete attendance record
    GET    /api/hr/attendances/report/    - Get attendance report
    POST   /api/hr/attendances/{id}/approve/ - Approve attendance
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AttendanceFilter
    ordering_fields = ['date', 'employee', 'created_at']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = Attendance.objects.select_related(
            'employee__user', 'approved_by'
        )
        
        # Filter by employee
        employee = self.request.query_params.get('employee')
        if employee:
            queryset = queryset.filter(employee_id=employee)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Get monthly attendance report"""
        month = int(request.query_params.get('month', timezone.now().month))
        year = int(request.query_params.get('year', timezone.now().year))
        
        attendances = Attendance.objects.filter(
            date__month=month,
            date__year=year
        ).values('employee__employee_id', 'status').annotate(
            count=Count('id')
        ).order_by('employee__employee_id')
        
        return Response({
            'month': month,
            'year': year,
            'data': list(attendances)
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve attendance record"""
        attendance = self.get_object()
        attendance.is_approved = True
        attendance.approved_by = request.user
        attendance.save()
        
        serializer = self.get_serializer(attendance)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==================== LEAVE ====================

class LeaveFilter(filters.FilterSet):
    employee = filters.NumberFilter(field_name='employee_id')
    status = filters.ChoiceFilter(choices=Leave.STATUS_CHOICES)
    leave_type = filters.ChoiceFilter(choices=Leave.LEAVE_TYPE_CHOICES)
    
    class Meta:
        model = Leave
        fields = ['employee', 'status', 'leave_type']


class LeaveViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk Leave - CRUD Operations
    
    GET    /api/hr/leaves/                - List all leaves
    POST   /api/hr/leaves/                - Create new leave request
    GET    /api/hr/leaves/{id}/           - Get leave detail
    PUT    /api/hr/leaves/{id}/           - Update leave request
    DELETE /api/hr/leaves/{id}/           - Cancel leave request
    POST   /api/hr/leaves/{id}/approve/   - Approve leave request
    POST   /api/hr/leaves/{id}/reject/    - Reject leave request
    """
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = LeaveFilter
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        queryset = Leave.objects.select_related(
            'employee__user', 'approved_by'
        )
        
        # Filter by employee
        employee = self.request.query_params.get('employee')
        if employee:
            queryset = queryset.filter(employee_id=employee)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve leave request"""
        leave = self.get_object()
        leave.status = 'approved'
        leave.approved_by = request.user
        leave.approved_date = timezone.now()
        leave.save()
        
        serializer = self.get_serializer(leave)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject leave request"""
        leave = self.get_object()
        leave.status = 'rejected'
        leave.approved_by = request.user
        leave.approved_date = timezone.now()
        leave.save()
        
        serializer = self.get_serializer(leave)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==================== SALARY ====================

class SalaryFilter(filters.FilterSet):
    employee = filters.NumberFilter(field_name='employee_id')
    status = filters.ChoiceFilter(choices=Salary.STATUS_CHOICES)
    period_month = filters.NumberFilter()
    period_year = filters.NumberFilter()
    
    class Meta:
        model = Salary
        fields = ['employee', 'status', 'period_month', 'period_year']


class SalaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk Salary - CRUD Operations
    
    GET    /api/hr/salaries/              - List all salaries
    POST   /api/hr/salaries/              - Create new salary record
    GET    /api/hr/salaries/{id}/         - Get salary detail
    PUT    /api/hr/salaries/{id}/         - Update salary record
    DELETE /api/hr/salaries/{id}/         - Delete salary record
    POST   /api/hr/salaries/{id}/approve/ - Approve salary
    POST   /api/hr/salaries/{id}/pay/     - Mark salary as paid
    """
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = SalaryFilter
    ordering_fields = ['period_year', 'period_month', 'created_at']
    ordering = ['-period_year', '-period_month']
    
    def get_queryset(self):
        queryset = Salary.objects.select_related(
            'employee__user', 'created_by'
        )
        
        # Filter by employee
        employee = self.request.query_params.get('employee')
        if employee:
            queryset = queryset.filter(employee_id=employee)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve salary calculation"""
        salary = self.get_object()
        
        if salary.status != 'calculated':
            return Response(
                {'error': 'Only calculated salaries can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        salary.status = 'approved'
        salary.save()
        
        serializer = self.get_serializer(salary)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """Mark salary as paid"""
        salary = self.get_object()
        
        if salary.status != 'approved':
            return Response(
                {'error': 'Only approved salaries can be paid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        salary.status = 'paid'
        salary.payment_date = timezone.now().date()
        salary.save()
        
        serializer = self.get_serializer(salary)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==================== OVERTIME ====================

class OvertimeFilter(filters.FilterSet):
    employee = filters.NumberFilter(field_name='employee_id')
    status = filters.ChoiceFilter(choices=Overtime.STATUS_CHOICES)
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')
    
    class Meta:
        model = Overtime
        fields = ['employee', 'status']


class OvertimeViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk Overtime - CRUD Operations
    
    GET    /api/hr/overtimes/             - List all overtimes
    POST   /api/hr/overtimes/             - Create new overtime record
    GET    /api/hr/overtimes/{id}/        - Get overtime detail
    PUT    /api/hr/overtimes/{id}/        - Update overtime record
    DELETE /api/hr/overtimes/{id}/        - Delete overtime record
    POST   /api/hr/overtimes/{id}/approve/ - Approve overtime
    """
    queryset = Overtime.objects.all()
    serializer_class = OvertimeSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = OvertimeFilter
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = Overtime.objects.select_related(
            'employee__user', 'approved_by'
        )
        
        # Filter by employee
        employee = self.request.query_params.get('employee')
        if employee:
            queryset = queryset.filter(employee_id=employee)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve overtime request"""
        overtime = self.get_object()
        overtime.is_approved = True
        overtime.approved_by = request.user
        overtime.save()
        
        serializer = self.get_serializer(overtime)
        return Response(serializer.data, status=status.HTTP_200_OK)
