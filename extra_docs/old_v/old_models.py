
# class CustPlace2(models.Model):
#     """Модель объекта т.органа второго типа.
#     Объединяет в одной модели все уровни (три: РТУ, таможня, пост),
#     поэтому: а) имеет поле level; б) в БД много ссылок таблицы на
#     саму себя. Фактически, имеем в таблице множество цепочек из
#     трёх звеньев каждая. Это заменяет generic_foreign_key.
#     Пока решено не разрабатывать в такой версии таблицы,
#     а остаться на пяти вместо одной. Rtu, CustHouse, CustPost,
#     CustPlace1Acc, CustPlace1Use."""

#     title = models.CharField(
#         max_length=255,
#         unique=False,  # !!!!!!
#         null=True,
#         verbose_name='Название'
#     )
#     code = models.CharField(
#        max_length=8,
#        unique=True,
#        null=True,
#        blank=False,
#        validators=[RegexValidator(regex=r'^1\d{7}$')],
#        verbose_name='Код т.органа'
#     )
#     address = models.CharField(
#         max_length=255,
#         default='-',
#         unique=False,
#         null=False,
#         blank=True,
#         verbose_name='Почтовый адрес'
#     )
#     level = models.CharField(choices=CUSTCHOICES,
#                              verbose_name='Уровень т.органа',
#                              max_length=1,
#                              null=False,
#                              blank=False
#                              )
#     upper_id = models.ForeignKey(to='CustPlace2',
#                                  null=True,
#                                  blank=True,
#                                  on_delete=models.RESTRICT,
#                                  verbose_name='Вышестоящий т. орган',
#                                  related_name='to_upper_level')
#     ztk_allowed = models.BooleanField(
#         null=False,
#         blank=False,
#         default=False,
#         verbose_name='Признак разрешения работать в ЗТК'
#         # Имеются в виду ЗТК т.н. отдельно-существующие.
#         # Не находящиеся на территории какого-либо
#         # пункта пропуска, ММПО, ОЭЗ.
#     )
#     standalone_allowed = models.BooleanField(
#         null=False,
#         blank=False,
#         default=True,
#         verbose_name='Признак разрешения работать без локации'
#         # Признак, что данному т.органу разрешено эксплуатировать приборы НЕ
#         # в каком-либо ПП, ММПО, СЭЗ, ОЭЗ.
#         # Рекомендуется выставить в True для:
#         # всех РТУ, всех таможен, всех внутренних(!) постов.
#     )

#     def save(self, *args, **kwargs):
#         """."""
#         temp = super().save(*args, **kwargs)
#         return temp  # noqa

#     class Meta:
#         """."""

#         verbose_name = 'Т.орган второго типа'
#         verbose_name_plural = 'Т.органы второго типа'

#     def __str__(self):
#         """."""
#         return f'таможенный орган 2-го типа, {self.level}-го уровня, являющийся: {self.title}'  # noqa
