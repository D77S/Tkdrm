from django.contrib import admin

from .models import Rtu, CustHouse, CustPost

admin.site.register(Rtu)
admin.site.register(CustHouse)
admin.site.register(CustPost)