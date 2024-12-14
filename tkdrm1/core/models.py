"""."""
# from django.core.exceptions import ValidationError
from django.core.validators import (MinValueValidator, MaxValueValidator,
                                    RegexValidator)
from django.db import models


class BaseModel(models.Model):
    """."""

    title = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        verbose_name='Название'
    )

    class Meta:
        abstract = True


class CustPlace(models.Model):
    """."""

    CustChoices = (('1', 'РТУ'), ('2', 'Таможня'), ('3', 'Пост'))

    title = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        verbose_name='Название'
    )
    code = models.CharField(
        max_length=8,
        unique=True,
        null=False,
        blank=False,
        validators=[RegexValidator(regex=r'^1\d{7}$')],
        verbose_name='Код т.органа'
    )
    # level = models.IntegerField(validators=[
    #     MinValueValidator(1),
    #     MaxValueValidator(3)],
    #     verbose_name='Уровень'
    #     )
    level = models.CharField(choices=CustChoices,
                             verbose_name='Уровень т.органа',
                             max_length=1,
                             null=False,
                             blank=False
                             )
    upper_id = models.ForeignKey(to="CustPlace",
                                 null=True,
                                 blank=True,
                                 on_delete=models.RESTRICT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name="to_upper_level")

    class Meta:
        verbose_name = 'Таможенный орган'
        verbose_name_plural = 'Таможенные органы'

    def __str__(self):
        """."""
        return self.title


class Rtu(BaseModel):
    """."""

    code = models.CharField(
        max_length=8,
        unique=True,
        null=False,
        blank=False,
        validators=[RegexValidator(regex=r'^1\d{2}00000$')],
        verbose_name='Код т.органа'
    )
    level = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(3)],
        default=1
        )

    class Meta:
        verbose_name = 'Региональное таможенное управление'
        verbose_name_plural = 'Региональные таможенные управления'

    def __str__(self):
        """."""
        return self.title


class CustHouse(BaseModel):
    """."""

    code = models.CharField(
        max_length=8,
        unique=True,
        null=False,
        blank=False,
        validators=[RegexValidator(regex=r'^1\d{5}000$')],
        verbose_name='Код т.органа'
    )
    level = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(3)],
        default=2,
        )
    upper_id = models.ForeignKey(to=Rtu,
                                 null=True,
                                 blank=False,
                                 on_delete=models.RESTRICT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name="cust_house_to_rtu")

    class Meta:
        verbose_name = 'Таможня'
        verbose_name_plural = 'Таможни'

    def __str__(self):
        """."""
        return self.title


class CustPost(BaseModel):
    """."""

    code = models.CharField(
        max_length=8,
        unique=True,
        null=False,
        blank=False,
        validators=[RegexValidator(regex=r'^1\d{7}$')],
        verbose_name='Код т.органа'
    )
    level = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(3)],
        default=3
        )
    upper_id = models.ForeignKey(to=CustHouse,
                                 null=True,
                                 blank=False,
                                 on_delete=models.RESTRICT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name="cust_post_to_cust_house")

    class Meta:
        verbose_name = 'Таможенный пост'
        verbose_name_plural = 'Таможенные посты'

    def __str__(self):
        """."""
        return self.title
