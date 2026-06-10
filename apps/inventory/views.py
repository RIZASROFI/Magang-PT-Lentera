"""
Inventory Views - Transaction Processing System
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from django.db.models import Sum, F
from django.db.models import ProtectedError
from datetime import datetime

from .models import (
    Category, Item, Supplier, StockIn, StockInItem,
    StockOut, StockOutItem, StockOpname, StockOpnameItem, StockAlert
)
from .serializers import (
    CategorySerializer, ItemListSerializer, ItemDetailSerializer, ItemCreateSerializer,
    SupplierSerializer, StockInListSerializer, StockInDetailSerializer,
    StockInCreateSerializer, StockOutListSerializer, StockOutDetailSerializer,
    StockOutCreateSerializer, StockOpnameSerializer, StockAlertSerializer
)

# Django Forms (HTML)
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from .forms import ItemForm


@login_required(login_url='frontend:login')
def item_create_view(request: HttpRequest) -> HttpResponse:

    """Tambah barang inventory (Django Form)."""
    is_modal = request.GET.get('modal') == '1' or request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.created_by = request.user
            item = form.save(commit=True)
            messages.success(request, 'Barang berhasil disimpan.')

            if is_modal:
                from django.http import JsonResponse
                return JsonResponse({
                    'ok': True, 
                    'message': 'Barang berhasil disimpan.',
                    'item_id': item.id,
                    'item_name': item.name
                })
            return redirect('/inventory/items/')
        else:
            if is_modal:
                from django.http import JsonResponse
                # Format error messages
                error_msgs = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_msgs.append(f"{field}: {error}")
                return JsonResponse({
                    'ok': False, 
                    'message': ' | '.join(error_msgs) or 'Terjadi kesalahan pada form',
                    'errors': form.errors
                }, status=400)
    else:
        form = ItemForm()

    template = 'inventory/item_create_popup_form.html' if is_modal else 'inventory/item_form.html'

    return render(request, template, {
        'form': form,
        'title': 'Tambah Barang',
        'back_url': '/inventory/items/'
    })


@login_required(login_url='frontend:login')
def item_edit_view(request: HttpRequest, id: int) -> HttpResponse:
    """Edit barang inventory (Django Form)."""
    item = get_object_or_404(Item, pk=id)

    is_modal = request.GET.get('modal') == '1' or request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Barang berhasil diperbarui.')
            if is_modal:
                from django.http import JsonResponse
                return JsonResponse({
                    'ok': True,
                    'message': 'Barang berhasil diperbarui.',
                    'item_id': item.id,
                    'item_name': item.name
                })
            return redirect('/inventory/items/')
        else:
            if is_modal:
                from django.http import JsonResponse
                error_msgs = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_msgs.append(f"{field}: {error}")
                return JsonResponse({
                    'ok': False,
                    'message': ' | '.join(error_msgs) or 'Terjadi kesalahan pada form',
                    'errors': form.errors
                }, status=400)
    else:
        form = ItemForm(instance=item, initial={'stock': item.current_stock})

    template = 'inventory/item_create_popup_form.html' if is_modal else 'inventory/item_form.html'

    return render(request, template, {
        'form': form,
        'title': f'Edit Barang: {item.sku}',
        'back_url': '/inventory/items/'
    })




class CategoryFilter(filters.FilterSet):

    parent = filters.NumberFilter(field_name='parent_id')
    is_active = filters.BooleanFilter()
    
    class Meta:
        model = Category
        fields = ['parent', 'is_active']


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Category"""
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CategoryFilter
    search_fields = ['name', 'code']


class ItemFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name='category_id')
    is_active = filters.BooleanFilter()
    is_trackable = filters.BooleanFilter()
    
    class Meta:
        model = Item
        fields = ['category', 'is_active', 'is_trackable']


class ItemViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Item/Barang"""
    queryset = Item.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_class = ItemFilter
    search_fields = ['name', 'sku', 'barcode', 'brand', 'model']
    ordering_fields = ['name', 'sku', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ItemListSerializer
        elif self.action == 'create':
            return ItemCreateSerializer
        return ItemDetailSerializer
    
    def get_queryset(self):
        queryset = Item.objects.select_related('category', 'default_supplier')
        
        # Default: hanya tampilkan item aktif
        queryset = queryset.filter(is_active=True)
        
        # Filter category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter active (override jika ?is_active=false)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """
        Hapus item secara permanen.
        Akan gagal (ProtectedError) jika item masih dirujuk oleh transaksi
        Stock In, Stock Out, atau Stock Opname.
        """
        instance = self.get_object()
        try:
            instance.delete()
            return Response(
                {'message': 'Item berhasil dihapus permanen.'},
                status=status.HTTP_200_OK
            )
        except ProtectedError as e:
            # Hitung jumlah referensi dari pesan error
            protected_objects = e.protected_objects if hasattr(e, 'protected_objects') else []
            return Response(
                {
                    'error': (
                        'Item tidak dapat dihapus karena masih memiliki data transaksi terkait '
                        f'({len(protected_objects)} referensi). '
                        'Hapus atau arsipkan transaksi terkait terlebih dahulu.'
                    ),
                    'detail': f'Item ini masih dirujuk oleh {len(protected_objects)} data transaksi.'
                },
                status=status.HTTP_409_CONFLICT
            )
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Items dengan stok rendah"""
        items = Item.objects.filter(is_active=True)
        low_stock_items = []
        
        for item in items:
            if item.current_stock <= item.min_stock:
                low_stock_items.append({
                    'id': item.id,
                    'name': item.name,
                    'sku': item.sku,
                    'current_stock': item.current_stock,
                    'min_stock': item.min_stock,
                    'category': item.category.name
                })
        
        return Response(low_stock_items)


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Supplier"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'phone', 'email', 'city']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Supplier statistics"""
        total = Supplier.objects.count()
        active = Supplier.objects.filter(is_active=True).count()
        
        return Response({
            'total': total,
            'active': active,
            'inactive': total - active
        })


class StockInViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Stock In (Barang Masuk)"""
    queryset = StockIn.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['source', 'status', 'supplier']
    search_fields = ['transaction_number', 'reference_number']
    ordering_fields = ['transaction_date', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StockInListSerializer
        elif self.action == 'create':
            return StockInCreateSerializer
        return StockInDetailSerializer
    
    def get_queryset(self):
        queryset = StockIn.objects.select_related('supplier', 'created_by', 'approved_by')
        
        # Filter status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter source
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source=source)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve stock in"""
        stock_in = self.get_object()
        if stock_in.status != 'pending':
            return Response(
                {'error': 'Hanya status pending yang bisa diapprove!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stock_in.status = 'approved'
        stock_in.approved_by = request.user
        stock_in.save()
        
        return Response({'message': 'Stock in disetujui!'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete stock in - tambahkan ke stok"""
        stock_in = self.get_object()
        if stock_in.status != 'approved':
            return Response(
                {'error': 'Hanya status approved yang bisa diselesaikan!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stock_in.status = 'completed'
        stock_in.is_completed = True
        stock_in.received_date = datetime.now().date()
        stock_in.save()
        
        return Response({'message': 'Stock in selesai, stok ditambahkan!'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel stock in - batalkan transaksi termasuk yang sudah completed"""
        stock_in = self.get_object()
        
        # Cegah cancel yang sudah cancel
        if stock_in.status == 'canceled':
            return Response(
                {'error': 'Stock in sudah dibatalkan sebelumnya!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stock_in.status = 'canceled'
        stock_in.is_completed = False
        stock_in.received_date = None
        stock_in.save()
        
        return Response({'message': 'Stock in berhasil dibatalkan!'})


class StockOutViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Stock Out (Barang Keluar)"""
    queryset = StockOut.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['out_type', 'status', 'project']
    search_fields = ['transaction_number', 'reference_number']
    ordering_fields = ['transaction_date', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StockOutListSerializer
        elif self.action == 'create':
            return StockOutCreateSerializer
        return StockOutDetailSerializer
    
    def get_queryset(self):
        queryset = StockOut.objects.select_related('project', 'created_by', 'approved_by')
        
        # Filter status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter out_type
        out_type = self.request.query_params.get('out_type')
        if out_type:
            queryset = queryset.filter(out_type=out_type)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        """
        Hapus transaksi barang keluar dan kembalikan stok barang.
        """
        # Kembalikan stok untuk setiap item
        for item in instance.items.all():
            if item.item:
                item.item.current_stock += item.quantity
                item.item.save(update_fields=['current_stock'])
        
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve stock out"""
        stock_out = self.get_object()
        if stock_out.status != 'pending':
            return Response(
                {'error': 'Hanya status pending yang bisa diapprove!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stock_out.status = 'approved'
        stock_out.approved_by = request.user
        stock_out.save()
        
        return Response({'message': 'Stock out disetujui!'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete stock out"""
        stock_out = self.get_object()
        if stock_out.status != 'approved':
            return Response(
                {'error': 'Hanya status approved yang bisa diselesaikan!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Stok sudah dikurangi saat transaksi dibuat, jadi hanya update status
        stock_out.status = 'completed'
        stock_out.is_completed = True
        stock_out.delivered_date = datetime.now().date()
        stock_out.save()
        
        return Response({'message': 'Stock out selesai!'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel stock out - batalkan transaksi dan kembalikan stok"""
        stock_out = self.get_object()
        
        # Cegah cancel yang sudah cancel
        if stock_out.status == 'canceled':
            return Response(
                {'error': 'Stock out sudah dibatalkan sebelumnya!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Kembalikan stok untuk setiap item
        for item in stock_out.items.all():
            if item.item:
                item.item.current_stock += item.quantity
                item.item.save(update_fields=['current_stock'])
        
        stock_out.status = 'canceled'
        stock_out.is_completed = False
        stock_out.delivered_date = None
        stock_out.save()
        
        return Response({'message': 'Stock out berhasil dibatalkan, stok dikembalikan!'})


class StockOpnameViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Stock Opname"""
    queryset = StockOpname.objects.all()
    serializer_class = StockOpnameSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Mulai stock opname"""
        opname = self.get_object()
        if opname.status != 'draft':
            return Response(
                {'error': 'Hanya draft yang bisa dimulai!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        opname.status = 'ongoing'
        opname.start_date = datetime.now().date()
        opname.save()
        
        return Response({'message': 'Stock opname dimulai!'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Selesaikan stock opname"""
        opname = self.get_object()
        if opname.status != 'ongoing':
            return Response(
                {'error': 'Hanya ongoing yang bisa diselesaikan!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Hitung total
        total_system = sum(item.system_quantity for item in opname.items.all())
        total_actual = sum(item.actual_quantity for item in opname.items.all())
        
        opname.total_system = total_system
        opname.total_actual = total_actual
        opname.difference = total_actual - total_system
        opname.end_date = datetime.now().date()
        opname.status = 'completed'
        opname.save()
        
        return Response({'message': 'Stock opname selesai!', 'difference': opname.difference})


class StockAlertViewSet(viewsets.ModelViewSet):
    """ViewSet untuk Stock Alert"""
    queryset = StockAlert.objects.all()
    serializer_class = StockAlertSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['alert_type', 'is_resolved']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = StockAlert.objects.select_related('item', 'resolved_by')
        
        # Filter unresolved
        unresolved = self.request.query_params.get('unresolved')
        if unresolved:
            queryset = queryset.filter(is_resolved=False)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve alert"""
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_by = request.user
        alert.notes = request.data.get('notes', '')
        alert.save()
        
        return Response({'message': 'Alertresolved!'})
    
    @action(detail=False, methods=['get'])
    def generate(self, request):
        """Generate alert untuk stok rendah"""
        low_stock_items = Item.objects.filter(is_active=True, min_stock__gt=0)
        created_count = 0
        
        for item in low_stock_items:
            if item.current_stock <= item.min_stock:
                alert, created = StockAlert.objects.get_or_create(
                    item=item,
                    alert_type='min_stock',
                    is_resolved=False,
                )
                if created:
                    created_count += 1
        
        return Response({
            'message': f'{created_count} alerts dibuat!',
            'count': created_count
        })


class InventoryReportViewSet(viewsets.ViewSet):
    """ViewSet untuk Laporan Inventory"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stock_summary(self, request):
        """Ringkasan stok"""
        total_items = Item.objects.filter(is_active=True).count()
        total_value = sum(
            item.current_stock * item.cost_price 
            for item in Item.objects.filter(is_active=True)
        )
        
        low_stock = Item.objects.filter(
            is_active=True
        ).extra(
            where=["(SELECT COALESCE(SUM(quantity), 0) FROM stock_ins WHERE stock_ins.is_completed=1 AND id IN (SELECT stock_in_id FROM stock_in_items WHERE item_id = inventory_items.id)) - (SELECT COALESCE(SUM(quantity), 0) FROM stock_outs WHERE stock_outs.is_completed=1 AND id IN (SELECT stock_out_id FROM stock_out_items WHERE item_id = inventory_items.id))) <= min_stock"]
        )
        
        return Response({
            'total_items': total_items,
            'total_value': total_value,
            'low_stock_count': low_stock.count()
        })
    
    @action(detail=False, methods=['get'])
    def movement(self, request):
        """Laporan pergerakan stok"""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        stock_ins = StockIn.objects.filter(is_completed=True)
        stock_outs = StockOut.objects.filter(is_completed=True)
        
        if from_date:
            stock_ins = stock_ins.filter(transaction_date__gte=from_date)
            stock_outs = stock_outs.filter(transaction_date__gte=from_date)
        
        if to_date:
            stock_ins = stock_ins.filter(transaction_date__lte=to_date)
            stock_outs = stock_outs.filter(transaction_date__lte=to_date)
        
        return Response({
            'stock_in': {
                'count': stock_ins.count(),
                'total_items': stock_ins.aggregate(total=models.Sum('total_items'))['total'] or 0,
                'total_amount': stock_ins.aggregate(total=models.Sum('total_amount'))['total'] or 0
            },
            'stock_out': {
                'count': stock_outs.count(),
                'total_items': stock_outs.aggregate(total=models.Sum('total_items'))['total'] or 0,
                'total_amount': stock_outs.aggregate(total=models.Sum('total_amount'))['total'] or 0
            }
        })
