"""."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """."""

    User = get_user_model()

    # Main begin
    data = get_frame()