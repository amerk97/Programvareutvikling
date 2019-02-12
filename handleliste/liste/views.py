from django.shortcuts import render
from django.http import HttpResponse


def liste(request):
    return render(request, 'liste/liste.html', {'title': 'List'})




# Create your views here.
