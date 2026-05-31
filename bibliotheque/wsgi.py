import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotheque.settings_prod')

application = get_wsgi_application()
