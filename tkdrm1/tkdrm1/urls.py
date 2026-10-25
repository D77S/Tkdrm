from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

admin.site.site_url = 'http://127.0.0.1:8000/all_list/by_cpl5/'

schema_view = get_schema_view(
   openapi.Info(
      title="DeV API",
      default_version='v1',
      description="Документация для проекта Dev List",
      # terms_of_service="URL страницы с пользовательским соглашением",
      contact=openapi.Contact(email="1@1.ru"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
   #  path('', include('mainpage.urls', namespace='mainpage')),
    path('all_list/', include('core.urls', namespace='core'))
]

urlpatterns += [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
       schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), 
       name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), 
       name='schema-redoc'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
