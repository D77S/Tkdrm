"""."""
from django.shortcuts import render


def index(request):
    """."""
    template_name = 'mainpage/index.html'
    return render(request, template_name)
