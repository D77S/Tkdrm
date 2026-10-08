"""."""
import sys
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from .utils import (get_frame,
                    clean_data_first,
                    clean_data_second)

class Command(BaseCommand):
    """."""

    def handle(self, *args, **options):
        """."""

        User = get_user_model()

        # Main begin
        print('import4.py начал работу.')
        data = get_frame(
            file='_свод_инфобаза.xlsx',
            skip=2,
            sheet='Лист1'
        )
        print('Данные из Excel загружены.')
        if data.empty:
            sys.exit()
        data_2 = clean_data_first(data)
        print('Первая очистка данных прошла.')
        data_3 = clean_data_second(data_2, 4)
        print('Вторая очистка данных прошла.')
