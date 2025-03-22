"""."""
import functools
import sys
import time
from django.db import connection, reset_queries
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from core.constants import ALL_DEV_PAG
from core.models import CustPlace1Use, CustPlaceToLocation, Device, RelToDev


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()
        start_queries = len(connection.queries)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        end_queries = len(connection.queries)
        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result
    return inner_func


@query_debugger
def all_list(request: HttpRequest):
    """."""
    template_name = 'all_list.html'
    all_dev_list = Device.objects.all().order_by('id')
    paginator = Paginator(all_dev_list, ALL_DEV_PAG)
    page_number = request.GET.get('page')
    curr_page_obj = paginator.get_page(page_number)

    curr_page_ids = [i.id for i in curr_page_obj]
    curr_page_devs_qset = Device.objects.filter(
        id__in=curr_page_ids).select_related(
        'type__category',
        'sour_type',
    ).order_by('id')
    curr_page_dev_objs_lst = [i for i in curr_page_devs_qset]

    curr_page_reltodevs = RelToDev.objects.filter(
        to_dev__in=curr_page_ids, is_main_for_dev=True
        ).select_related(
            'to_dev',
            'to_rel',
            'to_rel__cust_pl1',
            'to_rel__cust_pl1__rtu',
            'to_rel__cust_pl1__custhouse',
            'to_rel__cust_pl1__custpost'
        )

    curr_page_reltodevs_objs = [i for i in curr_page_reltodevs]
    curr_page_cpltoloc_ids = [i.to_rel_id for i in curr_page_reltodevs_objs]

    curr_page_cpllocs_qset = CustPlaceToLocation.objects.filter(
        id__in=curr_page_cpltoloc_ids
    )

    curr_page_cpllocs_objs = [i for i in curr_page_cpllocs_qset]

    curr_page_cpluses_ids = [i.id for i in curr_page_cpllocs_objs]

    curr_page_cpluses_objs = CustPlace1Use.objects.filter(
        id__in=curr_page_cpluses_ids).select_related(
            'rtu',
            'custhouse',
            'custpost'
        )

    curr_page_cpluses_list = [i for i in curr_page_cpluses_objs]

    curr_page_cpl1s = []

    for i in curr_page_cpluses_list:
        if i.rtu is not None:
            curr_page_cpl1s.append(i.rtu)
        elif i.custhouse is not None:
            curr_page_cpl1s.append(i.custhouse)
        elif i.custpost is not None:
            curr_page_cpl1s.append(i.custpost)

    curr_extra_page_obj = []
    offset = (curr_page_obj.number - 1) * ALL_DEV_PAG
    i = 0

    # for dev in curr_page_dev_objs_lst:
    #     i += 1
    #     temp = dev.from_dev.filter(is_main_for_dev=True).first()
    #     if temp is None:
    #         curr_extra_page_obj.append([i + offset, dev, None])
    #         continue
    #     temp2 = temp.to_rel.cust_pl1
    #     if temp.rtu is not None:
    #         currcp1loc = temp.rtu
    #     elif temp.custhouse is not None:
    #         currcp1loc = temp.custhouse
    #     elif temp.custpost is not None:
    #         currcp1loc = temp.custpost
    #     curr_extra_page_obj.append([i + offset, dev, currcp1loc])

    for dev in curr_page_dev_objs_lst:
        i += 1
        temp = []
        for rel_to_dev in curr_page_reltodevs_objs:
            if (rel_to_dev.to_dev == dev and
               rel_to_dev.is_main_for_dev is True):
                temp.append(rel_to_dev)
        if temp == []:
            curr_extra_page_obj.append([i + offset, dev, None])
            continue
        temp3 = temp[0].to_rel.cust_pl1
        if temp3.rtu is not None:
            temp4 = temp3.rtu
        elif temp3.custhouse is not None:
            temp4 = temp3.custhouse
        elif temp3.custpost is not None:
            temp4 = temp3.custpost
        curr_extra_page_obj.append([i + offset, dev, temp4])

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
