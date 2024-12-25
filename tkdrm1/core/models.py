"""."""
# from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

CUSTCHOICES = (('1', 'РТУ'), ('2', 'Таможня'), ('3', 'Пост'))


class CustPlace(models.Model):
    """."""

    title = models.CharField(
        max_length=255,
        unique=False,  # !!!!!!
        null=True,
        verbose_name='Название'
    )
    code = models.CharField(
       max_length=8,
       unique=True,
       null=True,
       blank=False,
       validators=[RegexValidator(regex=r'^1\d{7}$')],
       verbose_name='Код т.органа'
    )
    level = models.CharField(choices=CUSTCHOICES,
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
        """."""

        verbose_name = 'Таможенный орган'
        verbose_name_plural = 'Таможенные органы'

    def __str__(self):
        """."""
        return self.title


class Rtu(models.Model):
    """."""

    title = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        verbose_name='Название'
    )
    code = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=False,
        validators=[RegexValidator(regex=r'^1\d{2}00000$')],
        verbose_name='Код т.органа'
    )

    class Meta:
        """."""

        verbose_name = 'Региональное таможенное управление'
        verbose_name_plural = 'Региональные таможенные управления'

    def __str__(self):
        """."""
        return self.title


class CustHouse(models.Model):
    """."""

    title = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=False,
        verbose_name='Название'
    )
    code = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=False,
        validators=[RegexValidator(regex=r'^1\d{5}000$')],
        verbose_name='Код т.органа'
    )
    upper_id = models.ForeignKey(to=Rtu,
                                 null=False,
                                 blank=False,
                                 on_delete=models.RESTRICT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name="cust_house_to_rtu")

    class Meta:
        """."""

        verbose_name = 'Таможня'
        verbose_name_plural = 'Таможни'

    def __str__(self):
        """."""
        return self.title


class CustPost(models.Model):
    """."""

    title = models.CharField(
        max_length=255,
        unique=False,  # !!!!!!
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
    upper_id = models.ForeignKey(to=CustHouse,
                                 null=True,
                                 blank=False,
                                 on_delete=models.RESTRICT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name="cust_post_to_cust_house")

    class Meta:
        """."""

        verbose_name = 'Таможенный пост'
        verbose_name_plural = 'Таможенные посты'

    def __str__(self):
        """."""
        return self.title


class Owner(models.Model):
    """."""

    rtu = models.OneToOneField(
        Rtu,
        related_name='rtus',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    custhouse = models.OneToOneField(
        CustHouse,
        related_name='custhouses',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    custpost = models.OneToOneField(
        CustPost,
        related_name='custposts',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )


class Device(models.Model):
    """."""

    owner = models.ForeignKey(to=Owner,
                              null=False,
                              blank=False,
                              on_delete=models.RESTRICT,
                              verbose_name='Собственник',
                              related_name="cust_post_to_cust_house")

    def __str__(self):
        """."""
        return f'Объект прибора с id={self.id}'
