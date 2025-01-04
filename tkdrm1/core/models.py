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
        return f'РТУ: {self.title}'


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
        return f'таможня: {self.title}'


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
        return f'пост: {self.title}'


class CustPlace1(models.Model):
    """Модель объекта т.органа первого типа.
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

    def save(self, *args, **kwargs):
        temp = super().save(*args, **kwargs)
        Owner.objects.create(custplace1=self)
        return temp

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

        verbose_name = 'Т.орган первого типа'
        verbose_name_plural = 'Т.органы первого типа'

    def __str__(self):
        """."""
        temp = 'таможенный орган 1-го типа, являющийся: {curr}'
        if self.rtu is not None:
            return temp.format(curr=self.rtu)
        if self.custhouse is not None:
            return temp.format(curr=self.custhouse)
        return temp.format(curr=self.custpost)


class CustPlace2(models.Model):
    """Модель объекта т.органа второго типа."""

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

    def save(self, *args, **kwargs):
        temp = super().save(*args, **kwargs)
        Owner.objects.create(custplace2=self)
        return temp

    class Meta:
        """."""

        verbose_name = 'Т.орган второго типа'
        verbose_name_plural = 'Т.органы второго типа'

    def __str__(self):
        """."""
        return f'таможенный орган 2-го типа, {self.level}-го уровня, являющийся: {self.title}'  # noqa


class OtherTypes(models.Model):
    """Модель иных типов источников имущества."""

    title = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        verbose_name='Тип источника имущества'
    )

    def save(self, *args, **kwargs):
        temp = super().save(*args, **kwargs)
        Owner.objects.create(other=self)
        return temp

    class Meta:
        """."""

        verbose_name = 'Иной источник получения имущества'
        verbose_name_plural = 'Иные источники получения имущества'

    def __str__(self):
        """."""
        return f'иной источник, являющийся: {self.title}'


class Owner(models.Model):
    """Модель субъектов учета т.с.
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
        verbose_name='Субъект учета типа <т.орган первого типа>',
        related_name='custplaces1',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    custplace2 = models.OneToOneField(
        CustPlace2,
        verbose_name='Субъект учета типа <т.орган второго типа>',
        related_name='custplaces2',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    other = models.OneToOneField(
        OtherTypes,
        verbose_name='Субъект учета типа <иной тип>',  # noqa
        related_name='others',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )

    def delete(self, *args, **kwargs):
        temp = super().delete(*args, **kwargs)
        curr_custplace1 = self.custplace1
        curr_custplace2 = self.custplace2
        curr_other = self.other
        if curr_custplace1 is not None:
            CustPlace1.objects.get(id=curr_custplace1.id).delete()
        if curr_custplace2 is not None:
            CustPlace2.objects.get(id=curr_custplace2.id).delete()
        if curr_other is not None:
            OtherTypes.objects.get(id=curr_other.id).delete()
        return temp

    def clean(self):
        super().clean()
        check = (((self.custplace1 is None) and (self.custplace2 is None) and (self.other is not None)) or  # noqa
                 ((self.custplace1 is not None) and (self.custplace2 is not None) and (self.other is None)))  # noqa
        if not check:
            raise ValidationError('Ненулевое поле должно быть либо только последнее, либо только два первых.')  # noqa

    class Meta:
        """."""

        verbose_name = 'Субъект учета т.с.'
        verbose_name_plural = 'Субъект учета т.с.'

    def __str__(self):
        """."""
        temp = 'субъект учета т.с., являющийся: {curr}'
        if self.custplace1 is not None:
            return temp.format(curr=self.custplace1)
        if self.custplace2 is not None:
            return temp.format(curr=self.custplace2)
        return temp.format(curr=self.other)


class Device(models.Model):
    """."""

    pass

    class Meta:
        """."""

        verbose_name = 'Техническое средство'
        verbose_name_plural = 'Технические средства'

    def __str__(self):
        """."""
        return f'Объект прибора с id={self.id}'
