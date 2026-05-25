from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='frontend:login')
def employees_page(request):
    return render(request, 'frontend/hr/employees.html')

