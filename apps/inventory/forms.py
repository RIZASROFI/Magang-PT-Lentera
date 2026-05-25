from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone

from .models import Item, Category, Supplier, StockIn, StockInItem


class ItemForm(forms.ModelForm):
    category = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ketik kategori...'
        })
    )

    stock = forms.IntegerField(
        required=False,
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0',
            'step': '1',
        }),
        help_text='Qty stok yang ditambahkan saat item dibuat.'
    )

    # Untuk modal "Tambah Barang" yang tidak mengirim sell_price,
    # sell_price dibuat optional agar form tidak 400.
    sell_price = forms.DecimalField(
        required=False,
        initial=0,
        min_value=0,
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0',
            'step': '0.01'
        }),
    )


    class Meta:
        model = Item
        fields = [
            'name',
            'category',
            'brand',
            'cost_price',
            'sell_price',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama barang'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brand barang'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01'
            }),
            'sell_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01'
            }),
        }

    def clean_cost_price(self):
        cost_price = self.cleaned_data.get('cost_price')
        if cost_price is None:
            return Decimal('0')
        if cost_price < 0:
            raise ValidationError('Harga beli tidak boleh minus.')
        return cost_price

    def clean_sell_price(self):
        sell_price = self.cleaned_data.get('sell_price')
        if sell_price is None or sell_price == '':
            return Decimal('0')
        if sell_price < 0:
            raise ValidationError('Harga jual tidak boleh minus.')
        return sell_price



    def clean_category(self):
        category_name = self.cleaned_data.get('category', '').strip()
        if not category_name:
            raise ValidationError('Kategori harus diisi.')

        category = Category.objects.filter(name__iexact=category_name).first()
        if category:
            return category

        code = self._generate_category_code(category_name)
        return Category.objects.create(name=category_name, code=code)

    def _generate_category_code(self, name):
        import re

        base = re.sub(r'[^A-Za-z0-9]', '', name).upper()[:16] or 'CAT'
        code = base
        suffix = 1
        while Category.objects.filter(code=code).exists():
            suffix_str = str(suffix)
            code = f'{base[:20-len(suffix_str)]}{suffix_str}'
            suffix += 1
        return code

    def clean(self):
        cleaned_data = super().clean()
        cost_price = cleaned_data.get('cost_price') or Decimal('0')
        # sell_price bisa None jika tidak dikirim dari form.
        sell_price = cleaned_data.get('sell_price', None)

        # Hanya validasi kalau sell_price benar-benar dikirim dari form.
        # Modal tambah barang tidak mengirim sell_price, sehingga sell_price akan memakai default.
        # Skip validasi pada kasus itu.
        if 'sell_price' in self.data and sell_price is not None:
            if sell_price < cost_price:
                raise ValidationError('Harga jual tidak boleh lebih kecil dari harga beli.')




        return cleaned_data


    def save(self, commit=True):
        # description/current_stock bukan field model Item saat ini
        instance = super().save(commit=False)
        stock_value = self.cleaned_data.get('stock') or 0


        if not instance.sku:
            instance.sku = self._generate_sku(instance.name, instance.category)

        if commit:
            instance.save()
            if stock_value > 0:
                stock_in = StockIn.objects.create(

                    source='adjustment',
                    transaction_date=timezone.now().date(),
                    status='completed',
                    is_completed=True,
                )
                StockInItem.objects.create(
                    stock_in=stock_in,
                    item=instance,
                    quantity=stock_value,
                    unit_price=instance.cost_price or 0,
                    discount=0,
                )
                stock_in.total_items = stock_value
                stock_in.total_amount = stock_in.items.aggregate(total=Sum('total'))['total'] or 0
                stock_in.save()
        return instance

    def _generate_sku(self, name, category=None):
        import re

        raw = f"{category.name if category else ''}-{name}" if category else name
        base = re.sub(r'[^A-Za-z0-9]+', '-', raw).strip('-').upper()[:40] or 'ITEM'
        sku = base
        counter = 1
        while Item.objects.filter(sku=sku).exists():
            suffix = f"-{counter}"
            sku = f"{base[:40-len(suffix)]}{suffix}"
            counter += 1
        return sku

