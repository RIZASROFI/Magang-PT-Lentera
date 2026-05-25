from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.inventory.models import Category, Item, Supplier


class Command(BaseCommand):
    help = "Seed dummy data inventory perusahaan (CCTV, Kabel LAN, Module Videotron)"

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).order_by('-id').first() or User.objects.first()

        # Supplier default (jika belum ada)
        supplier, _ = Supplier.objects.get_or_create(
            code='SUP-DEFAULT',
            defaults={
                'name': 'Supplier Dummy',
                'contact_person': '',
                'phone': '',
                'email': '',
                'address': '',
                'city': '',
                'notes': '',
                'is_active': True,
            }
        )

        # Categories
        cat_cctv, _ = Category.objects.get_or_create(
            code='CAT-CCTV',
            defaults={
                'name': 'CCTV',
                'description': 'Kategori perangkat CCTV',
                'parent': None,
                'is_active': True,
            }
        )

        cat_network, _ = Category.objects.get_or_create(
            code='CAT-NET',
            defaults={
                'name': 'Networking',
                'description': 'Kategori kabel & networking',
                'parent': None,
                'is_active': True,
            }
        )

        cat_videotron, _ = Category.objects.get_or_create(
            code='CAT-VID',
            defaults={
                'name': 'Videotron',
                'description': 'Kategori modul videotron',
                'parent': None,
                'is_active': True,
            }
        )

        def upsert_item(*, sku, name, category, specs='', brand='', model='', unit='pcs',
                         min_stock=0, max_stock=0, cost_price=0, sell_price=0, warehouse_location='',
                         rack_location='', is_active=True, is_trackable=True, has_expiry=False,
                         image=None, default_supplier=supplier):
            item, created = Item.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': category,
                    'brand': brand,
                    'model': model,
                    'specs': specs,
                    'unit': unit,
                    'min_stock': min_stock,
                    'max_stock': max_stock,
                    'cost_price': cost_price,
                    'sell_price': sell_price,
                    'warehouse_location': warehouse_location,
                    'rack_location': rack_location,
                    'is_active': is_active,
                    'is_trackable': is_trackable,
                    'has_expiry': has_expiry,
                    'image': image,
                    'default_supplier': default_supplier,
                    'created_by': user,
                },
            )

            # update basic fields if already exist (idempotent)
            changed = False
            for field, value in {
                'name': name,
                'category': category,
                'brand': brand,
                'model': model,
                'specs': specs,
                'unit': unit,
                'min_stock': min_stock,
                'max_stock': max_stock,
                'cost_price': cost_price,
                'sell_price': sell_price,
                'warehouse_location': warehouse_location,
                'rack_location': rack_location,
                'is_active': is_active,
                'is_trackable': is_trackable,
                'has_expiry': has_expiry,
                'default_supplier': default_supplier,
            }.items():
                if getattr(item, field) != value:
                    setattr(item, field, value)
                    changed = True

            if changed:
                item.save()
            return item, created

        # Dummy Items
        items_to_seed = [
            dict(
                sku='SKU-CCTV-2MP-BULLET',
                name='CCTV Bullet 2MP',
                category=cat_cctv,
                specs='Resolusi 2MP, tahan cuaca, night vision.',
                brand='LENTERA',
                model='CB-2MP',
                unit='pcs',
                min_stock=5,
                max_stock=200,
                cost_price=150000,
                sell_price=250000,
                warehouse_location='WH-01',
                rack_location='RACK-A1',
                is_trackable=True,
                has_expiry=False,
            ),
            dict(
                sku='SKU-CABLE-LAN-CAT6-305M',
                name='Kabel LAN UTP Cat6 305 Meter',
                category=cat_network,
                specs='UTP Cat6, 305m/roll, indoor/outdoor.',
                brand='LANPRO',
                model='CAT6-305M',
                unit='roll',
                min_stock=10,
                max_stock=500,
                cost_price=300000,
                sell_price=450000,
                warehouse_location='WH-01',
                rack_location='RACK-B2',
                is_trackable=False,
                has_expiry=False,
            ),
            dict(
                sku='SKU-VID-MODULE-PIX',
                name='Module Videotron',
                category=cat_videotron,
                specs='Module untuk display/videotron, resolusi sesuai kebutuhan.',
                brand='VIDEOTRON',
                model='VM-PIX-8',
                unit='pcs',
                min_stock=2,
                max_stock=100,
                cost_price=500000,
                sell_price=750000,
                warehouse_location='WH-02',
                rack_location='RACK-C3',
                is_trackable=True,
                has_expiry=False,
            ),
        ]

        seeded = 0
        for data in items_to_seed:
            _, created = upsert_item(
                **data,
            )
            seeded += 1

        self.stdout.write(self.style.SUCCESS(f'Success seed inventory company dummy. Seeded items: {seeded}'))

