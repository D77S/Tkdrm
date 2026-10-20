from rest_framework import serializers
from core.models import (
    Device,
    DevTypes
)
from custplaces.models import (
    CustPlaceToLocation,
    CustPlace1Use
)

class CustPlace1UseSerializer(serializers.ModelSerializer):
    rtuv2 = serializers.SerializerMethodField()
    custhousev2 = serializers.SerializerMethodField()
    custpostv2 = serializers.SerializerMethodField()
    class Meta:
        model = CustPlace1Use
        fields = (
            'id',
            'rtuv2',
            'custhousev2',
            'custpostv2'
        )

    def get_rtuv2(self, obj):
        if obj.rtu is None and obj.custhouse is None and obj.custpost is not None:
            return obj.custpost.upper_id.upper_id.title
        elif obj.rtu is None and obj.custhouse is not None and obj.custpost is None:
            return obj.custhouse.upper_id.title
        elif obj.rtu is not None and obj.custhouse is None and obj.custpost is None:
            return obj.rtu.title
    def get_custhousev2(self, obj):
        if obj.rtu is None and obj.custhouse is None and obj.custpost is not None:
            return obj.custpost.upper_id.title
        elif obj.rtu is None and obj.custhouse is not None and obj.custpost is None:
            return obj.custhouse.title
        elif obj.rtu is not None and obj.custhouse is None and obj.custpost is None:
            return None
    def get_custpostv2(self, obj):
        if obj.rtu is None and obj.custhouse is None and obj.custpost is not None:
            return obj.custpost.title
        elif obj.rtu is None and obj.custhouse is not None and obj.custpost is None:
            return None
        elif obj.rtu is not None and obj.custhouse is None and obj.custpost is None:
            return None


class CustPlaceToLocSerializer(serializers.ModelSerializer):
    cust_pl1 = CustPlace1UseSerializer(
        read_only=True,
        many=False
    )
    class Meta:
        model = CustPlaceToLocation
        fields = ('id', 'cust_pl1', 'is_main_for_cust')

class DevTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevTypes
        fields = ('id', 'title',)

class AllDevsSerializer(serializers.ModelSerializer):
    type = DevTypeSerializer(
        read_only=True,
        many=False
    )
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
    type = DevTypeSerializer(
        read_only=True,
        many=False
    )
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
