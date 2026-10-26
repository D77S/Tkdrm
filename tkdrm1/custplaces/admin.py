from django.contrib import admin

from custplaces.models import (
    Rtu,
    CustHouse,
    CustPost,
    PprType,
    Ppr,
    Mmpo,
    Oez,
    Ztk,
    Svh,
    CustPlace1Acc,
    CustPlace1Use,
    LocationOfUse,
    CustPlaceToLocation
)

admin.site.empty_value_display = 'Не задано'

@admin.register(Rtu)
class RtuAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
        'address',
        'code',
        'ztk_allowed',
        'standalone_allowed'
    ]
    list_editable = [
        'title',
        'address',
        'code',
        'ztk_allowed',
        'standalone_allowed'
    ]
    list_per_page = 10
    ordering = ('title',)


@admin.register(CustHouse)
class CustHouseAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
        'address',
        'code',
        'upper_id',
        'ztk_allowed',
        'standalone_allowed'
    ]
    list_editable = [
        'title',
        'address',
        'code',
        'upper_id',
        'ztk_allowed',
        'standalone_allowed'
    ]
    list_per_page = 10
    ordering = ('title',)


@admin.register(CustPost)
class CustPostAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
        'address',
        'code',
        'upper_id',
        'ztk_allowed',
        'standalone_allowed'
    ]
    list_editable = [
        'title',
        'address',
        'code',
        'upper_id',
        'ztk_allowed',
        'standalone_allowed'
    ]
    list_per_page = 10
    ordering = ('title',)


@admin.register(PprType)
class PprTypeAdmin(admin.ModelAdmin):
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

@admin.register(Ppr)
class PprAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'pptype',
        'title',
        'tow_country'
    ]
    list_editable = [
        'pptype',
        'title',
        'tow_country'
    ]
    list_per_page = 10
    ordering = ('title',)

@admin.register(Mmpo)
class MmpoAdmin(admin.ModelAdmin):
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

@admin.register(Oez)
class OezAdmin(admin.ModelAdmin):
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

@admin.register(Ztk)
class ZtkAdmin(admin.ModelAdmin):
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

@admin.register(Svh)
class SvhAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'title',
        'is_state'
    ]
    list_editable = [
        'title',
        'is_state'
    ]
    list_per_page = 10
    ordering = ('title',)

@admin.register(CustPlace1Acc)
class CustPlace1AccAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'rtu',
        'custhouse',
        'custpost'
    ]

    list_editable = [
        'rtu',
        'custhouse',
        'custpost'
    ]
    search_fields = ('rtu__title', 'custhouse__title', 'custpost__title', 'rtu__code', 'custhouse__code', 'custpost__code')

    list_per_page = 10
    ordering = ('id',)

@admin.register(CustPlace1Use)
class CustPlace1UseAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'rtu',
        'custhouse',
        'custpost',
        'ztk_allowed',
        'standalone_allowed'
    ]

    list_editable = [
        'rtu',
        'custhouse',
        'custpost',
        'ztk_allowed',
        'standalone_allowed'
    ]
    list_per_page = 10
    ordering = ('id',)

@admin.register(LocationOfUse)
class LocationOfUseAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'ppr',
        'mmpo',
        'oez',
        'ztk',
        'svh'
    ]

    list_editable = [
        'ppr',
        'mmpo',
        'oez',
        'ztk',
        'svh'
    ]
    list_per_page = 5
    ordering = ('id',)

@admin.register(CustPlaceToLocation)
class CustPlaceToLocationAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'cust_pl1',
        'loc',
        'is_main_for_cust'
    ]
    list_editable = [
        'cust_pl1',
        'loc',
        'is_main_for_cust'
    ]
    search_fields = (
        'loc__ppr__title', 
        'loc__mmpo__title', 
        'loc__oez__title', 
        'loc__ztk__title', 
        'loc__svh__title',
        'cust_pl1__custpost__title'
    )
    list_per_page = 5
    ordering = ('id',)
