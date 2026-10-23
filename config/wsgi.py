import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

# Carga los datos desde la API del campus antes de atender visitas.
from apps.apidata.mirror import prepare  # noqa: E402

prepare()
