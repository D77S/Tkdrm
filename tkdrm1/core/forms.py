from django import forms
from core.models import (
    Rtu,
    CustHouse,
    CustPost,
    Ppr,
    Mmpo,
    Oez,
    Ztk,
    DevTypes,
    DevCatsL2,
    DevCatsL1,
    SourceTypes,
    StatusTypes,
)


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
        label='Собственник',
        required=True,
        # help_text='Собственник'
    )
    serial = forms.CharField(
        label='Серийный номер',
        max_length=20,
        required=False,
        # help_text='Серийный номер'
    )
    serial_flag = forms.ChoiceField(
        label='Девайсы текущего типа т.с., в плане наличия сер.номера',
        required=True,
        # help_text='Девайсы текущего типа т.с., в плане наличия сер.номера'
    )
    acc1_rtu = forms.ChoiceField(
        label='(За)баланс, главный №1, т.орган, в к-м стоит на, если он РТУ',
        required=True,
        # help_text='(За) баланс, главный №1, т.орган, в к-м стоит на, если он РТУ'  # noqa
    )
    acc1_ch = forms.ChoiceField(
        label='(За)баланс, главный №1, т.орган, в к-м стоит на, если он таможня',  # noqa
        required=True,
        # help_text='(За)баланс, главный №1, т.орган, в к-м стоит на, если он таможня'  # noqa
    )
    acc1_cp = forms.ChoiceField(
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
        label='Эксплуатация, главный №1, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, главный №1, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_main1_ch = forms.ChoiceField(
        label='Эксплуатация, главный №1, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, главный №1, т.орган, в к-м, если он таможня'  # noqa
    )
    use_main1_cp = forms.ChoiceField(
        label='Эксплуатация, главный №1, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, главный №1, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_main1_ppr = forms.ChoiceField(
        label='Эксплуатация, главный №1, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, главный №1, локация, если она пункт пропуска'  # noqa
    )
    use_main1_mmpo = forms.ChoiceField(
        label='Эксплуатация, главный №1, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, главный №1, локация, если она ММПО'  # noqa
    )
    use_main1_oez = forms.ChoiceField(
        label='Эксплуатация, главный №1, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, главный №1, локация, если она ОЭЗ'  # noqa
    )
    use_main1_ztk = forms.ChoiceField(
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
        label='Эксплуатация, прочие №1, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, прочие №1, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_oth1_ch = forms.ChoiceField(
        label='Эксплуатация, прочие №1, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, т.орган, в к-м, если он таможня'  # noqa
    )
    use_oth1_cp = forms.ChoiceField(
        label='Эксплуатация, прочие №1, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_oth1_ppr = forms.ChoiceField(
        label='Эксплуатация, прочие №1, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, локация, если она пункт пропуска'  # noqa
    )
    use_oth1_mmpo = forms.ChoiceField(
        label='Эксплуатация, прочие №1, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, локация, если она ММПО'  # noqa
    )
    use_oth1_oez = forms.ChoiceField(
        label='Эксплуатация, прочие №1, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, локация, если она ОЭЗ'  # noqa
    )
    use_oth1_ztk = forms.ChoiceField(
        label='Эксплуатация, прочие №1, локация, если она ЗТК',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №1, локация, если она ЗТК'  # noqa
    )
    #
    use_oth2_rtu = forms.ChoiceField(
        label='Эксплуатация, прочие №2, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, прочие №2, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_oth2_ch = forms.ChoiceField(
        label='Эксплуатация, прочие №2, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, т.орган, в к-м, если он таможня'  # noqa
    )
    use_oth2_cp = forms.ChoiceField(
        label='Эксплуатация, прочие №2, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_oth2_ppr = forms.ChoiceField(
        label='Эксплуатация, прочие №2, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, локация, если она пункт пропуска'  # noqa
    )
    use_oth2_mmpo = forms.ChoiceField(
        label='Эксплуатация, прочие №2, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, локация, если она ММПО'  # noqa
    )
    use_oth2_oez = forms.ChoiceField(
        label='Эксплуатация, прочие №2, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, локация, если она ОЭЗ'  # noqa
    )
    use_oth2_ztk = forms.ChoiceField(
        label='Эксплуатация, прочие №2, локация, если она ЗТК',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №2, локация, если она ЗТК'  # noqa
    )
    #
    use_oth3_rtu = forms.ChoiceField(
        label='Эксплуатация, прочие №3, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, прочие №3, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_oth3_ch = forms.ChoiceField(
        label='Эксплуатация, прочие №3, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, т.орган, в к-м, если он таможня'  # noqa
    )
    use_oth3_cp = forms.ChoiceField(
        label='Эксплуатация, прочие №3, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_oth3_ppr = forms.ChoiceField(
        label='Эксплуатация, прочие №3, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, локация, если она пункт пропуска'  # noqa
    )
    use_oth3_mmpo = forms.ChoiceField(
        label='Эксплуатация, прочие №3, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, локация, если она ММПО'  # noqa
    )
    use_oth3_oez = forms.ChoiceField(
        label='Эксплуатация, прочие №3, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, локация, если она ОЭЗ'  # noqa
    )
    use_oth3_ztk = forms.ChoiceField(
        label='Эксплуатация, прочие №3, локация, если она ЗТК',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №3, локация, если она ЗТК'  # noqa
    )
    #
    use_oth4_rtu = forms.ChoiceField(
        label='Эксплуатация, прочие №4, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, прочие №4, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_oth4_ch = forms.ChoiceField(
        label='Эксплуатация, прочие №4, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, т.орган, в к-м, если он таможня'  # noqa
    )
    use_oth4_cp = forms.ChoiceField(
        label='Эксплуатация, прочие №4, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_oth4_ppr = forms.ChoiceField(
        label='Эксплуатация, прочие №4, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, локация, если она пункт пропуска'  # noqa
    )
    use_oth4_mmpo = forms.ChoiceField(
        label='Эксплуатация, прочие №4, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, локация, если она ММПО'  # noqa
    )
    use_oth4_oez = forms.ChoiceField(
        label='Эксплуатация, прочие №4, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, локация, если она ОЭЗ'  # noqa
    )
    use_oth4_ztk = forms.ChoiceField(
        label='Эксплуатация, прочие №4, локация, если она ЗТК',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №4, локация, если она ЗТК'  # noqa
    )
    #
    use_oth5_rtu = forms.ChoiceField(
        label='Эксплуатация, прочие №5, т.орган, в к-м, если он РТУ',
        required=True,
        # help_text='Эксплуатация, прочие №5, т.орган, в к-м, если он РТУ'  # noqa
    )
    use_oth5_ch = forms.ChoiceField(
        label='Эксплуатация, прочие №5, т.орган, в к-м, если он таможня',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №5, т.орган, в к-м, если он таможня'  # noqa
    )
    use_oth5_cp = forms.ChoiceField(
        label='Эксплуатация, прочие №5, т.орган, в к-м, если он т.пост',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №5, т.орган, в к-м, если он т.пост'  # noqa
    )
    use_oth5_ppr = forms.ChoiceField(
        label='Эксплуатация, прочие №5, локация, если она пункт пропуска',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №5, локация, если она пункт пропуска'  # noqa
    )
    use_oth5_mmpo = forms.ChoiceField(
        label='Эксплуатация, прочие №5, локация, если она ММПО',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №5, локация, если она ММПО'  # noqa
    )
    use_oth5_oez = forms.ChoiceField(
        label='Эксплуатация, прочие №5, локация, если она ОЭЗ',  # noqa
        required=True,
        # help_text='Эксплуатация, прочие №5, локация, если она ОЭЗ'  # noqa
    )
    use_oth5_ztk = forms.ChoiceField(
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
    is_si = forms.ChoiceField(
        label='Является ли текущее т.с. СИ',
        required=True,
        # help_text='Является ли текущее т.с. СИ'
    )
    si_flag = forms.ChoiceField(
        label='Девайсы текущего типа т.с., в плане отнесения к СИ',
        required=True,
        # help_text='Текущий тип т.с., в плане отнесения к СИ'
    )
    status_use = forms.ChoiceField(
        label='Статус по использованию',
        required=True,
        # help_text='Статус по использованию'
    )
    note3 = forms.CharField(
        label='Намерения использовать в будущем в ином месте (если есть)',
        max_length=200,
        required=True,
        # help_text='Намерения использовать в будущем в ином месте (если есть)'
    )
    id = forms.IntegerField(
        label='ID',
        required=True,
        # help_text='Номер записи в базе данных'
    )

    def __init__(self, *args, **kwargs):
        EMPTY_SITE = [(0, '----'),]
        super().__init__(*args, **kwargs)
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
        rtus_choices = EMPTY_SITE + [
            (item.pk, ', '.join([item.title, item.code])) for item in rtus if item.code  # noqa
        ]
        chs_choices = EMPTY_SITE + [
            (item.pk, ', '.join([item.title, item.code])) for item in chs if item.code  # noqa
        ]
        cps_choices = EMPTY_SITE + [
            (item.pk, ', '.join([item.title, item.code])) for item in cps if item.code  # noqa
        ]
        pprs_choices = EMPTY_SITE + [
            (item.pk, ', '.join([
                item.title,
                item.pptype.title,
                item.tow_country if item.tow_country else ''
            ])) for item in pprs
        ]
        mmpos_choices = EMPTY_SITE + [(item.pk, item.title) for item in mmpos]
        oezs_choices = EMPTY_SITE + [(item.pk, item.title) for item in oezs]
        ztks_choices = EMPTY_SITE + [(item.pk, item.title) for item in ztks]

        si_flag_choices = [
            (0, 'Могут относиться к СИ/инд, или нет'),
            (1, 'Обязаны относиться к  СИ/инд'),
            (2, 'Обязаны не относиться к СИ/инд')
        ]

        is_si_choices = [
            (0, 'Не подлежит к отнесению к СИ/инд'),
            (1, 'Является СИ'),
            (2, 'Является индикатором')
        ]

        serial_flag_choices = [
            (0, 'Могут иметь сер.номер, или нет'),
            (1, 'Обязаны иметь сер.номер'),
            (2, 'Обязаны не иметь сер.номер')
        ]

        self.fields['type'].choices = [
            (item.pk, item.title) for item in dev_types
        ]
        self.fields['cat_l2'].choices = [
            (item.pk, item.title) for item in dev_cat_l2_s
        ]
        self.fields['cat_l1'].choices = [
            (item.pk, item.title) for item in dev_cat_l1_s
        ]
        self.fields['source'].choices = [
            (item.pk, item.title) for item in dev_sour_s
        ]
        self.fields['status_use'].choices = [
            (item.pk, item.title) for item in status_types
        ]
        self.fields['acc1_rtu'].choices = rtus_choices
        self.fields['acc1_ch'].choices = chs_choices
        self.fields['acc1_cp'].choices = cps_choices
        self.fields['use_main1_rtu'].choices = rtus_choices
        self.fields['use_main1_ch'].choices = chs_choices
        self.fields['use_main1_cp'].choices = cps_choices
        self.fields['use_main1_ppr'].choices = pprs_choices
        self.fields['use_main1_mmpo'].choices = mmpos_choices
        self.fields['use_main1_oez'].choices = oezs_choices
        self.fields['use_main1_ztk'].choices = ztks_choices
        self.fields['use_oth1_rtu'].choices = rtus_choices
        self.fields['use_oth1_ch'].choices = chs_choices
        self.fields['use_oth1_cp'].choices = cps_choices
        self.fields['use_oth1_ppr'].choices = pprs_choices
        self.fields['use_oth1_mmpo'].choices = mmpos_choices
        self.fields['use_oth1_oez'].choices = oezs_choices
        self.fields['use_oth1_ztk'].choices = ztks_choices
        self.fields['use_oth2_rtu'].choices = rtus_choices
        self.fields['use_oth2_ch'].choices = chs_choices
        self.fields['use_oth2_cp'].choices = cps_choices
        self.fields['use_oth2_ppr'].choices = pprs_choices
        self.fields['use_oth2_mmpo'].choices = mmpos_choices
        self.fields['use_oth2_oez'].choices = oezs_choices
        self.fields['use_oth2_ztk'].choices = ztks_choices
        self.fields['use_oth3_rtu'].choices = rtus_choices
        self.fields['use_oth3_ch'].choices = chs_choices
        self.fields['use_oth3_cp'].choices = cps_choices
        self.fields['use_oth3_ppr'].choices = pprs_choices
        self.fields['use_oth3_mmpo'].choices = mmpos_choices
        self.fields['use_oth3_oez'].choices = oezs_choices
        self.fields['use_oth3_ztk'].choices = ztks_choices
        self.fields['use_oth4_rtu'].choices = rtus_choices
        self.fields['use_oth4_ch'].choices = chs_choices
        self.fields['use_oth4_cp'].choices = cps_choices
        self.fields['use_oth4_ppr'].choices = pprs_choices
        self.fields['use_oth4_mmpo'].choices = mmpos_choices
        self.fields['use_oth4_oez'].choices = oezs_choices
        self.fields['use_oth4_ztk'].choices = ztks_choices
        self.fields['use_oth5_rtu'].choices = rtus_choices
        self.fields['use_oth5_ch'].choices = chs_choices
        self.fields['use_oth5_cp'].choices = cps_choices
        self.fields['use_oth5_ppr'].choices = pprs_choices
        self.fields['use_oth5_mmpo'].choices = mmpos_choices
        self.fields['use_oth5_oez'].choices = oezs_choices
        self.fields['use_oth5_ztk'].choices = ztks_choices
        self.fields['si_flag'].choices = si_flag_choices
        self.fields['is_si'].choices = is_si_choices
        self.fields['serial_flag'].choices = serial_flag_choices
