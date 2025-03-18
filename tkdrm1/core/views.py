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
        'cp1_acc__rtu',
        'cp1_acc__custhouse',
        'cp1_acc__custpost',
        'cp2_acc',
        'sour_type',
    ).prefetch_related(
        'from_dev'
    ).order_by('id')
    temp_dev: Device = all_dev_list.first()
    temp = temp_dev.from_dev.filter(is_main_for_dev=True)
    print(temp)
    paginator = Paginator(all_dev_list, ALL_DEV_PAG)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj,
               'all_dev': all_dev_list}
    return render(request, template_name, context)


def dev_detail(request, pk):
    """."""
    template_name = 'dev_detail.html'
    context = {'dev': get_object_or_404(Device, pk=pk)}
    return render(request, template_name, context)
