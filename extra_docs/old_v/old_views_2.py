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
from core.forms import DevDetailForm
from core.models import (
    Device,
    RelToDev
)
from custplaces.models import (
    Rtu,
    CustHouse,
    CustPost,
    Ppr,
    Mmpo,
    Oez,
    Ztk,
    CustPlace1Use,
    CustPlaceToLocation,
    LocationOfUse
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

    dev: Device = get_object_or_404(Device, pk=pk)

    main_reltodevs: QuerySet[RelToDev] = RelToDev.objects.filter(
        to_dev=dev,
        is_main_for_dev=True
    )
    other_reltodevs: QuerySet[RelToDev] = RelToDev.objects.filter(
        to_dev=dev,
        is_main_for_dev=False
    )

    main_cpls: list[CustPlaceToLocation] = [
        item.to_rel for item in main_reltodevs
    ]
    other_cpls: list[CustPlaceToLocation] = [
        item.to_rel for item in other_reltodevs
    ]

    main_cpl_use_pre: list[
        list[CustPlace1Use, LocationOfUse]
    ] = [[item.cust_pl1, item.loc] for item in main_cpls]
    other_cpl_use_pre: list[
        list[CustPlace1Use, LocationOfUse]
    ] = [[item.cust_pl1, item.loc] for item in other_cpls]

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
            # temp3 = None
        elif item[1].ppr is not None:
            temp2 = item[1].ppr
            # temp3 = item[1].ppr.pptype.title
        elif item[1].mmpo is not None:
            temp2 = item[1].mmpo
            # temp3 = 'ММПО'
        elif item[1].oez is not None:
            temp2 = item[1].oez
            # temp3 = 'ОЭЗ'
        elif item[1].ztk is not None:
            temp2 = item[1].ztk
            # temp3 = 'ЗТК'
        else:
            temp2 = None
            # temp3 = None
        main_cpl_use_fin.append([
            temp1,
            temp2,
            # temp3
        ])

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
            # temp3 = None
        elif item[1].ppr is not None:
            temp2 = item[1].ppr
            # temp3 = item[1].ppr.pptype.title
        elif item[1].mmpo is not None:
            temp2 = item[1].mmpo
            # temp3 = 'ММПО'
        elif item[1].oez is not None:
            temp2 = item[1].oez
            # temp3 = 'ОЭЗ'
        elif item[1].ztk is not None:
            temp2 = item[1].ztk
            # temp3 = 'ЗТК'
        else:
            temp2 = None
            # temp3 = None
        other_cpl_use_fin.append([
            temp1,
            temp2,
            # temp3
        ])

    initial = {
        'type': dev.type.pk,
        'subtype': dev.sub_type,
        'cat_l2': dev.type.category.pk,
        'cat_l1': dev.type.category.cat_l1.pk,
        'upper_dev': dev.upper_id.pk if dev.upper_id else None,
        'source': dev.sour_type.pk,
        'serial': dev.serial,
        'acc1_rtu': dev.cp1_acc.rtu.pk if dev.cp1_acc.rtu is not None else 0,
        'acc1_ch': dev.cp1_acc.custhouse.pk if dev.cp1_acc.custhouse is not None else 0,  # noqa
        'acc1_cp': dev.cp1_acc.custpost.pk if dev.cp1_acc.custpost is not None else 0,  # noqa
        'use_main1_rtu': 0,
        'use_main1_ch': 0,
        'use_main1_cp': 0,
        'use_main1_ppr': 0,
        'use_main1_mmpo': 0,
        'use_main1_oez': 0,
        'use_main1_ztk': 0,
        'use_oth1_rtu': 0,
        'use_oth1_ch': 0,
        'use_oth1_cp': 0,
        'use_oth1_ppr': 0,
        'use_oth1_mmpo': 0,
        'use_oth1_oez': 0,
        'use_oth1_ztk': 0,
        'use_oth2_rtu': 0,
        'use_oth2_ch': 0,
        'use_oth2_cp': 0,
        'use_oth2_ppr': 0,
        'use_oth2_mmpo': 0,
        'use_oth2_oez': 0,
        'use_oth2_ztk': 0,
        'use_oth3_rtu': 0,
        'use_oth3_ch': 0,
        'use_oth3_cp': 0,
        'use_oth3_ppr': 0,
        'use_oth3_mmpo': 0,
        'use_oth3_oez': 0,
        'use_oth3_ztk': 0,
        'use_oth4_rtu': 0,
        'use_oth4_ch': 0,
        'use_oth4_cp': 0,
        'use_oth4_ppr': 0,
        'use_oth4_mmpo': 0,
        'use_oth4_oez': 0,
        'use_oth4_ztk': 0,
        'use_oth5_rtu': 0,
        'use_oth5_ch': 0,
        'use_oth5_cp': 0,
        'use_oth5_ppr': 0,
        'use_oth5_mmpo': 0,
        'use_oth5_oez': 0,
        'use_oth5_ztk': 0,
        'note1': dev.note1,
        'status_use': dev.status_use.pk,
        'service_type': dev.service_type.pk,
        'note3': dev.note3,
        'id': dev.pk,
    }

    if len(main_cpl_use_fin) > 1:
        print('Внимание, для т.с. более одного основного места эксплуатации!')
    index = 0
    for item in main_cpl_use_fin:
        index += 1
        if isinstance(item[0], Rtu):
            initial['use_main{}_rtu'.format(index)] = item[0].pk
        elif isinstance(item[0], CustHouse):
            initial['use_main{}_ch'.format(index)] = item[0].pk
        elif isinstance(item[0], CustPost):
            initial['use_main{}_cp'.format(index)] = item[0].pk
        if isinstance(item[1], Ppr):
            initial['use_main{}_ppr'.format(index)] = item[1].pk
        elif isinstance(item[1], Mmpo):
            initial['use_main{}_mmpo'.format(index)] = item[1].pk
        elif isinstance(item[1], Oez):
            initial['use_main{}_oez'.format(index)] = item[1].pk
        elif isinstance(item[1], Ztk):
            initial['use_main{}_ztk'.format(index)] = item[1].pk

    if len(other_cpl_use_fin) > 5:
        print('Внимание, для т.с. более 5-ти вспомогат. мест эксплуатации!')
    index = 0
    for item in other_cpl_use_fin:
        index += 1
        if isinstance(item[0], Rtu):
            initial['use_oth{}_rtu'.format(index)] = item[0].pk
        elif isinstance(item[0], CustHouse):
            initial['use_oth{}_ch'.format(index)] = item[0].pk
        elif isinstance(item[0], CustPost):
            initial['use_oth{}_cp'.format(index)] = item[0].pk
        if isinstance(item[1], Ppr):
            initial['use_oth{}_ppr'.format(index)] = item[1].pk
        elif isinstance(item[1], Mmpo):
            initial['use_oth{}_mmpo'.format(index)] = item[1].pk
        elif isinstance(item[1], Oez):
            initial['use_oth{}_oez'.format(index)] = item[1].pk
        elif isinstance(item[1], Ztk):
            initial['use_oth{}_ztk'.format(index)] = item[1].pk

    if dev.type.si_flag is None:
        initial['si_flag'] = 0
    elif dev.type.si_flag is True:
        initial['si_flag'] = 1
    elif dev.type.si_flag is False:
        initial['si_flag'] = 2

    if dev.type.serial_flag is None:
        initial['serial_flag'] = 0
    elif dev.type.serial_flag is True:
        initial['serial_flag'] = 1
    elif dev.type.serial_flag is False:
        initial['serial_flag'] = 2

    if dev.is_si is None:
        initial['is_si'] = 0
    elif dev.is_si is True:
        initial['is_si'] = 1
    elif dev.is_si is False:
        initial['is_si'] = 2

    devdetailform = DevDetailForm(initial=initial)

    devdetailform.fields['serial_flag'].disabled = True
    devdetailform.fields['id'].disabled = True
    devdetailform.fields['si_flag'].disabled = True

    context = {
        'devdetailform': devdetailform,
    }
    template_name = 'dev_detail2.html'
    return render(request, template_name, context)


# def dev_create(request):
#     """Вью-функция для цели СОЗДАНИЯ НОВОГО одного прибора."""
#     if request.GET:
#         devdetailform = DevDetailForm(request.GET)
#         if devdetailform.is_valid():
#             print('Form is valid')
#         else:
#             print('Form is not valid!')
#     else:
#         devdetailform = DevDetailForm()
#     devdetailform.fields['id'].disabled = True
#     context = {
#         'devdetailform': devdetailform,
#     }
#     template_name = 'dev_detail2.html'
#     return render(request, template_name, context)
