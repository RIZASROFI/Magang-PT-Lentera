from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='frontend:login')
def inventaris_perusahaan(request):
    return render(request, 'frontend/inventory/inventaris_perusahaan.html')

