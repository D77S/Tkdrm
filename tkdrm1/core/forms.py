from django import forms
from core.models import (Device,
                         DevTypes,
                         DevCatsL2,
                         DevCatsL1)


class DevDetailForm(forms.Form):
    type = forms.ChoiceField(
        choices=[],
        label='Тип прибора',
        required=True,
        # help_text='Тип прибора'
    )
    subtype = forms.CharField(
        label='Подтип',
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
        curr_dev = Device.objects.get(id=self.initial['id'])
        dev_types = DevTypes.objects.all()
        # dev_cat_l2_s = DevCatsL2.objects.all()
        type_choices = [
            (dev_type.pk, dev_type.title) for dev_type in dev_types
        ]
        self.fields['type'].choices = type_choices

        # curr = None
        # if self.initial:
        #     curr = self.initial.get('subtype')
        # if curr is None:
        #     self.fields.pop('subtype')
