"""
WSGI config for nakliyenet project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nakliyenet.settings')

application = get_wsgi_application()
