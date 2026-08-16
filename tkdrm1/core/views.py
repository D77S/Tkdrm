"""."""
# import functools
# import sys
import time
# from django.db import connection, reset_queries
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from core.constants import ALL_DEV_PAG
from core.forms import DevDetailForm, DevEditForm
from core.models import (
    Device,
    RelToDev,
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


def time_counter(time_list: list, st: str):
    stamp = time.perf_counter()
    time_list.append([stamp, st])
    curr_delta = time_list[-1:][0][0] - time_list[-2:][0][0]
    print(f'Отметка {len(time_list)}. {st}. С предыдущей отметки заняло {curr_delta}')  # noqa
    return time_list


# @query_debugger
def all_list_by_cpl(request: HttpRequest):
    """."""
    template_name = 'all_list.html'
    time_list = []
    time_list = time_counter(time_list, 'Начало запроса из БД перечня приборов.')  # noqa
    devs_qset = Device.objects.all().select_related(
        'type__category',
    ).order_by('id')
    time_list = time_counter(time_list, 'Конец запроса из БД перечня приборов.')  # noqa
    devs_dict = {item.id: {'dev': item} for item in devs_qset}

    time_list = time_counter(time_list, 'Начало запроса из БД перечня reltodevs.')  # noqa
    reltodevs = RelToDev.objects.all().select_related(
            'to_dev__type',
            'to_rel__cust_pl1__rtu',
            'to_rel__cust_pl1__custhouse__upper_id',
            'to_rel__cust_pl1__custpost__upper_id__upper_id'
    ).order_by('-is_main_for_dev')
    time_list = time_counter(time_list, 'Конец запроса из БД перечня reltodevs.')  # noqa

    for reltodev in reltodevs:
        dev_id = reltodev.to_dev.id
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
    """Вью-функция по детализированному выводу
    одного уже существующего в БД девайса
    для цели ПРОСМОТРА."""

    devs_qs = Device.objects.select_related(
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
    )
    instance: Device = get_object_or_404(devs_qs, pk=pk)
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

def dev_edit(request, pk):
    """Вью-функция по детализированному выводу
    одного уже существующего в БД девайса
    для цели РЕДАКТИРОВАНИЯ."""

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


def dev_delete(request, pk):
    """Вью-функция по удалению
    одного уже существующего в БД девайса."""
    instance=get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        instance.delete()
    return redirect('core:all_list_by_cpl')
