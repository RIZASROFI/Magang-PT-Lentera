from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='frontend:login')
def company_inventory(request):
    # Sudah diminta user untuk tidak menampilkan halaman ini.
    # Tetap arahkan ke inventaris_perusahaan.
    from django.shortcuts import redirect
    return redirect('/inventory/inventaris-perusahaan/')



