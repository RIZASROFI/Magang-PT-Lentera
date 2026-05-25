"""
Finance Views - Management Information System
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from django.db.models import Sum, Q
from datetime import datetime

from .models import (
    Account, JournalEntry, JournalEntryItem, IncomeCategory, Income,
    ExpenseCategory, Expense, Invoice, Payment
)
from .serializers import (
    AccountSerializer, JournalEntryListSerializer, JournalEntryDetailSerializer,
    IncomeCategorySerializer, IncomeSerializer, ExpenseCategorySerializer,
    ExpenseSerializer, InvoiceSerializer, InvoiceListSerializer,
    PaymentSerializer
)


class AccountFilter(filters.FilterSet):
    account_type = filters.ChoiceFilter(choices=Account.ACCOUNT_TYPE_CHOICES)
    is_cash = filters.BooleanFilter()
    is_active = filters.BooleanFilter()
    
    class Meta:
        model = Account
        fields = ['account_type', 'is_cash', 'is_active']


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Account/COA"""
    queryset = Account.objects.filter(parent__isnull=True)
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AccountFilter
    search_fields = ['code', 'name']
    ordering = ['code']
    
    @action(detail=False, methods=['get'])
    def cash_accounts(self, request):
        """Get cash/bank accounts"""
        accounts = Account.objects.filter(is_cash=True, is_active=True)
        return Response(AccountSerializer(accounts, many=True).data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Account statistics"""
        total = Account.objects.count()
        active = Account.objects.filter(is_active=True).count()
        cash = Account.objects.filter(is_cash=True).count()
        
        return Response({
            'total': total,
            'active': active,
            'cash_accounts': cash
        })


class JournalEntryViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Journal Entry"""
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntryListSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['entry_number', 'description', 'reference_number']
    ordering = ['-date', '-entry_number']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JournalEntryListSerializer
        return JournalEntryDetailSerializer
    
    def get_queryset(self):
        queryset = JournalEntry.objects.select_related('created_by', 'approved_by')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def post(self, request, pk=None):
        """Post journal entry"""
        journal = self.get_object()
        
        if journal.status != 'draft':
            return Response(
                {'error': 'Hanya draft yang bisa dipost!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if journal.total_debit != journal.total_credit:
            return Response(
                {'error': 'Total debit harus sama dengan total credit!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        journal.status = 'posted'
        journal.save()
        
        return Response({'message': 'Journal entry dipost!'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel journal entry"""
        journal = self.get_object()
        
        if journal.status == 'canceled':
            return Response({'error': 'Sudah dicancel!'}, status=status.HTTP_400_BAD_REQUEST)
        
        journal.status = 'canceled'
        journal.save()
        
        return Response({'message': 'Journal entry dicancel!'})


class IncomeCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Income Category"""
    queryset = IncomeCategory.objects.all()
    serializer_class = IncomeCategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']


class IncomeViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Income"""
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'status', 'customer', 'project']
    search_fields = ['income_number', 'description']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = Income.objects.select_related('category', 'account', 'customer', 'project', 'created_by')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm income"""
        income = self.get_object()
        
        if income.status != 'pending':
            return Response(
                {'error': 'Hanya pending yang bisa dikonfirm!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        income.status = 'confirmed'
        income.save()
        
        return Response({'message': 'Income dikonfirm!'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete income"""
        income = self.get_object()
        
        if income.status not in ['pending', 'confirmed']:
            return Response({'error': 'Status tidak valid!'}, status=status.HTTP_400_BAD_REQUEST)
        
        income.status = 'completed'
        income.is_completed = True
        income.save()
        
        return Response({'message': 'Income selesai!'})


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Expense Category"""
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']


class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Expense"""
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'status', 'vendor', 'project']
    search_fields = ['expense_number', 'description']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = Expense.objects.select_related('category', 'account', 'vendor', 'project', 'created_by')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm expense"""
        expense = self.get_object()
        
        if expense.status != 'pending':
            return Response(
                {'error': 'Hanya pending yang bisa dikonfirm!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expense.status = 'confirmed'
        expense.save()
        
        return Response({'message': 'Expense dikonfirm!'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete expense"""
        expense = self.get_object()
        
        if expense.status not in ['pending', 'confirmed']:
            return Response({'error': 'Status tidak valid!'}, status=status.HTTP_400_BAD_REQUEST)
        
        expense.status = 'completed'
        expense.is_completed = True
        expense.save()
        
        return Response({'message': 'Expense selesai!'})


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Invoice"""
    queryset = Invoice.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['customer', 'project', 'status']
    search_fields = ['invoice_number']
    ordering = ['-date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer
    
    def get_queryset(self):
        queryset = Invoice.objects.select_related('customer', 'project', 'created_by')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Kirim invoice"""
        invoice = self.get_object()
        
        if invoice.status != 'draft':
            return Response({'error': 'Status tidak valid!'}, status=status.HTTP_400_BAD_REQUEST)
        
        invoice.status = 'sent'
        invoice.save()
        
        return Response({'message': 'Invoice dikirim!'})


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Payment"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['customer', 'invoice', 'payment_type']
    search_fields = ['payment_number']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = Payment.objects.select_related('invoice', 'customer', 'account', 'created_by')
        
        customer = self.request.query_params.get('customer')
        if customer:
            queryset = queryset.filter(customer_id=customer)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        
        # Update invoice jika ada
        invoice = serializer.instance.invoice
        if invoice:
            invoice.amount_paid += serializer.instance.amount
            invoice.save()
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Tandai invoice lunas"""
        payment = self.get_object()
        
        if payment.invoice:
            payment.invoice.status = 'paid'
            payment.invoice.save()
        
        return Response({'message': 'Invoice lunas!'})


class FinanceReportViewSet(viewsets.ViewSet):
    """ViewSet untuk Laporan Keuangan"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Ringkasan keuangan"""
        # Total Income
        total_income = Income.objects.filter(
            is_completed=True
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Total Expense
        total_expense = Expense.objects.filter(
            is_completed=True
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Cash Balance
        cash_accounts = Account.objects.filter(is_cash=True)
        cash_balance = sum(account.balance for account in cash_accounts)
        
        # Piutang
        receivables = Invoice.objects.exclude(
            status__in=['paid', 'canceled']
        ).aggregate(total=Sum('amount_due'))['total'] or 0
        
        # Hutang
        payables = 0  # Calculate dari purchase orders jika ada
        
        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'net_profit': total_income - total_expense,
            'cash_balance': cash_balance,
            'receivables': receivables,
            'payables': payables
        })
    
    @action(detail=False, methods=['get'])
    def profit_loss(self, request):
        """Laporan Rugi Laba"""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        incomes = Income.objects.filter(is_completed=True)
        expenses = Expense.objects.filter(is_completed=True)
        
        if from_date:
            incomes = incomes.filter(date__gte=from_date)
            expenses = expenses.filter(date__gte=from_date)
        
        if to_date:
            incomes = incomes.filter(date__lte=to_date)
            expenses = expenses.filter(date__lte=to_date)
        
        total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'net_profit': total_income - total_expense,
            'profit_margin': ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0
        })
    
    @action(detail=False, methods=['get'])
    def cash_flow(self, request):
        """Laporan Arus Kas"""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        cash_in = Income.objects.filter(is_completed=True)
        cash_out = Expense.objects.filter(is_completed=True)
        
        if from_date:
            cash_in = cash_in.filter(date__gte=from_date)
            cash_out = cash_out.filter(date__gte=from_date)
        
        if to_date:
            cash_in = cash_in.filter(date__lte=to_date)
            cash_out = cash_out.filter(date__lte=to_date)
        
        return Response({
            'cash_in': cash_in.aggregate(total=Sum('amount'))['total'] or 0,
            'cash_out': cash_out.aggregate(total=Sum('amount'))['total'] or 0,
            'net_cash_flow': (
                cash_in.aggregate(total=Sum('amount'))['total'] or 0
            ) - (
                cash_out.aggregate(total=Sum('amount'))['total'] or 0
            )
        })
