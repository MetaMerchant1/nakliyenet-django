#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Create/update superuser for ekremmozcan@gmail.com
python manage.py shell <<EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='ekremmozcan').exists():
    User.objects.create_superuser('ekremmozcan', 'ekremmozcan@gmail.com', 'admin123')
    print('✓ Superuser created: ekremmozcan@gmail.com')
else:
    # Update password if user exists
    u = User.objects.get(username='ekremmozcan')
    u.set_password('admin123')
    u.email = 'ekremmozcan@gmail.com'
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print('✓ Superuser updated: ekremmozcan@gmail.com')
EOF

# Update Django Site domain for sitemap
python manage.py shell <<EOF
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'nakliyenet.com'
site.name = 'NAKLIYE NET'
site.save()
print('✓ Site domain updated: nakliyenet.com')
EOF
