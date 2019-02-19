from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Item, ShoppingList
from .forms import ItemForm, ShoppingListForm
# Create your views here.

app_name = "shopping_list"


def index(request):
    item_list = Item.objects.order_by('id')  # will be cronological
    shopping_lists = ShoppingList.objects.order_by('id')
    shopping_list_form = ShoppingListForm()

    context = {
        'item_list': item_list,
        'shopping_lists': shopping_lists,
        'shopping_list_form': shopping_list_form
    }

    return render(request, 'shopping_list/index.html', context)


@require_POST
def add_item(request, shopping_list_id):
    shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
    form = ItemForm(request.POST)

    # to see in terminal if the input is sent
    print(request.POST['name'])
    print(request.POST['amount'])

    if form.is_valid():
        new_item = Item(
            name=request.POST['name'],
            amount=request.POST['amount'],
            shopping_list=shopping_list
        )
        new_item.save()

    shopping_list_id = new_item.shopping_list.id
    return shopping_list_details(request, shopping_list_id)


def bought_item(request, item_id):
    item = Item.objects.get(pk=item_id)
    item.bought = True
    item.save()
    shopping_list_id = item.shopping_list.id
    return shopping_list_details(request, shopping_list_id)


def not_bought_item(request, item_id):
    item = Item.objects.get(pk=item_id)
    item.bought = False
    item.save()
    shopping_list_id = item.shopping_list.id
    return shopping_list_details(request, shopping_list_id)


@require_POST
def delete_item(request, item_id):
    # item = Item.objects.filter(id__exact=item_id)
    item = Item.objects.get(pk=item_id)
    shopping_list_id = item.shopping_list.id
    item.delete()

    return shopping_list_details(request, shopping_list_id)


@require_POST
def create_list(request):
    shopping_list_form = ShoppingListForm(request.POST)

    # to see in terminal if the input is sent
    print(request.POST['title'])

    if shopping_list_form.is_valid():
        new_shopping_list = ShoppingList(
            title=request.POST['title']
        )
        new_shopping_list.save()

    return shopping_list_details(request, new_shopping_list.id)


def shopping_list_details(request, shopping_list_id):
    shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
    shopping_lists = ShoppingList.objects.order_by('id')
    shopping_list_form = ShoppingListForm()
    item_list = Item.objects.filter(shopping_list=shopping_list_id)
    item_form = ItemForm()

    context = {
        'shopping_list': shopping_list,
        'shopping_lists': shopping_lists,
        'shopping_list_form': shopping_list_form,
        'item_list': item_list,
        'item_form': item_form
    }

    return render(request, 'shopping_list/shoppinglist.html', context)


def delete_shopping_list(request, shopping_list_id):
    ShoppingList.objects.filter(pk=shopping_list_id).delete()

    return redirect('index')
