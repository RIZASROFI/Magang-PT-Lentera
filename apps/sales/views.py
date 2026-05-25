"""
Sales & Purchase Views - ERP Module
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from django.db.models import Sum

from .models import (
    Customer, Vendor, Quotation, QuotationItem,
    SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem
)
from .serializers import (
    CustomerSerializer, VendorSerializer, QuotationSerializer,
    SalesOrderSerializer, PurchaseOrderSerializer
)
from apps.core.permissions import IsAdminOrReadOnly


class CustomerFilter(filters.FilterSet):
    is_active = filters.BooleanFilter()
    city = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Customer
        fields = ['is_active', 'city']


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Customer"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = CustomerFilter
    search_fields = ['name', 'code', 'phone', 'email', 'city']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = Customer.objects.all()
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Customer statistics"""
        total = Customer.objects.count()
        active = Customer.objects.filter(is_active=True).count()
        
        return Response({
            'total': total,
            'active': active
        })


class VendorViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Vendor"""
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'city']
    ordering = ['name']


class QuotationViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Quotation"""
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['customer', 'status']
    search_fields = ['quotation_number', 'customer__name']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = Quotation.objects.select_related('customer', 'project', 'created_by')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Kirim quotation"""
        quotation = self.get_object()
        if quotation.status != 'draft':
            return Response({'error': 'Status tidak valid!'}, status=status.HTTP_400_BAD_REQUEST)
        quotation.status = 'sent'
        quotation.save()
        return Response({'message': 'Quotation dikirim!'})
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Terima quotation"""
        quotation = self.get_object()
        if quotation.status != 'sent':
            return Response({'error': 'Status tidak valid!'}, status=status.HTTP_400_BAD_REQUEST)
        quotation.status = 'accepted'
        quotation.save()
        return Response({'message': 'Quotation diterima!'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Tolak quotation"""
        quotation = self.get_object()
        quotation.status = 'rejected'
        quotation.notes = request.data.get('notes', '')
        quotation.save()
        return Response({'message': 'Quotation ditolak!'})
    
    @action(detail=True, methods=['post'])
    def convert_to_so(self, request, pk=None):
        """Convert ke Sales Order"""
        quotation = self.get_object()
        if quotation.status != 'accepted':
            return Response({'error': 'Quotation harus diterima dulu!'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create Sales Order from Quotation
        sales_order = SalesOrder.objects.create(
            quotation=quotation,
            customer=quotation.customer,
            project=quotation.project,
            date=quotation.date,
            subtotal=quotation.subtotal,
            tax=quotation.tax,
            discount=quotation.discount,
            terms=quotation.payment_terms,
            notes=quotation.notes,
            created_by=request.user
        )
        
        # Copy items
        for item in quotation.items.all():
            SalesOrderItem.objects.create(
                sales_order=sales_order,
                item=item.item,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount=item.discount,
                total=item.total
            )
        
        quotation.status = 'converted'
        quotation.save()
        
        return Response({
            'message': 'Quotation diubah ke Sales Order!',
            'sales_order_id': sales_order.id
        })


class SalesOrderViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Sales Order"""
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['customer', 'status', 'project']
    search_fields = ['sales_order_number', 'customer__name']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = SalesOrder.objects.select_related('customer', 'project', 'quotation', 'created_by')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm Sales Order"""
        so = self.get_object()
        if so.status != 'draft':
            return Response({'error': 'Status tidak valid!'}, status=status.HTTP_400_BAD_REQUEST)
        so.status = 'confirmed'
        so.save()
        return Response({'message': 'Sales Order dikonfirmasi!'})
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Mulai bekerja"""
        so = self.get_object()
        if so.status != 'confirmed':
            return Response({'error': 'Harus dikonfirmasi dulu!'}, status=status.HTTP_400_BAD_REQUEST)
        so.status = 'in_progress'
        so.save()
        return Response({'message': 'Pekerjaan dimulai!'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Selesaikan Sales Order"""
        so = self.get_object()
        so.status = 'completed'
        so.save()
        return Response({'message': 'Sales Order selesai!'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel Sales Order"""
        so = self.get_object()
        so.status = 'canceled'
        so.notes = request.data.get('notes', '')
        so.save()
        return Response({'message': 'Sales Order dibatalkan!'})


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Purchase Order"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['vendor', 'status']
    search_fields = ['purchase_order_number', 'vendor__name']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = PurchaseOrder.objects.select_related('vendor', 'created_by')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Kirim PO ke Vendor"""
        po = self.get_object()
        if po.status != 'draft':
            return Response({'error': 'Status tidak valid!'}, status=status.HTTP_400_BAD_REQUEST)
        po.status = 'sent'
        po.save()
        return Response({'message': 'PO dikirim ke vendor!'})
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Terima barang"""
        po = self.get_object()
        if po.status not in ['sent', 'confirmed']:
            return Response({'error': 'Status tidak valid!'}, status=status.HTTP_400_BAD_REQUEST)
        po.status = 'received'
        po.save()
        return Response({'message': 'Barang diterima!'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Selesaikan PO"""
        po = self.get_object()
        po.status = 'completed'
        po.save()
        return Response({'message': 'PO selesai!'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel PO"""
        po = self.get_object()
        po.status = 'canceled'
        po.notes = request.data.get('notes', '')
        po.save()
        return Response({'message': 'PO dibatalkan!'})


class SalesReportViewSet(viewsets.ViewSet):
    """ViewSet untuk Laporan Penjualan"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Ringkasan penjualan"""
        total_quotations = Quotation.objects.count()
        accepted_quotations = Quotation.objects.filter(status='accepted').count()
        
        total_sales = SalesOrder.objects.filter(status__in=['completed', 'in_progress'])
        total_orders = total_sales.count()
        total_value = total_sales.aggregate(total=Sum('total'))['total'] or 0
        
        return Response({
            'quotations': {
                'total': total_quotations,
                'accepted': accepted_quotations
            },
            'sales_orders': {
                'total': total_orders,
                'value': total_value
            }
        })
