from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from .models import Item, ShoppingList
from .forms import ItemForm, ShoppingListForm, ShareForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from user import views, urls

# Create your views here.
User = get_user_model()
app_name = "shopping_list"

# Return the user's shopping lists
def get_users_shopping_lists(user):
    owned_shopping_lists = ShoppingList.objects.filter(owner=user)
    other_shopping_lists = ShoppingList.objects.filter(participants=user)
    my_shopping_lists = other_shopping_lists | owned_shopping_lists
    return my_shopping_lists.distinct().order_by('id')


@login_required(login_url='')
def index(request):
    user = request.user
    my_shopping_lists = get_users_shopping_lists(user)
    shopping_list_form = ShoppingListForm()

    context = {
        'shopping_list_form': shopping_list_form,
        'my_shopping_lists': my_shopping_lists          # List of shopping lists the user owns/participates in
    }

    return render(request, 'shopping_list/index.html', context)


@login_required(login_url='')
@require_POST
def add_item(request, shopping_list_id):
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        # The shopping list was deleted while item was added
        redirect('index')

    form = ItemForm(request.POST)
    creator = request.user

    # Check if creator is a participator of list
    if creator != shopping_list.owner and creator not in shopping_list.participants.all():
        return HttpResponse('Error 401: Unauthorized. User does not have permission to add item.', status=401)

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


def bought_item(request, item_id, shopping_list_id):
    try:
        item = Item.objects.get(pk=item_id)
        item.bought = True
        item.save()
    finally:
        return redirect('detail', shopping_list_id)


def not_bought_item(request, item_id, shopping_list_id):
    try:
        item = Item.objects.get(pk=item_id)
        item.bought = False
        item.save()
    finally:
        return redirect('detail', shopping_list_id)


@require_POST
def delete_item(request, item_id, shopping_list_id):
    try:
        item = Item.objects.get(pk=item_id)
        shopping_list_id = item.shopping_list.id
        item.delete()
    finally:
        return redirect('detail', shopping_list_id)


@login_required(login_url='')
@require_POST
def create_list(request):
    shopping_list_form = ShoppingListForm(request.POST)
    owner = request.user

    if shopping_list_form.is_valid():
        new_shopping_list = ShoppingList(
            title=request.POST['title'],
            owner=owner
        )
        new_shopping_list.save()
        return redirect('detail', new_shopping_list.id)
    else:
        return redirect('index')


@login_required(login_url='')
def shopping_list_details(request, shopping_list_id):
    user = request.user
    shopping_list = ShoppingList.objects.get(pk=shopping_list_id)

    # Check if the user is a participator of the shopping list
    if user != shopping_list.owner and user not in shopping_list.participants.all():
        return HttpResponse('Error 401: Unauthorized. User does not have permission to view this shopping list.', status=401)

    my_shopping_lists = get_users_shopping_lists(user)
    shopping_list_form = ShoppingListForm()
    item_list = Item.objects.filter(shopping_list=shopping_list_id)
    item_form = ItemForm()
    share_form = ShareForm()

    context = {
        'shopping_list': shopping_list,             # ShoppingList which is being inspected by user
        'shopping_list_form': shopping_list_form,
        'item_list': item_list,                     # List of Item objects in the inspected ShoppingList
        'item_form': item_form,
        'share_form': share_form,
        'my_shopping_lists': my_shopping_lists,
    }

    return render(request, 'shopping_list/shoppinglist.html', context)


@login_required(login_url='')
def delete_shopping_list(request, shopping_list_id):
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)
        if request.user == shopping_list.owner:
            shopping_list.delete()
        else:
            return HttpResponse('Error 401: Unauthorized. User does not have permission to delete shopping list.', status=401)
    finally:
        return redirect('index')


@login_required(login_url='')
@require_POST
def share_shopping_list(request, shopping_list_id):
    shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
    share_form = ShareForm(request.POST)
    shopping_list_form = ShoppingListForm()
    item_list = Item.objects.filter(shopping_list=shopping_list_id)
    item_form = ItemForm()
    user = request.user
    my_shopping_lists = get_users_shopping_lists(user)

    if share_form.is_valid():
        username = request.POST['username']
        try:
            shared_with_user = User.objects.get(username=username)
        except User.DoesNotExist:
            message = 'User does not exist. Please enter an existing username.'
            context = {
                'message': message,
                'shopping_list': shopping_list,
                'my_shopping_lists': my_shopping_lists,
                'item_list': item_list,
                'item_form': item_form,
                'shopping_list_form': shopping_list_form,
                'share_form': share_form
            }
            return render(request, 'shopping_list/share_error_message.html', context)
        if shopping_list.owner != shared_with_user:
            shopping_list.participants.add(shared_with_user)
        return redirect('detail', shopping_list_id)
    else:
        return redirect('index')


@login_required(login_url='')
def remove_user_from_shopping_list(request, shopping_list_id, username):
    current_user = request.user

    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        # The shopping list has been deleted while this request was made
        return redirect('index')

    user = User.objects.get(username=username)
    try:
        if user == current_user and user == shopping_list.owner:
            change_owner_of_shopping_list(shopping_list_id, username)
        elif user in shopping_list.participants.all():
            shopping_list.participants.remove(user)
        elif user in shopping_list.admins.all():
            shopping_list.admins.remove(user)
    finally:
        # If the current user is removed from shopping list, redirect to index
        # Else redirect to the current shopping list
        if current_user == user:
            return redirect('index')
        return redirect('detail', shopping_list_id)


def change_owner_of_shopping_list(request, shopping_list_id, username):
    shopping_list = ShoppingList.objects.filter(pk=shopping_list_id).update(owner=User(username=username))


def make_user_admin_of_shopping_list(request, shopping_list_id, username):
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        # The shopping list was deleted while this request was made
        return redirect('index')

    user = User.objects.get(username=username)

    try:
        shopping_list.participants.remove(user)
        shopping_list.admins.add(user)
    except:
        # Something went wrong
        return redirect('index')
    finally:
        return redirect('detail', shopping_list_id)
