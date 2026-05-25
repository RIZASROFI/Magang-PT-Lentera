"""
HR URLs - Human Resources Management
PT Lentera Anugerah Dimensi - HR Module URLs
Complete CRUD Endpoints with Documentation
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, PositionViewSet, EmployeeViewSet,
    AttendanceViewSet, LeaveViewSet, SalaryViewSet, OvertimeViewSet
)

# Create router for automatic CRUD endpoints generation
router = DefaultRouter()

# Register viewsets - Router will auto-generate standard CRUD endpoints
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'positions', PositionViewSet, basename='position')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'attendances', AttendanceViewSet, basename='attendance')
router.register(r'leaves', LeaveViewSet, basename='leave')
router.register(r'salaries', SalaryViewSet, basename='salary')
router.register(r'overtimes', OvertimeViewSet, basename='overtime')

# Main URL patterns
app_name = 'hr'
urlpatterns = [
    path('', include(router.urls)),
]

"""
=============================================================================
GENERATED ENDPOINTS FROM ROUTER
=============================================================================

=== DEPARTMENT ENDPOINTS ===
LIST    GET    /api/hr/departments/
CREATE  POST   /api/hr/departments/
DETAIL  GET    /api/hr/departments/{id}/
UPDATE  PUT    /api/hr/departments/{id}/
PATCH   PATCH  /api/hr/departments/{id}/
DELETE  DELETE /api/hr/departments/{id}/
STATS   GET    /api/hr/departments/stats/

=== POSITION ENDPOINTS ===
LIST    GET    /api/hr/positions/
CREATE  POST   /api/hr/positions/
DETAIL  GET    /api/hr/positions/{id}/
UPDATE  PUT    /api/hr/positions/{id}/
PATCH   PATCH  /api/hr/positions/{id}/
DELETE  DELETE /api/hr/positions/{id}/

=== EMPLOYEE ENDPOINTS ===
LIST    GET    /api/hr/employees/
CREATE  POST   /api/hr/employees/
DETAIL  GET    /api/hr/employees/{id}/
UPDATE  PUT    /api/hr/employees/{id}/
PATCH   PATCH  /api/hr/employees/{id}/
DELETE  DELETE /api/hr/employees/{id}/
STATS   GET    /api/hr/employees/stats/
SALARY  GET    /api/hr/employees/{id}/salary/

=== ATTENDANCE ENDPOINTS ===
LIST    GET    /api/hr/attendances/
CREATE  POST   /api/hr/attendances/
DETAIL  GET    /api/hr/attendances/{id}/
UPDATE  PUT    /api/hr/attendances/{id}/
PATCH   PATCH  /api/hr/attendances/{id}/
DELETE  DELETE /api/hr/attendances/{id}/
REPORT  GET    /api/hr/attendances/report/
APPROVE POST   /api/hr/attendances/{id}/approve/

=== LEAVE ENDPOINTS ===
LIST    GET    /api/hr/leaves/
CREATE  POST   /api/hr/leaves/
DETAIL  GET    /api/hr/leaves/{id}/
UPDATE  PUT    /api/hr/leaves/{id}/
PATCH   PATCH  /api/hr/leaves/{id}/
DELETE  DELETE /api/hr/leaves/{id}/
APPROVE POST   /api/hr/leaves/{id}/approve/
REJECT  POST   /api/hr/leaves/{id}/reject/

=== SALARY ENDPOINTS ===
LIST    GET    /api/hr/salaries/
CREATE  POST   /api/hr/salaries/
DETAIL  GET    /api/hr/salaries/{id}/
UPDATE  PUT    /api/hr/salaries/{id}/
PATCH   PATCH  /api/hr/salaries/{id}/
DELETE  DELETE /api/hr/salaries/{id}/
APPROVE POST   /api/hr/salaries/{id}/approve/
PAY     POST   /api/hr/salaries/{id}/pay/

=== OVERTIME ENDPOINTS ===
LIST    GET    /api/hr/overtimes/
CREATE  POST   /api/hr/overtimes/
DETAIL  GET    /api/hr/overtimes/{id}/
UPDATE  PUT    /api/hr/overtimes/{id}/
PATCH   PATCH  /api/hr/overtimes/{id}/
DELETE  DELETE /api/hr/overtimes/{id}/
APPROVE POST   /api/hr/overtimes/{id}/approve/

=============================================================================
QUERY PARAMETERS & FILTERING
=============================================================================

List endpoints support the following query parameters:

Common Parameters:
- ?search=query              Search by text fields
- ?page=1                    Pagination (default page_size=100)
- ?page_size=50             Items per page
- ?ordering=-created_at      Order results (use - for descending)

Department Filters:
- ?is_active=true           Active departments only

Position Filters:
- ?department=1             Filter by department ID
- ?is_active=true           Active positions only

Employee Filters:
- ?department=1             Filter by department ID
- ?status=permanent         Filter by status (permanent, contract, probation, resigned, fired)
- ?is_active=true           Active employees only

Attendance Filters:
- ?employee=1               Filter by employee ID
- ?status=present           Filter by status
- ?date_from=2024-01-01     From date
- ?date_to=2024-01-31       To date

Leave Filters:
- ?employee=1               Filter by employee ID
- ?status=approved          Filter by status (pending, approved, rejected, canceled)
- ?leave_type=annual        Filter by leave type

Salary Filters:
- ?employee=1               Filter by employee ID
- ?status=paid              Filter by status
- ?period_month=1           Filter by month (1-12)
- ?period_year=2024         Filter by year

Overtime Filters:
- ?employee=1               Filter by employee ID
- ?status=pending           Filter by status
- ?date_from=2024-01-01     From date
- ?date_to=2024-01-31       To date

=============================================================================
EXAMPLE API CALLS
=============================================================================

1. List all employees in a department:
   GET /api/hr/employees/?department=1&ordering=employee_id

2. Get attendance report for January 2024:
   GET /api/hr/attendances/report/?month=1&year=2024

3. Search employee by name/email:
   GET /api/hr/employees/?search=john

4. Get pending leave requests:
   GET /api/hr/leaves/?status=pending&ordering=-start_date

5. Get employee's current salary:
   GET /api/hr/employees/1/salary/

6. List pending salary approvals:
   GET /api/hr/salaries/?status=calculated&page_size=50

7. Approve a leave request:
   POST /api/hr/leaves/5/approve/

8. Calculate and create salary for January:
   POST /api/hr/salaries/
   Content-Type: application/json
   {
       "employee": 1,
       "period_month": 1,
       "period_year": 2024,
       "basic_salary": 5000000,
       "allowances": 500000,
       "bonuses": 0,
       "overtime_pay": 0,
       "deductions": 0,
       "tax": 250000,
       "bpjs": 100000
   }

9. Mark salary as paid:
   POST /api/hr/salaries/1/pay/

10. Get department statistics:
    GET /api/hr/departments/stats/
"""
