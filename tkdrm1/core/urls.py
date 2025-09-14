"""."""
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('by_cpl/', views.all_list_by_cpl, name='all_list_by_cpl'),
    path('by_cpl/<int:pk>/', views.dev_detail, name='dev_detail'),
    path('by_cpl/2/<int:pk>/', views.dev_detail2, name='dev_detail2')
]
