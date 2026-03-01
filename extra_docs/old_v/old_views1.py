"""."""
# import functools
# import sys
# import time
# from django.db import connection, reset_queries
# from django.core.paginator import Paginator
from django.db.models import QuerySet
# from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
# from core.constants import ALL_DEV_PAG
# from core.forms import DevDetailForm
from core.models import (
    # Rtu,
    # CustHouse,
    # CustPost,
    # Ppr,
    # Mmpo,
    # Oez,
    # Ztk,
    CustPlace1Use,
    CustPlaceToLocation,
    LocationOfUse,
    Device,
    RelToDev
)


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
