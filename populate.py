import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burnette_store.settings')
django.setup()

from store.models import Product, Update, Bank, MobileMoney, SiteSettings

# Create site settings
settings, created = SiteSettings.objects.get_or_create(
    defaults={
        'admin_username': 'admin',
        'admin_password': 'password123',
        'site_title': 'Burnette Phone Store',
        'site_description': 'Your trusted phone store in Tanzania'
    }
)

# Create sample products
products_data = [
    {
        'name': 'iPhone 15 Pro',
        'description': 'Latest iPhone with advanced features',
        'price': 1500000,
        'image': 'iphone15.jpg',
        'category': 'Smartphone'
    },
    {
        'name': 'Samsung Galaxy S24',
        'description': 'Powerful Android smartphone',
        'price': 1200000,
        'image': 'galaxy_s24.jpg',
        'category': 'Smartphone'
    },
    {
        'name': 'Google Pixel 8',
        'description': 'Pure Android experience',
        'price': 1000000,
        'image': 'pixel8.jpg',
        'category': 'Smartphone'
    },
    {
        'name': 'OnePlus 12',
        'description': 'Fast charging and performance',
        'price': 900000,
        'image': 'oneplus12.jpg',
        'category': 'Smartphone'
    },
    {
        'name': 'Xiaomi 14',
        'description': 'Affordable flagship',
        'price': 800000,
        'image': 'xiaomi14.jpg',
        'category': 'Smartphone'
    },
    {
        'name': 'Huawei P60',
        'description': 'Great camera and battery',
        'price': 750000,
        'image': 'huawei_p60.jpg',
        'category': 'Smartphone'
    }
]

for data in products_data:
    Product.objects.get_or_create(
        name=data['name'],
        defaults=data
    )

# Create sample updates
updates_data = [
    {
        'title': 'New iPhone 15 Available',
        'content': 'We now have the latest iPhone 15 in stock. Limited quantities available!'
    },
    {
        'title': 'Flash Sale: 20% Off Samsung',
        'content': 'Get 20% discount on all Samsung Galaxy S24 models this weekend only.'
    },
    {
        'title': 'Free Delivery in Dar es Salaam',
        'content': 'Enjoy free delivery on orders over TZS 500,000 within Dar es Salaam.'
    }
]

for data in updates_data:
    Update.objects.get_or_create(
        title=data['title'],
        defaults=data
    )

# Create banks
banks_data = [
    'CRDB Bank',
    'NMB Bank',
    'NBC Bank',
    'Absa Bank',
    'Stanbic Bank'
]

for name in banks_data:
    Bank.objects.get_or_create(name=name)

# Create mobile money
mobiles_data = [
    'M-Pesa',
    'Tigo Pesa',
    'Airtel Money',
    'Halo Pesa'
]

for name in mobiles_data:
    MobileMoney.objects.get_or_create(name=name)

print("Sample data populated successfully!")