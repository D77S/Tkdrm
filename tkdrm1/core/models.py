"""."""
# from django.core.exceptions import ValidationError
from django.core.validators import (MinValueValidator, MaxValueValidator,
                                    RegexValidator)
from django.db import models


class Keepers(models.Model):
    """."""

    code = models.IntegerField(
        unique=True,
        null=False,
        blank=False,
        validators=[RegexValidator(regex=r'^1\d{8}$')]
    )
    title = models.CharField(
        max_length=255,
        unique=True,
        null=False
    )
    level = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(3)
        ])
    upper_id = models.ForeignKey(to="Keepers",
                                 null=True,
                                 blank=False,
                                 on_delete=models.RESTRICT,
                                 related_name="keepers_from_prev")

    def __str__(self):
        """."""
        return self.name
