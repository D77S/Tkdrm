"""."""
from django.shortcuts import render
from core.models import Device


def all_list(request):
    """."""
    template_name = 'all_list.html'
    all_dev_list = Device.objects.select_related('type')
    print(all_dev_list[:10])
    context = {
        'all_dev_list': all_dev_list,
    }
    return render(request, template_name, context)
