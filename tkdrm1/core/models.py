"""."""
# from django.core.exceptions import ValidationError
from django.core.validators import (MinValueValidator, MaxValueValidator,
                                    RegexValidator)
from django.db import models


class Rtu(models.Model):
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
        MaxValueValidator(3)],
        default=1
        )

    def __str__(self):
        """."""
        return self.name


class CustHouse(models.Model):
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
        MaxValueValidator(3)],
        default=2
        )
    rtu_id = models.ForeignKey(to=Rtu,
                               null=True,
                               blank=False,
                               on_delete=models.RESTRICT,
                               related_name="cust_house_to_rtu")

    def __str__(self):
        """."""
        return self.name


class CustPost(models.Model):
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
        MaxValueValidator(3)],
        default=3
        )
    cust_house_id = models.ForeignKey(to=CustHouse,
                                      null=True,
                                      blank=False,
                                      on_delete=models.RESTRICT,
                                      related_name="cust_post_to_cust_house")

    def __str__(self):
        """."""
        return self.name
