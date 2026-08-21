"""."""

from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware
from typing import Union

def real_lt(value: int) -> None:
    if value >= 240:
        raise ValidationError('Ожидается срок службы не более 240 месяцев') 

def real_date(value: Union[date, datetime]) -> None:
    if isinstance(value, date):
        if date(1990, 1, 1) <= value <= date(2100,12,31):
            return
    elif isinstance(value, datetime):
        if make_aware(datetime(1990, 1, 1, 0, 0, 0)) <= value <= make_aware(datetime(2100, 12, 31, 23, 59, 59)):
            return
    return ValidationError('Ожидается дата между 01.01.1990 и 31.12.2100')

def real_cat(value: int) -> None:
    if 1 <= value <= 4:
        return
    return ValidationError('Ожидается категория от 1 до 4')
