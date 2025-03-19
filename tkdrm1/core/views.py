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
    # all_dev_list = Device.objects.select_related('type')[:10]
    all_dev_list = Device.objects.select_related(
        'type__category',
        'sour_type',
    ).prefetch_related(
        'from_dev'
    ).order_by('id')

    paginator = Paginator(all_dev_list, ALL_DEV_PAG)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    cust_pl_loc = []
    for dev in page_obj:
        temp_cp_to_loc = dev.from_dev.filter(is_main_for_dev=True).first().to_rel  # noqa
        temp2 = temp_cp_to_loc.cust_pl1
        if temp2.rtu is not None:
            temp3 = temp2.rtu
        elif temp2.custhouse is not None:
            temp3 = temp2.custhouse
        elif temp2.custpost is not None:
            temp3 = temp2.custpost
        cust_pl_loc.append(temp3)
    print(cust_pl_loc)
    context = {
        # 'all_dev': all_dev_list,
        'page_obj': page_obj,
        'cust_pl_loc': cust_pl_loc
    }
    return render(request, template_name, context)


def dev_detail(request, pk):
    """."""
    template_name = 'dev_detail.html'
    context = {'dev': get_object_or_404(Device, pk=pk)}
    return render(request, template_name, context)
