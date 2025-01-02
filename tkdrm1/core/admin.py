from django.contrib import admin
from .models import (
    Rtu,
    CustHouse,
    CustPost,
    Device,
    Owner,
    CustPlace
)

admin.site.empty_value_display = 'Не задано'


@admin.register(Rtu)
class CoreRtuAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'code')
    # list_editable = ('code',)
    list_per_page = 14
    ordering = ('title',)


@admin.register(CustHouse)
class CoreCustHouseAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'code',
                    'upper_id')
    # list_editable = ('code',
    #                  'upper_id')
    list_per_page = 14
    ordering = ('title',)
    raw_id_fields = ('upper_id',)


@admin.register(CustPost)
class CoreCustPostAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'code',
                    'upper_id')
    # list_editable = ('code',
    #                  'upper_id')
    list_per_page = 14
    ordering = ('title',)
    raw_id_fields = ('upper_id',)


@admin.register(Device)
class CoreDeviceAdmin(admin.ModelAdmin):
    pass


@admin.register(Owner)
class CoreOwnerAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_per_page = 14
    list_filter = ('rtu', 'custhouse', 'custpost')


@admin.register(CustPlace)
class CoreCustPlaceAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'code',
                    'upper_id')
    # list_editable = ('code',
    #                  'upper_id')
    list_per_page = 14
    ordering = ('title',)
    list_filter = ('level',)
    raw_id_fields = ('upper_id',)
