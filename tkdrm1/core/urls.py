"""."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core import views

app_name = 'core'

router = DefaultRouter()
router.register('by_cpl5', views.DevViewSet, basename='dev_vs')

urlpatterns = [
    # Для REST API
    # Для вьюсета REST API
    path('', include(router.urls)),
    # # Для высокоуровневых классов REST API
    # path('by_cpl4/', views.AllDevList.as_view()),
    # path('by_cpl4/<int:pk>/', views.DevR.as_view()),
    # path('by_cpl4/create', views.DevC.as_view()),
    # path('by_cpl4/<int:pk>/edit', views.DevU.as_view()),
    # path('by_cpl4/<int:pk>/del', views.DevD.as_view()),
    # # Для низкоуровневых классов REST API
    # path('by_cpl3/', views.APIAllList.as_view()),
    # path('by_cpl3/<int:pk>/', views.APIDetail.as_view()),
    # path('by_cpl3/create', views.APIDetail.as_view()),
    # path('by_cpl3/<int:pk>/edit', views.APIDetail.as_view()),
    # path('by_cpl3/<int:pk>/del', views.APIDetail.as_view()),
    # # Для функций REST API
    # path('by_cpl2/', views.all_list_by_cpl2, name='all_list_by_cpl2'),
    # path('by_cpl2/<int:pk>/', views.dev_detail2, name='dev_detail2'),
    # path('by_cpl2/create', views.dev_create2, name='dev_create2'),
    # path('by_cpl2/<int:pk>/edit', views.dev_edit2, name='dev_edit2'),
    # path('by_cpl2/<int:pk>/del', views.dev_delete2, name='dev_delete2'),
    # # Для шаблонов
    # path('by_cpl/', views.all_list_by_cpl, name='all_list_by_cpl'),
    # path('by_cpl/create', views.dev_create, name='dev_create'),
    # path('by_cpl/<int:pk>/', views.dev_detail, name='dev_detail'),
    # path('by_cpl/<int:pk>/edit', views.dev_edit, name='dev_edit'),
    # path('by_cpl/<int:pk>/del', views.dev_delete, name='dev_delete'),
]
