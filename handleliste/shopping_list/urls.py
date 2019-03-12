from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('add/<shopping_list_id>', views.add_item, name='add'),
    path('bought/<item_id>/<shopping_list_id>', views.bought_item, name='bought'),
    path('not-bought/<item_id>/<shopping_list_id>', views.not_bought_item, name='not-bought'),
    path('delete-item/<item_id>/<shopping_list_id>', views.delete_item, name='delete-item'),
    path('create-list/', views.create_list, name='create-list'),
    path('shopping-lists/<shopping_list_id>', views.shopping_list_details, name='detail'),
    path('delete-list/<shopping_list_id>', views.delete_shopping_list, name='delete-shopping-list'),
    path('share-list/<shopping_list_id>', views.share_shopping_list, name='share-shopping-list'),
    path('remove-user-from-list/<shopping_list_id>/<username>', views.remove_user_from_shopping_list, name='remove-user-from-shopping-list'),
    path('change-owner-of-list/<shopping_list_id>/<username>', views.change_owner_of_shopping_list, name='change-owner')
]
