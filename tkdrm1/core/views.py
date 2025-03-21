"""."""
from typing import Union
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from core.constants import ALL_DEV_PAG
from core.models import Device, RelToDev


def all_list(request: HttpRequest):
    """."""
    template_name = 'all_list.html'
    all_dev_list = Device.objects.all().order_by('id')
    paginator = Paginator(all_dev_list, ALL_DEV_PAG)
    page_number = request.GET.get('page')
    curr_page_obj = paginator.get_page(page_number)
    curr_page_ids = []
    for dev in curr_page_obj.object_list:
        curr_page_ids.append(dev.id)

    curr_page_dev_list = Device.objects.filter(
        id__in=curr_page_ids).select_related(
        'type__category',
        'sour_type',
    ).prefetch_related(
        'from_dev'
    ).order_by('id')

    curr_extra_page_obj = []
    offset = (curr_page_obj.number - 1) * ALL_DEV_PAG
    i = 0
    for dev in curr_page_dev_list:
        i += 1
        temp_cp_to_loc = dev.from_dev.filter(is_main_for_dev=True).first().to_rel  # noqa
        temp2 = temp_cp_to_loc.cust_pl1
        if temp2.rtu is not None:
            currcp1loc = temp2.rtu
        elif temp2.custhouse is not None:
            currcp1loc = temp2.custhouse
        elif temp2.custpost is not None:
            currcp1loc = temp2.custpost
        curr_extra_page_obj.append([i + offset, dev, currcp1loc])
    print(curr_extra_page_obj)

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
