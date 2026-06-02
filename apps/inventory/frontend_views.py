from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def stock_in_page(request: HttpRequest) -> HttpResponse:
    """Render template halaman Barang Masuk (Stock In)."""
    return render(request, 'frontend/inventory/stock_in.html')


def stock_out_page(request: HttpRequest) -> HttpResponse:
    """Render template halaman Barang Keluar (Stock Out)."""
    return render(request, 'frontend/inventory/stock_out.html')

