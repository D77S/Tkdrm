"""."""
# import functools
# import sys
import asyncio
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


async def task(dev_id, devs_dict):
    temp = devs_dict[dev_id]["temp"]
    if len(temp) == 0:
        site_of_usage = None
    else:
        temp3 = temp[0].to_rel.cust_pl1
        if temp3.rtu is not None:
            site_of_usage = temp3.rtu
        elif temp3.custhouse is not None:
            site_of_usage = temp3.custhouse
        elif temp3.custpost is not None:
            site_of_usage = temp3.custpost
        else:
            site_of_usage = None
    return (devs_dict[dev_id]["dev"], site_of_usage)


async def async_execute(devs_dict):
    tasks = [asyncio.ensure_future(task(dev_id, devs_dict) for dev_id in devs_dict)]  # noqa
    await asyncio.wait(tasks)


# @query_debugger
def all_list(request: HttpRequest):
    """."""
    template_name = 'all_list.html'
    time_list = []
    time_list = time_counter(time_list, 'Начало запроса из БД перечня приборов.')  # noqa
    devs_qset = Device.objects.all().select_related(
        'type__category',
    ).order_by('id')

    devs_dict = {item.id: {"temp": [], "dev": item} for item in devs_qset}
    time_list = time_counter(time_list, 'Конец запроса из БД перечня приборов.')  # noqa
    reltodevs = RelToDev.objects.all().select_related(
            'to_dev__type',
            'to_rel',
            'to_rel__cust_pl1__rtu',
            'to_rel__cust_pl1__custhouse__upper_id',
            'to_rel__cust_pl1__custpost__upper_id__upper_id'
    )
    time_list = time_counter(time_list, 'Конец запроса из БД перечня reltodevs.')  # noqa

    for reltodev in reltodevs:
        dev = reltodev.to_dev
        dev_id = dev.id
        devs_dict[dev_id] = {"temp": [], "dev": dev}
        devs_dict[dev_id]["temp"].append(reltodev)

    for dev_id in devs_dict:
        devs_dict[dev_id]["temp"].sort(key=lambda x: not x.is_main_for_dev)

    temp_devs = []

    asyncio.run(async_execute(devs_dict))

    for dev_id in devs_dict:
        temp = devs_dict[dev_id]["temp"]
        if len(temp) == 0:
            site_of_usage = None
        else:
            temp3 = temp[0].to_rel.cust_pl1
            if temp3.rtu is not None:
                site_of_usage = temp3.rtu
            elif temp3.custhouse is not None:
                site_of_usage = temp3.custhouse
            elif temp3.custpost is not None:
                site_of_usage = temp3.custpost
            else:
                site_of_usage = None
        temp_devs.append((devs_dict[dev_id]["dev"], site_of_usage))







    time_list = time_counter(time_list, 'Конец расчета всех мест эксплуатации.')  # noqa

    temp_devs.sort(
        key=lambda item: (
            item[1] is None,
            item[1].title if item[1] is not None else None,
            item[0].id,
        )
    )

    delta = time_list[-1:][0][0] - time_list[0][0]
    print(f'Всего заняло {delta}.')

    paginator = Paginator([item[0] for item in temp_devs], ALL_DEV_PAG)
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
        temp = sorted(temp, key=lambda x: not (x.is_main_for_dev))
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
