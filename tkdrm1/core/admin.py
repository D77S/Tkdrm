from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.db import models
from django.forms import Textarea
from core.models import (
    SourceTypes,
    StatusTypes,
    ServiceTypes,
    DevCatsL1,
    DevCatsL2,
    DevTypes,
    Doings,
    Contracts,
    RelContrDoing,
    DTCReal,
    Device,
    DTCPotential,
    RelToDev
)
from custplaces.models import Ppr, Mmpo, Oez, Ztk, Svh

admin.site.empty_value_display = 'Не задано'


@admin.register(SourceTypes)
class SourceTypesAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
    ]
    list_editable = [
        'title',
    ]
    list_per_page = 10
    ordering = ('title',)

@admin.register(StatusTypes)
class StatusTypesAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
    ]
    list_editable = [
        'title',
    ]
    list_per_page = 10
    ordering = ('title',)

@admin.register(ServiceTypes)
class ServiceTypesAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
    ]
    list_editable = [
        'title',
    ]
    list_per_page = 10
    ordering = ('title',)

@admin.register(DevCatsL1)
class DevCatL1Admin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
    ]
    list_editable = [
        'title',
    ]
    list_per_page = 10
    ordering = ('title',)

@admin.register(DevCatsL2)
class DevCatL2Admin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
    ]
    list_editable = [
        'title',
    ]
    list_per_page = 10
    ordering = ('title',)

@admin.register(DevTypes)
class DevTypesAdmin(admin.ModelAdmin):
    formfield_overrides = {
         models.JSONField: {
             'widget': Textarea(attrs={
                 'rows': 2, 'style': 'width: 100%;'
                 })
             },
    }
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
        'category',
        'lifetime',
        'serial_flag',
        'upper_dev_flag',
        'si_flag',
        'sub_types'
    ]
    list_editable = [
        'title',
        'category',
        'lifetime',
        'serial_flag',
        'upper_dev_flag',
        'si_flag',
        'sub_types'
    ]
    search_fields = ('title',)
    list_per_page = 10
    ordering = ('title',)

@admin.register(Doings)
class DoingsAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
    ]
    list_editable = [
        'title',
    ]
    list_per_page = 10
    ordering = ('id',)

@admin.register(Contracts)
class ContractsAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
        'number',
        'date_of',
        'date_start',
        'date_end'
    ]
    list_editable = [
        'title',
        'number',
        'date_of',
        'date_start',
        'date_end' 
    ]
    list_per_page = 10
    ordering = ('id',)


@admin.register(RelContrDoing)
class RelContrDoingAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'to_doing',
        'to_contract',
        'min_count',
        'max_count'
    ]
    list_editable = [
        'to_doing',
        'to_contract',
        'min_count',
        'max_count'
    ]
    search_fields = ('to_contract__title', 'to_doing__title', 'to_contract__number')
    list_per_page = 10
    ordering = ('id',)

@admin.register(DTCReal)
class DTCRealAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'basis',
        'exact_moment'
    ]
    list_editable = [
    #     'basis',
        'exact_moment'
    ]
    list_per_page = 10
    ordering = ('id',)

class DTCPotentialInline(admin.TabularInline):
    """Инлайн для управления вхождением прибора в гос.контракты."""
    model = DTCPotential
    extra = 1  # Количество пустых строк для добавления новых связей
    autocomplete_fields = ('reltocd',)

class RelToDevInline(admin.TabularInline):
    """Инлайн для управления местами эксплуатации прибора."""
    model = RelToDev
    extra = 1
    # Позволяет удобно выбирать локации и сразу проставлять флаг приоритетности
    autocomplete_fields = ('to_rel',)

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'type',
        'serial',
        'get_rels_of_work'
    ]
    autocomplete_fields = (
        'type',
        'holder', 
        'cp1_acc', 
        'upper_id', 
        'rels_of_work', 
        'rels_of_contracts'
    )
    exclude = ('rels_of_work', 'rels_of_contracts')
    search_fields = ('serial', 'inventary', 'type__title')
    inlines = [RelToDevInline, DTCPotentialInline]
    list_per_page = 20
    ordering = ('id',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match and request.resolver_match.url_name.endswith('_changelist'):
            return qs.select_related(
                'type__category__cat_l1',
                'sour_type',
                'status_use',
                'service_type'
            )
        return qs.select_related('type', 'holder', 'cp1_acc', 'status_use', 'service_type')
        # qs = qs.select_related(
        #     'type',
        #     'type__category',
        #     'type__category__cat_l1',
        #     'holder',
        #     'holder__dept',
        #     'holder__empl',
        #     'cp1_acc',
        #     'cp1_acc__rtu',
        #     'cp1_acc__custhouse',
        #     'cp1_acc__custpost',
        #     'sour_type',
        #     'upper_id',
        #     'status_use',
        #     'service_type').prefetch_related(
        #         'from_dev__to_rel__cust_pl1',
        #         'from_dev__to_rel__loc',
        #         'f_dev_to_doing__reltocd__to_doing',
        #         'f_dev_to_doing__reltocd__to_contract',
        #         'f_dev_to_doing__from_dtcp_to_dtcr'
        #         )
        # return qs

    @admin.display(description='Связи по эксплуатации')
    def get_rels_of_work(self, obj):
        to_out = []
        for item in obj.rels_of_work.all():
            if item.loc:
                if isinstance(item.loc.to_site, Ppr):
                    item_loc_temp = ' '.join([item.loc.to_site.pptype.title, item.loc.to_site.title])
                elif isinstance(item.loc.to_site, Mmpo):
                    item_loc_temp = ' '.join(['ММПО', item.loc.to_site.title])
                elif isinstance(item.loc.to_site, Oez):
                    item_loc_temp = ' '.join(['ОЭЗ', item.loc.to_site.title])
                elif isinstance(item.loc.to_site, Ztk):
                    item_loc_temp = ' '.join(['ЗТК', item.loc.to_site.title])
                elif isinstance(item.loc.to_site, Svh) and item.loc.to_site.is_state:
                    item_loc_temp = ' '.join(['СВХ', item.loc.to_site.title])
                elif isinstance(item.loc.to_site, Svh) and not item.loc.to_site.is_state:
                    item_loc_temp = ' '.join(['СВХ-ЮЛ', item.loc.to_site.title])
                else:
                    item_loc_temp = item.loc.to_site.title
                to_out.append(' в '.join([item.cust_pl1.to_cp.title, item_loc_temp]))
            else:
                to_out.append(' '.join([item.cust_pl1.to_cp.title, 'без локации']))
        return '; '.join(to_out)

@admin.register(DTCPotential)
class DTCPotentialAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'dev',
        'reltocd'
    ]
    list_editable = [
    ]
    list_per_page = 10
    ordering = ('id',)

@admin.register(RelToDev)
class RelToDevAdmin(admin.ModelAdmin):
    pass

# Убираем стандартную модель Group
if admin.site.is_registered(Group):
    admin.site.unregister(Group)

# Убираем старую стандартную модель User
if admin.site.is_registered(User):
    admin.site.unregister(User)