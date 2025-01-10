from django.contrib import admin
from .models import (
    Rtu,
    CustHouse,
    CustPost,
    # CustPlace1,
    CustPlace2,
    Device,
    SourceTypes,
    # Owner
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


# @admin.register(CustPlace1)
# class CoreCustPlase1Admin(admin.ModelAdmin):
#     ordering = ('id',)
#     list_per_page = 14
#     list_filter = ('rtu', 'custhouse', 'custpost')


@admin.register(CustPlace2)
class CoreCustPlace2Admin(admin.ModelAdmin):
    list_display = ('title',
                    'code',
                    'upper_id')
    # list_editable = ('code',
    #                  'upper_id')
    list_per_page = 14
    ordering = ('title',)
    list_filter = ('level',)
    raw_id_fields = ('upper_id',)


@admin.register(SourceTypes)
class CoreSourceTypesAdmin(admin.ModelAdmin):
    pass


# @admin.register(Owner)
# class CoreOwnerAdmin(admin.ModelAdmin):
#     list_per_page = 14


@admin.register(Device)
class CoreDeviceAdmin(admin.ModelAdmin):
    pass
