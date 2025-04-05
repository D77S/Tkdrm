"""."""
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from core.constants import CUSTCHOICES, PPTYPESCHOICES, SERIAL_NUM_CHOICES


class Rtu(models.Model):
    """Модель РТУ."""

    title = models.CharField(
        max_length=255,
        default='Новое РТУ',
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
    ztk_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать в ЗТК'
        # Имеются в виду ЗТК т.н. отдельно-существующие.
        # Не находящиеся на территории какого-либо
        # пункта пропуска, ММПО, ОЭЗ.
    )
    standalone_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать без локации'
        # Для т.н. внутренних постов устанавливается в True
    )

    def save(self, *args, **kwargs):
        """Сохранение нового РТУ.

        Для него также создается/апдейтится объект модели 'субъект учета'."""
        temp = super().save(*args, **kwargs)
        CustPlace1Acc.objects.update_or_create(
            rtu=self,
            defaults={
                'custhouse': None,
                'custpost': None,
            }
        )
        CustPlace1Use.objects.update_or_create(
            rtu=self,
            defaults={
                'custhouse': None,
                'custpost': None,
                'ztk_allowed': self.ztk_allowed,
                'standalone_allowed': self.standalone_allowed
            }
        )
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'Региональное таможенное управление'
        verbose_name_plural = 'Региональные таможенные управления'

    def __str__(self):
        """."""
        return f'РТУ: {self.title}'


class CustHouse(models.Model):
    """Модель таможни."""

    title = models.CharField(
        max_length=255,
        default='Новая таможня',
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
        validators=[RegexValidator(regex=r'^1\d{4}000$')],
        verbose_name='Код т.органа'
    )
    ztk_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать в ЗТК'
        # Имеются в виду ЗТК т.н. отдельно-существующие.
        # Не находящиеся на территории какого-либо
        # пункта пропуска, ММПО, ОЭЗ.
    )
    standalone_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать без локации'
        # Для т.н. внутренних постов устанавливается в True
    )
    upper_id = models.ForeignKey(to=Rtu,
                                 null=False,
                                 blank=False,
                                 on_delete=models.PROTECT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name="cust_house_to_rtu")

    def save(self, *args, **kwargs):
        """Сохранение новой таможни.

        Для нее также создается/апдейтится объект модели 'субъект учета'."""
        temp = super().save(*args, **kwargs)
        CustPlace1Acc.objects.update_or_create(
            custhouse=self,
            defaults={
                'rtu': None,
                'custpost': None,
            }
        )
        CustPlace1Use.objects.update_or_create(
            custhouse=self,
            defaults={
                'rtu': None,
                'custpost': None,
                'ztk_allowed': self.ztk_allowed,
                'standalone_allowed': self.standalone_allowed
            }
        )
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'Таможня'
        verbose_name_plural = 'Таможни'

    def __str__(self):
        """."""
        return f'таможня: {self.title}'


class CustPost(models.Model):
    """Модель таможенного поста."""

    title = models.CharField(
        max_length=255,
        default='Новый пост',
        unique=False,  # !!!!!!
        null=False,
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
    ztk_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать в ЗТК'
        # Имеются в виду ЗТК т.н. отдельно-существующие.
        # Не находящиеся на территории какого-либо
        # пункта пропуска, ММПО, ОЭЗ.
    )
    standalone_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать без локации'
        # Для т.н. внутренних постов устанавливается в True
    )
    upper_id = models.ForeignKey(to=CustHouse,
                                 null=True,
                                 blank=False,
                                 on_delete=models.PROTECT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name='cust_post_to_cust_house')

    def save(self, *args, **kwargs):
        """Сохранение нового поста.

        В случае, если все условия:
        - вышестоящая таможня поста имеет имя 'ТНП';
        - вышестоящее этой таможне РТУ имеет имя 'ТНП'
        то только для такого поста также создается/апдейтится
        объект модели 'субъект учета'."""
        temp = super().save(*args, **kwargs)
        upper_ch = self.upper_id
        if upper_ch:
            upper_rtu = upper_ch.upper_id
        if upper_ch and upper_ch.title == 'ТНП' and upper_rtu and upper_rtu.title == 'ТНП':  # noqa
            CustPlace1Acc.objects.update_or_create(
                custpost=self,
                defaults={
                    'rtu': None,
                    'custhouse': None,
                }
            )
        CustPlace1Use.objects.update_or_create(
            custpost=self,
            defaults={
                'rtu': None,
                'custhouse': None,
                'ztk_allowed': self.ztk_allowed,
                'standalone_allowed': self.standalone_allowed
            }
        )
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'Таможенный пост'
        verbose_name_plural = 'Таможенные посты'

    def __str__(self):
        """."""
        return f'пост: {self.title}'


class Ppr(models.Model):
    """Модель пункта пропуска."""

    pptype = models.CharField(choices=PPTYPESCHOICES,
                              verbose_name='Тип п. пропуска',
                              max_length=1,
                              null=False,
                              blank=False
                              )
    title = models.CharField(
        max_length=255,
        unique=False,  # !!!!!!
        null=False,
        verbose_name='Название'
    )
    tow_country = models.CharField(
        max_length=255,
        unique=False,  # !!!!!!
        null=True,
        verbose_name='Сопредельное государство'
    )

    def save(self, *args, **kwargs):
        """Создание нового пункта пропуска.

        Для него также создается объект модели локации."""
        temp = super().save(*args, **kwargs)
        LocationOfUse.objects.update_or_create(
            ppr=self,
            defaults={
                'mmpo': None,
                'oez': None,
                'ztk': None,
                'is_ztk': False
            }
        )
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'объект пункта пропуска'
        verbose_name_plural = 'объекты пунктов пропуска'
        constraints = [
            models.UniqueConstraint(
                fields=['pptype', 'title', 'tow_country'],
                name='unique_type_title'
            ),
        ]

    def __str__(self):
        """."""
        return f'пункт пропуска: {self.title}'


class Mmpo(models.Model):
    """Модель ММПО"""

    title = models.CharField(
        max_length=255,
        unique=True,  # !!!!!!
        null=False,
        verbose_name='Название'
    )

    def save(self, *args, **kwargs):
        """Создание нового ММПО.

        Для него также создается объект модели локации."""
        temp = super().save(*args, **kwargs)
        LocationOfUse.objects.update_or_create(
            mmpo=self,
            defaults={
                'ppr': None,
                'oez': None,
                'ztk': None,
                'is_ztk': False
            }
        )
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'объект ММПО'
        verbose_name_plural = 'объекты ММПО'
        constraints = [
            models.UniqueConstraint(
                fields=['title',],
                name='unique_mmpo_title'
            ),
        ]

    def __str__(self):
        """."""
        return f'ММПО: {self.title}'


class Oez(models.Model):
    """Модель Особой Экономической Зоны"""

    title = models.CharField(
        max_length=255,
        unique=True,  # !!!!!!
        null=False,
        verbose_name='Название'
    )

    def save(self, *args, **kwargs):
        """Создание новой ОЭЗ.

        Для нее также создается объект модели локации."""
        temp = super().save(*args, **kwargs)
        LocationOfUse.objects.update_or_create(
            oez=self,
            defaults={
                'ppr': None,
                'mmpo': None,
                'ztk': None,
                'is_ztk': False
            }
        )
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'объект ОЭЗ'
        verbose_name_plural = 'объекты ОЭЗ'
        constraints = [
            models.UniqueConstraint(
                fields=['title',],
                name='unique_oez_title'
            ),
        ]

    def __str__(self):
        """."""
        return f'ОЭЗ: {self.title}'


class Ztk(models.Model):
    """Модель Зоны Таможенного Контроля"""

    title = models.CharField(
        max_length=255,
        unique=True,  # !!!!!!
        null=False,
        verbose_name='Название'
    )

    def save(self, *args, **kwargs):
        """Создание новой ЗТК.

        Для нее также создается объект модели локации."""
        temp = super().save(*args, **kwargs)
        LocationOfUse.objects.update_or_create(
            ztk=self,
            defaults={
                'ppr': None,
                'mmpo': None,
                'oez': None,
                'is_ztk': True
            }
        )
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'объект ЗТК'
        verbose_name_plural = 'объекты ЗТК'
        constraints = [
            models.UniqueConstraint(
                fields=['title',],
                name='unique_ztk_title'
            ),
        ]

    def __str__(self):
        """."""
        return f'ЗТК: {self.title}'


class CustPlace1Acc(models.Model):
    """Модель суъекта учета (балансового либо забалансового).

    Для объектов таможенных органов 1-го типа.
    Для каждой записи (строки) строго одно поле д. быть ненулевым.
    Иначе говоря, перечень валидных сочетаний полей ограничен таким:
    foo1, null, null;
    null, foo2, null;
    null, null, foo3.

    Вариант (null, null, foo3) допустим ТОЛЬКО если по объекту foo3
    для ОБОИХ уровней его вышестоящих объектов поля title равны "ТНП".
    """
    # https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/
    rtu = models.OneToOneField(
        Rtu,
        verbose_name='Название РТУ',
        related_name='rtus1acc',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    custhouse = models.OneToOneField(
        CustHouse,
        verbose_name='Название таможни',
        related_name='cs1acc',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    custpost = models.OneToOneField(
        CustPost,
        verbose_name='Название поста',
        related_name='posts1acc',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )

    def delete(self, *args, **kwargs):
        """."""
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
        return temp  # noqa

    def clean(self):
        """."""
        temp = super().clean()
        curr_rtu: Rtu = self.rtu
        curr_ch: CustHouse = self.custhouse
        curr_post: CustPost = self.custpost
        check1 = (((curr_rtu is None) and (curr_ch is None) and (curr_post is not None)) or  # noqa
                 ((curr_rtu is None) and (curr_ch is not None) and (curr_post is None)) or  # noqa
                 ((curr_rtu is not None) and (curr_ch is None) and (curr_post is None)))  # noqa
        check2 = ((curr_post is None) or
                 ((curr_post is not None) and (curr_ch.title == 'ТНП') and (curr_rtu.title == 'ТНП')))  # noqa
        if not check1:
            raise ValidationError('Ненулевое поле должно быть строго единственное.')  # noqa
        if not check2:
            raise ValidationError('Поле \'пост\' может быть ненулевым только для ТНП-ТНП-постов')  # noqa
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'Субъект учета для т.органа 1-го типа'
        verbose_name_plural = 'Субъекты учета для т.органа 1-го типа'
        constraints = [
            models.CheckConstraint(
                check=(models.Q(rtu__isnull=True) &
                       models.Q(custhouse__isnull=True) &
                       ~models.Q(custpost__isnull=True)) |
                (models.Q(rtu__isnull=True) &
                 ~models.Q(custhouse__isnull=True) &
                 models.Q(custpost__isnull=True)) |
                (~models.Q(rtu__isnull=True) &
                 models.Q(custhouse__isnull=True) &
                 models.Q(custpost__isnull=True)),
                name='CP1AccNullable'
            ),
        ]

    def __str__(self):
        """."""
        temp = 'субъект учета для таможенного органа 1-го типа, такого названия: {curr}'  # noqa
        if self.rtu is not None:
            return temp.format(curr=self.rtu)
        if self.custhouse is not None:
            return temp.format(curr=self.custhouse)
        return temp.format(curr=self.custpost)


class CustPlace1Use(models.Model):
    """Модель субъекта пользования.

    Для объектов таможенных органов 1-го типа.
    Для каждой записи (строки) строго одно поле д. быть ненулевым.
    Иначе говоря, перечень валидных сочетаний полей ограничен таким:
    foo1, null, null;
    null, foo2, null;
    null, null, foo3.
    """
    # https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/
    rtu = models.OneToOneField(
        Rtu,
        verbose_name='Название РТУ',
        related_name='rtus1use',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    custhouse = models.OneToOneField(
        CustHouse,
        verbose_name='Название таможни',
        related_name='cs1use',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    custpost = models.OneToOneField(
        CustPost,
        verbose_name='Название поста',
        related_name='posts1use',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    ztk_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать в ЗТК'
        # Имеются в виду ЗТК т.н. отдельно-существующие.
        # Не находящиеся на территории какого-либо
        # пункта пропуска, ММПО, ОЭЗ.
    )
    standalone_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать без локации'
        # Для т.н. внутренних постов устанавливается в True
    )

    def delete(self, *args, **kwargs):
        """."""
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
        return temp  # noqa

    def clean(self):
        """."""
        temp = super().clean()
        curr_rtu: Rtu = self.rtu
        curr_ch: CustHouse = self.custhouse
        curr_post: CustPost = self.custpost
        check1 = (((curr_rtu is None) and (curr_ch is None) and (curr_post is not None)) or  # noqa
                 ((curr_rtu is None) and (curr_ch is not None) and (curr_post is None)) or  # noqa
                 ((curr_rtu is not None) and (curr_ch is None) and (curr_post is None)))  # noqa
        if not check1:
            raise ValidationError('Ненулевое поле должно быть строго единственное.')  # noqa
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'Субъект эксплуатации для т.органа 1-го типа'
        verbose_name_plural = 'Субъекты эксплуатации для т.органа 1-го типа'
        constraints = [
            models.CheckConstraint(
                check=(models.Q(rtu__isnull=True) &
                       models.Q(custhouse__isnull=True) &
                       ~models.Q(custpost__isnull=True)) |
                (models.Q(rtu__isnull=True) &
                 ~models.Q(custhouse__isnull=True) &
                 models.Q(custpost__isnull=True)) |
                (~models.Q(rtu__isnull=True) &
                 models.Q(custhouse__isnull=True) &
                 models.Q(custpost__isnull=True)),
                name='CP1UseNullable'
            ),
        ]

    def __str__(self):
        """."""
        return f'промежутка с id={self.id}'


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
    upper_id = models.ForeignKey(to='CustPlace2',
                                 null=True,
                                 blank=True,
                                 on_delete=models.RESTRICT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name='to_upper_level')
    ztk_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать в ЗТК'
        # Имеются в виду ЗТК т.н. отдельно-существующие.
        # Не находящиеся на территории какого-либо
        # пункта пропуска, ММПО, ОЭЗ.
    )
    standalone_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать без локации'
        # Для т.н. внутренних постов устанавливается в True
    )

    def save(self, *args, **kwargs):
        """."""
        temp = super().save(*args, **kwargs)
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'Т.орган второго типа'
        verbose_name_plural = 'Т.органы второго типа'

    def __str__(self):
        """."""
        return f'таможенный орган 2-го типа, {self.level}-го уровня, являющийся: {self.title}'  # noqa


class SourceTypes(models.Model):
    """Модель типов источников имущества."""

    title = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        verbose_name='Тип источника имущества'
    )

    def save(self, *args, **kwargs):
        """."""
        temp = super().save(*args, **kwargs)
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'Источник получения имущества'
        verbose_name_plural = 'Источники получения имущества'

    def __str__(self):
        """."""
        return f'источник, являющийся: {self.title}'


class LocationOfUse(models.Model):
    """Модель локации пользования.

    Для каждой записи (строки) строго одно поле д. быть ненулевым.
    Иначе говоря, перечень валидных сочетаний полей ограничен таким:
    foo1, null, null, null;
    null, foo2, null, null;
    null, null, foo3, null;
    null, null, null, foo4.
    """
    # https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/
    ppr = models.OneToOneField(
        Ppr,
        verbose_name='Название п.пропуска',
        related_name='pprs',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    mmpo = models.OneToOneField(
        Mmpo,
        verbose_name='Название ММПО',
        related_name='mmpos',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    oez = models.OneToOneField(
        Oez,
        verbose_name='Название ОЭЗ',
        related_name='oezs',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    ztk = models.OneToOneField(
        Ztk,
        verbose_name='Название ЗТК',
        related_name='ztks',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    is_ztk = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Является ли ЗТК'
    )
    #  !!!!!!!!!
    #  M2M только на т.орган первого типа!!!
    #  Если в прод пойдет отсылка к т.органу второго типа,
    #  то исправить тут поле.
    custplaces = models.ManyToManyField(
        CustPlace1Use,
        through='CustPlaceToLocation'
    )

    def delete(self, *args, **kwargs):
        """."""
        temp = super().delete(*args, **kwargs)
        if self.ppr:
            Ppr.objects.get(id=self.ppr.id).delete()
        if self.mmpo:
            Mmpo.objects.get(id=self.mmpo.id).delete()
        if self.oez:
            Oez.objects.get(id=self.oez.id).delete()
        if self.ztk:
            Ztk.objects.get(id=self.ztk.id).delete()
        return temp  # noqa

    def clean(self):
        """."""
        temp = super().clean()
        curr_ppr: Ppr = self.ppr
        curr_mmpo: Mmpo = self.mmpo
        curr_oez: Oez = self.oez
        curr_ztk: Ztk = self.ztk
        check = (((curr_ppr is None) and (curr_mmpo is None) and (curr_oez is None) and (curr_ztk is not None)) or  # noqa
                  ((curr_ppr is None) and (curr_mmpo is None) and (curr_oez is not None) and (curr_ztk is None)) or  # noqa
                  ((curr_ppr is None) and (curr_mmpo is not None) and (curr_oez is None) and (curr_ztk is None)) or  # noqa
                  ((curr_ppr is not None) and (curr_mmpo is None) and (curr_oez is None) and (curr_ztk is None)))  # noqa
        if not check:
            raise ValidationError('Ненулевое поле должно быть строго единственное.')  # noqa
        return temp  # noqa

    class Meta:
        """."""

        verbose_name = 'объект локации'
        verbose_name_plural = 'объекты локации'
        constraints = [
            models.CheckConstraint(
                check=(models.Q(ppr__isnull=True) &
                       models.Q(mmpo__isnull=True) &
                       models.Q(oez__isnull=True) &
                       ~models.Q(ztk__isnull=True)) |
                (models.Q(ppr__isnull=True) &
                 models.Q(mmpo__isnull=True) &
                 ~models.Q(oez__isnull=True) &
                 models.Q(ztk__isnull=True)) |
                (models.Q(ppr__isnull=True) &
                 ~models.Q(mmpo__isnull=True) &
                 models.Q(oez__isnull=True) &
                 models.Q(ztk__isnull=True)) |
                (~models.Q(ppr__isnull=True) &
                 models.Q(mmpo__isnull=True) &
                 models.Q(oez__isnull=True) &
                 models.Q(ztk__isnull=True)),
                name='Loc_Nullable'
            ),
        ]

    def __str__(self):
        """."""
        temp = 'объект локации такого названия: {curr}'  # noqa
        if self.ppr is not None:
            return temp.format(curr=self.ppr)
        if self.mmpo is not None:
            return temp.format(curr=self.mmpo)
        if self.oez is not None:
            return temp.format(curr=self.oez)
        return temp.format(curr=self.ztk)


class CustPlaceToLocation(models.Model):
    """Отношения между 'обобщенным объектом т.органа'
    и 'обобщенной локацией использования'."""
    cust_pl1 = models.ForeignKey(to=CustPlace1Use,
                                 null=False,
                                 blank=False,
                                 on_delete=models.RESTRICT,
                                 verbose_name='т. орган_1',
                                 related_name='to_cp1')
    cust_pl2 = models.ForeignKey(to=CustPlace2,
                                 null=False,
                                 blank=False,
                                 on_delete=models.RESTRICT,
                                 verbose_name='т. орган_2',
                                 related_name='to_cp2')
    loc = models.ForeignKey(to=LocationOfUse,
                            null=True,
                            blank=False,
                            on_delete=models.RESTRICT,
                            verbose_name='локация',
                            related_name='to_location')
    is_main_for_cust = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Флаг приоритетности'
    )

    def clean(self):
        """."""
        temp = super().clean()
        check1 = (models.Q(self.cust_pl1.ztk_allowed is False) &
                  models.Q(self.loc.is_ztk is True))
        check2 = (models.Q(self.cust_pl1.standalone_allowed is False) &
                  models.Q(self.loc is None))
        if check1:
            raise ValidationError('Данный т.орган не может работать в ЗТК')
        if check2:
            raise ValidationError('Данный т.орган не может работать вне какого-либо административного субъекта')  # noqa
        return temp

    class Meta:
        """."""

        verbose_name = 'Отношение т.органа к локации эксплуатации'
        verbose_name_plural = 'Отношения т.органа к локации эксплуатации'
        constraints = [
            models.UniqueConstraint(
                fields=['cust_pl1', 'cust_pl2', 'loc'],
                name='unique_cp1_cp2_loc'
            ),
            models.UniqueConstraint(
                fields=['cust_pl1',],
                condition=models.Q(is_main_for_cust=True),
                name='uniq_main_for_cp1'
            )
        ]

    def __str__(self):
        """."""
        # temp = 'Отношение т.органа 1-го типа {curr1} и 2-го типа {curr2} к '\
        #        'локации эксплуатации {curr3}, с флагом приоритетности, равным {curr4}'  # noqa
        # return temp.format(
        #     curr1=self.cust_pl1,
        #     curr2=self.cust_pl2,
        #     curr3=self.loc,
        #     curr4=self.is_main_for_cust
        # )
        return f'Модель промежутки с id= {self.id}'


class DevCats(models.Model):
    """Модель категорий типов приборов."""
    title = models.CharField(
        max_length=255,
        default='Новая категория',
        unique=True,
        null=False,
        blank=False,
        verbose_name='Название категории'
    )

    class Meta:
        """."""

        verbose_name = 'Объект категории типа прибора'
        verbose_name_plural = 'Объекты категории типов приборов'

    def __str__(self):
        """."""
        return f'категория: {self.title}'


class DevTypes(models.Model):
    """Модель типов приборов."""

    title = models.CharField(
        max_length=255,
        default='Новый прибор',
        unique=False,
        null=False,
        blank=False,
        verbose_name='Название прибора'
    )
    category = models.ForeignKey(
        to=DevCats,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Категория прибора',
        related_name='dev_cat_to_dev_type'
    )
    serial_flag = models.CharField(
        choices=SERIAL_NUM_CHOICES,
        verbose_name='Тривариантный признак сер.номера',
        max_length=1,
        null=False,
        blank=False
    )
    upper_dev_flag = models.BooleanField(
        null=False,
        default=False,
        blank=True,
        verbose_name='Признак наличия вышестоящего девайса'
    )
    sub_types = models.JSONField(
        default=list,
        unique=False,
        null=True,
        blank=True,
        verbose_name='Допустимые подтипы'
    )

    class Meta:
        """."""

        verbose_name = 'Объект типа прибора'
        verbose_name_plural = 'Объекты типов приборов'

    def __str__(self):
        """."""
        return f'прибор типа {self.title}'


class Device(models.Model):
    """Модель объекта прибора (технического средства)."""

    type = models.ForeignKey(
        to=DevTypes,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Тип прибора',
        related_name='dev_type_to_dev_obj'
    )
    serial = models.CharField(
         max_length=255,
         unique=False,
         null=True,
         blank=False,
         verbose_name='Серийный номер'
    )
    # Субъект учета по (за)балансу, 1-го типа
    cp1_acc = models.ForeignKey(to=CustPlace1Acc,
                                null=False,
                                blank=False,
                                on_delete=models.PROTECT,
                                verbose_name='Учетчик-т.о. 1-го типа',
                                related_name='cp1acc_to_dev')
    # Субъект учета по (за)балансу, 2-го типа
    cp2_acc = models.ForeignKey(to=CustPlace2,
                                null=False,
                                blank=False,
                                on_delete=models.PROTECT,
                                verbose_name='Учетчик-т.о. 2-го типа',
                                related_name='cp2acc_to_dev')
    # Источник собственности
    sour_type = models.ForeignKey(to=SourceTypes,
                                  null=False,
                                  blank=False,
                                  on_delete=models.PROTECT,
                                  verbose_name='Источник собственности',
                                  related_name='s_type_to_dev')
    # Субъект пользования
    rels_of_work = models.ManyToManyField(
        CustPlaceToLocation,
        through='RelToDev'
    )
    sub_type = models.CharField(
        max_length=255,
        default=None,
        unique=False,
        null=True,
        blank=False,
        verbose_name='Подтип'
    )
    upper_id = models.ForeignKey(to='Device',
                                 null=True,
                                 blank=True,
                                 default=None,
                                 on_delete=models.RESTRICT,
                                 verbose_name='Вышестоящий девайс',
                                 related_name='to_upper_level')

    def test2(self):
        return self.from_dev

    class Meta:
        """."""

        verbose_name = 'Техническое средство'
        verbose_name_plural = 'Технические средства'
        # constraints = [
        #     models.CheckConstraint(
        #         check=(models.Q()),
        #         name='ser_num_valid'
        #     ),
        # ]

    def __str__(self):
        """."""
        return f'Объект прибора с id={self.id}'


class RelToDev(models.Model):
    """Модель-промежутка, связь M2M между
    'отношением т. органа и места его работы'
    и 'девайса'."""
    to_rel = models.ForeignKey(to=CustPlaceToLocation,
                               null=False,
                               blank=False,
                               on_delete=models.PROTECT,
                               verbose_name='т.орган и место',  # noqa
                               related_name='from_relation')
    to_dev = models.ForeignKey(to=Device,
                               null=False,
                               blank=False,
                               on_delete=models.PROTECT,
                               verbose_name='прибор',
                               related_name='from_dev')
    is_main_for_dev = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Флаг приоритетности'
    )

    class Meta:
        """."""

        verbose_name = 'объект промежутки'
        verbose_name_plural = 'объекты промежутки'
        constraints = [
            models.UniqueConstraint(
                fields=['to_rel', 'to_dev'],
                name='unique_to_rel_to_dev'
            ),
            models.UniqueConstraint(
                fields=['to_dev',],
                condition=models.Q(is_main_for_dev=True),
                name='uniq_main_for_dev'
            )
        ]

    def __str__(self):
        """."""
        return f'Объект промежутки с id={self.id}'
