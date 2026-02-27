from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import translation
from django.urls import reverse
from django.conf import settings

def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

def faq(request):
    return render(request, 'core/faq.html')

def set_language(request):
    """
    Standard Django language setting view
    """
    from django.views.i18n import set_language as django_set_language
    return django_set_language(request)
