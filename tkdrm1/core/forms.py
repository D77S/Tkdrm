from django import forms
from core.models import (
    # Device,
    DevTypes,
    DevCatsL2,
    DevCatsL1,
    SourceTypes
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
    id = forms.IntegerField(
        label='ID',
        required=True,
        # help_text='Номер записи в базе данных'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # curr_dev = Device.objects.get(id=self.initial['id'])
        dev_types = DevTypes.objects.all()
        dev_cat_l2_s = DevCatsL2.objects.all()
        dev_cat_l1_s = DevCatsL1.objects.all()
        dev_sour_s = SourceTypes.objects.all()
        self.fields['type'].choices = [
            (dev_type.pk, dev_type.title) for dev_type in dev_types
        ]
        self.fields['cat_l2'].choices = [
            (cat_l2.pk, cat_l2.title) for cat_l2 in dev_cat_l2_s
        ]
        self.fields['cat_l1'].choices = [
            (cat_l1.pk, cat_l1.title) for cat_l1 in dev_cat_l1_s
        ]
        self.fields['source'].choices = [
            (sour.pk, sour.title) for sour in dev_sour_s
        ]

        # curr = None
        # if self.initial:
        #     curr = self.initial.get('subtype')
        # if curr is None:
        #     self.fields.pop('subtype')
