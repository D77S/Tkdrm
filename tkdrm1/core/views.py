"""."""
# import functools
# import sys
import time
# from django.db import connection, reset_queries
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from core.constants import ALL_DEV_PAG
from core.models import (
    # CustPlace1Use,
    # CustPlaceToLocation,
    Device,
    RelToDev
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
def all_list(request: HttpRequest):
    """."""
    template_name = 'all_list.html'
    time_list = []
    time_list = time_counter(time_list, 'Начало запроса из БД перечня приборов.')  # noqa
    devs_qset = Device.objects.all().select_related(
        'type__category',
        'sour_type',
    ).order_by('id')
    temp_devs = []
    time_list = time_counter(time_list, 'Конец запроса из БД перечня приборов.')  # noqa
    reltodevs = RelToDev.objects.all().select_related(
            'to_dev',
            'to_rel',
            'to_rel__cust_pl1',
            'to_rel__cust_pl1__rtu',
            'to_rel__cust_pl1__custhouse',
            'to_rel__cust_pl1__custhouse__upper_id',
            'to_rel__cust_pl1__custpost',
            'to_rel__cust_pl1__custpost__upper_id',
            'to_rel__cust_pl1__custpost__upper_id__upper_id'
        )
    time_list = time_counter(time_list, 'Конец запроса из БД перечня reltodevs.')  # noqa
    for dev in devs_qset:
        temp = [i for i in reltodevs if i.to_dev == dev]
        if temp == []:
            aaa = None
        else:
            temp = sorted(temp, key=lambda x: x.is_main_for_dev)
            temp3 = temp[0].to_rel.cust_pl1
            if temp3.rtu is not None:
                aaa = temp3.rtu
            elif temp3.custhouse is not None:
                aaa = temp3.custhouse
            elif temp3.custpost is not None:
                aaa = temp3.custpost
            else:
                aaa = None
        temp_devs.append((dev, aaa))

    time_list = time_counter(time_list, 'Конец расчета всех мест эксплуатации.')  # noqa

    #
    # !!!!!!!
    # Получили список девайсов, но пока несортированный. В таком виде:
    # temp_devs = [
    # (dev1, aaa1),
    # (dev2, aaa2),
    # (dev3, aaa3),
    # ...
    # ]
    # Нужно еще дописать сортировку devs1,2,3,... по двум параметрам:
    # - сначала по aaa,
    # - потом ещё по dev.id
    # Результирующий сортированный список загрузить в dev_qset для последующей пагинации. # noqa
    delta = time_list[-1:][0][0] - time_list[0][0]
    print(f'Всего заняло {delta}.')

    paginator = Paginator(devs_qset, ALL_DEV_PAG)
    page_number = request.GET.get('page')
    curr_page_obj = paginator.get_page(page_number)
    curr_page_dev_objs_lst = [i for i in curr_page_obj]

    offset = (curr_page_obj.number - 1) * ALL_DEV_PAG
    i = 0
    curr_extra_page_obj = []

    for dev in curr_page_dev_objs_lst:
        i += 1
        temp = [i for i in reltodevs if i.to_dev == dev]
        if temp == []:
            curr_extra_page_obj.append([i + offset, dev, None])
            continue
        temp = sorted(temp, key=lambda x: x.is_main_for_dev)
        temp3 = temp[0].to_rel.cust_pl1
        if temp3.rtu is not None:
            curr_extra_page_obj.append([i + offset, dev, temp3.rtu])
        elif temp3.custhouse is not None:
            curr_extra_page_obj.append([i + offset, dev, temp3.custhouse])
        elif temp3.custpost is not None:
            curr_extra_page_obj.append([i + offset, dev, temp3.custpost])
        else:
            curr_extra_page_obj.append([i + offset, dev, None])

    context = {
        'page_obj': curr_page_obj,
        'extra_page_obj': curr_extra_page_obj
    }
    return render(request, template_name, context)


def dev_detail(request, pk):
    """."""
    template_name = 'dev_detail.html'
    context = {'dev': get_object_or_404(Device, pk=pk)}
    return render(request, template_name, context)
