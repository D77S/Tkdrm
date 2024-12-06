"""."""
from django.shortcuts import render


def all_list(request):
    """."""
    template_name = 'all_list.html'
    return render(request, template_name)
