"""
Frontend URL Patterns
"""

from django.urls import path
from . import frontend_views as views

app_name = 'frontend'

urlpatterns = [
    # Home & Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Auth Pages
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.register_page, name='register'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),

    # Inventaris Barang Perusahaan (UI)
    path('inventory/items/', __import__('apps.core.frontend_inventaris_perusahaan', fromlist=['inventaris_perusahaan']).inventaris_perusahaan, name='inventaris_items'),

    # Item create/edit forms (frontend paths for modal)
    path('inventory/items/create/', __import__('apps.inventory.views', fromlist=['item_create_view']).item_create_view, name='inventory_item_create'),
    path('inventory/items/<int:id>/edit/', __import__('apps.inventory.views', fromlist=['item_edit_view']).item_edit_view, name='inventory_item_edit'),

    # Halaman lain: nonaktif/redirect
    path('inventory/perusahaan/', __import__('apps.core.frontend_inventory', fromlist=['company_inventory']).company_inventory, name='inventory_perusahaan'),

    # Projects
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/create/', views.projects_form, name='projects_create'),
    path('projects/<int:id>/edit/', views.projects_form, name='projects_edit'),
    path('progress/', views.projects_progress, name='projects_progress'),

    # HR Frontend
    path('hr/employees/', __import__('apps.hr.frontend_views', fromlist=['employees_page']).employees_page, name='hr_employees'),

    # Stock In (Inventory UI)
    path('inventory/stock-in/', __import__('apps.inventory.frontend_views', fromlist=['stock_in_page']).stock_in_page, name='inventory_stock_in'),

    # Finance Frontend
    path('finance/accounts/', views.finance_accounts, name='finance_accounts'),
    path('finance/transactions/', views.finance_transactions, name='finance_transactions'),
    path('finance/reports/', views.finance_reports, name='finance_reports'),

    # Sales Frontend
    path('sales/customers/', views.sales_customers, name='sales_customers'),
    path('sales/quotations/', views.sales_quotations, name='sales_quotations'),
    path('sales/orders/', views.sales_orders, name='sales_orders'),
    path('sales/vendors/', views.sales_vendors, name='sales_vendors'),
    path('sales/purchase-orders/', views.sales_purchase_orders, name='sales_purchase_orders'),

    # HR Frontend
    path('hr/attendances/', views.hr_attendances, name='hr_attendances'),
    path('hr/salaries/', views.hr_salaries, name='hr_salaries'),
    path('hr/leaves/', views.hr_leaves, name='hr_leaves'),
]

