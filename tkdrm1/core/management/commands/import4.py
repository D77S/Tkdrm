"""."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from .utils import (get_frame,
                    clean_data_first)

class Command(BaseCommand):
    """."""

    def handle(self, *args, **options):
        """."""

        User = get_user_model()

        # Main begin
        data = get_frame(
            file='_свод_инфобаза.xlsx',
            skip=2,
            sheet='Лист1'
        )
        data_2 = clean_data_first(data)
