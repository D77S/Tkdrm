"""."""
from django.core.exceptions import ValidationError
# from django.db.models import CheckConstraint, Q
from django.core.validators import RegexValidator
from django.db import models

CUSTCHOICES = (('1', 'РТУ'), ('2', 'Таможня'), ('3', 'Пост'))


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

    def save(self, *args, **kwargs):
        temp = super().save(*args, **kwargs)
        CustPlace1.objects.create(rtu=self, custhouse=None, custpost=None)
        return temp

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
        validators=[RegexValidator(regex=r'^1\d{4}000$')],
        verbose_name='Код т.органа'
    )
    upper_id = models.ForeignKey(to=Rtu,
                                 null=False,
                                 blank=False,
                                 on_delete=models.PROTECT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name="cust_house_to_rtu")

    def save(self, *args, **kwargs):
        temp = super().save(*args, **kwargs)
        CustPlace1.objects.create(rtu=None, custhouse=self, custpost=None)
        return temp

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
                                 on_delete=models.PROTECT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name="cust_post_to_cust_house")

    def save(self, *args, **kwargs):
        temp = super().save(*args, **kwargs)
        CustPlace1.objects.create(rtu=None, custhouse=None, custpost=self)
        return temp

    class Meta:
        """."""

        verbose_name = 'Таможенный пост'
        verbose_name_plural = 'Таможенные посты'

    def __str__(self):
        """."""
        return self.title


class CustPlace1(models.Model):
    """Модель обобщенного объекта т.органа первого типа.
    Для каждой записи (строки) строго одно поле д. быть ненулевым.
    Иначе говоря, перечень валидных сочетаний полей ограничен таким:
    foo1, null, null;
    null, foo2, null;
    null, null, foo3;
    """

    rtu = models.OneToOneField(
        Rtu,
        verbose_name='Название РТУ',
        related_name='rtus',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    custhouse = models.OneToOneField(
        CustHouse,
        verbose_name='Название таможни',
        related_name='custhouses',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    custpost = models.OneToOneField(
        CustPost,
        verbose_name='Название поста',
        related_name='custposts',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )

    def delete(self, *args, **kwargs):
        temp = super().delete(*args, **kwargs)
        curr_rtu: Rtu = self.rtu
        curr_ch: CustHouse = self.custhouse
        curr_post: CustPost = self.custpost

        if curr_rtu is not None:
            curr_down_chs = CustHouse.objects.filter(upper_id=curr_rtu.id)
            if curr_down_chs.exists():
                for curr_down_ch in curr_down_chs:
                    curr_down_posts = CustPost.objects.filter(upper_id=curr_down_ch.id)  # noqa
                    if curr_down_posts.exists():
                        curr_down_posts.delete()
                curr_down_chs.delete()
            Rtu.objects.get(id=curr_rtu.id).delete()
        if curr_ch is not None:
            curr_down_posts = CustPost.objects.filter(upper_id=curr_ch.id)
            if curr_down_posts.exists():
                curr_down_posts.delete()
            CustHouse.objects.get(id=curr_ch.id).delete()
        if curr_post is not None:
            CustPost.objects.get(id=curr_post.id).delete()
        return temp

    def clean(self):
        super().clean()
        check = (((self.rtu is None) and (self.custhouse is None) and (self.custpost is not None)) or  # noqa
                 ((self.rtu is None) and (self.custhouse is not None) and (self.custpost is None)) or  # noqa
                 ((self.rtu is not None) and (self.custhouse is None) and (self.custpost is None)))  # noqa
        if not check:
            raise ValidationError('Ненулевое поле должно быть строго единственное.')  # noqa

    class Meta:
        """."""

        verbose_name = 'Обобщенный собственник первого типа'
        verbose_name_plural = 'Обобщенные собственники первого типа'

    def __str__(self):
        if self.rtu is not None:
            return self.rtu.title
        if self.custhouse is not None:
            return self.custhouse.title
        return self.custpost.title


class CustPlace2(models.Model):
    """Модель обобщенного объекта т.органа второго типа."""

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
    upper_id = models.ForeignKey(to="CustPlace2",
                                 null=True,
                                 blank=True,
                                 on_delete=models.RESTRICT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name="to_upper_level")

    class Meta:
        """."""

        verbose_name = 'Обобщенный объект т.органа второго типа'
        verbose_name_plural = 'Обобщенные объекты т.органа второго типа'

    def __str__(self):
        """."""
        return self.title


class RosgrTypes(models.Model):
    """Модель типов собственничества Росгранстроя."""

    pass


class Owner(models.Model):
    """Модель обобщенных объектов
    источников собственности.
    Для каждой записи (строки):
    строго одно поле должно быть ненулевым.
    Первые два поля идут 'единой парой' на период отладки
    и должны быть совместно либо оба нулевые, либо оба нет.
    Из них будет потом выбрано только одно какое-то.
    Иначе говоря, перечень валидных сочетаний полей ограничен таким:
    foo1, foo2, null;
    null, null, foo3;
    """

    custplace1 = models.OneToOneField(
        CustPlace1,
        verbose_name='Собственник типа <т.орган первого типа>',
        related_name='custplaces1',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    custplace2 = models.OneToOneField(
        CustPlace2,
        verbose_name='Собственник типа <т.орган второго типа>',
        related_name='custplaces2',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    rosgranstroy = models.ForeignKey(
        RosgrTypes,
        verbose_name='Собственник типа <Росгранстрой какого-то типа передачи>',  # noqa
        related_name='rosgrs',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        """."""

        verbose_name = 'Обобщенный объект собственника'
        verbose_name_plural = 'Обобщенные объекты собственника'

    def __str__(self):
        """."""
        return self.title


class Device(models.Model):
    """."""

    owner1 = models.ForeignKey(to=CustPlace1,
                               null=False,
                               blank=False,
                               on_delete=models.RESTRICT,
                               verbose_name='Собственник первого типа',
                               related_name='device_to_owner1')
    owner2 = models.ForeignKey(to=CustPlace2,
                               null=False,
                               blank=False,
                               on_delete=models.RESTRICT,
                               verbose_name='Собственник второго типа',
                               related_name='device_to_owner2')

    class Meta:
        """."""

        verbose_name = 'Техническое средство'
        verbose_name_plural = 'Технические средства'

    def __str__(self):
        """."""
        return f'Объект прибора с id={self.id}'
