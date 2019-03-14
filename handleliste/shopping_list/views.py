from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib import messages

from .models import Item, ShoppingList
from .forms import ItemForm, ShoppingListForm, ShareForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from user import views, urls

# Create your views here.
User = get_user_model()
app_name = "shopping_list"


# Return the user's shopping lists
def get_user_shopping_lists(user):
    owned_shopping_lists = ShoppingList.objects.filter(owner=user)
    other_shopping_lists = ShoppingList.objects.filter(participants=user)
    other2_shopping_lists = ShoppingList.objects.filter(admins=user)
    my_shopping_lists = other_shopping_lists | owned_shopping_lists | other2_shopping_lists
    return my_shopping_lists.distinct().order_by('id')


# Check if user is member of shopping list
def user_is_member_of_shopping_list(user, shopping_list):
    return user == shopping_list.owner or user in shopping_list.participants.all() \
           or user in shopping_list.admins.all()


# Check if user has admin permissions
def user_has_admin_rights(user, shopping_list):
    return user in shopping_list.admins.all() or user == shopping_list.owner


# Redirect the user to the main site
@login_required(login_url='')
def index(request):
    my_shopping_lists = get_user_shopping_lists(request.user)
    shopping_list_form = ShoppingListForm()

    context = {
        'shopping_list_form': shopping_list_form,
        'my_shopping_lists': my_shopping_lists,          # List of shopping lists the user owns/participates in
    }

    return render(request, 'shopping_list/index.html', context)


# Redirect the user to look at the shopping list details
@login_required(login_url='')
def shopping_list_details(request, shopping_list_id):
    user = request.user
    try:
        shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. Could not view the shopping list.")
        return redirect('index')

    if not user_is_member_of_shopping_list(request.user, shopping_list):
        messages.error(request,
                       "You are not a member of the shopping list and therefore do not have permission to view it.")
        return redirect('index')

    my_shopping_lists = get_user_shopping_lists(user)
    shopping_list_form = ShoppingListForm()
    item_list = Item.objects.filter(shopping_list=shopping_list_id)

    context = {
        'shopping_list': shopping_list,             # ShoppingList which is being inspected by user
        'shopping_list_form': shopping_list_form,
        'item_list': item_list,                     # List of Item objects in the inspected ShoppingList
        'item_form': ItemForm(),
        'share_form': ShareForm(),
        'my_shopping_lists': my_shopping_lists,
    }

    return render(request, 'shopping_list/shoppinglist.html', context)


# Add item to a shopping list
@login_required(login_url='')
@require_POST
def add_item(request, shopping_list_id):
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. Could not add item to the shopping list.")
        return redirect('index')

    creator = request.user

    # Check if creator is a member of the list
    if not user_is_member_of_shopping_list(request.user, shopping_list):
        messages.error(request,
                       "Could not add item. You are not a member of the shopping list. ")
        return redirect('index')

    form = ItemForm(request.POST)
    if form.is_valid():
        new_item = Item(
            name=request.POST['name'],
            amount=request.POST['amount'],
            shopping_list=shopping_list,
            creator=creator
        )
        new_item.save()
        return redirect('detail', shopping_list_id)
    else:
        return redirect('index')


# Mark an item as bought
@login_required(login_url='')
def bought_item(request, item_id, shopping_list_id):
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. Could not mark item as bought.")
        return redirect('index')

    if not user_is_member_of_shopping_list(request.user, shopping_list):
        messages.error(request, "You are not a member of the shopping list. Could not mark item as bought.")
        return redirect('index')

    try:
        item = Item.objects.get(pk=item_id)
        item.bought = True
        item.save()
    except Item.DoesNotExist:
        messages.error(request, "The item has been deleted. Could not mark item as bought.")
    finally:
        return redirect('detail', shopping_list_id)


# Unmark an item as bought
@login_required(login_url='')
def not_bought_item(request, item_id, shopping_list_id):
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. Could not mark item as not bought.")
        return redirect('index')

    if not user_is_member_of_shopping_list(request.user, shopping_list):
        messages.error(request, "You are not a member of the shopping list. Could not make item as not bought.")
        return redirect('index')

    try:
        item = Item.objects.get(pk=item_id)
        item.bought = False
        item.save()
    except Item.DoesNotExist:
        messages.error(request, "The item has been deleted. Could not mark item as not bought.")
    finally:
        return redirect('detail', shopping_list_id)


# Delete an item of a shopping list
@login_required(login_url='')
@require_POST
def delete_item(request, item_id, shopping_list_id):
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. Could not delete item.")
        return redirect('index')

    if not user_is_member_of_shopping_list(request.user, shopping_list):
        messages.error(request, "You are not a member of the shopping list. Could not delete item.")
        return redirect('index')

    try:
        item = Item.objects.get(pk=item_id)
        shopping_list_id = item.shopping_list.id
        item.delete()
    finally:
        return redirect('detail', shopping_list_id)


# Create a shopping list and get redirected to see it as your view
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
        messages.error(request, "Something went wrong with creation of shopping list. Please try again.")
        return redirect('index')


# Delete a shopping list
@login_required(login_url='')
def delete_shopping_list(request, shopping_list_id):
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
        if request.user == shopping_list.owner:
            shopping_list.delete()
        else:
            messages.error(request, "You are not the owner of the shopping list. Could not delete the shopping list.")
            return redirect('index')
    finally:
        return redirect('index')


# Add another user to the shopping list as a participator
@login_required(login_url='')
@require_POST
def share_shopping_list(request, shopping_list_id):
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. Could not share the shopping list.")
        return redirect('index')
    share_form = ShareForm(request.POST)

    # Redirects the user to index if they are not a member of the shopping list
    if not user_is_member_of_shopping_list(request.user, shopping_list):
        messages.error(request, "You are not a member of the shopping list. Could not share the shopping list.")
        return redirect('index')

    if share_form.is_valid():
        shared_with_user = User.objects.get(username=request.POST['username'])
        if not user_is_member_of_shopping_list(shared_with_user, shopping_list):
            shopping_list.participants.add(shared_with_user)
    else:
        messages.error(request, "User does not exist. Please share with an existing user.")
    return redirect('detail', shopping_list_id)


# Remove another user from the shopping list
@login_required(login_url='')
def remove_user_from_shopping_list(request, shopping_list_id, username):
    current_user = request.user
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
        user_to_be_removed = User.objects.get(username=username)
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. Could not remove user from shopping list.")
        return redirect('index')
    except User.DoesNotExist:
        return HttpResponse('Error 400: Bad request.', status=400)

    if not user_has_admin_rights(current_user, shopping_list):
        messages.error(request, "You are do not have admin rights. Could not remove user.")
        return redirect('index')

    try:
        if user_to_be_removed in shopping_list.participants.all():
            shopping_list.participants.remove(user_to_be_removed)
        elif user_to_be_removed in shopping_list.admins.all():
            if current_user != shopping_list.owner and current_user != user_to_be_removed:
                messages.error(request, "Could not remove the user since the user is an admin. To remove an admin, you have to be the owner of the shopping list")
                return redirect('index')
            shopping_list.admins.remove(user_to_be_removed)
    finally:
        # If the current user is leaves the shopping list, redirect to index
        # Else, if the current user kicks another user, redirect to the shopping list
        if current_user == user_to_be_removed:
            return redirect('index')
        return redirect('detail', shopping_list_id)


# Change the owner of a shopping list
@login_required(login_url='')
def change_owner_of_shopping_list(request, shopping_list_id, username):

    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
        new_owner = User.objects.get(username=username)
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. Could not change the owner of shopping list.")
        return redirect('index')
    except User.DoesNotExist:
        return HttpResponse('Error 400: Bad request.')

    if request.user != shopping_list.owner:
        return HttpResponse('Error 403: Forbidden. User does not have permission to change the owner of the shopping list.',
                            status=403)

    if not user_is_member_of_shopping_list(request.user, shopping_list):
        messages.error(request,
                       "Could not give ownership to another user. You are not a member of the shopping list. ")
        return redirect('index')

    if new_owner in shopping_list.admins.all():
        shopping_list.admins.remove(new_owner)
    else:
        # The new owner must be a admin of the shopping list to be able to become the owner of the list
        messages.error(request, "Could not give ownership of shopping list to the user. The user must be an admin of the shopping list.")
        return redirect('detail', shopping_list_id)
    shopping_list.owner = new_owner
    shopping_list.save()
    return redirect('index')


# Promote a participant to an admin of a shopping list
def make_user_admin_of_shopping_list(request, shopping_list_id, username):
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
        user = User.objects.get(username=username)
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. Could not make user an admin of the shopping list.")
        return redirect('index')
    except User.DoesNotExist:
        return HttpResponse('Error 400: Bad request.', status=400)

    if not user_is_member_of_shopping_list(request.user, shopping_list):
        messages.error(request,
                       "Could not make the user an admin. You are not a member of the shopping list. ")
        return redirect('index')

    if not user_has_admin_rights(request.user, shopping_list):
        messages.error(request,
                       "You do not have permission to make another user admin. You need to be an admin or owner of shopping list to do so.")
        return redirect('detail', shopping_list_id)

    try:
        shopping_list.admins.add(user)
        shopping_list.participants.remove(user)
    finally:
        return redirect('detail', shopping_list_id)