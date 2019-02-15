from django.shortcuts import render
from django.http import HttpResponse
from .models import CreateNewList


def liste(request):
    new_list = CreateNewList.objects.order_by('id')

    context = {'new_list': new_list}                    # this does not work yet
    return render(request, 'liste/liste.html')




