import os
import datetime
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tkdrm1.settings')
django.setup()

from django.utils import timezone  # noqa
from core.models import Device  # noqa
from core.constants import DOING1  # noqa

print(Device.objects.all())
