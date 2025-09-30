from django import forms
from core.models import (
    Rtu,
    CustHouse,
    CustPost,
    Ppr,
    Mmpo,
    Oez,
    Ztk,
    Device,
    DevTypes,
    DevCatsL2,
    DevCatsL1,
    SourceTypes,
    StatusTypes,
    ServiceTypes,
)

devs = Device.objects.all()
dev_types = DevTypes.objects.all()
dev_cat_l2_s = DevCatsL2.objects.all()
dev_cat_l1_s = DevCatsL1.objects.all()
dev_sour_s = SourceTypes.objects.all()
rtus = Rtu.objects.all()
chs = CustHouse.objects.all()
cps = CustPost.objects.all()
pprs = Ppr.objects.all()
mmpos = Mmpo.objects.all()
oezs = Oez.objects.all()
ztks = Ztk.objects.all()
status_types = StatusTypes.objects.all()
service_types = ServiceTypes.objects.all()


class DevDetailForm(forms.Form):
    type = forms.ChoiceField(
        choices=[],
        label='Тип прибора',
        required=True,
        # help_text='Тип прибора'
    )
    subtype = forms.CharField(
        label='Подтип (если есть)',
        max_length=20,
        required=False,
        # help_text='Подтип'
    )
    cat_l2 = forms.ChoiceField(
        choices=[],
        label='Категория уровня 2',
        required=True,
        # help_text='Категория уровня 2'
    )
    cat_l1 = forms.ChoiceField(
        choices=[],
        label='Категория уровня 1',
        required=True,
        # help_text='Категория уровня 1'
    )
    upper_dev = forms.IntegerField(
        label='ID вышестоящего прибора (если есть)',
        required=False,
        # help_text='ID вышестоящего прибора (если есть)'
    )
    source = forms.ChoiceField(
        choices=[],
        label='Собственник',
        required=True,
        # help_text='Собственник'
    )
    serial_flag = forms.ChoiceField(
        choices=[],
        label='Девайсы текущего типа т.с., в плане наличия сер.номера',
        required=True,
        # help_text='Девайсы текущего типа т.с., в плане наличия сер.номера'
    )
    serial = forms.CharField(
        label='Серийный номер',
        max_length=20,
        required=False,
        # help_text='Серийный номер'
    )
    si_flag = forms.ChoiceField(
        choices=[],
        label='Девайсы текущего типа т.с., в плане отнесения к СИ',
        required=True,
        # help_text='Текущий тип т.с., в плане отнесения к СИ'
    )
    is_si = forms.ChoiceField(
        choices=[],
        label='Является ли текущее т.с. СИ',
        required=True,
        # help_text='Является ли текущее т.с. СИ'
    )
    status_use = forms.ChoiceField(
        choices=[],
        label='Статус по использованию',
        required=True,
        # help_text='Статус по использованию'
    )
    service_type = forms.ChoiceField(
        choices=[],
        label='Статус по централизованному т.о./ремонту',
        required=True,
        # help_text='Статус по централизованному т.о./ремонту'
    )
    acc1_rtu = forms.ChoiceField(
        choices=[],
        label='(За)баланс, главный №1, т.орган, в к-м стоит на, если он РТУ',
        required=True,
        # help_text='(За) баланс, главный №1, т.орган, в к-м стоит на, если он РТУ'  # noqa
    )
    acc1_ch = forms.ChoiceField(
        choices=[],
        label='(За)баланс, главный №1, т.орган, в к-м стоит на, если он таможня',  # noqa
        required=True,
        # help_text='(За)баланс, главный №1, т.орган, в к-м стоит на, если он таможня'  # noqa
    )
    acc1_cp = forms.ChoiceField(
        choices=[],
        label='(За)баланс, главный №1, т.орган, в к-м стоит на, если он т.пост',  # noqa
        required=True,
        # help_text='(За)баланс, главный №1, т.орган, в к-м стоит на, если он т.пост'  # noqa
    )
    #
    #
    # Если решим, что т.орган, который (за)балансодержатель, может быть не единственный, то  # noqa
    # сюда дописываем acc2_rtu, acc2_ch, acc2_cp, acc3_rtu, acc3_ch, acc3_cp, ...  # noqa
    #
    #
    use_main1_rtu = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, главный №1, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, главный №1, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_main1_ch = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, главный №1, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, главный №1, т.орган, в к-м, если он таможня'  # noqa
    )
    use_main1_cp = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, главный №1, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, главный №1, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_main1_ppr = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, главный №1, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, главный №1, локация, если она пункт пропуска'  # noqa
    )
    use_main1_mmpo = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, главный №1, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, главный №1, локация, если она ММПО'  # noqa
    )
    use_main1_oez = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, главный №1, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, главный №1, локация, если она ОЭЗ'  # noqa
    )
    use_main1_ztk = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, главный №1, локация, если она ЗТК',  # noqa
        required=True,
        # help_text='Эксплуатация, главный №1, локация, если она ЗТК'  # noqa
    )
    #
    #
    # Если решим, что т.орган, который главный эксплуатант, может быть не единственный, то  # noqa
    # сюда дописываем use_main2_rtu, use_main2_ch, use_main2_cp, use_main3_rtu, use_main3_ch, use_main3_cp, ...  # noqa
    #
    #
    use_oth1_rtu = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №1, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, прочие №1, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_oth1_ch = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №1, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, т.орган, в к-м, если он таможня'  # noqa
    )
    use_oth1_cp = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №1, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_oth1_ppr = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №1, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, локация, если она пункт пропуска'  # noqa
    )
    use_oth1_mmpo = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №1, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, локация, если она ММПО'  # noqa
    )
    use_oth1_oez = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №1, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, локация, если она ОЭЗ'  # noqa
    )
    use_oth1_ztk = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №1, локация, если она ЗТК',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, локация, если она ЗТК'  # noqa
    )
    #
    use_oth2_rtu = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №2, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, прочие №2, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_oth2_ch = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №2, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, т.орган, в к-м, если он таможня'  # noqa
    )
    use_oth2_cp = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №2, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_oth2_ppr = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №2, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, локация, если она пункт пропуска'  # noqa
    )
    use_oth2_mmpo = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №2, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, локация, если она ММПО'  # noqa
    )
    use_oth2_oez = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №2, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, локация, если она ОЭЗ'  # noqa
    )
    use_oth2_ztk = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №2, локация, если она ЗТК',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, локация, если она ЗТК'  # noqa
    )
    #
    use_oth3_rtu = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №3, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, прочие №3, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_oth3_ch = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №3, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, т.орган, в к-м, если он таможня'  # noqa
    )
    use_oth3_cp = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №3, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_oth3_ppr = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №3, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, локация, если она пункт пропуска'  # noqa
    )
    use_oth3_mmpo = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №3, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, локация, если она ММПО'  # noqa
    )
    use_oth3_oez = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №3, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, локация, если она ОЭЗ'  # noqa
    )
    use_oth3_ztk = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №3, локация, если она ЗТК',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, локация, если она ЗТК'  # noqa
    )
    #
    use_oth4_rtu = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №4, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, прочие №4, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_oth4_ch = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №4, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, т.орган, в к-м, если он таможня'  # noqa
    )
    use_oth4_cp = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №4, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_oth4_ppr = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №4, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, локация, если она пункт пропуска'  # noqa
    )
    use_oth4_mmpo = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №4, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, локация, если она ММПО'  # noqa
    )
    use_oth4_oez = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №4, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, локация, если она ОЭЗ'  # noqa
    )
    use_oth4_ztk = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №4, локация, если она ЗТК',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, локация, если она ЗТК'  # noqa
    )
    #
    use_oth5_rtu = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №5, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, прочие №5, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_oth5_ch = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №5, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №5, т.орган, в к-м, если он таможня'  # noqa
    )
    use_oth5_cp = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №5, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №5, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_oth5_ppr = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №5, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №5, локация, если она пункт пропуска'  # noqa
    )
    use_oth5_mmpo = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №5, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №5, локация, если она ММПО'  # noqa
    )
    use_oth5_oez = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №5, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №5, локация, если она ОЭЗ'  # noqa
    )
    use_oth5_ztk = forms.ChoiceField(
        choices=[],
        label='Эксплуатация, прочие №5, локация, если она ЗТК',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №5, локация, если она ЗТК'  # noqa
    )

    note1 = forms.CharField(
        label='Примечание 1 (если есть) (Район объекта эксплуатации)',
        max_length=200,
        required=False,
        # help_text='Примечание 1'
    )
    note3 = forms.CharField(
        label='Намерения использовать в будущем в ином месте (если есть)',
        max_length=200,
        required=False,
        # help_text='Намерения использовать в будущем в ином месте (если есть)'
    )
    id = forms.IntegerField(
        label='ID',
        required=False,
        # help_text='Номер записи в базе данных'
    )

    def __init__(self, *args, **kwargs):
        """."""
        EMPTY_OBJ = [(0, '----'),]
        super().__init__(*args, **kwargs)

        rtus_choices = EMPTY_OBJ + [
            (item.pk, ', '.join([item.title, item.code])) for item in rtus if item.code  # noqa
        ]
        chs_choices = EMPTY_OBJ + [
            (item.pk, ', '.join([item.title, item.code])) for item in chs if item.code  # noqa
        ]
        cps_choices = EMPTY_OBJ + [
            (item.pk, ', '.join([item.title, item.code])) for item in cps if item.code  # noqa
        ]
        pprs_choices = EMPTY_OBJ + [
            (item.pk, ', '.join([
                item.title,
                item.pptype.title,
                item.tow_country if item.tow_country else ''
            ])) for item in pprs
        ]
        mmpos_choices = EMPTY_OBJ + [(item.pk, item.title) for item in mmpos]
        oezs_choices = EMPTY_OBJ + [(item.pk, item.title) for item in oezs]
        ztks_choices = EMPTY_OBJ + [(item.pk, item.title) for item in ztks]
        serial_flag_choices = EMPTY_OBJ + [
            (1, 'Обязаны иметь сер.номер'),
            (2, 'Обязаны не иметь сер.номер'),
            (3, 'Могут иметь сер.номер, или нет'),
        ]
        is_si_choices = EMPTY_OBJ + [
            (1, 'Не подлежит к отнесению к СИ/инд'),
            (2, 'Является СИ'),
            (3, 'Является индикатором')
        ]
        si_flag_choices = EMPTY_OBJ + [
            (1, 'Обязаны быть либо СИ, либо инд'),
            (2, 'Обязаны не быть ни СИ, ни инд'),
            (3, 'Могут быть СИ, быть инд, либо ни тем ни другим')
        ]
        self.fields['type'].choices = EMPTY_OBJ + [
            (item.pk, item.title) for item in dev_types
        ]
        self.fields['cat_l2'].choices = EMPTY_OBJ + [
            (item.pk, item.title) for item in dev_cat_l2_s
        ]
        self.fields['cat_l1'].choices = EMPTY_OBJ + [
            (item.pk, item.title) for item in dev_cat_l1_s
        ]
        self.fields['source'].choices = EMPTY_OBJ + [
            (item.pk, item.title) for item in dev_sour_s
        ]
        self.fields['serial_flag'].choices = serial_flag_choices
        self.fields['acc1_rtu'].choices = rtus_choices
        self.fields['acc1_ch'].choices = chs_choices
        self.fields['acc1_cp'].choices = cps_choices

        for item in ['1',]:
            self.fields['use_main{}_rtu'.format(item)].choices = rtus_choices
            self.fields['use_main{}_ch'.format(item)].choices = chs_choices
            self.fields['use_main{}_cp'.format(item)].choices = cps_choices
            self.fields['use_main{}_ppr'.format(item)].choices = pprs_choices
            self.fields['use_main{}_mmpo'.format(item)].choices = mmpos_choices
            self.fields['use_main{}_oez'.format(item)].choices = oezs_choices
            self.fields['use_main{}_ztk'.format(item)].choices = ztks_choices

        for item in ['1', '2', '3', '4', '5']:
            self.fields['use_oth{}_rtu'.format(item)].choices = rtus_choices
            self.fields['use_oth{}_ch'.format(item)].choices = chs_choices
            self.fields['use_oth{}_cp'.format(item)].choices = cps_choices
            self.fields['use_oth{}_ppr'.format(item)].choices = pprs_choices
            self.fields['use_oth{}_mmpo'.format(item)].choices = mmpos_choices
            self.fields['use_oth{}_oez'.format(item)].choices = oezs_choices
            self.fields['use_oth{}_ztk'.format(item)].choices = ztks_choices

        self.fields['is_si'].choices = is_si_choices
        self.fields['si_flag'].choices = si_flag_choices
        self.fields['status_use'].choices = EMPTY_OBJ + [
            (item.pk, item.title) for item in status_types
        ]
        self.fields['service_type'].choices = EMPTY_OBJ + [
            (item.pk, item.title) for item in service_types
        ]

    def clean(self):
        """."""
        def check_single(field_name):
            """Достает из формы значение поля, выбранное юзером из списка,
            проверяет его на валидность, и если ОК, то
            возвращает его.
            Принимает название поля, которое надо отработать.
            Использует две переменные следующего уровня глобальности:
            cleaned_data и self.
            Пример:
            cleaned_data={..., field_name: field_value_selected_by_user, ...}
            self.fields[field_name].label = 'Человекочитаемое_название'
            sels.fields[field_name].choices = [
            ('0', '----'),
            ('11', option1),
            ('24', option2),
            ...
            ('39', option3)
            ]
            Функция проверяет, что field_value_selected_by_user
            есть в [11, 24, ..., 39],
            и есть есть, то возвращает его. Если нет - поднимает ошибку.
            """
            field_value = int(cleaned_data.get(field_name))
            label = self.fields[field_name].label
            if not (field_value in [item[0] for item in self.fields[field_name].choices[1:]]):  # noqa
                raise forms.ValidationError(
                    f'Поле \"{label}\" должно быть непустым',
                    code='invalid_value'
                )
            return field_value

        cleaned_data: dict = super().clean()

        # код типа девайса, получен из формы
        dev_type_code = check_single('type')
        # объект типа девайса, получен из БД по коду, полученному из формы
        dev_type = dev_types.get(pk=dev_type_code)
        # код категории L2 типа девайса, получен из формы
        cat_l2 = check_single('cat_l2')
        # код категории L2 типа девайса, получен из БД по коду типа девайса, полученному из формы  # noqa
        dev_type_catl2 = int(dev_types.get(pk=dev_type_code).category.pk)
        # проверка, что в форме соответствуют друг другу: код типа девайса и код его L2  # noqa
        if dev_type_catl2 != cat_l2:
            raise forms.ValidationError(
                'Поле \"Тип прибора\" не соовтетствует полю \"Категория уровня 2\". Измените одно из них (обычно второе).',  # noqa
                code='invalid_fieldset'
            )
        # код категории L1 типа девайса, получен из формы
        cat_l1 = check_single('cat_l1')
        # код категории L1 типа девайса, полчен из БД по коду типа девайса, полученному из формы  # noqa
        dev_type_cat_l1 = int(dev_type.category.cat_l1.pk)
        # проверка, что в форме соответствуют друг другу: код типа девайса и код его L1  # noqa
        if dev_type_cat_l1 != cat_l1:
            raise forms.ValidationError(
                'Поле \"Категория уровня 2\" не соовтетствует полю \"Категория уровня 1\". Измените одно из них (обычно второе).',  # noqa
                code='invalid_fieldset'
            )
        # код текущего девайса, если есть, получен из формы
        curr_dev_id = int(cleaned_data.get('id')) if cleaned_data.get('id') else None  # noqa
        # код девайса, вышестоящего текущему, если есть, получен из формы
        upper_dev_id = int(cleaned_data.get('upper_dev')) if cleaned_data.get('upper_dev') else None  # noqa
        # проверка, что код вышестоящего девайса, если есть, соответствует хоть одному реальному девайсу  # noqa
        if upper_dev_id and (upper_dev_id not in [int(item.pk) for item in devs]):  # noqa
            raise forms.ValidationError(
                'Поле \"ID вышестоящего прибора (если есть)\" должно быть либо пусто, либо содержать валидный id',  # noqa
                code='invalid_value'
            )
        # проверка, что код вышестоящего девайса, если есть, не указывает на сам текущий девайс  # noqa
        if upper_dev_id  and curr_dev_id and upper_dev_id == curr_dev_id:  # noqa
            raise forms.ValidationError(
                'Поле \"ID вышестоящего прибора (если есть)\" не должно совпадать с полем \"ID\"',  # noqa
                code='invalid_value'
            )
        # флаг возможности наличия вышестоящего девайса для текущего, получен из БД  # noqa
        from_db_dev_type_upp_fl = dev_type.upper_dev_flag if dev_type.upper_dev_flag else None  # noqa

        if not ((from_db_dev_type_upp_fl is True and upper_dev_id is not None) or  # noqa
                (from_db_dev_type_upp_fl is False and upper_dev_id is None) or
                from_db_dev_type_upp_fl is None):
            raise forms.ValidationError(
                'Поле \"Тип прибора" не соответствует полю \"ID вышестоящего прибора (если есть)\". Измените одно из них (обычно второе).',  # noqa
                code='invalid_fieldset'
            )

        check_single('source')
        form_dev_flag = check_single('serial_flag')
        from_db_dev_type_ser_flag = dev_type.serial_flag if dev_type.serial_flag else None  # noqa

        if not ((from_db_dev_type_ser_flag is True and form_dev_flag == 1) or  # noqa
                (from_db_dev_type_ser_flag is False and form_dev_flag == 2) or  # noqa
                (from_db_dev_type_ser_flag is None and form_dev_flag == 3)):  # noqa
            raise forms.ValidationError(
                'Поле \"Тип прибора\" не соотвтствует полю \"Девайсы текущего типа т.с., в плане наличия сер.номера\". Измените одно из них (обычно второе).',  # noqa
                code='invalid_fieldset'
            )

        form_serial = cleaned_data.get('serial') if cleaned_data.get('serial') else None  # noqa

        if not ((from_db_dev_type_ser_flag is True and form_serial is not None) or  # noqa
                (from_db_dev_type_ser_flag is False and form_serial is None) or
                (from_db_dev_type_ser_flag is None)):
            raise forms.ValidationError(
                'Поле \"Тип прибора\" не соотвтствует полю \"Серийный номер\". Измените одно из них (обычно второе).',  # noqa
                code='invalid_fieldset'
            )

        return cleaned_data

    # def save(self):
    #     # Получение данных формы
    #     data = self.cleaned_data

    #     # Создание или обновление модели A
    #     model_a, created_a = ModelA.objects.update_or_create(
    #         defaults={
    #             'field_a1': data['field1'],
    #             # другие поля модели A
    #         },
    #         # фильтр по уникальное условию или None (если создать новую)
    #     )

    #     # Создание или обновление модели B
    #     model_b, created_b = ModelB.objects.update_or_create(
    #         defaults={
    #             'field_b1': data['field2'],
    #             # другие поля модели B
    #         },
    #         # фильтр по условию
    #     )

    #     # Возвращать можно что угодно (например, созданные объекты)
    #     return model_a, model_b
