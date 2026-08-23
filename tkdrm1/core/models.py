"""."""
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
import datetime
import dateutil
from custplaces.models import (
    CustPlace1Acc,
    CustPlaceToLocation
)
from core.constants import DOING1
from users.models import TKDRMUser
from .validators import real_date, real_lt, real_cat


class SourceTypes(models.Model):
    """Модель типов источников имущества."""

    title = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        verbose_name='Тип источника имущества'
    )

    class Meta:
        """."""

        verbose_name = 'Источник получения имущества'
        verbose_name_plural = 'Источники получения имущества'

    def __str__(self):
        """."""
        return f'{self.title}'


class StatusTypes(models.Model):
    """Модель типов статуса по эксплуатации."""

    title = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        verbose_name='Тип статуса по эксплуатации'
    )

    class Meta:
        """."""

        verbose_name = 'Статус по эксплуатации'
        verbose_name_plural = 'Статусы по эксплуатации'

    def __str__(self):
        """."""
        return f'{self.title}'


class ServiceTypes(models.Model):
    """Модель видов действий с экземпляром прибора.

    Прибор на данный момент признан подвергающимя данным действиям с ним.
    Вне зависимости от субъекта действия: централизованно
    или децентрализованно.
    """

    title = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        verbose_name='Вид действий'
    )

    class Meta:
        """."""

        verbose_name = 'Вид действия'
        verbose_name_plural = 'Виды действий'

    def __str__(self):
        """."""
        return f'{self.title}'


class DevCatsL1(models.Model):
    """Модель категорий уровня 1 типов приборов."""
    title = models.CharField(
        max_length=255,
        default='Новая категория уровня 1',
        unique=True,
        null=False,
        blank=False,
        verbose_name='Название категории уровня 1'
    )

    class Meta:
        """."""

        verbose_name = 'Объект категории уровня 1 типа прибора'
        verbose_name_plural = 'Объекты категории уровня 1 типов приборов'

    def __str__(self):
        """."""
        return f'{self.title}'


class DevCatsL2(models.Model):
    """Модель категорий уровня 2 типов приборов."""
    title = models.CharField(
        max_length=255,
        default='Новая категория уровня 2',
        unique=True,
        null=False,
        blank=False,
        verbose_name='Название категории уровня 2'
    )
    cat_l1 = models.ForeignKey(
        to=DevCatsL1,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Категория уровня 2 прибора',
        related_name='dev_cat_to_dev_type'
    )

    class Meta:
        """."""

        verbose_name = 'Объект категории уровня 2 типа прибора'
        verbose_name_plural = 'Объекты категории уровня 2 типов приборов'

    def __str__(self):
        """."""
        return f'{self.title}'


class DevTypes(models.Model):
    """Модель типов приборов."""

    title = models.CharField(
        max_length=255,
        default='Новый прибора',
        unique=True,
        null=False,
        blank=False,
        verbose_name='Название прибора'
    )
    category = models.ForeignKey(
        to=DevCatsL2,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Категория прибора',
        related_name='dev_cat_to_dev_type'
    )
    lifetime = models.PositiveSmallIntegerField(
        null=False,
        unique=False,
        blank=False,
        default=2,
        validators=(real_lt,),
        verbose_name='Срок службы, мес.'
    )
    # Признак серийного номера:
    # True: он обязан быть у объекта;
    # False: его обязано не быть у объекта;
    # None: он может как быть, так и не быть.
    serial_flag = models.BooleanField(
        verbose_name='Признак сер.номера',
        default=None,
        null=True,
        blank=False
    )
    # Признак наличия у объекта вышестоящего объекта:
    # (например, видеокамера имеет вышестоящий объект: Янтарь)
    # True: все девайсы данного типа обязаны его иметь;
    # False: все девайсы данного типа обязаны его не иметь;
    # None: все девайсы данного типа могут как иметь, так и не иметь его.
    upper_dev_flag = models.BooleanField(
        null=True,
        default=False,
        blank=True,
        verbose_name='Признак наличия вышестоящего девайса'
    )
    # Признак принадлежности к СИ или инд.
    # True: все девайсы данного типа обязаны быть либо СИ, либо инд;
    # False: все девайсы данного типа обязаны не быть ни СИ, ни инд;
    # None: девайсы данного типа могут как иметь, так и не иметь его
    # (могут быть либо СИ, либо инд, либо ни тем ни другим).
    si_flag = models.BooleanField(
        null=True,
        default=False,
        blank=True,
        verbose_name='Признак принадлежности к СИ'
    )
    # пример заполнения поля sub_types: ['1П1', '1П2', '1П3', '1У', 'ПБ']
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
        return f'{self.title}'


class Doings(models.Model):
    """Виды возможных действий с приборами по контрактам."""
    #  Название действия.
    title = models.CharField(
        max_length=255,
        default='Новое действие',
        unique=True,
        null=False,
        blank=False,
        verbose_name='Название действия'
    )

    class Meta:
        """."""

        verbose_name = 'Объект возможного действия с прибором по контракту'
        verbose_name_plural = 'Объекты в. д. с п. по к.'

    def __str__(self):
        """."""
        return f'{self.title}'


class Contracts(models.Model):
    """Модель переченя централизованных гос.контрактов,
    по которым с приборами что-то делалось
    (ремонт, модернизация, продление ресурса, тех.обсл.)."""
    #  Название гос.контракта.
    title = models.CharField(
        max_length=255,
        default='Новый гос.контракт',
        unique=False,
        null=False,
        blank=False,
        verbose_name='Название'
    )
    #  Номер гос.контракта.
    number = models.PositiveSmallIntegerField(
        null=False,
        unique=False,
        blank=False,
        verbose_name='Номер гос.контракта'
    )
    # Дата заключения гос.контракта.
    date_of = models.DateField(
        null=False,
        unique=False,
        blank=False,
        validators=(real_date,),
        verbose_name='Дата заключения гос.контракта'
    )
    # Дата начала возможности действий по гос.контракту.
    date_start = models.DateField(
        null=False,
        unique=False,
        blank=False,
        validators=(real_date,),
        verbose_name='Дата начала действий по гос.контракту'
    )
    # Дата окончания возможности действий по гос.контракту.
    date_end = models.DateField(
        null=False,
        unique=False,
        blank=False,
        validators=(real_date,),
        verbose_name='Дата окончания действий по гос.контракту'
    )

    class Meta:
        """."""

        verbose_name = 'Объект гос.контракта'
        verbose_name_plural = 'Объекты гос.контрактов'
        constraints = [
            models.UniqueConstraint(
                fields=['number', 'date_of'],
                name='unique_nd'
            ),
        ]

    def __str__(self):
        """."""
        return f'Контракт номер {self.number}, от {self.date_of}'


class RelContrDoing(models.Model):
    """Виды связей действий и контрактов."""
    #  Какое действие.
    to_doing = models.ForeignKey(
        to=Doings,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Действие по контракту',
        related_name='from_doings'
    )
    # По какому контракту.
    to_contract = models.ForeignKey(
        to=Contracts,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Контракт',
        related_name='from_contracts'
    )
    # Сколько минимально раз должно делаться.
    min_count = models.PositiveSmallIntegerField(
        null=False,
        unique=False,
        blank=False,
        verbose_name='Минимально, раз'
    )
    # Сколько максимально раз должно делаться.
    max_count = models.PositiveSmallIntegerField(
        null=False,
        unique=False,
        blank=False,
        verbose_name='Максимально, раз'
    )

    class Meta:
        """."""

        verbose_name = 'Объект связи действия и контракта'
        verbose_name_plural = 'Объекты связи действия и контракта'
        constraints = [
            models.UniqueConstraint(
                fields=['to_doing', 'to_contract'],
                name='unique_dc'
            ),
        ]

    def __str__(self):
        """."""
        return f'По контракту {self.to_contract} действие {self.to_doing}'


class DTCReal(models.Model):
    """Модель событий. Событие: реальный единичный
    короткий кейс связи одного прибора с одним контрактам.
    Пример: реальный ремонт прибора по по контракту,
    в некий момент времени."""
    basis = models.ForeignKey(to='DTCPotential',
                              null=False,
                              blank=False,
                              on_delete=models.CASCADE,
                              verbose_name='Основание',
                              related_name='from_dtcp_to_dtcr')
    exact_moment = models.DateTimeField(
        null=False,
        unique=False,
        blank=False,
        default=timezone.now,
        validators=(real_date,),
        verbose_name=('Реальная реализация потенциального события' +
                      ' с прибором по контракту')
    )

    class Meta:
        """."""

        verbose_name = 'объект промежутки'
        verbose_name_plural = 'объекты промежутки'
        constraints = [
            models.UniqueConstraint(
                fields=['basis', 'exact_moment'],
                name='unique_dc_real'
            )
        ]

    def __str__(self):
        """."""
        return f'Событие с прибором: {self.basis.reltocd}, дата: {self.exact_moment}'


class Device(models.Model):
    """Модель объекта прибора (технического средства)."""
    # Тип технического средства.
    type = models.ForeignKey(
        to=DevTypes,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Тип технического средства',
        related_name='dev_type_to_dev_obj'
    )
    # Подтип технического средства.
    # Резервное поле, используется ТОЛЬКО если объект
    # недостаточно конкретизированно описывается связью от поля type.
    sub_type = models.CharField(
        max_length=255,
        default=None,
        unique=False,
        null=True,
        blank=True,
        verbose_name='Подтип технического средства'
    )
    # Серийный номер (если есть).
    serial = models.CharField(
        max_length=255,
        unique=False,
        null=True,
        blank=False,
        verbose_name='Cерийный номер (если есть)'
    )
    # Инвентарный номер (если есть).
    inventary = models.CharField(
        max_length=255,
        unique=False,
        null=True,
        blank=True,
        verbose_name='Инвентарный номер (если есть)'
    )
    # Должностное лицо т.органа (одно), ответственное за его эксплуатацию
    holder = models.ForeignKey(
        to=TKDRMUser,
        null=True,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        verbose_name='Должностное лицо, ответственное за эксплуатацию (только одно, если таковое есть)',
        related_name='from_man_to_dev'
    )
    # Дата изготовления (выпуска, производства)
    date_prod = models.DateField(
        null=False,
        unique=False,
        blank=True,
        default=datetime.date(1990, 1, 1),
        validators=(real_date,),
        verbose_name='Дата изготовления (выпуска, производства)'
    )
    # Дата ввода в эксплуатацию первоначальная при поставке
    date_expl = models.DateField(
        null=False,
        unique=False,
        blank=True,
        default=datetime.date(1991, 1, 1),
        validators=(real_date,),
        verbose_name='Дата ввода в эксплуатацию первоначальная при поставке'
    )

    # Вычисляемое поле.
    # Дата ввода в эксплуатацию при последнем продлении
    # срока службы (если было, иначе равна date_expl)
    @property
    def date_prolong(self):
        date_enter = self.date_expl
        date_enter = datetime.datetime.combine(date_enter, datetime.datetime.min.time())  # noqa
        date_enter = timezone.make_aware(date_enter)
        temps = self.f_dev_to_doing.all()
        for item in temps:
            temps2 = list(item.from_dtcp_to_dtcr.all())
            temps2.sort(key=lambda x: x.exact_moment, reverse=True)
            temp2 = temps2[0] if temps2 else None
            if temp2 and item.reltocd.to_doing.title == DOING1:
                date_enter = max(temp2.exact_moment, date_enter)
        return date_enter.date()
    # Гарантийный срок при поставке, месяцев
    warr_period = models.PositiveSmallIntegerField(
        null=False,
        unique=False,
        blank=False,
        default=24,
        verbose_name='Срок гарантии при поставке (месяцев)'
    )

    # Вычисляемое поле.
    # Дата истечения срока службы (с учетом его последнего продления, если было)
    @property
    def date_prod_expired(self):
        delta = self.type.lifetime
        date_ret = self.date_expl
        date_ret = datetime.datetime.combine(date_ret, datetime.datetime.min.time())  # noqa
        date_ret = timezone.make_aware(date_ret)
        temps = self.f_dev_to_doing.all()
        for item in temps:
            temps2 = list(item.from_dtcp_to_dtcr.all())
            temps2.sort(key=lambda x: x.exact_moment, reverse=True)
            temp2 = temps2[0] if temps2 else None
            if temp2 and item.reltocd.to_doing.title == DOING1:
                date_ret = max(temp2.exact_moment, date_ret)
        date_ret = date_ret + dateutil.relativedelta.relativedelta(years=delta)  # noqa
        return date_ret.date()
    # Дата окончания последней поверки (если было). Актуально только если
    # dev_type.si_flag=True and is_si=True and is_stud=False and status_use=1
    # , в этом случае должно быть не Null и быть в нужном
    # диапазоне.
    # В иных случаях может быть любым, в т.ч. Null.
    date_verif = models.DateField(
        null=True,
        unique=False,
        blank=True,
        default=None,
        validators=(real_date,),
        verbose_name='Дата окончания последней поверки (если было)'
    )

    # Вычисляемое поле.
    # Номер категории расчетный
    @property
    def cat_number_c(self):
        # дата сегодня
        today = datetime.date.today()
        today = datetime.datetime.combine(today, datetime.datetime.min.time())  # noqa
        today = timezone.make_aware(today)
        # дата ввода при поставке
        date_expl = self.date_expl
        date_expl = datetime.datetime.combine(date_expl, datetime.datetime.min.time())  # noqa
        date_expl = timezone.make_aware(date_expl)
        # дата истечения гарантии
        date_warr_end = self.date_expl + dateutil.relativedelta.relativedelta(
            months=self.warr_period
        )
        date_warr_end = datetime.datetime.combine(date_warr_end, datetime.datetime.min.time())  # noqa
        date_warr_end = timezone.make_aware(date_warr_end)
        # дата истечения срока службы с проверкой по возможным продлениям её
        delta = self.type.lifetime
        date_ret = self.date_expl
        date_ret = datetime.datetime.combine(date_ret, datetime.datetime.min.time())  # noqa
        date_ret = timezone.make_aware(date_ret)
        temps = self.f_dev_to_doing.all()
        for item in temps:
            temps2 = list(item.from_dtcp_to_dtcr.all())
            temps2.sort(key=lambda x: x.exact_moment, reverse=True)
            temp2 = temps2[0] if temps2 else None
            if temp2 and item.reltocd.to_doing.title == DOING1:
                date_ret = max(temp2.exact_moment, date_ret)
        date_ret += dateutil.relativedelta.relativedelta(years=delta)

        if date_expl <= today <= date_warr_end:
            return 1
        if date_warr_end < today <= date_ret:
            return 2
        if date_ret < today:
            return 3
        return None
    # Номер категории фактический (от 1 до 4, если есть)
    cat_number_f = models.PositiveSmallIntegerField(
        null=True,
        unique=False,
        default=None,
        blank=True,
        validators=(real_cat,),
        verbose_name='Номер категории фактический (от 1 до 4, если есть)'
    )
    # Субъект учета по (за)балансу.
    # Таможенный орган, в которое прибор либо находится
    # в оперативном управлении (или, что то же самое,
    # на балансовом учете), либо на забалансовом учете
    cp1_acc = models.ForeignKey(to=CustPlace1Acc,
                                null=False,
                                blank=False,
                                on_delete=models.PROTECT,
                                verbose_name='Таможенный орган, в котором числится в оперативном управлении (на балансовом учете), либо на забалансовом учете',
                                related_name='cp1acc_to_dev')
    # Источник собственности
    sour_type = models.ForeignKey(to=SourceTypes,
                                  null=False,
                                  blank=False,
                                  on_delete=models.PROTECT,
                                  verbose_name='Источник собственности',
                                  related_name='s_type_to_dev')
    # Балансовая стоимость (в руб., если имеется, отдельно данной единицы)
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        unique=False,
        blank=True,
        default=None,
        verbose_name='Величина балансовой стоимости (если есть, отдельно от прочих), руб.'
    )
    # Исправность. Прибор исправен, если все его составные части
    # полностью исправны, а если у него есть нижестоящие
    # (to_upper_level not Null), то и они все также.
    # Если состояние неизвестно, то = Null.
    condition = models.BooleanField(
        null=True,
        unique=False,
        blank=False,
        default=True,
        verbose_name='Состояние по исправности на текущий день (включая все блоки и все нижестоящие приборы, если известно, да-исправно, нет-неисправно)'
    )
    # Вышестоящий прибор (если есть).
    upper_id = models.ForeignKey(to='Device',
                                 null=True,
                                 blank=True,
                                 default=None,
                                 on_delete=models.SET_NULL,
                                 verbose_name='Вышестоящий прибор (если есть)',
                                 related_name='to_upper_level')
    # Является ли СИ конкретный экземпляр (да-СИ, нет-индикатор).
    is_si = models.BooleanField(
        null=True,
        unique=False,
        blank=False,
        default=False,
        verbose_name='Является ли СИ конкретный экземпляр (да-СИ, нет-индикатор)'
    )
    # Яляется ли учебным конкретный экземпляр (да-учебный, нет-нет).
    is_stud = models.BooleanField(
        null=True,
        unique=False,
        blank=False,
        default=False,
        verbose_name='Яляется ли учебным конкретный экземпляр (да-учебный, нет-нет)'
    )
    # Статус по эксплуатации.
    status_use = models.ForeignKey(to=StatusTypes,
                                   null=False,
                                   blank=False,
                                   on_delete=models.PROTECT,
                                   verbose_name='Статус по эксплуатации',
                                   related_name='status_use_to_dev')
    # Cтатус по централизованному т.о./ремонту, подлежит ли прибор.
    service_type = models.ForeignKey(
        to=ServiceTypes,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Статус по централизованному т.о./ремонту, подлежит ли прибор',
        related_name='serv_to_dev'
    )
    # M2M-поля
    # По использованию кем-то где-то
    rels_of_work = models.ManyToManyField(
        CustPlaceToLocation,
        through='RelToDev',
        verbose_name='Какой там.орган и в каком месте эксплуатирует прибор'
    )
    # Потенциальное вхождению прибора в контракты
    rels_of_contracts = models.ManyToManyField(
        RelContrDoing,
        through='DTCPotential',
        verbose_name='Потенциальное вхождение прибора в гос.контракты'
    )
    # Вычисляемое поле.
    # Коллекция реальных вхождений прибора в контракты
    @property
    def real_of_contrs(self):
        return DTCReal.objects.filter(basis__dev__id=self.id)
    # Примечение1 (район субъекта эксплуатации, если имеется и известно).
    note1 = models.CharField(
        max_length=255,
        default=None,
        unique=False,
        null=True,
        blank=True,
        verbose_name='Примечение1 (район субъекта эксплуатации, если имеется и известно)'
    )
    # Примечение2 (иные примечания, если имеется и известно).
    note2 = models.CharField(
        max_length=255,
        default=None,
        unique=False,
        null=True,
        blank=True,
        verbose_name='Примечение2 (иные примечания, если имеется и известно)'
    )
    # Примечение3 (сведения о месте следующей планируемой эксплуатации, если имеется и известно).
    note3 = models.CharField(
        max_length=255,
        default=None,
        unique=False,
        null=True,
        blank=True,
        verbose_name='Примечение3 (сведения о месте следующей планируемой эксплуатации, если имеется и известно)'
    )

    class Meta:
        """."""

        verbose_name = 'Техническое средство'
        verbose_name_plural = 'Технические средства'

    def __str__(self):
        """."""
        return f'Прибор, тип {self.type}, сер.номер {self.serial}, id={self.id}'

    def add_clean(self):
        super().clean()
        if not self.type:
            return
        for item_field, item_type_flag in [
            ('serial', self.type.serial_flag),
            ('upper_id', self.type.upper_dev_flag),
            ('is_si', self.type.si_flag),
        ]:
            field_value = getattr(self, item_field)
            if item_type_flag is True and field_value is None:
                raise ValidationError(f'Для данного типа прибора поле {item_field}  обязано быть не Null.')
            if item_type_flag is False and field_value is not None:
                raise ValidationError(f'Для данного типа прибора поле {item_field} обязано быть Null.')

    def save(self, *args, **kwargs):
        self.add_clean()
        super().save(*args, **kwargs)


class DTCPotential(models.Model):
    """Модель-промежутка M2M приборов и действий по контрактам.
    Потенциально возможные действия с приборами по контрактам.
    Пример: прибор входит (прописан) в контракте на ремонт
    всех приборов. Входит строго один раз.
    Объект модели - потенциальное, но не реальное,
    действие с прибором по контракту.
    Поэтому:
    - в объекте модели нет таймстампа;
    - сочетание обоих полей д.быть уникально."""

    dev = models.ForeignKey(to=Device,
                            null=False,
                            blank=False,
                            on_delete=models.CASCADE,
                            verbose_name='прибор',
                            related_name='f_dev_to_doing')
    reltocd = models.ForeignKey(to=RelContrDoing,
                                null=False,
                                blank=False,
                                on_delete=models.PROTECT,
                                verbose_name='действие',
                                related_name='f_doing_to_dev')

    class Meta:
        """."""

        verbose_name = 'объект промежутки'
        verbose_name_plural = 'объекты промежутки'
        constraints = [
            models.UniqueConstraint(
                fields=['dev', 'reltocd'],
                name='unique_dr'
            )
        ]

    def __str__(self):
        """."""
        return f'Объект промежутки с id={self.id}'


class RelToDev(models.Model):
    """Модель-промежутка, связь M2M между
    'отношением т. органа и места его работы'
    и прибора.

    Примеры:
    - "Самарский пост", работающий в "ММПО Восток", импользует "прибор 1",
    и это приоритетное место использования для прибора;
    - "Самарский пост", работающий в "ВПП Курск", использует "прибор 2",
    и это неприоритетное место использования для прибора.

    Для каждого прибор приоритетное - не больше одного.
    """
    to_rel = models.ForeignKey(to=CustPlaceToLocation,
                               null=False,
                               blank=False,
                               on_delete=models.PROTECT,
                               verbose_name='т.орган и место',  # noqa
                               related_name='from_relation')
    to_dev = models.ForeignKey(to=Device,
                               null=False,
                               blank=False,
                               on_delete=models.CASCADE,
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
