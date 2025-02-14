from django.db import models
from django.core.exceptions import ValidationError
from core.constants import PPTYPESCHOICES


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
        verbose_name='Код т.органа'
    )
    ztk_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать в ЗТК'
    )
    standalone_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать без локации'
    )

    def save(self, *args, **kwargs):
        """Создание нового РТУ.

        Для него также создается объект модели 'субъект учета'."""
        temp = super().save(*args, **kwargs)
        CustPlace1Use.objects.get_or_create(
            rtu=self,
            custhouse=None,
            custpost=None
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
        verbose_name='Код т.органа'
    )
    ztk_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать в ЗТК'
    )
    standalone_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать без локации'
    )
    upper_id = models.ForeignKey(to=Rtu,
                                 null=False,
                                 blank=False,
                                 on_delete=models.PROTECT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name="cust_house_to_rtu")

    def save(self, *args, **kwargs):
        """Создание новой таможня.

        Для нее также создается объект модели 'субъект учета'."""
        temp = super().save(*args, **kwargs)
        CustPlace1Use.objects.get_or_create(
            rtu=None,
            custhouse=self,
            custpost=None
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
        verbose_name='Код т.органа'
    )
    ztk_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать в ЗТК'
    )
    standalone_allowed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Признак разрешения работать без локации'
    )
    upper_id = models.ForeignKey(to=CustHouse,
                                 null=True,
                                 blank=False,
                                 on_delete=models.PROTECT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name='cust_post_to_cust_house')

    def save(self, *args, **kwargs):
        """Создание нового поста.

        В случае, если все условия:
        - вышестоящая таможня поста имеет имя 'ТНП';
        - вышестоящее этой таможне РТУ имеет имя 'ТНП'
        то только для такого поста также создается
        объект модели 'субъект учета'."""
        temp = super().save(*args, **kwargs)
        CustPlace1Use.objects.get_or_create(
            rtu=None,
            custhouse=None,
            custpost=self
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
        LocationOfUse.objects.get_or_create(
            ppr=self,
            mmpo=None,
            oez=None,
            ztk=None
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
        LocationOfUse.objects.get_or_create(
            ppr=None,
            mmpo=self,
            oez=None,
            ztk=None
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
        LocationOfUse.objects.get_or_create(
            ppr=None,
            mmpo=None,
            oez=self,
            ztk=None
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
        LocationOfUse.objects.get_or_create(
            ppr=None,
            mmpo=None,
            oez=None,
            ztk=self
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
        temp = 'субъект эксплуатации для таможенного органа 1-го типа, такого названия: {curr}'  # noqa
        if self.rtu is not None:
            return temp.format(curr=self.rtu)
        if self.custhouse is not None:
            return temp.format(curr=self.custhouse)
        return temp.format(curr=self.custpost)


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
    custplaces = models.ManyToManyField(  # !!!!!!!!!!!!!!!!!!!!!
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
    loc = models.ForeignKey(to=LocationOfUse,
                            null=False,
                            blank=False,
                            on_delete=models.RESTRICT,
                            verbose_name='локация',
                            related_name='to_location')
    is_main = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name='Флаг приоритетности'
    )

    class Meta:
        """."""

        verbose_name = 'Отношение т.органа к локации эксплуатации'
        verbose_name_plural = 'Отношения т.органа к локации эксплуатации'
        constraints = [
            models.UniqueConstraint(
                fields=['cust_pl1', 'cust_pl2', 'loc'],
                name='unique_cp1_cp2_loc'
            ),
            # !!!!!!!!!!!!!!!!! сюда надо констрейт
            #  Он должен разрешать создавать объект данной модели,
            #  только в том случае, если верно условие:
            #      ЕСЛИ поле loc ссылается на объект модели LocationOfUse,
            #          в котором поле ztk не является Null и ссылается на какой-то любой объект модели Ztk,  # noqa
            #      И ПРИ ЭТОМ поле cust_pl1 ссылается на объект модели CustPlace1Use,  # noqa
            #          в котором одно (и оно всего только одно) из полей rtu, customhouse, custompost  # noqa
            #          ссылается на какой-то любой объект одной из моделей (Rtu, CustomHouse, CustomPost),  # noqa
            #          в котором поле ztk_allowed == False,
            #      ТО ЗАПРЕТИТЬ СОЗДАНИЕ НОВОГО ОБЪЕКТА ДАННОЙ МОДЕЛИ CustPlaceToLocation  # noqa
        ]

    def __str__(self):
        """."""
        temp = 'Отношение т.органа 1-го типа {curr1} к '\
               'локации эксплуатации {curr3}, с флагом приоритетности, равным {curr4}'  # noqa
        return temp.format(
            curr1=self.cust_pl1,

            curr3=self.loc,
            curr4=self.is_main
        )
