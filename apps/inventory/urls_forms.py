from django.urls import path

from .views import item_create_view, item_edit_view

urlpatterns = [
    path('items/create/', item_create_view, name='inventory_item_create'),
    path('items/<int:id>/edit/', item_edit_view, name='inventory_item_edit'),
]

