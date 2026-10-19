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

class CustPlaceToLocViewSet(viewsets.ModelViewSet):
    queryset = CustPlaceToLocation.objects.all()
    serializer_class = CustPlaceToLocSerializer

class DevViewSet(viewsets.ModelViewSet):
    queryset=Device.objects.all()
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=DevDetailSerializer
    def get_serializer_class(self):
        if self.action == 'list':
            return AllDevsSerializer
        return DevDetailSerializer

#########################
# На высокоуровневых классах REST API
#########################

class AllDevList(generics.ListAPIView):
    queryset=Device.objects.all()
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=AllDevsSerializer

class DevR(generics.RetrieveAPIView):
    queryset=Device.objects.all()
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=DevDetailSerializer  

class DevC(generics.CreateAPIView):
    queryset=Device.objects.all()
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=DevDetailSerializer

class DevU(generics.UpdateAPIView):
    queryset=Device.objects.all()
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=DevDetailSerializer

class DevD(generics.DestroyAPIView):
    queryset=Device.objects.all()
    # Пагинатор настроен в settings, ключи
    # 'DEFAULT_PAGINATION_CLASS' и 'PAGE_SIZE'
    serializer_class=DevDetailSerializer  

#########################
# На низкоуровневых классах REST API
#########################

# Пагинатор для списка объектов
class CustomPagination(PageNumberPagination):
    page_size = 10
    # Позволяет клиенту менять размер страницы (напр., ?page_size=20)
    page_size_query_param = 'page_size'
    max_page_size = 100

class APIAllList(APIView):
    """Cписок всех объектов."""
    def get(self, request, *args, **kwargs):
        devs_qset = Device.objects.all().order_by('id')
        paginator = CustomPagination()
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

# Пагинатор для списка объектов тот же, что выше

# @query_debugger
@api_view(['GET',])
def all_list_by_cpl2(request: HttpRequest):
    """Список всех объектов."""
    devs_qset = Device.objects.all().order_by('id')
    paginator = CustomPagination()
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
