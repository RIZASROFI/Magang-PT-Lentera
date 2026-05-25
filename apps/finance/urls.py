"""
Finance URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccountViewSet, JournalEntryViewSet, IncomeCategoryViewSet,
    IncomeViewSet, ExpenseCategoryViewSet, ExpenseViewSet,
    InvoiceViewSet, PaymentViewSet, FinanceReportViewSet
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'journal', JournalEntryViewSet, basename='journal')
router.register(r'income-categories', IncomeCategoryViewSet, basename='income-category')
router.register(r'incomes', IncomeViewSet, basename='income')
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expense-category')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'reports', FinanceReportViewSet, basename='finance-report')

urlpatterns = [
    path('', include(router.urls)),
]
