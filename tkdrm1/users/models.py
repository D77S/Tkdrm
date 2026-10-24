from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from custplaces.models import CustPlace1Use


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


class TKDRMUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('dept', None)
        extra_fields.setdefault('empl', None)
        return super().create_superuser(username, email, password, **extra_fields)


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
        null=True,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Т.орган, в котором числится',
        related_name='from_place_to_user'
    )
    dept = models.ForeignKey(
        to=Departments,
        null=True,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Отдел т.органа, в к-м числится',
        related_name='from_dept_to_user'
    )

    objects = TKDRMUserManager()

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

    def clean(self):
        super().clean()
        if not self.is_superuser and (self.dept is None or self.empl is None):
            raise ValidationError({
                'dept': 'Для не superuser обязательно должены быть поля empl и dept оба не Null'
            })

    def __str__(self):
        """."""
        pater_name = self.pater_name if self.pater_name else ', отчество не указано, '
        out = ' '.join([
            self.first_name,
            pater_name,
            self.last_name,
            ', ',
            self.dept.__str__(),
            ', ',
            self.empl.__str__()
        ])
        return out
