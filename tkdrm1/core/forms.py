from django import forms
from django.db import models
from core.models import Device

class DevDetailForm(forms.ModelForm):
    #
    #  Форма для отображения одного объекта Device для просмотра.
    #  Не для редактирования и не для создания.
    #
    #  Поля, вычисляемые на лету из других полей.
    #  Их надо прописать сначала пустыми, чтобы можно было задать порядок отображения всех полей
    date_prolong = forms.DateField(
        label='Дата ввода в эксплуатацию при последнем продлении срока службы (если было)',
        required=False,
        disabled=True,
        initial=None,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    date_prod_expired = forms.DateField(
        label='Дата истечения срока службы (с учетом его последнего продления, если было)',
        required=False,
        disabled=True,
        initial=None,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    cat_number_c = forms.IntegerField(
        label='Номер категории расчетный (от 1 до 3)',
        required=False,
        disabled=True,
        initial=None,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    #  Поля вышестоящих типов относительно типа объекта
    dev_cat_l2 = forms.CharField(
        label='Вышестоящий тип уровня 2',
        required=False,
        disabled=True,
        initial=None,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    dev_cat_l1 = forms.CharField(
        label='Вышестоящий тип уровня 1',
        required=False,
        disabled=True,
        initial=None,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
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
            'date_prolong',
            'warr_period',
            'date_prod_expired',
            'date_verif',
            'cat_number_c',
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

        self.fields['dev_cat_l2'] = forms.CharField(
            label='Вышестоящий тип уровня 2',
            initial=self.instance.type.category
            )
        self.fields['dev_cat_l1'] = forms.CharField(
            label='Вышестоящий тип уровня 1',
            initial=self.instance.type.category.cat_l1
            )

        if self.instance and self.instance.pk:
            #  Обрезаем кверисеты, редактировать поля не будем, все наборы не нужны
            for field_name, field in self.fields.items():
                if isinstance(field, forms.ModelChoiceField):
                    # field.disable = True
                    current_relation = getattr(self.instance, field_name)
                    model_field = self.instance._meta.get_field(field_name)
                    if isinstance(model_field, models.ManyToManyField):
                        relation_manager = getattr(self.instance, field_name)
                        field.queryset = relation_manager.all()
                    else:
                        current_relation = getattr(self.instance, field_name)
                        if current_relation:
                            field.queryset = current_relation.__class__.objects.filter(pk=current_relation.pk)
                        else:
                            field.queryset = field.queryset.none()
            #  Вычисляем значения полей, вычисляемые на лету из других полей
            if hasattr(self.instance, 'date_prolong'):
                self.fields['date_prolong'] = forms.DateField(
                    label='Дата ввода в эксплуатацию при последнем продлении срока службы (если было)',
                    required=False,
                    disabled=True,
                    initial=getattr(self.instance, 'date_prolong')
                )
            if hasattr(self.instance, 'date_prod_expired'):
                self.fields['date_prod_expired'] = forms.DateField(
                    label='Дата истечения срока службы (с учетом его последнего продления, если было)',
                    required=False,
                    disabled=True,
                    initial=getattr(self.instance, 'date_prod_expired')
                )
            if hasattr(self.instance, 'cat_number_c'):
                self.fields['cat_number_c'] = forms.IntegerField(
                    label='Номер категории расчетный (от 1 до 3)',
                    required=False,
                    disabled=True,
                    initial=getattr(self.instance, 'cat_number_c')
                )     
            #  Для полей, где value is None, замена None на "Не задано"
            #  Для всех
            for field_name, field in self.fields.items():
                if getattr(self.instance, field_name, None) is None:
                    field.widget.attrs['placeholder'] = 'Не задано'
            # Отдельно для FK
            self.fields['upper_id'].empty_label = 'Не задано'

        #  Для всех полей отключение редактирования, требуется только отображение
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['disabled'] = 'disabled'


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

        #  Предзагрузка
        self.fields['type'].queryset = (
            self.fields['type'].queryset.select_related('category__cat_l1')
        )

        #  Для поля cp1_acc удаляем из перечня возможных вариантов
        #  выбор два варианта с текстом 'ТНП'
        if self.fields['cp1_acc']:
            temp_qs = self.fields['cp1_acc'].queryset.all()
            for item in temp_qs:
                if ((item.rtu and item.rtu.title == 'ТНП') or
                    (item.custhouse and item.custhouse.title == 'ТНП')):
                    self.fields['cp1_acc'].queryset = self.fields[
                        'cp1_acc'].queryset.exclude(id=item.id)

        #  Для полей, где value is None, замена None на "Не задано"
        for field_name, field in self.fields.items():
            if getattr(self.instance, field_name, None) is None:
                field.widget.attrs['placeholder'] = 'Не задано'
