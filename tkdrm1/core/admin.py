from django.contrib import admin
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
class CoreSourceTypesAdmin(admin.ModelAdmin):
    pass


@admin.register(Device)
class CoreDeviceAdmin(admin.ModelAdmin):
    pass
