from django.contrib import admin
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

@admin.register(Device)
class CoreDeviceAdmin(admin.ModelAdmin):
    pass
