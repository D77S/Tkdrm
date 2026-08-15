from django import forms
from django.db import models
from core.models import DevCatsL1, DevCatsL2, Device, RelContrDoing
from custplaces.models import CustPlace1Acc, CustPlaceToLocation
from users.models import TKDRMUser

class DevDetailForm(forms.ModelForm):
    #
    #  Форма для отображения одного объекта Device для просмотра.
    #  Не для редактирования и не для создания.
    #
    #  Поля, вычисляемые на лету из других полей.
    #  Их надо прописать сначала пустыми, чтобы можно было задать порядок отображения всех полей
    date_prolong_f = forms.DateField(
        label='Дата ввода в эксплуатацию при последнем продлении срока службы (если было)',
        required=False,
        initial=None,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    date_prod_expired_f = forms.DateField(
        label='Дата истечения срока службы (с учетом его последнего продления, если было)',
        required=False,
        initial=None,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    cat_number_c_f = forms.IntegerField(
        label='Номер категории расчетный (от 1 до 3)',
        required=False,
        initial=None,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    #  Поля вышестоящих типов относительно типа объекта
    dev_cat_l2 = forms.CharField(
        label='Вышестоящий тип уровня 2',
    )
    dev_cat_l1 = forms.CharField(
        label='Вышестоящий тип уровня 1',
    )

    class Meta:
        model = Device
        fields = [
            'type',
            'dev_cat_l2',
            'dev_cat_l1',
            'sub_type',
            'serial',
            'inventary',
            'holder',
            'date_prod',
            'date_expl',
            'date_prolong_f',
            'warr_period',
            'date_prod_expired_f',
            'date_verif',
            'cat_number_c_f',
            'cat_number_f',
            'cp1_acc',
            'sour_type',
            'cost',
            'condition',
            'upper_id',
            'is_si',
            'is_stud',
            'status_use',
            'service_type',
            'rels_of_work',
            'rels_of_contracts',
            'note1',
            'note2',
            'note3'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #  По всем полям типа O2M (FK) обрезаем все кверисеты
        #  до единственного значения в поля выбора.
        #  Меняем null на "не задано".
        #  Отключаем редактирование по всем полям.
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                curr_item = getattr(self.instance, field_name)
                if curr_item:
                    model_field = self.instance._meta.get_field(field_name)
                    if isinstance(model_field, models.ForeignKey):
                        field.queryset = curr_item.__class__.objects.filter(pk=curr_item.pk)
                        #  Для поля 'type' ещё зададим два зависимых поля формы
                        if field_name == 'type' and self.fields.get('dev_cat_l2'):
                            self.fields['dev_cat_l2'].initial = curr_item.category
                        if field_name == 'type' and self.fields.get('dev_cat_l1'):
                            self.fields['dev_cat_l1'].initial = curr_item.category.cat_l1
                    elif isinstance(model_field, models.ManyToManyField):
                        pass
                else:
                    field.queryset = field.queryset.none()
            if getattr(self.instance, field_name, None) is None:
                self.fields[field_name].widget.attrs['placeholder'] = 'Не задано'
            self.fields[field_name].widget.attrs['disabled'] = 'disabled'


        #  М2М поля
        #  'rels_of_contracts'
        if self.fields.get('rels_of_contracts'):
            curr_manager = getattr(self.instance, 'rels_of_contracts')
            self.fields['rels_of_contracts'].queryset = curr_manager.select_related(
                'to_contract',
                'to_doing'
            ).all()
        #  'rels_of_work'
        if self.fields.get('rels_of_work'):
            curr_manager = getattr(self.instance, 'rels_of_work')
            self.fields['rels_of_work'].queryset = curr_manager.select_related(
                'cust_pl1',
                'loc'
            ).all()

        # if self.fields.get('upper_id'):
        #     curr_item = getattr(self.instance, 'upper_id')
        #     if curr_item:
        #         self.fields['upper_id'].queryset = self.fields['upper_id'].queryset.filter(pk=curr_item.pk)
        #     else:
        #         self.fields['upper_id'].queryset = self.fields['upper_id'].queryset.none()


        #  Вычисляем значения полей, вычисляемые на лету из других полей
        if self.fields.get('date_prolong_f'):
            self.fields[
                'date_prolong_f'
            ].initial=self.instance.date_prolong.strftime('%d.%m.%Y')
        if self.fields.get('date_prod_expired_f'):
            self.fields[
                'date_prod_expired_f'
            ].initial=self.instance.date_prod_expired.strftime('%d.%m.%Y')
        if self.fields.get('cat_number_c_f'):
            self.fields[
                'cat_number_c_f'
            ].initial=self.instance.cat_number_c

        if  self.fields.get('upper_id'):
            self.fields['upper_id'].empty_label = 'Не задано'


class DevEditForm(forms.ModelForm):
    #  Форма для отображения одного объекта Device для редактирования.
    #
    pass

    class Meta:
        model = Device
        fields = [
            'type',
            'sub_type',
            'serial',
            'inventary',
            'holder',
            'date_prod',
            'date_expl',
            'warr_period',
            'date_verif',
            'cat_number_f',
            'cp1_acc',
            'sour_type',
            'cost',
            'condition',
            'upper_id',
            'is_si',
            'is_stud',
            'status_use',
            'service_type',
            'rels_of_work',
            'rels_of_contracts',
            'note1',
            'note2',
            'note3'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #  Предзагрузка кверисетов для полей, имеющих зависимости.
        if self.fields.get('holder'):
            self.fields['holder'].queryset = TKDRMUser.objects.select_related(
                'dept',
                'empl__rtu',
                'empl__custhouse',
                'empl__custpost'
            )
        else:
            self.fields['holder'].queryset = self.fields['holder'].queryset.none()
        if self.fields.get('cp1_acc'):
            self.fields['cp1_acc'].queryset = CustPlace1Acc.objects.select_related(
                'rtu',
                'custhouse',
                'custpost'
            )
        else:
            self.fields['cp1_acc'].queryset = self.fields['cp1_acc'].queryset.none()

        if self.fields.get('upper_id'):
            self.fields['upper_id'].queryset = Device.objects.select_related(
                'type'
            )
        else:
            self.fields['upper_id'].queryset = self.fields['upper_id'].queryset.none()

        if self.fields.get('rels_of_work'):
            self.fields['rels_of_work'].queryset = CustPlaceToLocation.objects.prefetch_related(
                'cust_pl1__rtu',
                'cust_pl1__custhouse',
                'cust_pl1__custpost',
                'loc__ppr__pptype',
                'loc__mmpo',
                'loc__oez',
                'loc__ztk'
            )
        else:
            self.fields['rels_of_work'].queryset = self.fields['rels_of_work'].queryset.none()
        if self.fields.get('rels_of_contracts'):
            self.fields['rels_of_contracts'].queryset = RelContrDoing.objects.prefetch_related(
                'to_doing',
                'to_contract'
            )
        else:
            self.fields['rels_of_contracts'].queryset = self.fields['rels_of_contracts'].queryset.none()
 
        #  Для поля cp1_acc удаляем из перечня возможных вариантов
        #  выбор два варианта с текстом 'ТНП'
        if self.fields.get('cp1_acc'):
            temp_qs = self.fields['cp1_acc'].queryset.all()
            for item in temp_qs:
                if ((item.rtu and item.rtu.title == 'ТНП') or
                    (item.custhouse and item.custhouse.title == 'ТНП')):
                    self.fields['cp1_acc'].queryset = self.fields[
                        'cp1_acc'].queryset.exclude(id=item.id)

        #  Меняем null на "не задано".
        for field_name in self.fields:
            if getattr(self.instance, field_name, None) is None:
                self.fields[field_name].widget.attrs['placeholder'] = 'Не задано'
