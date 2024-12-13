from django.contrib import admin
from .models import Rtu, CustHouse, CustPost

empty_value_display = 'Не задано'


@admin.register(Rtu)
class CoreRtuAdmin(admin.ModelAdmin):
    exclude=('level',)
    list_display=('title',
                  'code')
    list_editable=('code',)
    list_per_page=10
    ordering=('title',)


@admin.register(CustHouse, CustPost)
class CoreCustAdmin(CoreRtuAdmin):
    list_display=('title',
                  'code',
                  'upper_id')
    list_editable=('code',
                   'upper_id')


# admin.site.register(Rtu, CoreRtuAdmin)
# admin.site.register(CustHouse, CoreCustAdmin)
# admin.site.register(CustPost, CoreCustAdmin)
