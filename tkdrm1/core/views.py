"""."""
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from core.models import Device


def all_list(request):
    """."""
    template_name = 'all_list.html'
    # all_dev_list = Device.objects.select_related('type')[:10]
    all_dev_list = Device.objects.select_related().order_by('id')
    paginator = Paginator(all_dev_list, 10)
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
