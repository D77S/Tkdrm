from rest_framework import serializers
from core.models import (
    Device,
    DevTypes,
    DevCatsL1,
    DevCatsL2,
    SourceTypes,
    StatusTypes,
    ServiceTypes,
    Contracts,
    Doings,
    RelContrDoing,
    DTCReal,
    DTCPotential
)
from custplaces.models import (
    CustPlaceToLocation,
    CustPlace1Use,
    CustPlace1Acc,
    LocationOfUse
)

from users.models import (
    TKDRMUser,
    Departments
)

class CommonCustPlaceMixin(serializers.Serializer):
    FIELDS = (
            'id',
            'rtuv2',
            'custhousev2',
            'custpostv2'
    )
    rtuv2 = serializers.SerializerMethodField()
    custhousev2 = serializers.SerializerMethodField()
    custpostv2 = serializers.SerializerMethodField()

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


class CustPlace1UseSerializer(serializers.ModelSerializer, CommonCustPlaceMixin):
    class Meta:
        model = CustPlace1Use
        fields = CommonCustPlaceMixin.FIELDS


class CustPlace1AccSerializer(serializers.ModelSerializer, CommonCustPlaceMixin):
    class Meta:
        model = CustPlace1Acc
        fields = CommonCustPlaceMixin.FIELDS


class LocUseSerializer(serializers.ModelSerializer):
    locname = serializers.SerializerMethodField()
    loctype = serializers.SerializerMethodField()
    class Meta:
        model = LocationOfUse
        fields = ('locname', 'loctype')
    def get_locname(self, obj):
        if obj.ppr:
            return obj.ppr.title
        elif obj.mmpo:
            return obj.mmpo.title
        elif obj.oez:
            return obj.oez.titile
        elif obj.ztk:
            return obj.ztk.title
        elif obj.svh:
            return obj.svh.title
        else:
            return None
    def get_loctype(self, obj):
        if obj.ppr:
            return obj.ppr.pptype.title
        elif obj.mmpo:
            return 'ММПО'
        elif obj.oez:
            return 'ОЭЗ'
        elif obj.ztk:
            return 'ЗТК'
        elif obj.svh and obj.svh.is_state:
            return 'СВХ'
        elif obj.svh and not obj.svh.is_state:
            return 'СВХ-ЮЛ'
        else:
            return None


class CustPlaceToLocSerializer(serializers.ModelSerializer):
    cust_pl1 = CustPlace1UseSerializer(
        read_only=True,
        many=False
    )
    loc = LocUseSerializer(
        read_only = True,
        many=False
    )
    main_for_dev = serializers.SerializerMethodField()
    class Meta:
        model = CustPlaceToLocation
        fields = (
            'id',
            'cust_pl1',
            'loc',
            'is_main_for_cust',
            'main_for_dev'
        )
    def get_main_for_dev(self, obj):
        dev = self.context.get('dev')
        if not dev:
            return None
        rel_obj = obj.from_relation.filter(to_dev=dev).first()
        if rel_obj:
            return rel_obj.is_main_for_dev
        return None


class DevCatL1Serializer(serializers.ModelSerializer):
    class Meta:
        model = DevCatsL1
        fields = ('id', 'title')


class DevCatL2Serializer(serializers.ModelSerializer):
    cat_l1 = DevCatL1Serializer(
        read_only=True,
        many=False
    )
    class Meta:
        model = DevCatsL2
        fields = ('id', 'title', 'cat_l1')


class DevTypeSerializer(serializers.ModelSerializer):
    category = DevCatL2Serializer(
        read_only=True,
        many=False
    )
    class Meta:
        model = DevTypes
        fields = (
            'id',
            'title',
            'category',
            'lifetime',
        )


class HoldDeptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = ('id', 'title')


class DevHoldSerializer(serializers.ModelSerializer):
    empl = CustPlace1UseSerializer(
        read_only=True,
        many=False
    )
    dept = HoldDeptSerializer(
        read_only=False,
        many=False
    )
    class Meta:
        model = TKDRMUser
        fields = (
            'id',
            'username',
            'first_name',
            'pater_name',
            'last_name',
            'email',
            'is_active',
            'empl',
            'dept'
        )


class DevSourSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceTypes
        fields = ('id', 'title')


class DevStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusTypes
        fields = ('id', 'title')


class DevServSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTypes
        fields = ('id', 'title')


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contracts
        fields = ['id', 'title', 'number', 'date_of']


class DoingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doings
        fields = ['id', 'title']


class DTCRealSerializer(serializers.ModelSerializer):
    class Meta:
        model = DTCReal
        fields = ['exact_moment']

class RelContrDoingSerializer(serializers.ModelSerializer):
    to_contract = ContractSerializer(
        read_only=True,
        many=False
    )
    to_doing = DoingSerializer(
        read_only=True,
        many=False
    )
    basis = serializers.SerializerMethodField()

    class Meta:
        model = RelContrDoing
        fields = ['id', 'to_contract', 'to_doing', 'basis']

    def get_basis(self, obj):
        device = self.context.get('device')
        if not device:
            return []
        reals = DTCReal.objects.filter(
            basis__dev=device,
            basis__reltocd=obj
        )
        return DTCRealSerializer(
            reals,
            read_only=True,
            many=True
        ).data


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
    holder = DevHoldSerializer(
        read_only=True,
        many=False
    )
    cats_corresp = serializers.SerializerMethodField()
    cp1_acc = CustPlace1AccSerializer(
        read_only=True,
        many=False
    )
    sour_type = DevSourSerializer(
        read_only=True,
        many=False
    )
    status_use = DevStatusSerializer(
        read_only=True,
        many=False
    )
    service_type = DevServSerializer(
        read_only=True,
        many=False
    )
    rels_of_work = CustPlaceToLocSerializer(
        read_only=True,
        many=True
    )
    rels_of_contracts = serializers.SerializerMethodField()
    class Meta:
        model = Device
        fields = (
            'id',
            'type',
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
            'cats_corresp',
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
    def to_representation(self, instance):
        self.context['dev'] = instance
        return super().to_representation(instance)
    def get_cats_corresp(self, obj):
        if obj.cat_number_c == obj.cat_number_f:
            return True
        return False
    def get_rels_of_contracts(self, obj):
        context = self.context.copy()
        context['device'] = obj
        queryset = obj.rels_of_contracts.all()
        return RelContrDoingSerializer(queryset, many=True, context=context).data
