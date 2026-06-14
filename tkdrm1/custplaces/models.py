"""."""
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class BaseCPModel(models.Model):
    title = models.CharField(
        max_length=255,
        default='Новый таможенный орган',
        unique=False,
        null=False,
        blank=False,
        verbose_name='Название'
    )
    address = models.CharField(
        max_length=255,
        default='-',
        unique=False,
        null=False,
        blank=True,
        verbose_name='Почтовый адрес'
    )
    # Признак, что данному т.о. органу разрешено
    # эксплуатировать приборы в ЗТК.
    # Имеются в виду ЗТК т.н. отдельно-существующие.
    # Не находящиеся на территории какого-либо
    # пункта пропуска, ММПО, ОЭЗ.
    ztk_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать в ЗТК'
    )
    # Признак, что данному т.о. органу разрешено
    # эксплуатировать приборы без локации.
    # Не в каком-либо ПП, ММПО, СЭЗ, ОЭЗ.
    # Рекомендуется выставить в True для:
    standalone_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=True,
        verbose_name='Признак разрешения работать без локации'
    )

    class Meta:
        abstract = True


class Rtu(BaseCPModel):
    """Модель РТУ."""

    code = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=False,
        validators=[RegexValidator(regex=r'^1\d{2}00000$')],
        verbose_name='Код т.органа'
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
        return f'{self.title}'


class CustHouse(BaseCPModel):
    """Модель таможни."""

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
                                 related_name='from_ch_to_rtu')

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
        return f'{self.title}'


class CustPost(BaseCPModel):
    """Модель таможенного поста."""

    code = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=False,
        validators=[RegexValidator(regex=r'^1\d{7}$')],
        verbose_name='Код т.органа'
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
        return f'{self.title}'


class PprType(models.Model):
    """Модель типов пунктов пропуска."""
    title = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        verbose_name='Тип пункта пропуска'
    )

    class Meta:
        """."""

        verbose_name = 'объект типа пункта пропуска'
        verbose_name_plural = 'объекты типа пунктов пропуска'

    def __str__(self):
        """."""
        return f' {self.title}'


class Ppr(models.Model):
    """Модель пункта пропуска."""

    pptype = models.ForeignKey(
        to=PprType,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Тип п. пропуска',
        related_name='from_pptype'
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
        return f'пункт(е) пропуска {self.pptype} {self.title}'


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
        return f'ММПО {self.title}'


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
        return f'ОЭЗ {self.title}'


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
        return f'ЗТК {self.title}'


class CustPlace1Acc(models.Model):
    """Модель суъекта учета (балансового либо забалансового).

    Для каждой записи (строки) строго одно поле должно быть ненулевым.
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
        temp = '{curr}'  # noqa
        if self.rtu is not None:
            return temp.format(curr=self.rtu)
        if self.custhouse is not None:
            return temp.format(curr=self.custhouse)
        return temp.format(curr=self.custpost)


class CustPlace1Use(models.Model):
    """Модель субъекта пользования.

    Для каждой записи (строки) строго одно поле должно быть ненулевым.
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

    # Вычисляемое поле.
    # Локатор на один из типов т.органов.
    @property
    def to_cp(self):
        if self.rtu:
            return self.rtu
        elif self.custhouse:
            return self.custhouse
        elif self.custpost:
            return self.custpost
        else:
            return None

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
        return f'{self.to_cp}'


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

    # Вычисляемое поле.
    # Локатор на один из типов локации пользования.
    @property
    def to_site(self):
        if self.ppr:
            return self.ppr
        elif self.mmpo:
            return self.mmpo
        elif self.oez:
            return self.oez
        elif self.ztk:
            return self.ztk
        else:
            return None

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
        return f'{self.to_site}'


class CustPlaceToLocation(models.Model):
    """Отношения между 'обобщенным объектом т.органа'
    и 'обобщенной локацией использования'.

    Примеры:
    - "Московский таможенный пост" имеет право работать в "МПП Темрюк",
    и это приоритетное место работы для поста;
    - "Самарская таможня" имеет право работать в "ММПО Кавказ",
    и это неприоритетное место работы для таможни.

    Для каждого т.органа приоритетное - не больше одного.
    """
    cust_pl1 = models.ForeignKey(to=CustPlace1Use,
                                 null=False,
                                 blank=False,
                                 on_delete=models.RESTRICT,
                                 verbose_name='т. орган_1',
                                 related_name='to_cp1')
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
                fields=['cust_pl1', 'loc'],
                name='unique_cp_loc'
            ),
            models.UniqueConstraint(
                fields=['cust_pl1',],
                condition=models.Q(is_main_for_cust=True),
                name='uniq_main_for_cp1'
            )
        ]

    def __str__(self):
        """."""
        temp = 'основное' if self.is_main_for_cust else 'вспомогательное'
        return f'{self.cust_pl1} эксплуатирует в {self.loc}, и для данного т.органа это {temp} место эксплуатации'  # noqa
