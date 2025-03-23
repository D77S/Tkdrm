"""."""
# import functools
# import sys
# import time
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


# @query_debugger
def all_list(request: HttpRequest):
    """."""
    template_name = 'all_list.html'

    print('Начало запроса из БД перечня приборов.')

    devs_qset = Device.objects.all().select_related(
        'type__category',
        'sour_type',
    ).order_by('id')
    dev_objs_lst = [i for i in devs_qset]

    print('Конец запроса из БД перечня приборов и преобразование их из кверисета в лист.')  # noqa

    # curr_page_ids = [i.id for i in curr_page_obj]
    # curr_page_devs_qset = Device.objects.filter(
    #     id__in=curr_page_ids).select_related(
    #     'type__category',
    #     'sour_type',
    # ).order_by('id')

    # curr_page_dev_objs_lst = [i for i in curr_page_devs_qset]

    # curr_page_reltodevs = RelToDev.objects.filter(
    #     to_dev__in=curr_page_ids
    #     ).select_related(
    #         'to_dev',
    #         'to_rel',
    #         'to_rel__cust_pl1',
    #         'to_rel__cust_pl1__rtu',
    #         'to_rel__cust_pl1__custhouse',
    #         'to_rel__cust_pl1__custpost'
    #     )

    print('Начало запроса из БД перечня RelToDev.')

    reltodevs = RelToDev.objects.select_related(
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
    reltodevs_objs = [i for i in reltodevs]

    print('Конец запроса из БД перечня RelToDev и преобразование их из кверисета в лист.')  # noqa

    # curr_page_cpltoloc_ids = [i.to_rel_id for i in curr_page_reltodevs_objs]
    # curr_page_cpllocs_qset = CustPlaceToLocation.objects.filter(
    #     id__in=curr_page_cpltoloc_ids
    # )
    # curr_page_cpllocs_objs = [i for i in curr_page_cpllocs_qset]
    # curr_page_cpluses_ids = [i.id for i in curr_page_cpllocs_objs]
    # curr_page_cpluses_objs = CustPlace1Use.objects.filter(
    #     id__in=curr_page_cpluses_ids).select_related(
    #         'rtu',
    #         'custhouse',
    #         'custpost'
    #     )
    # curr_page_cpluses_list = [i for i in curr_page_cpluses_objs]
    # curr_page_cpl1s = []
    # for i in curr_page_cpluses_list:
    #     if i.rtu is not None:
    #         curr_page_cpl1s.append(i.rtu)
    #     elif i.custhouse is not None:
    #         curr_page_cpl1s.append(i.custhouse)
    #     elif i.custpost is not None:
    #         curr_page_cpl1s.append(i.custpost)

    print('Начало расчета места эксплуатации по каждому.')

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

    print('Конец расчета мест эксплуатации по каждому.')

    # !!!!тут сортировать перечень приборов!!!!!
    # !!!!сортированное пергрузить в dev_qset!!!!

    paginator = Paginator(dev_objs_lst, ALL_DEV_PAG)
    page_number = request.GET.get('page')
    curr_page_obj = paginator.get_page(page_number)
    curr_page_dev_objs_lst = [i for i in curr_page_obj]

    offset = (curr_page_obj.number - 1) * ALL_DEV_PAG
    i = 0
    curr_extra_page_obj = []

    for dev in curr_page_dev_objs_lst:
        i += 1
        temp = [i for i in reltodevs_objs if i.to_dev == dev]
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
