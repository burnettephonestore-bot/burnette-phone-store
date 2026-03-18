import os
import django
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burnette_store.settings')
django.setup()

from store.models import SiteSettings

s = SiteSettings.objects.first()
if s:
    print('Logo URL:', s.logo_url)
    print('Logo File:', s.logo_file.url if s.logo_file else 'None')
    
    # Set the logo_file to the specified image
    if not s.logo_file or str(s.logo_file) != 'logos/WhatsApp_Image_2026-03-15_at_21.18.39.jpeg':
        s.logo_file = 'logos/WhatsApp_Image_2026-03-15_at_21.18.39.jpeg'
        s.save()
        print('Logo file set to:', s.logo_file.url)
    else:
        print('Logo file already set to the desired one')
else:
    print('No SiteSettings found')