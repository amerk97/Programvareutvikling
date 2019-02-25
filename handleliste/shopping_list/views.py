from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Item, ShoppingList
from .forms import ItemForm, ShoppingListForm, ShareForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

# Create your views here.
User = get_user_model()
app_name = "shopping_list"


@login_required(login_url='')                     # TODO: add url
def index(request):
    user = request.user                                 # TODO: check if it is logged in and if the user exists
    owned_shopping_lists = ShoppingList.objects.filter(owner=user)
    other_shopping_lists = ShoppingList.objects.filter(participants=user)
    my_shopping_lists = owned_shopping_lists | other_shopping_lists
    shopping_list_form = ShoppingListForm()

    context = {
        'shopping_list_form': shopping_list_form,
        'my_shopping_lists': my_shopping_lists          # List of shopping lists the user owns/participates in
    }

    return render(request, 'shopping_list/index.html', context)


@require_POST
def add_item(request, shopping_list_id):
    shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
    form = ItemForm(request.POST)                       # TODO: check if user is a participator of list
    creator = request.user                              # TODO: check if user exists and is logged in

    if form.is_valid():
        new_item = Item(
            name=request.POST['name'],
            amount=request.POST['amount'],
            shopping_list=shopping_list,
            creator=creator
        )
        new_item.save()
        shopping_list_id = new_item.shopping_list.id
        return redirect('detail', shopping_list_id)
    else:
        return redirect('index')


def bought_item(request, item_id):
    item = Item.objects.get(pk=item_id)
    item.bought = True
    item.save()
    shopping_list_id = item.shopping_list.id

    return redirect('detail', shopping_list_id)


def not_bought_item(request, item_id):
    item = Item.objects.get(pk=item_id)
    item.bought = False
    item.save()
    shopping_list_id = item.shopping_list.id

    return redirect('detail', shopping_list_id)


@require_POST
def delete_item(request, item_id):
    item = Item.objects.get(pk=item_id)
    shopping_list_id = item.shopping_list.id
    item.delete()

    return redirect('detail', shopping_list_id)


@require_POST
def create_list(request):
    shopping_list_form = ShoppingListForm(request.POST)
    owner = request.user                                # TODO: check if user exists and is logged in

    if shopping_list_form.is_valid():
        new_shopping_list = ShoppingList(
            title=request.POST['title'],
            owner=owner
        )
        new_shopping_list.save()
        return redirect('detail', new_shopping_list.id)
    else:
        return redirect('index')


def shopping_list_details(request, shopping_list_id):
    shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
    shopping_lists = ShoppingList.objects.order_by('id')
    shopping_list_form = ShoppingListForm()
    item_list = Item.objects.filter(shopping_list=shopping_list_id)
    item_form = ItemForm()
    share_form = ShareForm()                            # TODO: check if user is a owner/participator of the list
    user = request.user                                 # TODO: check if user exists and is logged in
    owned_shopping_lists = ShoppingList.objects.filter(owner=user)
    other_shopping_lists = ShoppingList.objects.filter(participants=user)
    my_shopping_lists = owned_shopping_lists | other_shopping_lists

    context = {
        'shopping_list': shopping_list,             # ShoppingList which is being inspected by user
        'shopping_lists': shopping_lists,           # List of ShoppingList objects
        'shopping_list_form': shopping_list_form,
        'item_list': item_list,                     # List of Item objects in the inspected ShoppingList
        'item_form': item_form,
        'share_form': share_form,
        'my_shopping_lists': my_shopping_lists,
    }

    return render(request, 'shopping_list/shoppinglist.html', context)


def delete_shopping_list(request, shopping_list_id):
    ShoppingList.objects.filter(pk=shopping_list_id).delete()

    return redirect('index')


@require_POST
def share_shopping_list(request, shopping_list_id):
    shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
    share_form = ShareForm(request.POST)

    if share_form.is_valid():
        username = request.POST['username']
        user = User.objects.get(username=username)
        if shopping_list.owner != user:
            shopping_list.participants.add(user)
        return redirect('detail', shopping_list_id)
    else:
        return redirect('index')

