from django.db import models

class CustPlace1Acc(models.Model):
    class Type:
        RTU = 1
        CUST_HOUSE = 2
        CUST_POST = 3
        CHOICES = ((RTU, "РТУ"),
                   (CUST_HOUSE, "Таможня"),
                   (CUST_POST, "Пост"))
    title = models.CharField(
        max_length=255,
        unique=False,  # !!!!!
        null=False,
        blank=False,
        verbose_name='Название'
    )
    code = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=False,
        # валидацию можно прописать отдельной функцией в модели
        # validators=[RegexValidator(regex=r'^1\d{4}000$')],
        verbose_name='Код т.органа'
    )
    address = models.CharField(
        max_length=255,
        default='-',
        unique=False,
        null=False,
        blank=True,
        verbose_name='Почтовый адрес'
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
        default=True,
        verbose_name='Признак разрешения работать без локации'
        # Признак, что данному т.органу разрешено эксплуатировать приборы НЕ в
        # каком-либо ПП, ММПО, СЭЗ, ОЭЗ.
        # Рекомендуется выставить в True для:
        # всех РТУ, всех таможен, всех внутренних(!) постов.
    )
    upper_id = models.ForeignKey(to="self",
                                 null=True,
                                 blank=True,
                                 on_delete=models.PROTECT,
                                 verbose_name='Вышестоящий т. орган',
                                 related_name='from_ch_to_rtu')
    type = models.IntegerField(choices=Type.CHOICES)

    class Meta:
        db_table = "cust_place_1_acc"
        ordering = ["id"]


# прописываем, какие именно объекты будут пониматься как Rtu
class RtuManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=CustPlace1Acc.Type.RTU)

    # перегружаем не только извлечение объектов, но и создание
    def create(self, **kwargs):
        kwargs["type"] = CustPlace1Acc.Type.RTU
        return super().create(**kwargs)

    # можно ещё перегрузить bulk_create, но мне лень


class Rtu(CustPlace1Acc):
    # заменяем стандартный метод получения объектов
    # - только те, у которых проставлен тип RTU
    objects = RtuManager()
    class Meta:
        proxy = True
