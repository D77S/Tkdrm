"""."""
from django.urls import path

from core import views

app_name = 'core'

urlpatterns = [
    path('by_cpl/', views.all_list_by_cpl, name='all_list_by_cpl'),
    path('by_cpl2/', views.all_list_by_cpl2, name='all_list_by_cpl2'),
    path('by_cpl/create', views.dev_create, name='dev_create'),
    path('by_cpl/<int:pk>/', views.dev_detail, name='dev_detail'),
    path('by_cpl/<int:pk>/edit', views.dev_edit, name='dev_edit'),
    path('by_cpl/<int:pk>/del', views.dev_delete, name='dev_delete'),
]
