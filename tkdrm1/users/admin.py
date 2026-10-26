from django.contrib import admin
from users.models import Departments, TKDRMUser

admin.site.empty_value_display = 'Не задано'

@admin.register(Departments)
class DepartmentsAdmin(admin.ModelAdmin):
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

@admin.register(TKDRMUser)
class TKDRMUserAdmin(admin.ModelAdmin):
    list_display_links = ['id']
    list_display = [
        'id',
        'first_name',
        'pater_name',
        'last_name',
        'empl',
        'dept'
    ]
    list_editable = [
        'first_name',
        'pater_name',
        'last_name',
        'empl',
        'dept'
    ]
    autocomplete_fields = ('empl',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_per_page = 10
    ordering = ('id',)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'dept', 
            'empl__rtu', 
            'empl__custhouse', 
            'empl__custpost'
        )
