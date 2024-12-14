from django.contrib import admin
from .models import Rtu, CustHouse, CustPost, CustPlace

admin.site.empty_value_display = 'Не задано'


@admin.register(Rtu)
class CoreRtuAdmin(admin.ModelAdmin):
    exclude = ('level',)
    list_display = ('title',
                    'code')
    list_editable = ('code',)
    list_per_page = 14
    ordering = ('title',)


@admin.register(CustHouse)
class CoreCustHouseAdmin(CoreRtuAdmin):
    list_display = ('title',
                    'code',
                    'upper_id')
    list_editable = ('code',
                     'upper_id')
    raw_id_fields = ('upper_id',)


@admin.register(CustPost)
class CoreCustPostAdmin(CoreRtuAdmin):
    list_display = ('title',
                    'code',
                    'upper_id')
    list_editable = ('code',
                     'upper_id')
    raw_id_fields = ('upper_id',)


@admin.register(CustPlace)
class CoreCustPlaceAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'code',
                    'upper_id')
    list_editable = ('code',
                     'upper_id')
    list_per_page = 14
    ordering = ('title',)
    list_filter = ('level',)
    raw_id_fields = ('upper_id',)
