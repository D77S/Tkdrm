from rest_framework import serializers
from core.models import Device
from custplaces.models import CustPlaceToLocation


class CustPlaceToLocSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustPlaceToLocation
        fields = ('cust_pl1', 'is_main_for_cust')

class AllDevsSerializer(serializers.ModelSerializer):
    # По полю rels_of_work вернется список.
    # В большинстве случаев он будет из единственного объекта.
    # Но если все-таки из нескольких, то для задачи "общий список"
    # из них нужен тот, у которого is_main_for_cust=True.
    # Таких будет не больше одного (констрейт в БД).
    # Если с таким флагом их будет ноль, то
    # для задачи "общий список" - брать из списка любой.
    rels_of_work = CustPlaceToLocSerializer(
        read_only=True,
        many=True
    )
    class Meta:
        model = Device
        fields = (
            'id',
            'rels_of_work',
            'type',
            'serial',
        )

class DevDetailSerializer(serializers.ModelSerializer):
    rels_of_work = CustPlaceToLocSerializer(
        read_only=True,
        many=True
    )
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
            'service_type',
            'rels_of_work',
            'rels_of_contracts',
            'note1',
            'note2',
            'note3'
        )
