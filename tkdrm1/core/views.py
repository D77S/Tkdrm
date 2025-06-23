"""."""
# import functools
# import sys
import time
# from django.db import connection, reset_queries
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from core.constants import ALL_DEV_PAG
from core.models import (
    # Rtu,
    # CustHouse,
    # CustPost,
    CustPlace1Use,
    CustPlaceToLocation,
    LocationOfUse,
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
    """."""
    template_name = 'dev_detail.html'

    dev: Device = get_object_or_404(Device, pk=pk)

    dev_cpl_acc = dev.cp1_acc
    if dev_cpl_acc.rtu is not None:
        dev_cpl_acc_fin = dev_cpl_acc.rtu
    elif dev_cpl_acc.custhouse is not None:
        dev_cpl_acc_fin = dev_cpl_acc.custhouse
    elif dev_cpl_acc.custpost is not None:
        dev_cpl_acc_fin = dev_cpl_acc.custpost
    else:
        dev_cpl_acc_fin = None
    print(f'{dev_cpl_acc_fin=}')

    main_reltodevs: QuerySet[RelToDev] = RelToDev.objects.filter(
        to_dev=dev,
        is_main_for_dev=True
    )
    other_reltodevs: QuerySet[RelToDev] = RelToDev.objects.filter(
        to_dev=dev,
        is_main_for_dev=False
    )

    print(f'{main_reltodevs=}, {other_reltodevs=}')

    main_cpls: list[CustPlaceToLocation] = [
        item.to_rel for item in main_reltodevs
    ]
    other_cpls: list[CustPlaceToLocation] = [
        item.to_rel for item in other_reltodevs
    ]
    print(f'{main_cpls=} {other_cpls=}')

    main_cpl_use_pre: list[
        list[CustPlace1Use, LocationOfUse]
    ] = [[item.cust_pl1, item.loc] for item in main_cpls]
    other_cpl_use_pre: list[
        list[CustPlace1Use, LocationOfUse]
    ] = [[item.cust_pl1, item.loc] for item in other_cpls]
    print(f'{main_cpl_use_pre=} {other_cpl_use_pre}')

    main_cpl_use_fin = []
    for item in main_cpl_use_pre:
        if item[0].rtu is not None:
            temp1 = item[0].rtu
        elif item[0].custhouse is not None:
            temp1 = item[0].custhouse
        elif item[0].custpost is not None:
            temp1 = item[0].custpost
        else:
            temp1 = None

        if item[1] is None:
            temp2 = None
            temp3 = None
        elif item[1].ppr is not None:
            temp2 = item[1].ppr
            temp3 = item[1].ppr.pptype.title
        elif item[1].mmpo is not None:
            temp2 = item[1].mmpo
            temp3 = 'ММПО'
        elif item[1].oez is not None:
            temp2 = item[1].oez
            temp3 = 'ОЭЗ'
        elif item[1].ztk is not None:
            temp2 = item[1].ztk
            temp3 = 'ЗТК'
        else:
            temp2 = None
            temp3 = None
        main_cpl_use_fin.append([temp1, temp2, temp3])

    other_cpl_use_fin = []
    for item in other_cpl_use_pre:
        if item[0].rtu is not None:
            temp1 = item[0].rtu
        elif item[0].custhouse is not None:
            temp1 = item[0].custhouse
        elif item[0].custpost is not None:
            temp1 = item[0].custpost
        else:
            temp1 = None

        if item[1] is None:
            temp2 = None
            temp3 = None
        elif item[1].ppr is not None:
            temp2 = item[1].ppr
            temp3 = item[1].ppr.pptype.title
        elif item[1].mmpo is not None:
            temp2 = item[1].mmpo
            temp3 = 'ММПО'
        elif item[1].oez is not None:
            temp2 = item[1].oez
            temp3 = 'ОЭЗ'
        elif item[1].ztk is not None:
            temp2 = item[1].ztk
            temp3 = 'ЗТК'
        else:
            temp2 = None
            temp3 = None
        other_cpl_use_fin.append([temp1, temp2, temp3])
    print(f'{main_cpl_use_fin=} {other_cpl_use_fin=}')

    main_cpl_use_fin_count = len(main_cpl_use_fin)
    main_rowspan = main_cpl_use_fin_count + 1
    other_cpl_use_fin_count = len(other_cpl_use_fin)
    other_rowspan = other_cpl_use_fin_count + 1
    total_count = main_cpl_use_fin_count + other_cpl_use_fin_count
    total_rowspan = 1
    if main_cpl_use_fin_count > 0:
        total_rowspan += (main_cpl_use_fin_count + 1)
    if other_cpl_use_fin_count > 0:
        total_rowspan += (other_cpl_use_fin_count + 1)

    print(f'{main_cpl_use_fin_count=} {other_cpl_use_fin_count=}')

    context = {
        'dev': dev,
        'dev_cpl_acc_fin': dev_cpl_acc_fin,
        'main_cpl_use_fin': main_cpl_use_fin,
        'other_cpl_use_fin': other_cpl_use_fin,
        'main_cpl_use_fin_count': main_cpl_use_fin_count,
        'other_cpl_use_fin_count': other_cpl_use_fin_count,
        'total_count': total_count,
        'main_rowspan': main_rowspan,
        'other_rowspan': other_rowspan,
        'total_rowspan': total_rowspan
    }
    return render(request, template_name, context)
