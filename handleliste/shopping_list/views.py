from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib import messages

from .models import Item, ShoppingList, Comment, Reply
from .forms import ItemForm, ShoppingListForm, ShareForm, CommentForm, ReplyForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from user import views, urls

# Create your views here.
User = get_user_model()
app_name = "shopping_list"


# Redirect the user to the main site
@login_required(login_url='')
def index(request):
    my_shopping_lists = ShoppingList.get_user_shopping_lists(request.user)
    shopping_list_form = ShoppingListForm()

    context = {
        'shopping_list_form': shopping_list_form,
        'my_shopping_lists': my_shopping_lists,          # List of shopping lists the user owns/participates in
    }

    return render(request, 'shopping_list/index.html', context)


# Redirect the user to look at the shopping list details
@login_required(login_url='')
def shopping_list_details(request, shopping_list_id):
    error_message = 'Could not view the shopping list.'
    user = request.user
    try:
        shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
    except ShoppingList.DoesNotExist:
        messages.error(request, 'The shopping list has either been deleted or you might not have permission to view it. ' + error_message)
        return redirect('index')

    if not shopping_list.user_is_member(request.user):
        messages.error(request, 'You are not a member of the shopping list. ' + error_message)
        return redirect('index')

    my_shopping_lists = ShoppingList.get_user_shopping_lists(user)
    shopping_list_form = ShoppingListForm()
    item_list = Item.objects.filter(shopping_list=shopping_list_id)
    comments = Comment.objects.filter(shopping_list=shopping_list).order_by("date")
    comment_form = CommentForm()
    reply_form = ReplyForm()

    context = {
        'shopping_list': shopping_list,             # ShoppingList which is being inspected by user
        'shopping_list_form': shopping_list_form,
        'item_list': item_list,                     # List of Item objects in the inspected ShoppingList
        'item_form': ItemForm(),
        'comments': comments,
        'share_form': ShareForm(),
        'my_shopping_lists': my_shopping_lists,
        'comment_form': comment_form,
        'reply_form': reply_form
    }

    return render(request, 'shopping_list/shoppinglist.html', context)


# Add item to a shopping list
@login_required(login_url='')
@require_POST
def add_item(request, shopping_list_id):
    error_message = 'Could not add item to the shopping list.'
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, 'The shopping list has been deleted. ' + error_message)
        return redirect('index')

    creator = request.user

    if not shopping_list.user_is_member(request.user):
        messages.error(request, 'You are not a member of the shopping list. ' + error_message)
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
    error_message = 'Could not mark item as bought.'
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, 'The shopping list has been deleted. ' + error_message)
        return redirect('index')

    if not shopping_list.user_is_member(request.user):
        messages.error(request, 'You are not a member of the shopping list. ' + error_message)
        return redirect('index')

    try:
        item = Item.objects.get(pk=item_id)
        item.bought = True
        item.save()
    except Item.DoesNotExist:
        messages.error(request, 'The item has been deleted. ' + error_message)
    finally:
        return redirect('detail', shopping_list_id)


# Unmark an item as bought
@login_required(login_url='')
def not_bought_item(request, item_id, shopping_list_id):
    error_message = 'Could not mark item as not bought.'
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, 'The shopping list has been deleted. ' + error_message)
        return redirect('index')

    if not shopping_list.user_is_member(request.user):
        messages.error(request, 'You are not a member of the shopping list. ' + error_message)
        return redirect('index')

    try:
        item = Item.objects.get(pk=item_id)
        item.bought = False
        item.save()
    except Item.DoesNotExist:
        messages.error(request, 'The item has been deleted. ' + error_message)
    finally:
        return redirect('detail', shopping_list_id)


# Delete an item of a shopping list
@login_required(login_url='')
@require_POST
def delete_item(request, item_id, shopping_list_id):
    error_message = 'Could not delete item.'
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, 'The shopping list has been deleted. ' + error_message)
        return redirect('index')

    if not shopping_list.user_is_member(request.user):
        messages.error(request, 'You are not a member of the shopping list. ' + error_message)
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
    error_message = 'Could not delete the shopping list.'
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
        if request.user == shopping_list.owner:
            shopping_list.delete()
            messages.success(request, "Successfully deleted the shopping list!")
        else:
            messages.error(request, 'You are not the owner of the shopping list. ' + error_message)
    finally:
        return redirect('index')


# Add another user to the shopping list as a participator
@login_required(login_url='')
@require_POST
def share_shopping_list(request, shopping_list_id):
    error_message = 'Could not share the shopping list.'
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, 'The shopping list has been deleted. ' + error_message)
        return redirect('index')
    share_form = ShareForm(request.POST)

    if not shopping_list.user_is_member(request.user):
        messages.error(request, 'You are not a member of the shopping list. ' + error_message)
        return redirect('index')

    if share_form.is_valid():
        shared_with_user = User.objects.get(username=request.POST['username'])
        if not shopping_list.user_is_member(shared_with_user):
            shopping_list.participants.add(shared_with_user)
    else:
        messages.error(request, "User does not exist. Please share with an existing user.")
    return redirect('detail', shopping_list_id)


# Remove another user from the shopping list
@login_required(login_url='')
def remove_user_from_shopping_list(request, shopping_list_id, username):
    current_user = request.user
    error_message = 'Could not remove user from shopping list.'
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
        user_to_be_removed = User.objects.get(username=username)
    except ShoppingList.DoesNotExist:
        messages.error(request, 'The shopping list has been deleted. ')
        return redirect('index')
    except User.DoesNotExist:
        return HttpResponse('Error 400: Bad request.', status=400)

    if not shopping_list.user_is_member(request.user):
        messages.error(request, "You are not a member of the shopping list. " + error_message)
        return redirect('index')

    if not shopping_list.user_has_admin_rights(current_user) and current_user != user_to_be_removed:
        messages.error(request, 'You are do not have admin rights. ' + error_message)
        return redirect('detail', shopping_list_id)

    try:
        if user_to_be_removed in shopping_list.participants.all():
            shopping_list.participants.remove(user_to_be_removed)
        elif user_to_be_removed in shopping_list.admins.all():
            if current_user != shopping_list.owner and current_user != user_to_be_removed:
                messages.error(request,
                               "To remove an admin, you must be the owner of the shopping list. " + error_message)
                return redirect('index')
            shopping_list.admins.remove(user_to_be_removed)
    finally:
        # If the current user is leaves the shopping list, redirect to index
        # Else, if the current user kicks another user, redirect to the shopping list
        if current_user == user_to_be_removed:
            messages.success(request, "Successfully left the shopping list!")
            return redirect('index')
        return redirect('detail', shopping_list_id)


# Change the owner of a shopping list
@login_required(login_url='')
def change_owner_of_shopping_list(request, shopping_list_id, username):
    error_message = 'Could not change the owner of shopping list.'

    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
        new_owner = User.objects.get(username=username)
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. " + error_message)
        return redirect('index')
    except User.DoesNotExist:
        return HttpResponse('Error 400: Bad request.')

    if not shopping_list.user_is_member(request.user):
        messages.error(request, "You are not a member of the shopping list. " + error_message)
        return redirect('index')

    if request.user != shopping_list.owner:
        return HttpResponse('Error 403: Forbidden. User does not have permission to change the owner of the shopping list.',
                            status=403)

    if new_owner in shopping_list.admins.all():
        shopping_list.admins.remove(new_owner)
        shopping_list.owner = new_owner
        shopping_list.save()
        messages.success(request, 'Successfully changed the owner of the shopping list! You have left the shopping list.')
        return redirect('index')
    else:
        # The new owner must be a admin of the shopping list to be able to become the owner of the list
        messages.error(request, "The new owner must be an admin of the shopping list." + error_message)
        return redirect('detail', shopping_list_id)


# Promote a participant to an admin of a shopping list
def make_user_admin_of_shopping_list(request, shopping_list_id, username):
    error_message = 'Could not make user an admin of the shopping list.'
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
        user = User.objects.get(username=username)
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. " + error_message)
        return redirect('index')
    except User.DoesNotExist:
        return HttpResponse('Error 400: Bad request.', status=400)

    if not shopping_list.user_is_member(request.user):
        messages.error(request, "You are not a member of the shopping list. " + error_message)
        return redirect('index')

    if not shopping_list.user_has_admin_rights(request.user):
        messages.error(request,
                       "You must an admin/owner of shopping list to promote a participant to an admin. " + error_message)
        return redirect('detail', shopping_list_id)

    if not shopping_list.user_is_member(user):
        messages.error(request, f"{user} is not a member of the shopping list. " + error_message)

    try:
        shopping_list.admins.add(user)
        shopping_list.participants.remove(user)
    finally:
        return redirect('detail', shopping_list_id)


# Add comment to a shopping list
@login_required(login_url='')
@require_POST
def add_comment(request, shopping_list_id):
    error_message = 'Could not add comment.'
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, "The shopping list has been deleted. " + error_message)
        return redirect('index')

    if not shopping_list.user_is_member(request.user):
        messages.error(request, "You are not a member of the shopping list. " + error_message)
        return redirect('index')

    form = CommentForm(request.POST)
    if form.is_valid():
        new_comment = Comment(
            author=request.user,
            content=request.POST['content'],
            shopping_list=shopping_list
        )
        new_comment.save()
        return redirect('detail', shopping_list_id)
    else:
        for msg in form.errors:
            messages.error(request, f"{form.errors[msg]}")
        return redirect('detail', shopping_list_id)


@login_required(login_url='')
def delete_comment(shopping_list_id, comment_id):
    error_message = "Could not delete comment."
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.success(request, "The shopping list has been deleted by another user. Your comment was successfully deleted with it.")
        return redirect('index')

    try:
        comment = Comment.objects.filter(pk=comment_id)
    except Comment.DoesNotExist:
        if shopping_list.user_is_member(request.user):
            messages.success(request, "The comment has already been deleted.")
            return redirect('detail', shopping_list_id)
        else:
            messages.error(request, "You are not a member of the shopping list. " + error_message)
            return redirect('index')

    if not shopping_list.user_is_member(request.user):
        messages.error(request, "You are not a member of the shopping list. " + error_message)
        return redirect('index')

    if not shopping_list.user_has_admin_rights(request.user) and request.user != comment.author:
        messages.error(request, "You do not have permission to delete this comment. " +
                                "You must be the author or have admin rights to do so. " + error_message)
        return redirect('detail, shopping_list_id')

    comment.delete()
    messages.success(request, "Successfully deleted the comment!")
    return redirect('detail', shopping_list_id)


# Add reply to a comment
@login_required(login_url='')
@require_POST
def reply(request, shopping_list_id, comment_id):
    error_message = 'Could not reply to this comment.'
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.error(request, 'This shopping list does not exist.' + error_message)
        return redirect('index')

    try:
        comment = Comment.objects.filter(pk=comment_id)[0]
    except Comment.DoesNotExist:
        if shopping_list.user_is_member(request.user):
            messages.error(request, "The comment was deleted by another user. " + error_message)
            return redirect('detail', shopping_list_id)
        else:
            messages.error(request, "You are not a member of the shopping list. " + error_message)
            return redirect('index')

    if not shopping_list.user_is_member(request.user):
        messages.error(request, "You are not a member of the shopping list. " + error_message)
        return redirect('index')

    form = ReplyForm(request.POST)
    if form.is_valid():
        new_item = Reply(
            author=request.user,
            content=request.POST['content'],
            parent_comment=comment
        )
        new_item.save()
    else:
        messages.error(request, 'The form was invalid.')
    return redirect('detail', shopping_list_id)


# Delete reply
def delete_reply(request,  shopping_list_id, reply_id):
    error_message = "Could not delete reply."
    try:
        shopping_list = ShoppingList.objects.filter(pk=shopping_list_id)[0]
    except ShoppingList.DoesNotExist:
        messages.success(request, "The shopping list has been deleted by another user. Your reply was successfully deleted with it.")
        return redirect('index')

    try:
        reply = Reply.objects.filter(pk=reply_id)[0]
    except Reply.DoesNotExist:
        if shopping_list.user_is_member(request.user):
            messages.success(request, "Successfully deleted the reply!")
            return redirect('detail', shopping_list_id)
        else:
            messages.error(request, "You are not a member of the shopping list. " + error_message)
            return redirect('index')

    if not shopping_list.user_is_member(request.user):
        messages.error(request, "You are not a member of the shopping list. " + error_message)
        return redirect('index')

    if not shopping_list.user_has_admin_rights(request.user) and request.user != reply.author:
        messages.error(request, "You do not have permission to delete this reply. " +
                                "You must be the author or have admin rights to do so. " + error_message)
        return redirect('detail, shopping_list_id')

    reply.delete()
    messages.success(request, "Successfully deleted the comment!")
    return redirect('detail', shopping_list_id)
