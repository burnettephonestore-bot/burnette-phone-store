import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burnette_store.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import Request, Product, UserProfile
from django.db.models import Q

print('All users and their phones:')
for u in User.objects.all():
    if hasattr(u, 'userprofile'):
        print(f'User: {u.username}, Email: {u.email}, Phone: {u.userprofile.phone}')
    else:
        print(f'User: {u.username}, Email: {u.email}, No profile')

print('\nAll legacy requests (user=None):')
legacy_qs = Request.objects.filter(user__isnull=True)
for r in legacy_qs:
    print(f'ID: {r.id}, Name: {r.contact_name}, Phone: {r.contact_phone}, Email: {r.contact_email}')

print('\nAll requests (including with users):')
all_requests = Request.objects.all()
for r in all_requests:
    print(f'ID: {r.id}, User: {r.user}, Name: {r.contact_name}, Phone: {r.contact_phone}, Email: {r.contact_email}')

print('\nTesting filtering for admin user:')
admin_user = User.objects.get(username='admin')
admin_phone = ''
if hasattr(admin_user, 'userprofile'):
    admin_phone = admin_user.userprofile.phone or ''
print(f'Admin email: {admin_user.email}, phone: "{admin_phone}"')

qs_admin = Request.objects.filter(
    Q(user=admin_user) |
    Q(user__isnull=True, contact_email=admin_user.email) |
    Q(user__isnull=True, contact_phone=admin_phone)
)
print(f'Admin sees {qs_admin.count()} requests')
for r in qs_admin:
    print(f'  ID: {r.id}, User: {r.user}, Phone: {r.contact_phone}, Email: {r.contact_email}')
print('\nTesting filtering for testuser:')
testuser = User.objects.get(username='testuser')
testuser_phone = ''
if hasattr(testuser, 'userprofile'):
    testuser_phone = testuser.userprofile.phone or ''
print(f'Testuser email: {testuser.email}, phone: "{testuser_phone}"')

qs_testuser = Request.objects.filter(
    Q(user=testuser) |
    Q(user__isnull=True, contact_email=testuser.email) |
    Q(user__isnull=True, contact_phone=testuser_phone)
)
print(f'Testuser sees {qs_testuser.count()} requests')
for r in qs_testuser:
    print(f'  ID: {r.id}, User: {r.user}, Phone: {r.contact_phone}, Email: {r.contact_email}')