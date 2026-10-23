"""."""
# import functools
# import sys
import time
# from django.db import connection, reset_queries
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status, viewsets
from django.core.paginator import Paginator
# from django.forms.models import model_to_dict
from django.db.models import OuterRef, Subquery, F, Value
from django.db.models.functions import Coalesce
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from core.constants import ALL_DEV_PAG
from core.forms import DevDetailForm, DevEditForm
from core.models import (
    Device,
    RelToDev,
)
from custplaces.models import (
    CustPlaceToLocation,
)
from core.serializers import (
    AllDevsSerializer,
    CustPlaceToLocSerializer,
    DevDetailSerializer
)

# def query_debugger(func):
#     @functools.wraps(func)
#     def inner_func(*args, **kwargs):
#         reset_queries()
#         start_queries = len(connection.queries)
#         start = time.perf_counter()
#         result = func(*args, **kwargs)
#         end = time.perf_counter()
#         end_queries = len(connection.queries)
#         print(f"Function : {func.__name__}")
#         print(f"Number of Queries : {end_queries - start_queries}")
#         print(f"Finished in : {(end - start):.2f}s")
#         return result
#     return inner_func

#########################
def time_counter(time_list: list, st: str):
    stamp = time.perf_counter()
    time_list.append([stamp, st])
    curr_delta = time_list[-1:][0][0] - time_list[-2:][0][0]
    print(f'Отметка {len(time_list)}. {st}. С предыдущей отметки заняло {curr_delta}')  # noqa
    return time_list

#########################
# На REST API
#########################

#########################
# На вьюсетах REST API
#########################

# class CustPlaceToLocViewSet(viewsets.ModelViewSet):
#     queryset = CustPlaceToLocation.objects.all()
#     serializer_class = CustPlaceToLocSerializer

class DevViewSet(viewsets.ModelViewSet):
    queryset=Device.objects.all().order_by('id')
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=DevDetailSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        detailed_actions = ['retrieve', 'update', 'partial_update']
        if self.action in detailed_actions:
            return queryset.select_related(
                'type__category__cat_l1',
                'holder__dept',
                'holder__empl__rtu',
                'holder__empl__custhouse',
                'holder__empl__custpost',
                'cp1_acc__rtu',
                'cp1_acc__custhouse',
                'cp1_acc__custpost',
                'sour_type',
                'status_use',
                'service_type',
                'upper_id'
                ).prefetch_related(
                    'f_dev_to_doing__from_dtcp_to_dtcr',
                    'f_dev_to_doing__reltocd__to_doing',
                    'f_dev_to_doing__reltocd__to_contract',
                    'from_dev__to_rel__cust_pl1__rtu',
                    'from_dev__to_rel__cust_pl1__custhouse',
                    'from_dev__to_rel__cust_pl1__custpost',
                    'from_dev__to_rel__loc__ppr__pptype',
                    'from_dev__to_rel__loc__mmpo',
                    'from_dev__to_rel__loc__oez',
                    'from_dev__to_rel__loc__ztk'
            ).order_by('id')
        elif self.action == 'list':
            base_rel_qs = RelToDev.objects.filter(to_dev_id=OuterRef('pk'))
            main_rel_subquery = base_rel_qs.filter(is_main_for_dev=True).values('to_rel_id')[:1]
            any_rel_subquery = base_rel_qs.values('to_rel_id')[:1]
            cpl_subquery_base = CustPlaceToLocation.objects.filter(
                id=OuterRef('target_cust_place_to_location_id')
            )
            #####
            temp_qs =  Device.objects.select_related('type').annotate(
                device_type_title=F('type__title'),
                target_cust_place_to_location_id=Coalesce(
                    Subquery(main_rel_subquery),
                    Subquery(any_rel_subquery)
                ),
           sort_rtu_title=Subquery(
               cpl_subquery_base.annotate(
                   resolved_rtu_title=Coalesce(
                       'cust_pl1__custpost__upper_id__upper_id__title', 
                        'cust_pl1__custhouse__upper_id__title',
                        'cust_pl1__rtu__title',
                        Value(None)
                    )
                ).values('resolved_rtu_title')[:1]
            ),
            sort_house_title=Subquery(
                cpl_subquery_base.annotate(
                    resolved_house_title=Coalesce(
                        'cust_pl1__custpost__upper_id__title',
                        'cust_pl1__custhouse__title',
                        Value(None)
                    )
                ).values('resolved_house_title')[:1]
            ),
            sort_post_title=Subquery(
                cpl_subquery_base.values('cust_pl1__custpost__title')[:1]
            ),
            sort_ppr_title=Subquery(cpl_subquery_base.values('loc__ppr__pptype__title')[:1]),
            sort_ppr_type_title=Subquery(cpl_subquery_base.values('loc__ppr__title')[:1]),
            sort_mmpo_title=Subquery(cpl_subquery_base.values('loc__mmpo__title')[:1]),
            sort_oez_title=Subquery(cpl_subquery_base.values('loc__oez__title')[:1]),
            sort_ztk_title=Subquery(cpl_subquery_base.values('loc__ztk__title')[:1]),
            sort_svh_title=Subquery(cpl_subquery_base.values('loc__svh__title')[:1])
            )
            #####
            temp_qs = temp_qs.order_by(
                # === ПРИОРИТЕТ 1: Структура таможенных органов ===
                Coalesce('sort_rtu_title', Value('\xff')).asc(),      # 1. Группируем по алфавиту РТУ. Без РТУ — вниз.
                Coalesce('sort_house_title', Value('\xff')).asc(),    # 2. Внутри одного РТУ — по алфавиту Таможни.
                Coalesce('sort_post_title', Value('\xff')).asc(),     # 3. Затем по алфавиту Поста.
                # === ПРИОРИТЕТ 2: Тип сайта и локации эксплуатации ===
                Coalesce('sort_ppr_type_title', Value('\xff')).asc(), # 4. По типу пункта пропуска.
                Coalesce('sort_ppr_title', Value('\xff')).asc(),      # 5. По названию пункта пропуска.
                Coalesce('sort_mmpo_title', Value('\xff')).asc(),     # 6. По названию ММПО.
                Coalesce('sort_oez_title', Value('\xff')).asc(),      # 7. По названию ОЭЗ.
                Coalesce('sort_ztk_title', Value('\xff')).asc(),      # 8. По названию ЗТК.
                Coalesce('sort_svh_title', Value('\xff')).asc(),      # 9. По названию СВХ.
                # === ПРИОРИТЕТ 3: Характеристики самого прибора ===
                'device_type_title',                                  # 10. По названию типа технического средства.
                'id'                                                  # 11. Гарант стабильности пагинации в СУБД.
            )
            return temp_qs
        return queryset.order_by('id')
    def get_serializer_class(self):
        if self.action == 'list':
            return AllDevsSerializer
        return DevDetailSerializer
# Пример ответа вьюсета на запрос списка объектов:
# {
#     "count": 11469,
#     "next": "http://127.0.0.1:8000/all_list/by_cpl5/?page=4",
#     "previous": "http://127.0.0.1:8000/all_list/by_cpl5/?page=2",
#     "results": [
#         {
#             "id": 7,
#             "rels_of_work": [
#                 {
#                     "id": 2,
#                     "cust_pl1": {
#                         "id": 86,
#                         "rtuv2": "Дальневосточное таможенное управление",
#                         "custhousev2": "Бурятская таможня",
#                         "custpostv2": "Таможенный пост ЖДПП Наушки"
#                     },
#                     "is_main_for_cust": true
#                 }
#             ],
#             "type": {
#                 "id": 49,
#                 "title": "ВН-Ж",
#                 "category": {
#                     "id": 4,
#                     "title": "ВН",
#                     "cat_l1": {
#                         "id": 1,
#                         "title": "Стационарные"
#                     }
#                 },
#                 "lifetime": 2
#             },
#             "serial": "0152-08"
#         },
#         {
#             "id": 8,
#             "rels_of_work": [
#                 {
#                     "id": 2,
#                     "cust_pl1": {
#                         "id": 86,
#                         "rtuv2": "Дальневосточное таможенное управление",
#                         "custhousev2": "Бурятская таможня",
#                         "custpostv2": "Таможенный пост ЖДПП Наушки"
#                     },
#                     "is_main_for_cust": true
#                 }
#             ],
#             "type": {
#                 "id": 31,
#                 "title": "ВН-А",
#                 "category": {
#                     "id": 4,
#                     "title": "ВН",
#                     "cat_l1": {
#                         "id": 1,
#                         "title": "Стационарные"
#                     }
#                 },
#                 "lifetime": 2
#             },
#             "serial": "0359-07"
#         }
#     ]
# }
#
# Пример ответа въюсета на запрос об одном объекте
# {
#     "id": 13,
#     "type": {
#         "id": 50,
#         "title": "ССД",
#         "category": {
#             "id": 5,
#             "title": "Телеком",
#             "cat_l1": {
#                 "id": 1,
#                 "title": "Стационарные"
#             }
#         },
#         "lifetime": 2
#     },
#     "sub_type": null,
#     "serial": "272-09",
#     "inventary": null,
#     "holder": {
#         "id": 2,
#         "username": "cvdwa",
#         "first_name": "Иван",
#         "pater_name": "Иванович",
#         "last_name": "Иванов",
#         "email": "a@a.com",
#         "is_active": true,
#         "empl": {
#             "id": 86,
#             "rtuv2": "Дальневосточное таможенное управление",
#             "custhousev2": "Бурятская таможня",
#             "custpostv2": "Таможенный пост ЖДПП Наушки"
#         },
#         "dept": {
#             "id": 1,
#             "title": "ОПИДК"
#         }
#     },
#     "date_prod": "2009-01-01",
#     "date_expl": "2009-01-01",
#     "date_prolong": "2009-01-01",
#     "warr_period": 18,
#     "date_prod_expired": "2011-01-01",
#     "date_verif": null,
#     "cat_number_c": 3,
#     "cat_number_f": 3,
#     "cats_corresp": true,
#     "cp1_acc": {
#         "id": 11,
#         "rtuv2": "Дальневосточное таможенное управление",
#         "custhousev2": "Бурятская таможня",
#         "custpostv2": null
#     },
#     "sour_type": {
#         "id": 1,
#         "title": "РФ в лице там.органа"
#     },
#     "cost": null,
#     "condition": true,
#     "upper_id": null,
#     "is_si": null,
#     "is_stud": false,
#     "status_use": {
#         "id": 1,
#         "title": "Используется"
#     },
#     "service_type": {
#         "id": 4,
#         "title": "Только ремонт"
#     },
#     "rels_of_work": [
#         {
#             "id": 2,
#             "cust_pl1": {
#                 "id": 86,
#                 "rtuv2": "Дальневосточное таможенное управление",
#                 "custhousev2": "Бурятская таможня",
#                 "custpostv2": "Таможенный пост ЖДПП Наушки"
#             },
#             "loc": {
#                 "locname": "Наушки",
#                 "loctype": "ЖДПП"
#             },
#             "is_main_for_cust": true,
#             "main_for_dev": true
#         }
#     ],
#     "rels_of_contracts": [
#         {
#             "id": 4,
#             "to_contract": {
#                 "id": 3,
#                 "title": "Гос.контракт на одновременно техническое обслуживание и ремонт",
#                 "number": 65,
#                 "date_of": "2013-04-02"
#             },
#             "to_doing": {
#                 "id": 3,
#                 "title": "Ремонт"
#             },
#             "basis": []
#         },
#         {
#             "id": 6,
#             "to_contract": {
#                 "id": 5,
#                 "title": "Гос.контракт на одновременно техническое обслуживание и ремонт",
#                 "number": 119,
#                 "date_of": "2014-10-28"
#             },
#             "to_doing": {
#                 "id": 2,
#                 "title": "Техническое обслуживание"
#             },
#             "basis": [
#                 {
#                     "exact_moment": "2014-11-23T00:00:00Z"
#                 }
#             ]
#         }
#     ],
#     "note1": null,
#     "note2": null,
#     "note3": null
# }

#########################
# На высокоуровневых классах REST API
#########################

class AllDevList(generics.ListAPIView):
    queryset=Device.objects.all().order_by('id')
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=AllDevsSerializer

class DevR(generics.RetrieveAPIView):
    queryset=Device.objects.all().order_by('id')
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=DevDetailSerializer  

class DevC(generics.CreateAPIView):
    queryset=Device.objects.all().order_by('id')
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=DevDetailSerializer

class DevU(generics.UpdateAPIView):
    queryset=Device.objects.all().order_by('id')
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=DevDetailSerializer

class DevD(generics.DestroyAPIView):
    queryset=Device.objects.all().order_by('id')
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=DevDetailSerializer  

#########################
# На низкоуровневых классах REST API
#########################

class APIAllList(APIView):
    """Cписок всех объектов."""
    def get(self, request, *args, **kwargs):
        devs_qset = Device.objects.all().order_by('id')
        # Пагинатор настроен в settings, ключи
        # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(devs_qset, request, view=self)
        if page is not None:
            serializer = AllDevsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = AllDevsSerializer(devs_qset, many=True)
        return Response(serializer.data)

class APIDetail(APIView):
    """Действия с одним объектом: просмотр, создание, правка, удаление."""
    def get(self, request, *args, **kwargs):
        instance: Device = get_object_or_404(Device, pk=self.kwargs.get('pk'))
        serializer = DevDetailSerializer(instance)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        serializer = DevDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, *args, **kwargs):
        instance: Device = get_object_or_404(Device, pk=self.kwargs.get('pk'))
        serializer = DevDetailSerializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request, *args, **kwargs):
        instance: Device = get_object_or_404(Device, pk=self.kwargs.get('pk'))
        serializer = DevDetailSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, *args, **kwargs):
        instance: Device = get_object_or_404(Device, pk=self.kwargs.get('pk'))
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#########################
# На функциях REST API
#########################

# @query_debugger
@api_view(['GET',])
def all_list_by_cpl2(request: HttpRequest):
    """Список всех объектов."""
    devs_qset = Device.objects.all().order_by('id')
    paginator = PageNumberPagination()
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    page = paginator.paginate_queryset(devs_qset, request)
    if page is not None:
        serializer = AllDevsSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    serializer = AllDevsSerializer(devs_qset, many=True)
    return Response(serializer.data)


@api_view(['GET',])
def dev_detail2(request: HttpRequest, pk):
    """Вью-функция по просмотру
    одного девайса в БД.
    Для REST API."""
    # devs_qs = Device.objects.select_related(
    #     'type__category__cat_l1',
    #     'holder__dept',
    #     'holder__empl__rtu',
    #     'holder__empl__custhouse',
    #     'holder__empl__custpost',
    #     'cp1_acc__rtu',
    #     'cp1_acc__custhouse',
    #     'cp1_acc__custpost',
    #     'sour_type',
    #     'status_use',
    #     'service_type',
    #     'upper_id'
    # ).prefetch_related(
    #     'f_dev_to_doing__from_dtcp_to_dtcr',
    #     'f_dev_to_doing__reltocd__to_doing',
    #     'f_dev_to_doing__reltocd__to_contract',
    #     'from_dev__to_rel__cust_pl1__rtu',
    #     'from_dev__to_rel__cust_pl1__custhouse',
    #     'from_dev__to_rel__cust_pl1__custpost',
    #     'from_dev__to_rel__loc__ppr__pptype',
    #     'from_dev__to_rel__loc__mmpo',
    #     'from_dev__to_rel__loc__oez',
    #     'from_dev__to_rel__loc__ztk'
    # )
    # instance: Device = get_object_or_404(devs_qs, pk=pk)
    instance: Device = get_object_or_404(Device, pk=pk)

    serializer = DevDetailSerializer(instance)
    return Response(serializer.data)


@api_view(['POST',])
def dev_create2(request: HttpRequest):
    """Вью-функция по созданию
    одного девайса в БД.
    Для REST API."""
    serializer = DevDetailSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH',])
def dev_edit2(request: HttpRequest, pk):
    """Вью-функция по редактированию
    одного девайса в БД.
    Для REST API."""
    # devs_qset = Device.objects.select_related(
    #     'type__category__cat_l1',
    #     'holder__dept',
    #     'holder__empl__rtu',
    #     'holder__empl__custhouse__upper_id',
    #     'holder__empl__custpost__upper_id__upper_id',
    #     'cp1_acc__rtu',
    #     'cp1_acc__custhouse',
    #     'cp1_acc__custpost',
    #     'sour_type',
    #     'status_use',
    #     'service_type',
    #     'upper_id'
    # ).prefetch_related(
    #     'f_dev_to_doing__from_dtcp_to_dtcr',
    #     'f_dev_to_doing__reltocd__to_doing',
    #     'f_dev_to_doing__reltocd__to_contract',
    #     'from_dev__to_rel__cust_pl1__rtu',
    #     'from_dev__to_rel__cust_pl1__custhouse',
    #     'from_dev__to_rel__cust_pl1__custpost',
    #     'from_dev__to_rel__loc__ppr__pptype',
    #     'from_dev__to_rel__loc__mmpo',
    #     'from_dev__to_rel__loc__oez',
    #     'from_dev__to_rel__loc__ztk'
    # )
    # instance: Device = get_object_or_404(devs_qset, pk=pk)
    instance: Device = get_object_or_404(Device, pk=pk)

    serializer = DevDetailSerializer(instance, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE',])
def dev_delete2(request: HttpRequest, pk):
    """Вью-функция по удалению
    одного девайса в БД."""
    instance: Device = get_object_or_404(Device, pk=pk)
    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

#########################
# На шаблонах
#########################

# @query_debugger
def all_list_by_cpl(request: HttpRequest):
    """Список всех объектов."""
    template_name = 'all_list.html'
    time_list = []
    time_list = time_counter(time_list, 'Начало запроса из БД перечня приборов.')  # noqa
    devs_qset = Device.objects.all().select_related(
        'type__category',
    ).order_by('id')
    time_list = time_counter(time_list, 'Конец запроса из БД перечня приборов.')  # noqa
    devs_dict = {item.pk: {'dev': item} for item in devs_qset}

    time_list = time_counter(time_list, 'Начало запроса из БД перечня reltodevs.')  # noqa
    reltodevs = RelToDev.objects.all().select_related(
            'to_dev__type',
            'to_rel__cust_pl1__rtu',
            'to_rel__cust_pl1__custhouse__upper_id',
            'to_rel__cust_pl1__custpost__upper_id__upper_id'
    ).order_by('-is_main_for_dev')
    time_list = time_counter(time_list, 'Конец запроса из БД перечня reltodevs.')  # noqa

    for reltodev in reltodevs:
        dev_id = reltodev.to_dev.pk
        if devs_dict[dev_id].get('main_found') is True:
            continue
        else:
            devs_dict[dev_id].update(temp_main=reltodev,
                                     main_found=reltodev.is_main_for_dev)

    time_list = time_counter(time_list, 'Конец обсчёта всех reltodevs.')  # noqa

    temp_devs = []

    for dev_id in devs_dict:
        temp = devs_dict[dev_id].get('temp_main')
        if temp is None:
            site_of_usage = (None, None, None)
        else:
            cpluse = temp.to_rel.cust_pl1
            if cpluse.rtu is not None:
                site_of_usage = (cpluse.rtu, None, None)
            elif cpluse.custhouse is not None:
                site_of_usage = (
                    cpluse.custhouse.upper_id,
                    cpluse.custhouse,
                    None
                )
            elif cpluse.custpost is not None:
                site_of_usage = (
                    cpluse.custpost.upper_id.upper_id,
                    cpluse.custpost.upper_id,
                    cpluse.custpost
                )
            else:
                site_of_usage = (None, None, None)
        temp_devs.append((devs_dict[dev_id]['dev'], site_of_usage))

    time_list = time_counter(time_list, 'Конец расчета всех мест эксплуатации.')  # noqa

    temp_devs.sort(
        key=lambda item: (
            item[1] is None,
            item[1][0] is None,
            item[1][1] is None,
            item[1][2] is None,
            item[1][0].title if item[1][0] is not None else None,
            item[1][1].title if item[1][1] is not None else None,
            item[1][2].title if item[1][2] is not None else None,
            item[0].id,
        )
    )

    time_list = time_counter(time_list, 'Конец сортировки всех мест эксплуатации.')  # noqa

    temp_devs2 = []
    for i, item in enumerate(temp_devs):
        temp_devs2.append((i + 1, item[0], item[1]))

    paginator = Paginator(temp_devs2, ALL_DEV_PAG)
    page_number = request.GET.get('page')
    curr_page_obj = paginator.get_page(page_number)

    delta = time_list[-1:][0][0] - time_list[0][0]
    print(f'Всего заняло {delta}.')

    context = {'page_obj': curr_page_obj}
    return render(request, template_name, context)


def dev_detail(request, pk):
    """Вью-функция по просмотру
    одного девайса в БД.
    Для шаблонов."""

    # devs_qs = Device.objects.select_related(
    #     'type__category__cat_l1',
    #     'holder__dept',
    #     'holder__empl__rtu',
    #     'holder__empl__custhouse',
    #     'holder__empl__custpost',
    #     'cp1_acc__rtu',
    #     'cp1_acc__custhouse',
    #     'cp1_acc__custpost',
    #     'sour_type',
    #     'status_use',
    #     'service_type',
    #     'upper_id'
    # ).prefetch_related(
    #     'f_dev_to_doing__from_dtcp_to_dtcr',
    #     'f_dev_to_doing__reltocd__to_doing',
    #     'f_dev_to_doing__reltocd__to_contract',
    #     'from_dev__to_rel__cust_pl1__rtu',
    #     'from_dev__to_rel__cust_pl1__custhouse',
    #     'from_dev__to_rel__cust_pl1__custpost',
    #     'from_dev__to_rel__loc__ppr__pptype',
    #     'from_dev__to_rel__loc__mmpo',
    #     'from_dev__to_rel__loc__oez',
    #     'from_dev__to_rel__loc__ztk'
    # )
    # instance: Device = get_object_or_404(devs_qs, pk=pk)
    instance: Device = Device.objects.get(pk=pk)

    initial={'obj_id': pk}
    dev_detail_form = DevDetailForm(
        instance=instance,
        initial=initial
    )
    context = {
        'dev_detail_form': dev_detail_form
    }
    template_name = 'dev_detail.html'
    return render(request, template_name, context)


def dev_create(request: HttpRequest):
    """Вью-функция по созданию
    одного девайса в БД.
    Для шаблонов."""
    dev_edit_form = DevEditForm(request.POST or None)
    context = {
        'dev_edit_form': dev_edit_form
    }
    if request.method == 'POST':
        if dev_edit_form.is_valid():
            dev_edit_form.save()
            return redirect('core:all_list_by_cpl')

    template_name = 'dev_create.html'
    return render(request, template_name, context)


def dev_edit(request, pk):
    """Вью-функция по редактированию
    одного девайса в БД.
    Для шаблонов."""

    devs_qs = Device.objects.select_related(
        'type__category__cat_l1',
        'holder__dept',
        'holder__empl__rtu',
        'holder__empl__custhouse__upper_id',
        'holder__empl__custpost__upper_id__upper_id',
        'cp1_acc__rtu',
        'cp1_acc__custhouse',
        'cp1_acc__custpost',
        'sour_type',
        'status_use',
        'service_type',
        'upper_id'
    ).prefetch_related(
        'f_dev_to_doing__from_dtcp_to_dtcr',
        'f_dev_to_doing__reltocd__to_doing',
        'f_dev_to_doing__reltocd__to_contract',
        'from_dev__to_rel__cust_pl1__rtu',
        'from_dev__to_rel__cust_pl1__custhouse',
        'from_dev__to_rel__cust_pl1__custpost',
        'from_dev__to_rel__loc__ppr__pptype',
        'from_dev__to_rel__loc__mmpo',
        'from_dev__to_rel__loc__oez',
        'from_dev__to_rel__loc__ztk'
    )

    instance: Device = get_object_or_404(devs_qs, pk=pk)
    initial={'obj_id': pk}
    dev_edit_form = DevEditForm(
        request.POST or None,
        instance=instance,
        initial=initial
    )
    context = {
        'dev_edit_form': dev_edit_form
    }

    if request.method == 'POST':
        if dev_edit_form.is_valid():
            dev_edit_form.save()
            return redirect('core:all_list_by_cpl')

    template_name = 'dev_edit.html'
    return render(request, template_name, context)


def dev_delete(request: HttpRequest, pk):
    """Вью-функция по удалению
    одного девайса в БД.
    Для шаблонов."""
    instance=get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        instance.delete()
    return redirect('core:all_list_by_cpl')
