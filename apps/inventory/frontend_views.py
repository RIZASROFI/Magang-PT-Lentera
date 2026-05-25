from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def stock_in_page(request: HttpRequest) -> HttpResponse:
    """Render template halaman Barang Masuk (Stock In)."""
    return render(request, 'frontend/inventory/stock_in.html')

