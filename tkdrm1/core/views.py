"""."""
# import functools
# import sys
from sys import getsizeof
import time
# from django.db import connection, reset_queries
from django.db.models import F
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
from tqdm import tqdm

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


# @query_debugger
def all_list(request: HttpRequest):
    """."""
    template_name = 'all_list.html'

    start = time.perf_counter()
    print('Отметка 1. Начало запроса из БД перечня приборов.')

    devs_qset = Device.objects.all().select_related(
        'type__category',
        'sour_type',
    )

    print(f'Отметка 2. Конец запроса из БД перечня приборов. Заняло: {(time.perf_counter() - start):.4f}')  # noqa

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

    print(f'Отметка 3. Конец запроса из БД перечня reltodevs. Заняло: {(time.perf_counter() - start):.4f}')  # noqa

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

    print(f'Отметка 5. Конец расчета всех мест эксплуатации. Заняло: {(time.perf_counter() - start):.4f}')  # noqa

    # extra_dev_objs_lst = []

    # for dev in dev_objs_lst:
    #     temp = [i for i in reltodevs_objs if i.to_dev == dev]
    #     if temp == []:
    #         extra_dev_objs_lst.append([dev,
    #                                    None,
    #                                    None,
    #                                    None])
    #         continue
    #     temp = sorted(temp, key=lambda x: x.is_main_for_dev)
    #     temp3 = temp[0].to_rel.cust_pl1
    #     if temp3.rtu is not None:
    #         extra_dev_objs_lst.append([dev,
    #                                    temp3.rtu,
    #                                    None,
    #                                    None])
    #     elif temp3.custhouse is not None:
    #         extra_dev_objs_lst.append([dev,
    #                                    temp3.custhouse.upper_id,
    #                                    temp3.custhouse, None])
    #     elif temp3.custpost is not None:
    #         extra_dev_objs_lst.append([dev,
    #                                    temp3.custpost.upper_id.upper_id,
    #                                    temp3.custpost.upper_id,
    #                                    temp3.custpost])
    #     else:
    #         extra_dev_objs_lst.append([dev,
    #                                    None,
    #                                    None,
    #                                    None])

    print(f'Конец расчета мест эксплуатации по каждому. Заняло: {(time.perf_counter() - start):.4f}')

    # !!!!тут сортировать перечень приборов!!!!!
    # !!!!сортированное пергрузить в dev_qset!!!!

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
