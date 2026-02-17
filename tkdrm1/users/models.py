from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import CustPlace1Use


class Departments(models.Model):
    """Отделы т.органов, в которых числятся юзеры."""

    title = models.CharField(
        max_length=255,
        default='Новый отдел',
        unique=True,
        null=False,
        blank=False,
        verbose_name='Название отдела т.органа'
    )

    class Meta:
        """."""

        verbose_name = 'Отдел т.органа'
        verbose_name_plural = 'Отделы т.органа'

    def __str__(self):
        """."""
        return f'отдел: {self.title}'


class TKDRMUser(AbstractUser):
    """Юзеры проекта."""

    pater_name = models.CharField(
        max_length=255,
        unique=False,
        null=True,
        blank=True,
        verbose_name='Отчество'
    )
    empl = models.ForeignKey(
        to=CustPlace1Use,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Т.орган, в котором числится',
        related_name='from_place_to_user'
    )
    dept = models.ForeignKey(
        to=Departments,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Отдел т.органа, в к-м числится',
        related_name='from_dept_to_user'
    )

    class Meta:
        """."""

        verbose_name = 'Юзер'
        verbose_name_plural = 'Юзеры'
        constraints = [
            models.UniqueConstraint(
                fields=['empl', 'dept'],
                name='unique_empl_dept'
            )
        ]

    def __str__(self):
        """."""
        return f'объект юзера с id={self.id}'
