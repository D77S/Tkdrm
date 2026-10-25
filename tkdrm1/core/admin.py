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

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    pass

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