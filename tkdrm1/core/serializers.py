from rest_framework import serializers
from core.models import Device

class AllDevsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = (
            'id',
            'rels_of_work',
            'type',
            'serial',
        )

class DevDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = (
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
            'rels_of_work',
            'rels_of_contracts',
            'note1',
            'note2',
            'note3'
        )
